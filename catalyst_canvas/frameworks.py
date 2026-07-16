"""Canonical framework registry and portable framework packages."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Mapping

from .ideation import normalize_custom_frameworks, normalize_prompt

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORKS_PATH = ROOT / "contracts" / "frameworks.json"
FRAMEWORKS: Dict[str, Dict[str, Any]] = json.loads(FRAMEWORKS_PATH.read_text(encoding="utf-8"))

ALIASES = {
    "aida": "AIDA",
    "jtbd": "JTBD",
    "jobs to be done": "JTBD",
    "value proposition": "ValueProposition",
    "value proposition canvas": "ValueProposition",
    "message house": "MessageHouse",
    "swot": "SWOT",
    "pestle": "PESTLE",
    "5w1h": "FiveWOneH",
    "five w one h": "FiveWOneH",
    "hero": "HeroGuide",
    "hero's journey": "HeroGuide",
    "heros journey": "HeroGuide",
    "hero guide": "HeroGuide",
    "matrix": "AssumptionMatrix",
    "content matrix": "AssumptionMatrix",
    "assumption matrix": "AssumptionMatrix",
    "impact effort": "ImpactEffort",
    "impact-effort": "ImpactEffort",
    "impact–effort": "ImpactEffort",
}


def _custom_map(custom_frameworks: Any = None) -> Dict[str, Dict[str, Any]]:
    return {record["key"]: record for record in normalize_custom_frameworks(custom_frameworks)}


def framework_registry(custom_frameworks: Any = None) -> Dict[str, Dict[str, Any]]:
    registry: Dict[str, Dict[str, Any]] = {}
    for key, value in FRAMEWORKS.items():
        registry[key] = {**deepcopy(value), "key": key, "origin": "builtin", "organization": "", "created_by": "", "version": "1.0", "tags": []}
    registry.update(_custom_map(custom_frameworks))
    return registry


def normalize_framework_key(value: Any, custom_frameworks: Any = None) -> str:
    text = str(value or "AIDA").strip()
    registry = framework_registry(custom_frameworks)
    if text in registry:
        return text
    alias = ALIASES.get(text.lower())
    if alias and alias in registry:
        return alias
    return "AIDA"


def framework_record(value: Any, custom_frameworks: Any = None) -> Dict[str, Any]:
    key = normalize_framework_key(value, custom_frameworks)
    record = deepcopy(framework_registry(custom_frameworks)[key])
    record["key"] = key
    record["prompts"] = [normalize_prompt(prompt, index) for index, prompt in enumerate(record.get("prompts") or [], start=1)]
    return record


def framework_prompt_strings(value: Any, custom_frameworks: Any = None) -> List[str]:
    record = framework_record(value, custom_frameworks)
    return [f"{item['label']}: {item['question']}" for item in record["prompts"]]


def export_framework_package(custom_frameworks: Any, *, organization: str = "") -> Dict[str, Any]:
    records = normalize_custom_frameworks(custom_frameworks)
    return {
        "package_contract": "catalyst-canvas-framework-package/1.0",
        "organization": str(organization or "").strip(),
        "frameworks": records,
    }


def import_framework_package(payload: Mapping[str, Any]) -> List[Dict[str, Any]]:
    if payload.get("package_contract") != "catalyst-canvas-framework-package/1.0":
        raise ValueError("Unsupported framework package contract.")
    return normalize_custom_frameworks(payload.get("frameworks"))
