import os
import sys
import threading
import subprocess
import ctypes
from ctypes import wintypes
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from ..core.models import Rule, AuditLogEntry
from ..core.database import Database, get_default_db_path
from ..core.engine import RuleEngine
from ..core.watcher import DirectoryWatcher
from ..core.duplicate_finder import DuplicateFinder

# --- Windows Native Dialog Structures ---
BIF_RETURNONLYFSDIRS = 0x00000001
BIF_NEWDIALOGSTYLE   = 0x00000040

class BROWSEINFOW(ctypes.Structure):
    _fields_ = [
        ("hwndOwner", wintypes.HWND),
        ("pidlRoot", wintypes.LPCVOID),
        ("pszDisplayName", wintypes.LPWSTR),
        ("lpszTitle", wintypes.LPCWSTR),
        ("ulFlags", wintypes.UINT),
        ("lpfn", wintypes.LPCVOID),
        ("lParam", wintypes.LPARAM),
        ("iImage", wintypes.INT)
    ]

class OPENFILENAMEW(ctypes.Structure):
    _fields_ = [
        ("lStructSize", wintypes.DWORD),
        ("hwndOwner", wintypes.HWND),
        ("hInstance", wintypes.HINSTANCE),
        ("lpstrFilter", wintypes.LPCWSTR),
        ("lpstrCustomFilter", wintypes.LPWSTR),
        ("nMaxCustFilter", wintypes.DWORD),
        ("nFilterIndex", wintypes.DWORD),
        ("lpstrFile", wintypes.LPWSTR),
        ("nMaxFile", wintypes.DWORD),
        ("lpstrFileTitle", wintypes.LPWSTR),
        ("nMaxFileTitle", wintypes.DWORD),
        ("lpstrInitialDir", wintypes.LPCWSTR),
        ("lpstrTitle", wintypes.LPCWSTR),
        ("Flags", wintypes.DWORD),
        ("nFileOffset", wintypes.WORD),
        ("nFileExtension", wintypes.WORD),
        ("lpstrDefExt", wintypes.LPCWSTR),
        ("lCustData", wintypes.LPARAM),
        ("lpfnHook", wintypes.LPCVOID),
        ("lpTemplateName", wintypes.LPCWSTR),
        ("pvReserved", wintypes.LPVOID),
        ("dwReserved", wintypes.DWORD),
        ("FlagsEx", wintypes.DWORD),
    ]

app = FastAPI(title="FileFlow Automation Engine", version="1.0.2")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = Database(get_default_db_path())
engine = RuleEngine(db)
watcher = DirectoryWatcher(engine)

@app.on_event("startup")
def startup_event():
    # Sync folders from DB into watcher
    folders = db.get_monitored_folders()
    for f in folders:
        watcher.watch_folder(f["path"], f["recursive"])
    watcher.start()

@app.on_event("shutdown")
def shutdown_event():
    watcher.stop()

# --- Native Folder & File Picker API ---
BIF_EDITBOX = 0x00000010

@app.post("/api/browse-folder")
def browse_folder():
    """Opens a native Windows folder picker dialog."""
    try:
        ctypes.windll.ole32.OleInitialize(None)
        try:
            bi = BROWSEINFOW()
            bi.hwndOwner = 0
            bi.lpszTitle = "Select Origin / Watched Folder"
            bi.ulFlags = BIF_RETURNONLYFSDIRS | BIF_NEWDIALOGSTYLE | BIF_EDITBOX

            pidl = ctypes.windll.shell32.SHBrowseForFolderW(ctypes.byref(bi))
            if pidl:
                buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
                success = ctypes.windll.shell32.SHGetPathFromIDListW(pidl, buf)
                ctypes.windll.ole32.CoTaskMemFree(pidl)
                if success and buf.value:
                    return {"path": os.path.normpath(buf.value)}
            return {"path": ""}
        finally:
            ctypes.windll.ole32.OleUninitialize()
    except Exception as e:
        print(f"browse_folder error: {e}")
        return {"path": "", "error": str(e)}

