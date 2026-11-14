import os
import hashlib
from typing import List, Dict, Any, Optional
from send2trash import send2trash

class DuplicateFinder:
    @staticmethod
    def get_file_hash(filepath: str, chunk_size: int = 65536) -> Optional[str]:
        """Compute SHA-256 hash of a file."""
        hasher = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (IOError, OSError, PermissionError):
            return None

    @staticmethod
    def get_quick_hash(filepath: str, sample_size: int = 4096) -> Optional[str]:
        """Compute quick hash of first sample_size bytes for fast pre-filtering."""
        hasher = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                chunk = f.read(sample_size)
                hasher.update(chunk)
            return hasher.hexdigest()
        except (IOError, OSError, PermissionError):
            return None

    @classmethod
    def scan_folder(cls, folder_path: str, recursive: bool = True) -> List[Dict[str, Any]]:
        """
        Scans a folder and returns duplicate file groups.
        """
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            return []

        # Step 1: Group files by file size
        size_groups: Dict[int, List[str]] = {}
        for root, _, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                try:
                    stat = os.stat(full_path)
                    size = stat.st_size
                    if size > 0:  # Skip 0-byte files or treat separately
                        size_groups.setdefault(size, []).append(full_path)
                except (IOError, OSError, PermissionError):
                    continue
            if not recursive:
                break

        # Step 2: Pre-filter by quick header hash
        quick_hash_groups: Dict[str, List[str]] = {}
        for size, file_paths in size_groups.items():
            if len(file_paths) > 1:
                for path in file_paths:
                    q_hash = cls.get_quick_hash(path)
                    if q_hash:
                        key = f"{size}_{q_hash}"
                        quick_hash_groups.setdefault(key, []).append(path)

        # Step 3: Full SHA-256 verification
        duplicate_results: List[Dict[str, Any]] = []
        for key, candidate_paths in quick_hash_groups.items():
            if len(candidate_paths) > 1:
                full_hash_groups: Dict[str, List[str]] = {}
                for path in candidate_paths:
                    full_h = cls.get_file_hash(path)
                    if full_h:
                        full_hash_groups.setdefault(full_h, []).append(path)

                for f_hash, matches in full_hash_groups.items():
                    if len(matches) > 1:
                        # Fetch file info for display
                        files_info = []
                        size_bytes = 0
                        for m in matches:
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
                                "size_bytes": size_bytes,
                                "size_formatted": cls._format_size(size_bytes),
                                "count": len(files_info),
                                "files": files_info
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
