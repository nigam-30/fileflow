import sys
import os
import ctypes

# Set AppUserModelID so Windows uses FileFlow's custom icon on the taskbar instead of Python's default
if sys.platform == 'win32':
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('fileflow.desktop.app.v1')
    except Exception:
        pass

# Ensure backend directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    if sys._MEIPASS not in sys.path:
        sys.path.insert(0, sys._MEIPASS)

from src.main import main

if __name__ == "__main__":
    main()
