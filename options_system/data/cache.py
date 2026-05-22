"""Disk + in-memory cache with TTL.

yfinance is rate-limited and flaky; aggressive caching is required to keep
the scanner from hammering Yahoo for every candidate. Keyed by a stable hash
of the call signature, payload pickled to disk.
"""
from __future__ import annotations

import hashlib
import os
import pickle
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

from ..config import cache_dir, load_config


@dataclass
class _Entry:
    value: Any
    expires_at: float


class TTLCache:
    """Two-tier cache: in-memory dict + on-disk pickle."""

    def __init__(self, namespace: str, ttl_seconds: int, on_disk: bool = True):
        self.namespace = namespace
        self.ttl_seconds = ttl_seconds
        self.on_disk = on_disk
        self._mem: Dict[str, _Entry] = {}
        self._dir = cache_dir() / namespace
        if on_disk:
            self._dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _key(args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> str:
        raw = repr(args) + repr(sorted(kwargs.items()))
        return hashlib.sha1(raw.encode()).hexdigest()

    def _disk_path(self, key: str) -> Path:
        return self._dir / f"{key}.pkl"

    def get(self, key: str) -> Optional[Any]:
        # Memory first.
        entry = self._mem.get(key)
        now = time.time()
        if entry and entry.expires_at > now:
            return entry.value
        if entry:
            self._mem.pop(key, None)

        # Disk fallback.
        if not self.on_disk:
            return None
        path = self._disk_path(key)
        if not path.exists():
            return None
        try:
            with path.open("rb") as f:
                disk_entry: _Entry = pickle.load(f)
        except (pickle.PickleError, EOFError, OSError):
            try:
                path.unlink()
            except OSError:
                pass
            return None
        if disk_entry.expires_at <= now:
            try:
                path.unlink()
            except OSError:
                pass
            return None
        self._mem[key] = disk_entry
        return disk_entry.value

    def set(self, key: str, value: Any) -> None:
        entry = _Entry(value=value, expires_at=time.time() + self.ttl_seconds)
        self._mem[key] = entry
        if self.on_disk:
            try:
                with self._disk_path(key).open("wb") as f:
                    pickle.dump(entry, f)
            except (OSError, pickle.PickleError):
                pass

    def clear(self) -> None:
        self._mem.clear()
        if self.on_disk:
            for p in self._dir.glob("*.pkl"):
                try:
                    p.unlink()
                except OSError:
                    pass


def cached(namespace: str, ttl_key: str) -> Callable:
    """Decorator: cache method results under `namespace`.

    `ttl_key` selects which entry under data_config.cache.ttl_seconds applies.
    The wrapped method's `self` is excluded from the cache key.
    """
    cfg = load_config("data_config")
    cache_cfg = cfg.get("cache", {}) or {}
    enabled = cache_cfg.get("enabled", True)
    ttl_map = cache_cfg.get("ttl_seconds", {}) or {}
    ttl = int(ttl_map.get(ttl_key, 60))
    on_disk = bool(cache_cfg.get("on_disk", True))

    cache_obj: Optional[TTLCache] = (
        TTLCache(namespace=namespace, ttl_seconds=ttl, on_disk=on_disk)
        if enabled else None
    )

    def decorator(fn: Callable) -> Callable:
        def wrapper(self, *args: Any, **kwargs: Any) -> Any:
            if cache_obj is None or os.environ.get("OPTIONS_NOCACHE"):
                return fn(self, *args, **kwargs)
            key = TTLCache._key((fn.__name__, *args), kwargs)
            hit = cache_obj.get(key)
            if hit is not None:
                return hit
            value = fn(self, *args, **kwargs)
            if value is not None:
                cache_obj.set(key, value)
            return value
        wrapper.__wrapped__ = fn  # type: ignore[attr-defined]
        wrapper._cache = cache_obj  # type: ignore[attr-defined]
        return wrapper
    return decorator
