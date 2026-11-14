import sqlite3
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import os
import shutil
from .models import Rule, AuditLogEntry, LogStatus

def get_default_db_path() -> str:
    """Returns a permanent Windows user data path for the FileFlow database."""
    appdata = os.environ.get("APPDATA") or os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    base_dir = os.path.join(appdata, "FileFlowData")
    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, "fileflow.db")

class Database:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None or db_path == "fileflow.db":
            self.db_path = get_default_db_path()
        else:
            self.db_path = db_path
        self._init_db()
        self._migrate_legacy_db_if_needed()
        try:
            self.purge_old_logs(max_age_hours=12)
        except Exception:
            pass

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _migrate_legacy_db_if_needed(self):
        """Automatically copies rules from any legacy local db files if the main db is empty."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT count(*) FROM rules")
                if cursor.fetchone()[0] > 0:
                    return  # Already has rules

            # Check potential legacy locations
            legacy_candidates = [
                os.path.join(os.getcwd(), "fileflow.db"),
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fileflow.db"),
                r"D:\File Juggler 3\fileflow\backend\fileflow.db",
                r"D:\File Juggler 3\fileflow.db"
            ]

            for cand in legacy_candidates:
                if os.path.exists(cand) and os.path.abspath(cand) != os.path.abspath(self.db_path):
                    try:
                        leg_conn = sqlite3.connect(cand)
                        leg_conn.row_factory = sqlite3.Row
                        leg_cur = leg_conn.cursor()
                        leg_cur.execute("SELECT id, name, enabled, data FROM rules")
                        rows = leg_cur.fetchall()
                        if rows:
                            with self._get_connection() as conn:
                                cur = conn.cursor()
                                for r in rows:
                                    cur.execute("""
                                        INSERT OR REPLACE INTO rules (id, name, enabled, data)
                                        VALUES (?, ?, ?, ?)
                                    """, (r["id"], r["name"], r["enabled"], r["data"]))
                                conn.commit()
                        leg_conn.close()
                    except Exception:
                        pass
        except Exception:
            pass

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Rules table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rules (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Monitored folders table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS monitored_folders (
                    path TEXT PRIMARY KEY,
                    recursive INTEGER NOT NULL DEFAULT 0,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Processed files (state & loop prevention)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processed_files (
                    file_path TEXT PRIMARY KEY,
                    file_hash TEXT,
                    mtime REAL,
                    last_rule_id TEXT,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Audit logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    rule_id TEXT,
                    rule_name TEXT,
                    source_path TEXT NOT NULL,
                    destination_path TEXT,
                    action_type TEXT,
                    status TEXT NOT NULL,
                    details TEXT
                )
            """)
            conn.commit()

    # Rule Operations
    def save_rule(self, rule: Rule) -> Rule:
        rule.updated_at = datetime.utcnow()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO rules (id, name, enabled, data, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    enabled = excluded.enabled,
                    data = excluded.data,
                    updated_at = excluded.updated_at
            """, (rule.id, rule.name, 1 if rule.enabled else 0, rule.model_dump_json(), rule.updated_at.isoformat()))
            conn.commit()
        return rule

    def get_rule(self, rule_id: str) -> Optional[Rule]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM rules WHERE id = ?", (rule_id,))
            row = cursor.fetchone()
            if row:
                return Rule.model_validate_json(row["data"])
        return None

    def get_rules(self, enabled_only: bool = False) -> List[Rule]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if enabled_only:
                cursor.execute("SELECT data FROM rules WHERE enabled = 1 ORDER BY created_at ASC")
            else:
                cursor.execute("SELECT data FROM rules ORDER BY created_at ASC")
            rows = cursor.fetchall()
            return [Rule.model_validate_json(row["data"]) for row in rows]

    def delete_rule(self, rule_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM rules WHERE id = ?", (rule_id,))
            conn.commit()
            return cursor.rowcount > 0

    # Monitored Folders Operations
    def add_monitored_folder(self, path: str, recursive: bool = False) -> bool:
        norm_path = os.path.normpath(path)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO monitored_folders (path, recursive, enabled)
                VALUES (?, ?, 1)
            """, (norm_path, 1 if recursive else 0))
            conn.commit()
            return True

    def remove_monitored_folder(self, path: str) -> bool:
        norm_path = os.path.normpath(path)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM monitored_folders WHERE path = ?", (norm_path,))
            conn.commit()
            return cursor.rowcount > 0

    def get_monitored_folders(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT path, recursive, enabled FROM monitored_folders WHERE enabled = 1")
            return [{"path": row["path"], "recursive": bool(row["recursive"])} for row in cursor.fetchall()]

    # Deduplication & Loop Detection
    def is_recently_processed(self, file_path: str, mtime: float, rule_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT mtime, last_rule_id FROM processed_files WHERE file_path = ?", 
                (os.path.normpath(file_path),)
            )
            row = cursor.fetchone()
            if row:
                # If mtime matches and same rule, skip to prevent infinite loops
                if abs(row["mtime"] - mtime) < 0.001 and row["last_rule_id"] == rule_id:
                    return True
        return False

    def mark_processed(self, file_path: str, mtime: float, rule_id: str, file_hash: Optional[str] = None):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO processed_files (file_path, file_hash, mtime, last_rule_id, processed_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(file_path) DO UPDATE SET
                    file_hash = excluded.file_hash,
                    mtime = excluded.mtime,
                    last_rule_id = excluded.last_rule_id,
                    processed_at = CURRENT_TIMESTAMP
            """, (os.path.normpath(file_path), file_hash, mtime, rule_id))
            conn.commit()

    # Audit Logs
    def purge_old_logs(self, max_age_hours: int = 12):
        """Purge audit logs older than max_age_hours (default: 12 hours)."""
        now = datetime.now().astimezone()
        cutoff = now - timedelta(hours=max_age_hours)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, timestamp FROM audit_logs")
            rows = cursor.fetchall()
            ids_to_delete = []
            for r in rows:
                ts_raw = str(r["timestamp"]) if r["timestamp"] else ""
                if not ts_raw:
                    continue
                try:
                    if "T" in ts_raw:
                        dt = datetime.fromisoformat(ts_raw)
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc).astimezone()
                    else:
                        dt = datetime.strptime(ts_raw, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).astimezone()
                    if dt < cutoff:
                        ids_to_delete.append(r["id"])
                except Exception:
                    pass
            if ids_to_delete:
                for i in range(0, len(ids_to_delete), 500):
                    batch = ids_to_delete[i:i+500]
                    cursor.execute(f"DELETE FROM audit_logs WHERE id IN ({','.join(['?']*len(batch))})", batch)
                conn.commit()

    def add_log(self, entry: AuditLogEntry):
        # Auto-purge logs older than 12 hours
        try:
            self.purge_old_logs(max_age_hours=12)
        except Exception:
            pass

        now_local = datetime.now().astimezone()
        ts = entry.timestamp if entry.timestamp else now_local
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc).astimezone()
        ts_iso = ts.isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_logs (timestamp, rule_id, rule_name, source_path, destination_path, action_type, status, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ts_iso,
                entry.rule_id,
                entry.rule_name,
                entry.source_path,
                entry.destination_path,
                entry.action_type,
                entry.status.value,
                entry.details
            ))
            conn.commit()

    def get_logs(self, limit: int = 100) -> List[AuditLogEntry]:
        # Auto-purge logs older than 12 hours before returning
        try:
            self.purge_old_logs(max_age_hours=12)
        except Exception:
            pass

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            logs = []
            for r in rows:
                ts_raw = str(r["timestamp"]) if r["timestamp"] else ""
                try:
                    if "T" in ts_raw:
                        dt = datetime.fromisoformat(ts_raw)
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc).astimezone()
                    else:
                        dt = datetime.strptime(ts_raw, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).astimezone()
                except Exception:
                    dt = datetime.now().astimezone()

                logs.append(AuditLogEntry(
                    id=r["id"],
                    timestamp=dt,
                    rule_id=r["rule_id"],
                    rule_name=r["rule_name"],
                    source_path=r["source_path"],
                    destination_path=r["destination_path"],
                    action_type=r["action_type"],
                    status=LogStatus(r["status"]),
                    details=r["details"]
                ))
            return logs

    def clear_logs(self):
        """Clears all audit logs."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM audit_logs")
            conn.commit()
