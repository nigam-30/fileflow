import os
import hashlib
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
from send2trash import send2trash

IGNORE_DIRS = {
    '.git', '.svn', '.hg', 'node_modules', '__pycache__', 
    '.pytest_cache', '$recycle.bin', 'system volume information',
    '.vscode', '.idea'
}

class DuplicateFinder:
    @staticmethod
    def get_dual_sample_hash(filepath: str, sample_size: int = 8192) -> Optional[str]:
        """
        Fast Stage-2 filter: Read the first 8 KB and last 8 KB of the file.
        Files of identical size almost always differ at the head (header/metadata)
        or the tail (content/footer). This eliminates 99.9% of non-duplicates in microseconds
        without having to read megabytes or gigabytes of file payload.
        """
        try:
            size = os.path.getsize(filepath)
            hasher = hashlib.md5()
            with open(filepath, 'rb') as f:
                head = f.read(sample_size)
                hasher.update(head)
                if size > sample_size * 2:
                    f.seek(size - sample_size)
                    tail = f.read(sample_size)
                    hasher.update(tail)
            return hasher.hexdigest()
        except (IOError, OSError, PermissionError):
            return None

    @staticmethod
    def get_file_hash(filepath: str, chunk_size: int = 262144) -> Optional[str]:
        """
        Full Stage-3 cryptographic verification: Compute complete SHA-256 hash.
        Uses an optimized 256 KB buffer for high-throughput disk reads.
        """
        hasher = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (IOError, OSError, PermissionError):
            return None

    @staticmethod
    def verify_byte_for_byte(file1: str, file2: str, chunk_size: int = 262144) -> bool:
        """
        Stage-4 Bit-for-Bit binary verification (as used by fdupes / jdupes).
        Guarantees 100% identical data with zero hash collision risk.
        """
        try:
            with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
                while True:
                    b1 = f1.read(chunk_size)
                    b2 = f2.read(chunk_size)
                    if b1 != b2:
                        return False
                    if not b1:
                        return True
        except (IOError, OSError, PermissionError):
            return False

    @classmethod
    def scan_folder(cls, folder_path: str, recursive: bool = True) -> List[Dict[str, Any]]:
        """
        Scans a folder and returns confirmed duplicate file groups using
        a high-performance 4-stage progressive filtering pipeline:
          Stage 1: Exact File Size grouping (filters out 99% of unique files instantly)
          Stage 2: Head + Tail Dual Partial Hash (rapid weed-out without full disk reads)
          Stage 3: Full SHA-256 Cryptographic Checksum (in parallel across CPU threads)
          Stage 4: Bit-for-Bit Direct Binary Verification
        """
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            return []

        # --- Stage 1: Group files by exact byte size ---
        size_groups: Dict[int, List[str]] = {}
        for root, dirs, files in os.walk(folder_path):
            # Prune ignored system/cache folders
            dirs[:] = [d for d in dirs if d.lower() not in IGNORE_DIRS]

            for file in files:
                full_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(full_path)
                    if size > 0:  # Skip 0-byte files
                        size_groups.setdefault(size, []).append(full_path)
                except (IOError, OSError, PermissionError):
                    continue

            if not recursive:
                break

        # Filter only sizes with 2 or more files
        candidate_size_groups = {s: paths for s, paths in size_groups.items() if len(paths) > 1}
        if not candidate_size_groups:
            return []

        # --- Stage 2: Fast Head + Tail Partial Hash ---
        # Flatten candidate paths for fast parallel hashing
        paths_to_sample = [p for paths in candidate_size_groups.values() for p in paths]
        partial_hashes: Dict[str, Optional[str]] = {}
        with ThreadPoolExecutor(max_workers=min(16, (os.cpu_count() or 4) * 2)) as executor:
            results = executor.map(cls.get_dual_sample_hash, paths_to_sample)
            for path, p_hash in zip(paths_to_sample, results):
                partial_hashes[path] = p_hash

        quick_hash_groups: Dict[str, List[str]] = {}
        for size, file_paths in candidate_size_groups.items():
            for path in file_paths:
                p_hash = partial_hashes.get(path)
                if p_hash:
                    key = f"{size}_{p_hash}"
                    quick_hash_groups.setdefault(key, []).append(path)

        # Filter candidates that survived partial hash
        surviving_quick = {k: paths for k, paths in quick_hash_groups.items() if len(paths) > 1}
        if not surviving_quick:
            return []

        # --- Stage 3: Full Parallel SHA-256 Cryptographic Hash ---
        paths_to_full = [p for paths in surviving_quick.values() for p in paths]
        full_hashes: Dict[str, Optional[str]] = {}
        with ThreadPoolExecutor(max_workers=min(8, (os.cpu_count() or 4))) as executor:
            results = executor.map(cls.get_file_hash, paths_to_full)
            for path, f_hash in zip(paths_to_full, results):
                full_hashes[path] = f_hash

        duplicate_results: List[Dict[str, Any]] = []

        for key, candidate_paths in surviving_quick.items():
            full_hash_groups: Dict[str, List[str]] = {}
            for path in candidate_paths:
                f_hash = full_hashes.get(path)
                if f_hash:
                    full_hash_groups.setdefault(f_hash, []).append(path)

            for f_hash, matches in full_hash_groups.items():
                if len(matches) > 1:
                    # --- Stage 4: Bit-for-Bit binary verification ---
                    # Anchor against the first file and confirm every other file matches bit-for-bit
                    primary = matches[0]
                    verified_matches = [primary]
                    for other in matches[1:]:
                        if cls.verify_byte_for_byte(primary, other):
                            verified_matches.append(other)

                    if len(verified_matches) > 1:
                        files_info = []
                        size_bytes = 0
                        for m in verified_matches:
                            try:
                                st = os.stat(m)
                                size_bytes = st.st_size
                                files_info.append({
                                    "path": m,
                                    "name": os.path.basename(m),
                                    "directory": os.path.dirname(m),
                                    "size_bytes": size_bytes,
                                    "modified": st.st_mtime
                                })
                            except Exception:
                                continue

                        if len(files_info) > 1:
                            duplicate_results.append({
                                "hash": f_hash,
                                "hash_short": f"{f_hash[:8]}...{f_hash[-6:]}",
                                "size_bytes": size_bytes,
                                "size_formatted": cls._format_size(size_bytes),
                                "count": len(files_info),
                                "files": files_info,
                                "verification_method": "SHA-256 + Bit-for-Bit Binary Verified"
                            })

        # Sort by total wasted space descending
        duplicate_results.sort(key=lambda x: x["size_bytes"] * (x["count"] - 1), reverse=True)
        return duplicate_results

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

    @staticmethod
    def delete_file(file_path: str, recycle: bool = True) -> bool:
        if not os.path.exists(file_path):
            return False
        try:
            if recycle:
                send2trash(file_path)
            else:
                os.remove(file_path)
            return True
        except Exception:
            return False
