import sys
import os
import threading
import time
import socket
import urllib.request
import ctypes
import webview
import uvicorn
from PIL import Image
import pystray
from pystray import MenuItem as item

# Set AppUserModelID so Windows taskbar groups and shows FileFlow's custom icon
_instance_mutex = None
if sys.platform == 'win32':
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('fileflow.desktop.app.v1')
        kernel32 = ctypes.windll.kernel32
        _instance_mutex = kernel32.CreateMutexW(None, False, "Local\\FileFlow_Desktop_Instance_Mutex")
        if kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
            print("Another instance of FileFlow is already running. Exiting.")
            sys.exit(0)
    except Exception as e:
        print(f"Startup guard warning: {e}")

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
    from src.api.server import app, get_or_create_api_token
    from src.core.memory import trim_memory
except ModuleNotFoundError:
    try:
        from api.server import app, get_or_create_api_token
        from core.memory import trim_memory
    except ModuleNotFoundError:
        from .api.server import app, get_or_create_api_token
        from .core.memory import trim_memory

DEFAULT_PORT = 8765

def find_free_port(preferred: int = DEFAULT_PORT) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", preferred))
            return preferred
        except OSError:
            pass
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]

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

def wait_for_server(port: int, token: str, timeout: float = 8.0) -> bool:
    start_time = time.time()
    url = f"http://127.0.0.1:{port}/api/rules"
    while time.time() - start_time < timeout:
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'FileFlow', 'X-FileFlow-Token': token}
            )
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

def get_tray_image() -> Image.Image:
    candidates = []
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            candidates.append(os.path.join(sys._MEIPASS, "icon.png"))
            candidates.append(os.path.join(sys._MEIPASS, "icon.ico"))
        exe_dir = os.path.dirname(sys.executable)
        candidates.append(os.path.join(exe_dir, "icon.png"))
        candidates.append(os.path.join(exe_dir, "_internal", "icon.png"))
        candidates.append(os.path.join(exe_dir, "icon.ico"))
    else:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidates.append(os.path.join(root_dir, "icon.png"))
        candidates.append(os.path.join(root_dir, "icon.ico"))
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        candidates.append(os.path.join(backend_dir, "icon.ico"))

    for c in candidates:
        if os.path.exists(c):
            try:
                return Image.open(c)
            except Exception:
                pass
    return Image.new("RGBA", (32, 32), (37, 99, 235, 255))

class DesktopApi:
    def __init__(self, token: str = ""):
        self._window = None
        self._token = token

    def set_window(self, window):
        self._window = window

    def get_api_token(self):
        return self._token

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
    # 0. Acquire dynamic port and session authentication token
    port = find_free_port(DEFAULT_PORT)
    token = get_or_create_api_token()

    # 1. Start server in daemon thread
    server_thread = threading.Thread(target=start_server, args=(port,), daemon=True)
    server_thread.start()

    # 2. Wait until internal engine is ready
    server_ready = wait_for_server(port, token=token, timeout=8.0)
    if not server_ready:
        log_path = os.path.join(APP_DIR, "fileflow_error.log")
        with open(log_path, "a") as f:
            f.write("Failed to connect to internal server within timeout\n")

    # 3. Create native desktop window
    url = f"http://127.0.0.1:{port}/?token={token}"
    api = DesktopApi(token=token)
    window = webview.create_window(
        title="FileFlow - Automated File Organizer",
        url=url,
        width=1150,
        height=780,
        min_size=(900, 600),
        js_api=api
    )
    api.set_window(window)

    is_quitting = False
    has_notified_tray = False
    tray_icon = None

    def show_window(icon=None, item=None):
        try:
            window.show()
            window.restore()
        except Exception as e:
            print(f"[WINDOW RESTORE ERROR] {e}")

    def trigger_scan_tray(icon=None, item=None):
        def _scan():
            try:
                req = urllib.request.Request(
                    f"http://127.0.0.1:{port}/api/scan",
                    method="POST",
                    headers={"X-FileFlow-Token": token}
                )
                urllib.request.urlopen(req, timeout=5)
            except Exception:
                pass
        threading.Thread(target=_scan, daemon=True).start()

    def check_updates_tray(icon=None, item=None):
        def _check():
            try:
                from core.updater import check_for_updates
                info = check_for_updates(force=True)
                if info.get("update_available"):
                    show_window()
                    if tray_icon:
                        tray_icon.notify(
                            f"FileFlow v{info.get('latest_version')} is available!",
                            "Update Available"
                        )
                else:
                    if tray_icon:
                        tray_icon.notify(
                            "You are running the latest version of FileFlow (v1.0.3).",
                            "Up to Date"
                        )
            except Exception as e:
                print(f"[CHECK UPDATE ERROR] {e}")
        threading.Thread(target=_check, daemon=True).start()

    def exit_app(icon=None, item=None):
        nonlocal is_quitting
        is_quitting = True
        if tray_icon:
            try:
                tray_icon.stop()
            except Exception:
                pass
        try:
            window.destroy()
        except Exception:
            pass
        os._exit(0)

    def on_closing():
        nonlocal has_notified_tray
        if not is_quitting:
            # Hide the window to keep background watchers and rules active
            window.hide()
            trim_memory()

            if not has_notified_tray and tray_icon:
                has_notified_tray = True
                try:
                    tray_icon.notify(
                        "FileFlow is running in the background to organize your files. Right-click this tray icon to exit.",
                        "FileFlow Minimized"
                    )
                except Exception:
                    pass
            # Returning False cancels the destroy event in pywebview
            return False
        return True

    window.events.closing += on_closing

    # 4. Start system tray icon in detached thread
    try:
        tray_image = get_tray_image()
        tray_menu = pystray.Menu(
            item("Open FileFlow", show_window, default=True),
            pystray.Menu.SEPARATOR,
            item("Scan / Organize Now", trigger_scan_tray),
            item("Check for Updates", check_updates_tray),
            pystray.Menu.SEPARATOR,
            item("Exit FileFlow", exit_app)
        )
        tray_icon = pystray.Icon(
            "FileFlow",
            tray_image,
            "FileFlow - Background File Organizer",
            menu=tray_menu
        )
        tray_icon.run_detached()

        # Check for updates in background shortly after boot
        def check_update_background():
            time.sleep(5)
            try:
                from core.updater import check_for_updates
                update_info = check_for_updates()
                if update_info.get("update_available") and tray_icon:
                    ver = update_info.get("latest_version")
                    tray_icon.notify(
                        f"FileFlow v{ver} is now available! Click to update.",
                        "Update Available"
                    )
            except Exception:
                pass
        threading.Thread(target=check_update_background, daemon=True).start()
    except Exception as e:
        print(f"[TRAY ERROR] Could not initialize system tray: {e}")

    # 5. Background RAM Trim Worker: periodically trims working set when idle
    def background_trim_worker():
        while not is_quitting:
            time.sleep(60)
            try:
                trim_memory()
            except Exception:
                pass
    threading.Thread(target=background_trim_worker, daemon=True).start()

    icon_path = get_icon_path()
    if icon_path:
        webview.start(icon=icon_path)
    else:
        webview.start()

    if tray_icon:
        try:
            tray_icon.stop()
        except Exception:
            pass

if __name__ == "__main__":
    main()
