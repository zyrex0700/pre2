from __future__ import annotations

import sys
from pathlib import Path


def bootstrap_project_root() -> Path:
    """Ensure repository root is on sys.path for direct script execution.

    This allows commands like `python scripts/health_check.py` to resolve `src.*`
    without requiring editable installs.
    """
    root = Path(__file__).resolve().parents[1]
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    return root