@app.post("/api/browse-file")
def browse_file():
    """Opens a native Windows file picker dialog."""
    try:
        ofn = OPENFILENAMEW()
        ofn.lStructSize = ctypes.sizeof(OPENFILENAMEW)
        ofn.hwndOwner = 0
        buf = ctypes.create_unicode_buffer(1024)
        ofn.lpstrFile = ctypes.cast(buf, wintypes.LPWSTR)
        ofn.nMaxFile = 1024
        ofn.lpstrTitle = "Select File to Test"
        ofn.Flags = 0x00080000 | 0x00001000 | 0x00000800  # OFN_EXPLORER | OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST

        if ctypes.windll.comdlg32.GetOpenFileNameW(ctypes.byref(ofn)):
            if buf.value:
                return {"path": os.path.normpath(buf.value)}
        return {"path": ""}
    except Exception as e:
        print(f"browse_file error: {e}")
        return {"path": "", "error": str(e)}

# --- Duplicate Finder API ---
class DuplicateScanRequest(BaseModel):
    folder_path: str
    recursive: bool = True

class DuplicateDeleteRequest(BaseModel):
    file_path: str
    recycle: bool = True

@app.post("/api/duplicates/scan")
def scan_duplicates(req: DuplicateScanRequest):
    if not os.path.exists(req.folder_path) or not os.path.isdir(req.folder_path):
        raise HTTPException(status_code=400, detail="Folder does not exist or is not a directory")
    
    results = DuplicateFinder.scan_folder(req.folder_path, req.recursive)
    total_wasted = sum(group["size_bytes"] * (group["count"] - 1) for group in results)
    
    return {
        "folder": req.folder_path,
        "duplicate_groups": results,
        "total_groups": len(results),
        "total_wasted_bytes": total_wasted,
        "total_wasted_formatted": DuplicateFinder._format_size(total_wasted)
    }

@app.post("/api/duplicates/delete")
def delete_duplicate(req: DuplicateDeleteRequest):
    success = DuplicateFinder.delete_file(req.file_path, req.recycle)
    if not success:
        raise HTTPException(status_code=500, detail="Could not delete or recycle file")
    return {"success": True, "path": req.file_path}

# --- Rules API ---
@app.get("/api/rules", response_model=List[Rule])
def list_rules():
    return db.get_rules()

@app.post("/api/rules", response_model=Rule)
def create_or_update_rule(rule: Rule):
    saved = db.save_rule(rule)
    # Automatically register any origin/monitored folders specified in this rule
    for folder in rule.monitored_folders:
        clean_folder = os.path.normpath(folder.strip())
        if clean_folder and os.path.exists(clean_folder):
            db.add_monitored_folder(clean_folder, recursive=False)
            watcher.watch_folder(clean_folder, recursive=False)

    # Auto-scan: Automatically scan and organize existing files in the rule's origin folders
    def autoscan_folders(folder_paths: List[str]):
        try:
            for folder in folder_paths:
                clean_f = os.path.normpath(folder.strip())
                if clean_f and os.path.exists(clean_f):
                    for root, _, files in os.walk(clean_f):
                        for f in files:
                            full_p = os.path.join(root, f)
                            watcher.process_file(full_p)
        except Exception as e:
            print(f"[AUTOSCAN ERROR] {e}")

    if rule.enabled and rule.monitored_folders:
        threading.Thread(target=autoscan_folders, args=(list(rule.monitored_folders),), daemon=True).start()

    return saved

@app.delete("/api/rules/{rule_id}")
def delete_rule(rule_id: str):
    if not db.delete_rule(rule_id):
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"success": True}

@app.patch("/api/rules/{rule_id}/toggle")
def toggle_rule(rule_id: str):
    rule = db.get_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    rule.enabled = not rule.enabled
    db.save_rule(rule)
    return {"success": True, "enabled": rule.enabled}

# --- Monitored Folders API ---
class FolderRequest(BaseModel):
    path: str
    recursive: bool = False

@app.get("/api/folders")
def list_folders():
    return db.get_monitored_folders()

