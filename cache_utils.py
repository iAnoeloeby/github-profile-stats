import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

CACHE_PATH = ".cache-runtime/stats.json"
CACHE_VERSION = 1


# ---------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------

def _utc_now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def load_cache() -> Optional[Dict[str, Any]]:
    if not os.path.exists(CACHE_PATH):
        return None

    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return None

    if data.get("version") != CACHE_VERSION:
        return None

    return data


def save_cache(data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)

    payload = {
        "version": CACHE_VERSION,
        "updated_at": _utc_now_iso(),
        **data,
    }

    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


# ---------------------------------------------------------------------
# Lines changed helpers
# ---------------------------------------------------------------------

def get_lines_changed(cache: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not cache:
        return None
    return cache.get("lines_changed")


def set_lines_changed(
    cache: Optional[Dict[str, Any]],
    additions: int,
    deletions: int,
    last_commit_date: str,
) -> Dict[str, Any]:
    if cache is None:
        cache = {}

    cache["lines_changed"] = {
        "additions": additions,
        "deletions": deletions,
        "last_commit_date": last_commit_date,
    }

    return cache


# ---------------------------------------------------------------------
# Recent commits helpers
# ---------------------------------------------------------------------

def get_recent_commits(cache: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not cache:
        return None
    return cache.get("recent_commits")


def set_recent_commits(
    cache: Optional[Dict[str, Any]],
    fingerprints: list[str],
) -> Dict[str, Any]:
    if cache is None:
        cache = {}

    cache["recent_commits"] = {
        "fingerprints": fingerprints,
        "last_checked": _utc_now_iso(),
    }

    return cache
