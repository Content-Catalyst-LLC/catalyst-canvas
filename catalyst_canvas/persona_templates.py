"""Reusable v1.4 persona templates."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_PATH = ROOT / "contracts" / "persona_templates.json"
PERSONA_TEMPLATES: Dict[str, Dict[str, Any]] = json.loads(TEMPLATES_PATH.read_text(encoding="utf-8"))


def list_persona_templates() -> Dict[str, Dict[str, Any]]:
    return deepcopy(PERSONA_TEMPLATES)


def persona_template(key: str) -> Dict[str, Any]:
    normalized = str(key or "").strip().lower()
    if normalized not in PERSONA_TEMPLATES:
        raise KeyError(f"Unknown persona template: {key}")
    return deepcopy(PERSONA_TEMPLATES[normalized])
