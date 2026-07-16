"""Persona, stakeholder, journey, and behavioral-signal helpers.

The v1.4 research studio is source-aware by design. Research records may
capture observations, research findings, and assumptions, but analytics rows
remain evidence hints and never create demographic or identity claims.
"""
from __future__ import annotations

import csv
import io
from typing import Any, Dict, Iterable, List, Mapping


def _text(value: Any, fallback: str = "") -> str:
    value = str(value or "").strip()
    return value or fallback


def _list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.splitlines() if item.strip()]
    if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray, Mapping)):
        return [_text(item) for item in value if _text(item)]
    return [_text(value)] if _text(value) else []


def _choice(value: Any, allowed: set[str], fallback: str) -> str:
    value = _text(value, fallback).lower()
    return value if value in allowed else fallback


def _score(value: Any, fallback: int = 3) -> int:
    try:
        return max(1, min(5, int(value)))
    except (TypeError, ValueError):
        return fallback


def _emotion(value: Any) -> int:
    try:
        return max(-2, min(2, int(value)))
    except (TypeError, ValueError):
        return 0


def normalize_empathy_map(value: Any, *, pains: List[str], gains: List[str], behaviors: List[str]) -> Dict[str, List[str]]:
    source = value if isinstance(value, Mapping) else {}
    return {
        "says": _list(source.get("says")),
        "thinks": _list(source.get("thinks")),
        "does": _list(source.get("does")) or list(behaviors),
        "feels": _list(source.get("feels")),
        "sees": _list(source.get("sees")),
        "hears": _list(source.get("hears")),
        "pains": _list(source.get("pains")) or list(pains),
        "gains": _list(source.get("gains")) or list(gains),
    }


def normalize_persona_attributes(value: Any) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else []
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"statement": item}
        statement = _text(source.get("statement"))
        if not statement:
            continue
        records.append({
            "attribute_id": _text(source.get("attribute_id"), f"attribute-{index:03d}"),
            "category": _choice(
                source.get("category"),
                {"job", "need", "pain", "gain", "behavior", "barrier", "motivation", "context", "other"},
                "other",
            ),
            "statement": statement,
            "basis": _choice(source.get("basis"), {"observed", "research", "assumed"}, "assumed"),
            "confidence": _choice(source.get("confidence"), {"low", "medium", "high"}, "low"),
            "evidence_ids": _list(source.get("evidence_ids")),
            "notes": _text(source.get("notes")),
        })
    return records


def normalize_personas(
    value: Any,
    *,
    audience: Mapping[str, Any],
    challenge: str,
    goal: str,
    constraint: str,
) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if isinstance(value, Mapping) else [])
    if not raw:
        name = _text(str(audience.get("primary", "")).split(",")[0], "Primary user")
        raw = [{
            "name": name,
            "role": "Primary participant",
            "description": f"Needs help addressing: {challenge}.",
            "context": f"Works toward {goal.lower()} while navigating {constraint.lower()}.",
            "jobs": [goal],
            "goals": [goal],
            "needs": [goal],
            "pains": [constraint],
            "barriers": [constraint],
            "source_type": "assumption",
            "confidence": "low",
            "validation_status": "hypothesis",
        }]
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"name": item}
        goals = _list(source.get("goals")) or _list(source.get("needs"))
        needs = _list(source.get("needs")) or goals
        jobs = _list(source.get("jobs")) or goals
        pains = _list(source.get("pains"))
        gains = _list(source.get("gains"))
        behaviors = _list(source.get("behaviors"))
        barriers = _list(source.get("barriers")) or pains
        motivations = _list(source.get("motivations")) or gains
        records.append({
            "persona_id": _text(source.get("persona_id"), f"persona-{index:03d}"),
            "name": _text(source.get("name"), "Primary user"),
            "role": _text(source.get("role")),
            "description": _text(source.get("description")),
            "context": _text(source.get("context")),
            "jobs": jobs,
            "goals": goals,
            "needs": needs,
            "pains": pains,
            "gains": gains,
            "behaviors": behaviors,
            "barriers": barriers,
            "motivations": motivations,
            "accessibility_needs": _list(source.get("accessibility_needs")),
            "preferred_channels": _list(source.get("preferred_channels")),
            "quotes": _list(source.get("quotes")),
            "empathy_map": normalize_empathy_map(source.get("empathy_map"), pains=pains, gains=gains, behaviors=behaviors),
            "attributes": normalize_persona_attributes(source.get("attributes")),
            "evidence_ids": _list(source.get("evidence_ids")),
            "assumption_ids": _list(source.get("assumption_ids")),
            "tags": _list(source.get("tags")),
            "source_type": _choice(source.get("source_type"), {"observed", "research", "assumption", "mixed"}, "assumption"),
            "source_notes": _text(source.get("source_notes")),
            "confidence": _choice(source.get("confidence"), {"low", "medium", "high"}, "low"),
            "confidence_notes": _text(source.get("confidence_notes")),
            "validation_status": _choice(source.get("validation_status"), {"hypothesis", "researching", "validated", "retired"}, "hypothesis"),
        })
    return records


