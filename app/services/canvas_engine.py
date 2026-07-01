"""Core local Flask Canvas engine.

This complements python/catalyst_canvas_core.py. The repository-level core module
is optimized for CLI/reproducible exports; this service is optimized for the
local Flask demo workflow.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict

from .pov_hmw import build_hmw, build_point_of_view


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_form(form: Dict[str, Any], existing: Dict[str, Any] | None = None) -> Dict[str, Any]:
    data = dict(existing or {})
    for key in [
        "title", "challenge", "audience", "goal", "constraint", "persona_name", "persona_role",
        "persona_needs", "persona_pains", "evidence", "assumption", "prototype", "test_plan",
        "success_signal", "risk_note", "review_note"
    ]:
        if key in form:
            data[key] = str(form.get(key, "")).strip()

    data.setdefault("title", "Untitled Catalyst Canvas Brief")
    data.setdefault("created_at", now())
    data["updated_at"] = now()

    if not data.get("how_might_we"):
        data["how_might_we"] = build_hmw(data.get("challenge", ""), data.get("audience", ""), data.get("goal", ""), data.get("constraint", ""))

    data["point_of_view"] = build_point_of_view(
        data.get("persona_name") or data.get("audience", ""),
        data.get("persona_needs") or data.get("goal", ""),
        data.get("persona_pains") or data.get("constraint", ""),
    )
    return data


def to_markdown(canvas: Dict[str, Any]) -> str:
    title = canvas.get("title") or "Catalyst Canvas Brief"
    lines = [
        f"# {title}",
        "",
        "## Problem Frame",
        f"- **Challenge:** {canvas.get('challenge', '')}",
        f"- **Audience:** {canvas.get('audience', '')}",
        f"- **Goal:** {canvas.get('goal', '')}",
        f"- **Constraint:** {canvas.get('constraint', '')}",
        "",
        "## Persona",
        f"- **Name:** {canvas.get('persona_name', '')}",
        f"- **Role:** {canvas.get('persona_role', '')}",
        f"- **Needs:** {canvas.get('persona_needs', '')}",
        f"- **Pains:** {canvas.get('persona_pains', '')}",
        "",
        "## Point of View / HMW",
        f"- **Point of view:** {canvas.get('point_of_view', '')}",
        f"- **How might we:** {canvas.get('how_might_we', '')}",
        "",
        "## Evidence and Assumptions",
        f"- **Evidence:** {canvas.get('evidence', '')}",
        f"- **Key assumption:** {canvas.get('assumption', '')}",
        "",
        "## Prototype and Test",
        f"- **Prototype:** {canvas.get('prototype', '')}",
        f"- **Test plan:** {canvas.get('test_plan', '')}",
        f"- **Success signal:** {canvas.get('success_signal', '')}",
        "",
        "## Review Notes",
        f"- **Risk note:** {canvas.get('risk_note', '')}",
        f"- **Review note:** {canvas.get('review_note', '')}",
        "",
        "## Boundary",
        "This Canvas brief is a design-thinking and problem-framing artifact. It does not guarantee adoption, product-market fit, compliance, funding, or implementation success.",
    ]
    return "\n".join(lines).strip() + "\n"


def to_pretty_json(canvas: Dict[str, Any]) -> str:
    return json.dumps(canvas, indent=2, ensure_ascii=False)