@app.post("/api/folders")
def add_folder(req: FolderRequest):
    if not os.path.exists(req.path):
        raise HTTPException(status_code=400, detail="Directory path does not exist")
    db.add_monitored_folder(req.path, req.recursive)
    watcher.watch_folder(req.path, req.recursive)
    return {"success": True}

@app.delete("/api/folders")
def remove_folder(path: str):
    success = db.remove_monitored_folder(path)
    watcher.unwatch_folder(path)
    return {"success": success}

# --- App Update & System Helpers ---
class OpenUrlRequest(BaseModel):
    url: str

@app.get("/api/app/update")
def get_update_status(force: bool = False):
    from ..core.updater import check_for_updates
    return check_for_updates(force=force)

@app.post("/api/open-external")
def open_external_url(req: OpenUrlRequest):
    import webbrowser
    webbrowser.open(req.url)
    return {"success": True}

# --- Activity Logs ---
@app.get("/api/logs", response_model=List[AuditLogEntry])
def get_logs(limit: int = 100):
    return db.get_logs(limit)

@app.delete("/api/logs")
def clear_logs():
    db.clear_logs()
    return {"status": "cleared"}

# --- Test / Simulation Playground ---
class TestFileRequest(BaseModel):
    file_path: str
    rule_id: Optional[str] = None

@app.post("/api/test-file")
def test_file(req: TestFileRequest):
    if not os.path.exists(req.file_path):
        raise HTTPException(status_code=400, detail="File does not exist")

    variables = engine.extract_variables(req.file_path)
    rules = [db.get_rule(req.rule_id)] if req.rule_id else db.get_rules()
    
    matches = []
    for r in rules:
        if r:
            matched = engine.matches_rule(r, dict(variables))
            matches.append({
                "rule_id": r.id,
                "rule_name": r.name,
                "matched": matched,
                "actions": [a.model_dump() for a in r.actions] if matched else []
            })

    return {
        "file": req.file_path,
        "variables": variables,
        "evaluations": matches
    }

# --- Manual Scan Trigger ---
@app.post("/api/scan")
def trigger_scan():
    folders = db.get_monitored_folders()
    folder_set = {os.path.normpath(f["path"]).lower(): (f["path"], f.get("recursive", False)) for f in folders}
    
    # Also include any folders configured on enabled rules for this scan run
    rules = db.get_rules(enabled_only=True)
    for r in rules:
        for mf in r.monitored_folders:
            clean = os.path.normpath(mf.strip())
            if clean and os.path.exists(clean) and clean.lower() not in folder_set:
                folder_set[clean.lower()] = (clean, False)

    total_processed = 0
    for key, (folder_path, recursive) in folder_set.items():
        if os.path.exists(folder_path):
            for root, _, files in os.walk(folder_path):
                for file in files:
                    full_p = os.path.join(root, file)
                    watcher.process_file(full_p)
                    total_processed += 1
                if not recursive:
                    break
    return {"success": True, "files_scanned": total_processed}

# --- Static Frontend Serving for Desktop Distribution ---
def get_dist_dir():
    # 1. PyInstaller frozen environment
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            p = os.path.join(sys._MEIPASS, "frontend", "dist")
            if os.path.exists(p):
                return p
        exe_dir = os.path.dirname(sys.executable)
        p = os.path.join(exe_dir, "_internal", "frontend", "dist")
        if os.path.exists(p):
            return p
        p = os.path.join(exe_dir, "frontend", "dist")
        if os.path.exists(p):
            return p

    # 2. Source development environment: walk up to find 'frontend/dist'
    curr = os.path.abspath(os.path.dirname(__file__))
    for _ in range(5):
        candidate = os.path.join(curr, "frontend", "dist")
        if os.path.exists(candidate) and os.path.isfile(os.path.join(candidate, "index.html")):
            return candidate
        parent = os.path.dirname(curr)
        if parent == curr:
            break
        curr = parent
    return None

dist_dir = get_dist_dir()
if dist_dir and os.path.exists(dist_dir):
    assets_dir = os.path.join(dist_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        file_path = os.path.join(dist_dir, full_path)
        if full_path and os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(dist_dir, "index.html"))