def normalize_stakeholders(value: Any) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if isinstance(value, Mapping) else [])
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"name": item}
        score_map = {"low": 2, "medium": 3, "high": 5, "unknown": 3}
        influence = source.get("influence", 3)
        interest = source.get("interest", 3)
        impact = source.get("impact", 3)
        if isinstance(influence, str) and not influence.isdigit():
            influence = score_map.get(influence.lower(), 3)
        if isinstance(interest, str) and not interest.isdigit():
            interest = score_map.get(interest.lower(), 3)
        if isinstance(impact, str) and not impact.isdigit():
            impact = score_map.get(impact.lower(), 3)
        records.append({
            "stakeholder_id": _text(source.get("stakeholder_id"), f"stakeholder-{index:03d}"),
            "name": _text(source.get("name"), "Unnamed stakeholder"),
            "stakeholder_type": _choice(source.get("stakeholder_type"), {"user", "buyer", "sponsor", "decision_maker", "operator", "regulator", "partner", "community", "affected_group", "other"}, "other"),
            "relationship": _text(source.get("relationship"), "affected"),
            "influence": _score(influence),
            "interest": _score(interest),
            "impact": _score(impact),
            "stance": _choice(source.get("stance"), {"champion", "supportive", "neutral", "concerned", "resistant", "unknown"}, "unknown"),
            "decision_role": _choice(source.get("decision_role"), {"accountable", "approver", "advisor", "contributor", "informed", "affected"}, "affected"),
            "engagement_strategy": _text(source.get("engagement_strategy")),
            "responsibilities": _list(source.get("responsibilities")),
            "tensions": _list(source.get("tensions")),
            "notes": _text(source.get("notes")),
            "evidence_ids": _list(source.get("evidence_ids")),
            "dependencies": _list(source.get("dependencies")),
            "tags": _list(source.get("tags")),
        })
    return records


def normalize_journey_stages(value: Any) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else []
    if not raw:
        raw = [
            {"name": "Discover", "actions": ["Recognize the need or trigger"], "emotion": 0},
            {"name": "Evaluate", "actions": ["Compare options and evidence"], "emotion": -1},
            {"name": "Act", "actions": ["Take the next practical step"], "emotion": 1},
            {"name": "Learn", "actions": ["Review the result and decide what changes"], "emotion": 0},
        ]
    stages: List[Dict[str, Any]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"name": item}
        pain_points = _list(source.get("pain_points")) or _list(source.get("frictions"))
        stages.append({
            "stage_id": _text(source.get("stage_id"), f"stage-{index:03d}"),
            "sequence": index,
            "name": _text(source.get("name"), f"Stage {index}"),
            "actions": _list(source.get("actions")),
            "questions": _list(source.get("questions")),
            "thoughts": _list(source.get("thoughts")),
            "emotion": _emotion(source.get("emotion")),
            "pain_points": pain_points,
            "frictions": _list(source.get("frictions")) or pain_points,
            "opportunities": _list(source.get("opportunities")),
            "touchpoints": _list(source.get("touchpoints")),
            "channels": _list(source.get("channels")),
            "evidence_ids": _list(source.get("evidence_ids")),
            "experiment_ids": _list(source.get("experiment_ids")),
            "owner": _text(source.get("owner")),
            "metrics": _list(source.get("metrics")),
        })
    return stages


