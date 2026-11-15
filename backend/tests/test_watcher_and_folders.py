import os
import shutil
import tempfile
import pytest
from src.core.database import Database
from src.core.engine import RuleEngine
from src.core.watcher import DirectoryWatcher
from src.core.memory import trim_memory

@pytest.fixture
def temp_env():
    tmp_dir = tempfile.mkdtemp(prefix="fileflow_watcher_")
    db_path = os.path.join(tmp_dir, "test.db")
    db = Database(db_path)
    engine = RuleEngine(db)
    watcher = DirectoryWatcher(engine)
    yield tmp_dir, db, watcher
    watcher.stop()
    shutil.rmtree(tmp_dir, ignore_errors=True)

def test_folder_removal_case_insensitive(temp_env):
    tmp_dir, db, watcher = temp_env
    test_folder = os.path.join(tmp_dir, "WatchFolder")
    os.makedirs(test_folder, exist_ok=True)

    # Add uppercase path
    assert db.add_monitored_folder(test_folder, recursive=False) is True
    folders = db.get_monitored_folders()
    assert len(folders) == 1

    # Remove using lowercase path or trailing slash
    lowercase_path = test_folder.lower() + os.sep
    assert db.remove_monitored_folder(lowercase_path) is True

    # Verify folder was removed
    folders_after = db.get_monitored_folders()
    assert len(folders_after) == 0

def test_watcher_unwatch_folder(temp_env):
    tmp_dir, db, watcher = temp_env
    test_folder = os.path.join(tmp_dir, "WatchFolder")
    os.makedirs(test_folder, exist_ok=True)

    watcher.watch_folder(test_folder)
    assert len(watcher.watched_paths) == 1

    # Unwatch folder
    watcher.unwatch_folder(test_folder.lower())
    assert len(watcher.watched_paths) == 0
    assert len(watcher.watches) == 0

def test_memory_trim_execution():
    # Verify trim_memory executes without exceptions
    trim_memory()
