from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import yaml


@dataclass
class Signal:
    action: str
    confidence: float
    entry_type: str
    sl: float
    tp: float
    reason: str


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def load_yaml(path: str | Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
