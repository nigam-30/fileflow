import os
from typing import Dict, Any
from .base import BaseExtractor

class MediaExtractor(BaseExtractor):
    SUPPORTED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "bmp", "gif", "tiff"}

    def can_handle(self, file_path: str) -> bool:
        ext = os.path.splitext(file_path)[1].lstrip(".").lower()
        return ext in self.SUPPORTED_EXTENSIONS

    def extract(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            return {}

        results: Dict[str, Any] = {
            "image.width": 0,
            "image.height": 0,
            "image.format": "",
            "image.megapixels": 0.0,
            "image.camera_make": "",
            "image.camera_model": "",
            "image.date_taken": ""
        }

        try:
            from PIL import Image, ExifTags
            with Image.open(file_path) as img:
                w, h = img.size
                results["image.width"] = w
                results["image.height"] = h
                results["image.format"] = (img.format or "").upper()
                results["image.megapixels"] = round((w * h) / 1000000.0, 2)

                exif = img.getexif()
                if exif:
                    for tag_id, value in exif.items():
                        tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                        if tag_name == "Make":
                            results["image.camera_make"] = str(value).strip()
                        elif tag_name == "Model":
                            results["image.camera_model"] = str(value).strip()
                        elif tag_name == "DateTimeOriginal" or tag_name == "DateTime":
                            # typically "YYYY:MM:DD HH:MM:SS" -> convert to "YYYY-MM-DD"
                            raw_dt = str(value).strip()
                            if len(raw_dt) >= 10:
                                results["image.date_taken"] = raw_dt[:10].replace(":", "-")
        except Exception:
            pass

        return results
