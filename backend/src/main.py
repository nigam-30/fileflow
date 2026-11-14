import sys
import os
import threading
import time
import socket
import urllib.request
import ctypes
import webview
import uvicorn

# Set AppUserModelID so Windows taskbar groups and shows FileFlow's custom icon
if sys.platform == 'win32':
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('fileflow.desktop.app.v1')
    except Exception:
        pass

# Setup paths for frozen and development environments
if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
    if hasattr(sys, '_MEIPASS'):
        sys.path.insert(0, sys._MEIPASS)
        sys.path.insert(0, os.path.join(sys._MEIPASS, "src"))
else:
    APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, APP_DIR)

try:
    from src.api.server import app
except ModuleNotFoundError:
    try:
        from api.server import app
    except ModuleNotFoundError:
        from .api.server import app

PORT = 8765

def start_server(port: int):
    try:
        config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
        server = uvicorn.Server(config)
        server.install_signal_handlers = lambda: None
        server.run()
    except Exception as e:
        log_path = os.path.join(APP_DIR, "fileflow_error.log")
        with open(log_path, "a") as f:
            f.write(f"Server exception: {e}\n")

def wait_for_server(port: int, timeout: float = 8.0) -> bool:
    start_time = time.time()
    url = f"http://127.0.0.1:{port}/api/rules"
    while time.time() - start_time < timeout:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'FileFlow'})
            with urllib.request.urlopen(req, timeout=0.5) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.15)
    return False

def get_icon_path() -> str:
    candidates = []
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            candidates.append(os.path.join(sys._MEIPASS, "icon.ico"))
            candidates.append(os.path.join(sys._MEIPASS, "icon.png"))
        exe_dir = os.path.dirname(sys.executable)
        candidates.append(os.path.join(exe_dir, "icon.ico"))
        candidates.append(os.path.join(exe_dir, "_internal", "icon.ico"))
    else:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidates.append(os.path.join(root_dir, "icon.ico"))
        candidates.append(os.path.join(root_dir, "icon.png"))
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        candidates.append(os.path.join(backend_dir, "icon.ico"))

    for c in candidates:
        if os.path.exists(c):
            return c
    return None

class DesktopApi:
    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    def browse_folder(self):
        try:
            if self._window:
                result = self._window.create_file_dialog(webview.FOLDER_DIALOG)
                if result and len(result) > 0:
                    return os.path.normpath(result[0])
        except Exception as e:
            print(f"DesktopApi.browse_folder error: {e}")
        return ""

    def browse_file(self):
        try:
            if self._window:
                result = self._window.create_file_dialog(webview.OPEN_DIALOG)
                if result and len(result) > 0:
                    return os.path.normpath(result[0])
        except Exception as e:
            print(f"DesktopApi.browse_file error: {e}")
        return ""

def main():
    # 1. Start server in daemon thread
    server_thread = threading.Thread(target=start_server, args=(PORT,), daemon=True)
    server_thread.start()

    # 2. Wait until internal engine is ready
    server_ready = wait_for_server(PORT, timeout=8.0)
    if not server_ready:
        log_path = os.path.join(APP_DIR, "fileflow_error.log")
        with open(log_path, "a") as f:
            f.write("Failed to connect to internal server within timeout\n")

    # 3. Create native desktop window
    url = f"http://127.0.0.1:{PORT}"
    api = DesktopApi()
    window = webview.create_window(
        title="FileFlow - Automated File Organizer",
        url=url,
        width=1150,
        height=780,
        min_size=(900, 600),
        js_api=api
    )
    api.set_window(window)
    
    icon_path = get_icon_path()
    if icon_path:
        webview.start(icon=icon_path)
    else:
        webview.start()

if __name__ == "__main__":
    main()
