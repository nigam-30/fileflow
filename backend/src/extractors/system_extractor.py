import os
from datetime import datetime
from typing import Dict, Any
from .base import BaseExtractor

class SystemExtractor(BaseExtractor):
    def can_handle(self, file_path: str) -> bool:
        return True

    def extract(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            return {}

        stat = os.stat(file_path)
        name = os.path.basename(file_path)
        stem, ext = os.path.splitext(name)
        ext = ext.lstrip(".").lower()
        
        created_dt = datetime.fromtimestamp(stat.st_ctime)
        modified_dt = datetime.fromtimestamp(stat.st_mtime)
        accessed_dt = datetime.fromtimestamp(stat.st_atime)
        now_dt = datetime.now()

        parent_path = os.path.dirname(os.path.abspath(file_path))
        parent_folder = os.path.basename(parent_path)

        size_bytes = stat.st_size
        size_kb = round(size_bytes / 1024.0, 2)
        size_mb = round(size_bytes / (1024.0 * 1024.0), 2)

        return {
            "file.name": name,
            "file.stem": stem,
            "file.extension": ext,
            "file.path": os.path.abspath(file_path),
            "file.parent_path": parent_path,
            "file.parent_folder": parent_folder,
            "file.size_bytes": size_bytes,
            "file.size_kb": size_kb,
            "file.size_mb": size_mb,
            "file.created_date": created_dt.strftime("%Y-%m-%d"),
            "file.created_year": created_dt.strftime("%Y"),
            "file.created_month": created_dt.strftime("%m"),
            "file.created_day": created_dt.strftime("%d"),
            "file.created_time": created_dt.strftime("%H-%M-%S"),
            "file.modified_date": modified_dt.strftime("%Y-%m-%d"),
            "file.modified_year": modified_dt.strftime("%Y"),
            "file.modified_month": modified_dt.strftime("%m"),
            "file.modified_day": modified_dt.strftime("%d"),
            "file.current_date": now_dt.strftime("%Y-%m-%d"),
            "file.current_year": now_dt.strftime("%Y"),
            "file.current_month": now_dt.strftime("%m"),
            "file.current_day": now_dt.strftime("%d"),
            "file.mtime": stat.st_mtime
        }
