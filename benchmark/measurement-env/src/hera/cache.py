"""Provider-agnostic cache handle persistence.

Stores `{cache_name, content_hash, model, expiry}` keyed by content_hash at
`~/.cache/hera/cache_<hash>.json`. Provider implementations create the cache
upstream (e.g. Gemini's `client.caches.create`) and persist the handle here so
subsequent runs can reuse it without rebuilding the prefix.

Refresh policy: refresh-on-NotFound. If the provider rejects the cache name
(expired / deleted), the caller catches the failure, recreates, and overwrites
the persisted handle.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

CACHE_DIR = Path(os.path.expanduser("~/.cache/hera"))


@dataclass(frozen=True)
class CacheHandle:
    cache_name: str  # provider-side cache id (e.g. "cachedContents/abc123" for Gemini)
    content_hash: str
    model: str
    created_at: str  # ISO timestamp
    ttl_seconds: int


def hash_content(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()[:16]


def _path_for(content_hash: str) -> Path:
    return CACHE_DIR / f"cache_{content_hash}.json"


def load(content_hash: str) -> Optional[CacheHandle]:
    p = _path_for(content_hash)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text())
        return CacheHandle(**data)
    except Exception:
        return None


def save(handle: CacheHandle) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    p = _path_for(handle.content_hash)
    p.write_text(json.dumps(asdict(handle), indent=2))
    return p


def discard(content_hash: str) -> None:
    p = _path_for(content_hash)
    if p.exists():
        p.unlink()
