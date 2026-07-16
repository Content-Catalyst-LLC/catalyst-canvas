"""Canonical ideation framework registry loaded from a shared JSON source."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORKS_PATH = ROOT / "contracts" / "frameworks.json"
FRAMEWORKS: Dict[str, Dict[str, Any]] = json.loads(FRAMEWORKS_PATH.read_text(encoding="utf-8"))

ALIASES = {
    "aida": "AIDA",
    "jtbd": "JTBD",
    "jobs to be done": "JTBD",
    "hero": "Hero",
    "hero's journey": "Hero",
    "heros journey": "Hero",
    "matrix": "Matrix",
    "content matrix": "Matrix",
    "assumption matrix": "Matrix",
}


def normalize_framework_key(value: Any) -> str:
    text = str(value or "AIDA").strip()
    if text in FRAMEWORKS:
        return text
    return ALIASES.get(text.lower(), "AIDA")


def framework_record(value: Any) -> Dict[str, Any]:
    key = normalize_framework_key(value)
    record = deepcopy(FRAMEWORKS[key])
    record["key"] = key
    record["prompts"] = [
        {"prompt_id": f"prompt-{index:03d}", **prompt}
        for index, prompt in enumerate(record["prompts"], start=1)
    ]
    return record


def framework_prompt_strings(value: Any) -> List[str]:
    record = framework_record(value)
    return [f"{item['label']}: {item['question']}" for item in record["prompts"]]
