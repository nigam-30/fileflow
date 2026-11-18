import time
import json
import urllib.request
from typing import Dict, Any, Optional

CURRENT_VERSION = "1.0.3"
GITHUB_REPO = "nigam-30/fileflow"
CACHE_DURATION_SECONDS = 3600 * 2  # 2 hours cache

_cache: Dict[str, Any] = {
    "timestamp": 0,
    "data": None
}

def parse_version(v: str) -> tuple:
    clean = v.lstrip('v').strip()
    parts = []
    for x in clean.split('.'):
        num_str = "".join([c for c in x if c.isdigit()])
        parts.append(int(num_str) if num_str else 0)
    return tuple(parts)

def check_for_updates(force: bool = False) -> Dict[str, Any]:
    global _cache
    now = time.time()
    
    if not force and _cache["data"] and (now - _cache["timestamp"] < CACHE_DURATION_SECONDS):
        return _cache["data"]

    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": f"FileFlow-Desktop/{CURRENT_VERSION}",
            "Accept": "application/vnd.github.v3+json"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=4.0) as resp:
            if resp.status == 200:
                payload = json.loads(resp.read().decode("utf-8"))
                latest_tag = payload.get("tag_name", "0.0.0")
                latest_parsed = parse_version(latest_tag)
                current_parsed = parse_version(CURRENT_VERSION)

                update_available = latest_parsed > current_parsed

                # Find installer asset if available
                download_url = payload.get("html_url", "")
                assets = payload.get("assets", [])
                for a in assets:
                    name = a.get("name", "").lower()
                    if name.endswith(".exe") and "setup" in name:
                        download_url = a.get("browser_download_url", download_url)
                        break

                result = {
                    "update_available": update_available,
                    "current_version": CURRENT_VERSION,
                    "latest_version": latest_tag.lstrip("v"),
                    "release_name": payload.get("name") or latest_tag,
                    "release_notes": payload.get("body", ""),
                    "release_url": payload.get("html_url", ""),
                    "download_url": download_url,
                    "published_at": payload.get("published_at", "")
                }
                _cache["timestamp"] = now
                _cache["data"] = result
                return result
    except Exception as e:
        print(f"[UPDATER ERROR] Could not check for updates: {e}")

    # Fallback response on network error or offline
    fallback = {
        "update_available": False,
        "current_version": CURRENT_VERSION,
        "latest_version": CURRENT_VERSION,
        "release_name": f"FileFlow v{CURRENT_VERSION}",
        "release_notes": "",
        "release_url": f"https://github.com/{GITHUB_REPO}/releases",
        "download_url": f"https://github.com/{GITHUB_REPO}/releases",
        "published_at": ""
    }
    return fallback
