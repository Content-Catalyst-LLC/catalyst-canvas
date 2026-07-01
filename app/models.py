"""Small data helpers for Catalyst Canvas."""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Any, Dict, List


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CanvasBrief:
    title: str = "Untitled Catalyst Canvas Brief"
    challenge: str = ""
    audience: str = ""
    goal: str = ""
    constraint: str = ""
    persona_name: str = ""
    persona_role: str = ""
    persona_needs: str = ""
    persona_pains: str = ""
    evidence: str = ""
    assumption: str = ""
    how_might_we: str = ""
    prototype: str = ""
    test_plan: str = ""
    success_signal: str = ""
    risk_note: str = ""
    review_note: str = ""
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


SAMPLE_PERSONAS = [
    {
        "slug": "sustainability-manager",
        "name": "Sustainability Manager",
        "role": "Responsible for turning broad climate or ESG commitments into measurable, reportable work.",
        "needs": "Clear indicators, defensible claims, reusable outputs, and documentation that can survive review.",
        "pains": "Fragmented data, shifting definitions, unclear ownership, and pressure to communicate before evidence is ready.",
    },
    {
        "slug": "civic-program-lead",
        "name": "Civic Program Lead",
        "role": "Coordinates public-interest initiatives across stakeholders, funders, partners, and community needs.",
        "needs": "A structured way to frame problems, compare priorities, and explain tradeoffs.",
        "pains": "Too many competing narratives, limited resources, and incomplete information.",
    },
    {
        "slug": "technical-content-lead",
        "name": "Technical Content Lead",
        "role": "Translates complex systems, data, or developer workflows into usable public-facing materials.",
        "needs": "Clear audience assumptions, evidence-linked claims, reusable examples, and credible narrative structure.",
        "pains": "Overpromising, vague positioning, stakeholder drift, and content disconnected from technical reality.",
    },
]
