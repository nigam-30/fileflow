import os
import re
from typing import Dict, Any
from .base import BaseExtractor

class TextExtractor(BaseExtractor):
    SUPPORTED_EXTENSIONS = {"txt", "csv", "log", "json", "xml", "html", "md", "yaml", "yml", "ini", "cfg"}

    def can_handle(self, file_path: str) -> bool:
        ext = os.path.splitext(file_path)[1].lstrip(".").lower()
        return ext in self.SUPPORTED_EXTENSIONS

    def extract(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            return {}
        
        # Read up to first 256 KB to stay fast
        content = ""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(256 * 1024)
        except Exception:
            return {}

        return {
            "content.text": content,
            "content.line_count": content.count("\n") + 1
        }
