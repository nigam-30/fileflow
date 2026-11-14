import os
from typing import Dict, Any
from .base import BaseExtractor

class PdfExtractor(BaseExtractor):
    def can_handle(self, file_path: str) -> bool:
        return file_path.lower().endswith(".pdf")

    def extract(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            return {}

        results: Dict[str, Any] = {
            "pdf.title": "",
            "pdf.author": "",
            "pdf.creator": "",
            "pdf.producer": "",
            "pdf.page_count": 0,
            "content.text": ""
        }

        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            results["pdf.page_count"] = len(reader.pages)

            metadata = reader.metadata
            if metadata:
                results["pdf.title"] = metadata.title or ""
                results["pdf.author"] = metadata.author or ""
                results["pdf.creator"] = metadata.creator or ""
                results["pdf.producer"] = metadata.producer or ""

            # Extract text from first 5 pages max to be performant
            extracted_text = []
            for i, page in enumerate(reader.pages[:5]):
                text = page.extract_text()
                if text:
                    extracted_text.append(text)
            
            full_text = "\n".join(extracted_text)
            results["content.text"] = full_text
        except Exception:
            pass

        return results
