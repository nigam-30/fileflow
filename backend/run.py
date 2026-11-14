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
ROOT_DIR = os.path.dirname(BASE_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    if sys._MEIPASS not in sys.path:
        sys.path.insert(0, sys._MEIPASS)
else:
    dist_index = os.path.join(ROOT_DIR, "frontend", "dist", "index.html")
    if not os.path.exists(dist_index):
        print("=" * 65)
        print("⚠️  FileFlow Frontend Not Built Yet!")
        print("=" * 65)
        print("To compile the frontend UI, open a terminal and run:")
        print("   cd frontend")
        print("   npm install")
        print("   npm run build")
        print("   cd ..")
        print("Then run: python backend/run.py")
        print("=" * 65)
        sys.exit(1)

from src.main import main

if __name__ == "__main__":
    main()
