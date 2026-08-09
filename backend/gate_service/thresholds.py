import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = REPO_ROOT / "gate.config.json"


def load_thresholds() -> dict[str, Any]:
    """Load gate.config.json or return a safe fallback if missing/malformed.

    Never crashes. Returns:
      - default_kill_threshold: 0.75
      - file_thresholds: {}
    """
    fallback = {"default_kill_threshold": 0.75, "file_thresholds": {}}

    try:
        if not CONFIG_PATH.exists():
            return fallback

        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        return {
            "default_kill_threshold": data.get("default_kill_threshold", 0.75),
            "file_thresholds": data.get("file_thresholds", {}),
        }
    except Exception:
        # Fail closed, never crash, never silently pass.
        return fallback
