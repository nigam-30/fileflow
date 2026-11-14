import sys
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

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
    print("Then run: python run.py")
    print("=" * 65)
    sys.exit(1)

from src.main import main

if __name__ == "__main__":
    main()
