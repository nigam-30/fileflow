import os
import subprocess
import sys
import shutil

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIST = os.path.join(ROOT_DIR, "frontend", "dist")
SRC_DIR = os.path.join(BACKEND_DIR, "src")
ICON_PATH = os.path.join(ROOT_DIR, "icon.ico")

print(f"Building FileFlow Executable from {ROOT_DIR}...")

if not os.path.exists(FRONTEND_DIST):
    print("Error: frontend/dist does not exist! Please run npm run build first.")
    sys.exit(1)

# PyInstaller command
pyinstaller_args = [
    sys.executable, "-m", "PyInstaller",
    "--name=FileFlow",
    "--onedir",
    "--windowed",
    "--clean",
    "--noconfirm",
    f"--icon={ICON_PATH}",
    f"--paths={BACKEND_DIR}",
    f"--add-data={SRC_DIR};src",
    f"--add-data={FRONTEND_DIST};frontend/dist",
    f"--add-data={ICON_PATH};.",
    "--hidden-import=src",
    "--hidden-import=src.api",
    "--hidden-import=src.api.server",
    "--hidden-import=src.core",
    "--hidden-import=src.core.models",
    "--hidden-import=src.core.database",
    "--hidden-import=src.core.engine",
    "--hidden-import=src.core.watcher",
    "--hidden-import=src.core.duplicate_finder",
    "--hidden-import=src.extractors",
    "--hidden-import=src.extractors.system_extractor",
    "--hidden-import=src.extractors.text_extractor",
    "--hidden-import=src.extractors.pdf_extractor",
    "--hidden-import=src.extractors.media_extractor",
    "--hidden-import=src.actions",
    "--hidden-import=src.actions.dispatcher",
    "--hidden-import=uvicorn.logging",
    "--hidden-import=uvicorn.loops",
    "--hidden-import=uvicorn.loops.auto",
    "--hidden-import=uvicorn.protocols",
    "--hidden-import=uvicorn.protocols.http",
    "--hidden-import=uvicorn.protocols.http.auto",
    "--hidden-import=uvicorn.protocols.websockets",
    "--hidden-import=uvicorn.protocols.websockets.auto",
    "--hidden-import=uvicorn.lifespan",
    "--hidden-import=uvicorn.lifespan.on",
    "--hidden-import=watchdog",
    "--hidden-import=send2trash",
    "--hidden-import=pypdf",
    "--hidden-import=PIL",
    "--hidden-import=webview",
    "--distpath=" + os.path.join(ROOT_DIR, "dist"),
    "--workpath=" + os.path.join(ROOT_DIR, "build"),
    os.path.join(BACKEND_DIR, "run.py")
]

print("Running command:")
print(" ".join(pyinstaller_args))

result = subprocess.run(pyinstaller_args)
if result.returncode == 0:
    dist_output = os.path.join(ROOT_DIR, "dist", "FileFlow")
    
    # Copy frontend/dist to both locations to ensure zero 404s
    target_frontend = os.path.join(dist_output, "frontend", "dist")
    if os.path.exists(target_frontend):
        shutil.rmtree(target_frontend)
    shutil.copytree(FRONTEND_DIST, target_frontend)

    target_internal = os.path.join(dist_output, "_internal", "frontend", "dist")
    if not os.path.exists(target_internal):
        shutil.copytree(FRONTEND_DIST, target_internal)
    
    # Copy icons to dist folder
    if os.path.exists(ICON_PATH):
        shutil.copy2(ICON_PATH, os.path.join(dist_output, "icon.ico"))
        shutil.copy2(ICON_PATH, os.path.join(dist_output, "_internal", "icon.ico"))
    icon_png = os.path.join(ROOT_DIR, "icon.png")
    if os.path.exists(icon_png):
        shutil.copy2(icon_png, os.path.join(dist_output, "icon.png"))
        shutil.copy2(icon_png, os.path.join(dist_output, "_internal", "icon.png"))
    
    print("\n✅ Build succeeded! FileFlow.exe is ready at:")
    print(os.path.join(dist_output, "FileFlow.exe"))
else:
    print(f"\n❌ Build failed with exit code {result.returncode}")
    sys.exit(result.returncode)