def normalize_journeys(value: Any, *, personas: List[Mapping[str, Any]], goal: str) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if isinstance(value, Mapping) else [])
    if not raw:
        return []
    default_persona = personas[0]["persona_id"] if personas else "persona-001"
    persona_name_map = {str(p.get("name", "")).lower(): p.get("persona_id", default_persona) for p in personas}
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"title": item}
        requested_persona = _text(source.get("persona_id"))
        if not requested_persona and source.get("persona_name"):
            requested_persona = str(persona_name_map.get(_text(source.get("persona_name")).lower(), ""))
        records.append({
            "journey_id": _text(source.get("journey_id"), f"journey-{index:03d}"),
            "title": _text(source.get("title"), "Primary experience journey"),
            "persona_id": requested_persona or default_persona,
            "scenario": _text(source.get("scenario"), "The persona moves from recognizing the problem to selecting a useful next step."),
            "desired_outcome": _text(source.get("desired_outcome"), goal),
            "status": _choice(source.get("status"), {"draft", "research", "review", "validated", "archived"}, "draft"),
            "stages": normalize_journey_stages(source.get("stages")),
            "evidence_ids": _list(source.get("evidence_ids")),
            "assumption_ids": _list(source.get("assumption_ids")),
            "tags": _list(source.get("tags")),
        })
    return records


def normalize_behavioral_signals(value: Any) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if isinstance(value, Mapping) else [])
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"metric": item}
        metric = _text(source.get("metric"))
        if not metric:
            continue
        records.append({
            "signal_id": _text(source.get("signal_id"), f"signal-{index:03d}"),
            "source_type": _choice(source.get("source_type"), {"analytics_csv", "ga4_export", "observation", "other"}, "analytics_csv"),
            "metric": metric,
            "segment": _text(source.get("segment"), "all users"),
            "value": _text(source.get("value")),
            "period": _text(source.get("period")),
            "interpretation": _text(source.get("interpretation")),
            "evidence_status": "hint",
            "limitation": _text(
                source.get("limitation"),
                "Behavioral analytics indicate activity patterns but do not prove intent, identity, motivation, or demographic attributes.",
            ),
            "evidence_ids": _list(source.get("evidence_ids")),
            "tags": _list(source.get("tags")),
        })
    return records


def parse_behavioral_signal_csv(text: str, *, source_type: str = "analytics_csv") -> List[Dict[str, Any]]:
    """Parse analytics rows without converting them into persona identity claims.

    Supported columns are metric, segment, value, period, interpretation,
    limitation, evidence_ids, and tags. Extra columns are ignored intentionally.
    """
    reader = csv.DictReader(io.StringIO(text or ""))
    rows: List[Dict[str, Any]] = []
    for row in reader:
        if not _text(row.get("metric")):
            continue
        rows.append({
            "source_type": source_type,
            "metric": row.get("metric"),
            "segment": row.get("segment"),
            "value": row.get("value"),
            "period": row.get("period"),
            "interpretation": row.get("interpretation"),
            "limitation": row.get("limitation"),
            "evidence_ids": [part.strip() for part in _text(row.get("evidence_ids")).split(",") if part.strip()],
            "tags": [part.strip() for part in _text(row.get("tags")).split(",") if part.strip()],
        })
    return normalize_behavioral_signals(rows)


def research_summary(
    personas: List[Mapping[str, Any]],
    stakeholders: List[Mapping[str, Any]],
    journeys: List[Mapping[str, Any]],
    behavioral_signals: List[Mapping[str, Any]] | None = None,
    *,
    generated_at: str,
) -> Dict[str, Any]:
    behavioral_signals = behavioral_signals or []
    evidence_links = set()
    assumption_links = set()
    for record in [*personas, *stakeholders, *journeys, *behavioral_signals]:
        evidence_links.update(record.get("evidence_ids", []))
        assumption_links.update(record.get("assumption_ids", []))
        for stage in record.get("stages", []):
            evidence_links.update(stage.get("evidence_ids", []))
    if journeys and all(p.get("validation_status") == "validated" for p in personas) and evidence_links:
        readiness = "evidence_backed"
    elif journeys and stakeholders and any(p.get("confidence") in {"medium", "high"} for p in personas):
        readiness = "review_ready"
    elif personas or stakeholders or journeys or behavioral_signals:
        readiness = "in_progress"
    else:
        readiness = "hypothesis"
    return {
        "persona_count": len(personas),
        "stakeholder_count": len(stakeholders),
        "journey_count": len(journeys),
        "behavioral_signal_count": len(behavioral_signals),
        "evidence_link_count": len(evidence_links),
        "assumption_link_count": len(assumption_links),
        "readiness": readiness,
        "generated_at": generated_at,
    }
