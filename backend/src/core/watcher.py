import os
import time
import threading
from typing import Dict, Set, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from .engine import RuleEngine

class FileEventHandler(FileSystemEventHandler):
    def __init__(self, on_file_ready: Callable[[str], None], debounce_seconds: float = 1.0):
        super().__init__()
        self.on_file_ready = on_file_ready
        self.debounce_seconds = debounce_seconds
        self.pending_files: Dict[str, float] = {}
        self.lock = threading.Lock()
        self._running = True
        self._worker_thread = threading.Thread(target=self._debounce_worker, daemon=True)
        self._worker_thread.start()

    def _debounce_worker(self):
        while self._running:
            time.sleep(0.3)
            now = time.time()
            ready_files = []

            with self.lock:
                for file_path, timestamp in list(self.pending_files.items()):
                    if now - timestamp >= self.debounce_seconds:
                        ready_files.append(file_path)
                        del self.pending_files[file_path]

            for path in ready_files:
                if os.path.exists(path) and os.path.isfile(path):
                    if self._is_file_ready(path):
                        try:
                            self.on_file_ready(path)
                        except Exception as e:
                            print(f"[WATCHER ERROR] Failed processing {path}: {e}")

    def _is_file_ready(self, file_path: str, max_retries: int = 5, retry_delay: float = 0.5) -> bool:
        """Verifies the file is completely written and not locked by another process."""
        for _ in range(max_retries):
            try:
                with open(file_path, "rb"):
                    return True
            except (IOError, OSError):
                time.sleep(retry_delay)
        return False

    def on_created(self, event: FileSystemEvent):
        if not event.is_directory:
            with self.lock:
                self.pending_files[event.src_path] = time.time()

    def on_modified(self, event: FileSystemEvent):
        if not event.is_directory:
            with self.lock:
                self.pending_files[event.src_path] = time.time()

    def on_moved(self, event: FileSystemEvent):
        if not event.is_directory and event.dest_path:
            with self.lock:
                self.pending_files[event.dest_path] = time.time()

    def stop(self):
        self._running = False


class DirectoryWatcher:
    def __init__(self, rule_engine: RuleEngine):
        self.rule_engine = rule_engine
        self.observer = Observer()
        self.handler = FileEventHandler(on_file_ready=self.process_file)
        self.watched_paths: Set[str] = set()
        self.watches: Dict[str, Any] = {}

    def process_file(self, file_path: str):
        print(f"[EVENT] File ready for processing: {file_path}")
        logs = self.rule_engine.process_file(file_path)
        for log in logs:
            print(f"[ACTION] {log.rule_name} -> {log.action_type}: {log.status.value} ({log.details})")

    def watch_folder(self, folder_path: str, recursive: bool = False):
        folder_path = os.path.abspath(folder_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)

        clean_key = os.path.normcase(os.path.normpath(folder_path)).rstrip(os.sep)
        if clean_key not in self.watches:
            try:
                watch = self.observer.schedule(self.handler, folder_path, recursive=recursive)
                self.watches[clean_key] = watch
                self.watched_paths.add(folder_path)
                print(f"[WATCHER] Now monitoring: {folder_path} (recursive={recursive})")
            except Exception as e:
                print(f"[WATCHER ERROR] Failed to schedule {folder_path}: {e}")

    def unwatch_folder(self, folder_path: str):
        clean_key = os.path.normcase(os.path.normpath(folder_path)).rstrip(os.sep)
        watch = self.watches.pop(clean_key, None)
        if watch:
            try:
                self.observer.unschedule(watch)
                print(f"[WATCHER] Successfully stopped monitoring: {folder_path}")
            except Exception as e:
                print(f"[WATCHER ERROR] Failed to unschedule {folder_path}: {e}")
        self.watched_paths = {p for p in self.watched_paths if os.path.normcase(os.path.normpath(p)).rstrip(os.sep) != clean_key}

    def start(self):
        if not self.observer.is_alive():
            self.observer.start()
            print("[WATCHER] Service started.")

    def stop(self):
        self.handler.stop()
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            print("[WATCHER] Service stopped.")
