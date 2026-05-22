"""Config loader. YAML files in this directory drive all tunable thresholds."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "PyYAML is required. Install with `pip install pyyaml`."
    ) from exc


CONFIG_DIR = Path(__file__).parent


def _config_path(name: str) -> Path:
    if not name.endswith((".yaml", ".yml")):
        name = f"{name}.yaml"
    return CONFIG_DIR / name


@lru_cache(maxsize=None)
def load_config(name: str) -> Dict[str, Any]:
    """Load a YAML config file from the config directory.

    Cached — call `clear_config_cache()` after editing files at runtime.
    """
    path = _config_path(name)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r") as f:
        return yaml.safe_load(f) or {}


def clear_config_cache() -> None:
    load_config.cache_clear()


def load_all() -> Dict[str, Dict[str, Any]]:
    """Load every YAML config in the directory keyed by filename stem."""
    out: Dict[str, Dict[str, Any]] = {}
    for path in CONFIG_DIR.glob("*.yaml"):
        out[path.stem] = load_config(path.name)
    return out


def get(config_name: str, *keys: str, default: Any = None) -> Any:
    """Dotted-style nested lookup: `get('strategy_rules', 'pop', 'min')`."""
    cfg: Any = load_config(config_name)
    for k in keys:
        if not isinstance(cfg, dict) or k not in cfg:
            return default
        cfg = cfg[k]
    return cfg


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def cache_dir() -> Path:
    p = project_root() / "data" / "cache"
    p.mkdir(parents=True, exist_ok=True)
    return p


def logs_dir() -> Path:
    p = project_root() / "logging_system" / "logs"
    p.mkdir(parents=True, exist_ok=True)
    return p
