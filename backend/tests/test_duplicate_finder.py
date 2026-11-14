import os
import shutil
import tempfile
import pytest
from src.core.duplicate_finder import DuplicateFinder

@pytest.fixture
def temp_dup_dir():
    tmp = tempfile.mkdtemp(prefix="fileflow_dup_test_")
    yield tmp
    shutil.rmtree(tmp, ignore_errors=True)

def test_duplicate_finder_exact_duplicates(temp_dup_dir):
    # Create two identical files
    f1 = os.path.join(temp_dup_dir, "file1.txt")
    f2 = os.path.join(temp_dup_dir, "file2.txt")
    content = b"Exact duplicate content inside FileFlow test suite" * 50

    with open(f1, "wb") as f:
        f.write(content)
    with open(f2, "wb") as f:
        f.write(content)

    results = DuplicateFinder.scan_folder(temp_dup_dir, recursive=False)
    assert len(results) == 1
    assert results[0]["count"] == 2
    assert results[0]["size_bytes"] == len(content)
    assert "SHA-256 + Bit-for-Bit" in results[0]["verification_method"]

def test_duplicate_finder_same_size_different_content(temp_dup_dir):
    # Create two files with the exact same byte length but different bytes
    # This directly tests that files with the same size are NOT falsely flagged!
    f1 = os.path.join(temp_dup_dir, "sample_A.bin")
    f2 = os.path.join(temp_dup_dir, "sample_B.bin")
    
    data_a = b"A" * 1024
    data_b = b"B" * 1024

    with open(f1, "wb") as f:
        f.write(data_a)
    with open(f2, "wb") as f:
        f.write(data_b)

    results = DuplicateFinder.scan_folder(temp_dup_dir, recursive=False)
    # Should NOT find any duplicates!
    assert len(results) == 0

def test_duplicate_finder_same_head_different_tail(temp_dup_dir):
    # Two files with same size (e.g. 30 KB), same first 8KB, but different tail
    f1 = os.path.join(temp_dup_dir, "video1.dat")
    f2 = os.path.join(temp_dup_dir, "video2.dat")

    common_head = b"COMMON_HEADER" * 1000  # ~13KB
    tail_a = b"TAIL_ALPHA" * 1000
    tail_b = b"TAIL_BETA_" * 1000

    with open(f1, "wb") as f:
        f.write(common_head + tail_a)
    with open(f2, "wb") as f:
        f.write(common_head + tail_b)

    results = DuplicateFinder.scan_folder(temp_dup_dir, recursive=False)
    # Should NOT find any duplicates!
    assert len(results) == 0
