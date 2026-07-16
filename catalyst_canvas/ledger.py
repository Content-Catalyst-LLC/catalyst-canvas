"""Research source, evidence, claim, assumption, and handoff helpers.

Coverage indicators are descriptive workflow signals. They do not score truth,
research quality, or the people represented by the research.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping


def _text(value: Any, fallback: str = "") -> str:
    text = str(value or "").strip()
    return text or fallback


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


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_sources(value: Any) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if isinstance(value, Mapping) else [])
    records: List[Dict[str, Any]] = []
    allowed = {"document", "interview", "observation", "dataset", "analytics", "stakeholder_statement", "website", "other"}
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"title": item}
        title = _text(source.get("title"))
        if not title:
            continue
        records.append({
            "source_id": _text(source.get("source_id"), f"source-{index:03d}"),
            "source_type": _choice(source.get("source_type", source.get("type")), allowed, "other"),
            "title": title,
            "creator": _text(source.get("creator")),
            "publisher": _text(source.get("publisher")),
            "source_date": _text(source.get("source_date", source.get("date"))),
            "accessed_at": _text(source.get("accessed_at")),
            "url": _text(source.get("url", source.get("link"))),
            "owner": _text(source.get("owner")),
            "description": _text(source.get("description", source.get("notes"))),
            "rights": _text(source.get("rights")),
            "limitations": _list(source.get("limitations")),
            "tags": _list(source.get("tags")),
            "knowledge_library_record_id": _text(source.get("knowledge_library_record_id")),
            "provenance_note": _text(source.get("provenance_note")),
        })
    return records


def normalize_evidence(value: Any) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if _text(value) else [])
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"summary": item}
        summary = _text(source.get("summary", source.get("note")))
        quote = _text(source.get("quote", source.get("quotation")))
        records.append({
            "evidence_id": _text(source.get("evidence_id"), f"evidence-{index:03d}"),
            "source_id": _text(source.get("source_id")),
            "evidence_type": _choice(source.get("evidence_type", source.get("type")), {"quote", "observation", "data_point", "summary", "note", "artifact", "other"}, "note"),
            "title": _text(source.get("title"), "Evidence record"),
            "summary": summary,
            "quote": quote,
            "locator": _text(source.get("locator")),
            "citation": _text(source.get("citation")),
            "url": _text(source.get("url", source.get("link"))),
            "captured_at": _text(source.get("captured_at")),
            "captured_by": _text(source.get("captured_by", source.get("owner"))),
            "confidence": _choice(source.get("confidence"), {"low", "medium", "high", "unknown"}, "unknown"),
            "limitations": _list(source.get("limitations", source.get("limitation"))),
            "contradiction_ids": _list(source.get("contradiction_ids")),
            "tags": _list(source.get("tags")),
        })
    return records


def normalize_claims(value: Any) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if isinstance(value, Mapping) else [])
    records: List[Dict[str, Any]] = []
    states = {"supported", "partially_supported", "unsupported", "disputed", "outdated"}
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"statement": item}
        statement = _text(source.get("statement"))
        if not statement:
            continue
        records.append({
            "claim_id": _text(source.get("claim_id"), f"claim-{index:03d}"),
            "statement": statement,
            "state": _choice(source.get("state", source.get("status")), states, "unsupported"),
            "owner": _text(source.get("owner")),
            "confidence": _choice(source.get("confidence"), {"low", "medium", "high", "unknown"}, "unknown"),
            "evidence_ids": _list(source.get("evidence_ids")),
            "assumption_ids": _list(source.get("assumption_ids")),
            "source_ids": _list(source.get("source_ids")),
            "uncertainty": _text(source.get("uncertainty")),
            "limitations": _list(source.get("limitations")),
            "contradictions": _list(source.get("contradictions")),
            "missing_data": _list(source.get("missing_data")),
            "review_status": _choice(source.get("review_status"), {"draft", "review", "approved", "rejected"}, "draft"),
            "reviewed_by": _text(source.get("reviewed_by")),
            "reviewed_at": _text(source.get("reviewed_at")),
            "updated_at": _text(source.get("updated_at")),
            "tags": _list(source.get("tags")),
        })
    return records


def normalize_assumptions(value: Any) -> List[Dict[str, Any]]:
    defaults = [
        "The stated audience is the right primary user for the first iteration.",
        "The goal is specific enough to test with a small prototype.",
        "The constraint is material and should remain visible in the design process.",
        "A lightweight brief can reduce ambiguity before heavier implementation work begins.",
    ]
    raw = value if isinstance(value, list) else ([value] if _text(value) else defaults)
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"statement": item}
        records.append({
            "assumption_id": _text(source.get("assumption_id"), f"assumption-{index:03d}"),
            "statement": _text(source.get("statement")),
            "owner": _text(source.get("owner")),
            "confidence": _choice(source.get("confidence"), {"low", "medium", "high", "unknown"}, "unknown"),
            "criticality": _choice(source.get("criticality"), {"low", "medium", "high"}, "medium"),
            "consequence": _text(source.get("consequence")),
            "test_method": _text(source.get("test_method")),
            "status": _choice(source.get("status"), {"untested", "planned", "testing", "supported", "refuted", "challenged", "retired"}, "untested"),
            "experiment_ids": _list(source.get("experiment_ids", source.get("test_ids"))),
            "evidence_ids": _list(source.get("evidence_ids")),
            "due_date": _text(source.get("due_date")),
            "limitations": _list(source.get("limitations")),
            "tags": _list(source.get("tags")),
        })
    return records


def normalize_research_questions(value: Any) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if isinstance(value, Mapping) else [])
    records = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"question": item}
        question = _text(source.get("question"))
        if not question:
            continue
        records.append({
            "research_question_id": _text(source.get("research_question_id"), f"research-question-{index:03d}"),
            "question": question,
            "owner": _text(source.get("owner")),
            "status": _choice(source.get("status"), {"open", "investigating", "answered", "deferred", "closed"}, "open"),
            "priority": _choice(source.get("priority"), {"low", "medium", "high"}, "medium"),
            "source_ids": _list(source.get("source_ids")),
            "evidence_ids": _list(source.get("evidence_ids")),
            "notes": _text(source.get("notes")),
            "tags": _list(source.get("tags")),
        })
    return records


def normalize_interview_guides(value: Any) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if isinstance(value, Mapping) else [])
    records = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"title": item}
        records.append({
            "interview_guide_id": _text(source.get("interview_guide_id"), f"interview-guide-{index:03d}"),
            "title": _text(source.get("title"), f"Interview guide {index}"),
            "purpose": _text(source.get("purpose")),
            "audience": _text(source.get("audience")),
            "questions": _list(source.get("questions")),
            "owner": _text(source.get("owner")),
            "status": _choice(source.get("status"), {"draft", "ready", "in_use", "retired"}, "draft"),
            "source_ids": _list(source.get("source_ids")),
            "tags": _list(source.get("tags")),
        })
    return records


def normalize_observation_notes(value: Any) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if isinstance(value, Mapping) else [])
    records = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"note": item}
        note = _text(source.get("note"))
        if not note:
            continue
        records.append({
            "observation_note_id": _text(source.get("observation_note_id"), f"observation-{index:03d}"),
            "title": _text(source.get("title"), f"Observation {index}"),
            "note": note,
            "observed_at": _text(source.get("observed_at")),
            "observer": _text(source.get("observer")),
            "context": _text(source.get("context")),
            "source_id": _text(source.get("source_id")),
            "evidence_ids": _list(source.get("evidence_ids")),
            "limitations": _list(source.get("limitations")),
            "tags": _list(source.get("tags")),
        })
    return records


def normalize_handoffs(value: Any) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if isinstance(value, Mapping) else [])
    records = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"target": item}
        target = _choice(source.get("target"), {"knowledge_library", "research_librarian"}, "knowledge_library")
        records.append({
            "handoff_id": _text(source.get("handoff_id"), f"handoff-{index:03d}"),
            "target": target,
            "status": _choice(source.get("status"), {"draft", "ready", "sent", "accepted", "rejected"}, "draft"),
            "purpose": _text(source.get("purpose")),
            "context_note": _text(source.get("context_note")),
            "source_ids": _list(source.get("source_ids")),
            "evidence_ids": _list(source.get("evidence_ids")),
            "claim_ids": _list(source.get("claim_ids")),
            "assumption_ids": _list(source.get("assumption_ids")),
            "created_at": _text(source.get("created_at")),
            "created_by": _text(source.get("created_by")),
        })
    return records


def ledger_summary(
    sources: List[Mapping[str, Any]],
    evidence: List[Mapping[str, Any]],
    claims: List[Mapping[str, Any]],
    assumptions: List[Mapping[str, Any]],
    questions: List[Mapping[str, Any]],
    *,
    generated_at: str,
) -> Dict[str, Any]:
    claim_states = {state: 0 for state in ["supported", "partially_supported", "unsupported", "disputed", "outdated"]}
    for claim in claims:
        state = str(claim.get("state", "unsupported"))
        claim_states[state] = claim_states.get(state, 0) + 1
    material_claims = [claim for claim in claims if claim.get("review_status") != "rejected"]
    linked_claims = [claim for claim in material_claims if claim.get("evidence_ids") or claim.get("source_ids")]
    exposed_assumptions = [item for item in assumptions if item.get("criticality") == "high" and item.get("status") in {"untested", "planned", "testing", "challenged"}]
    unowned_assumptions = [item for item in assumptions if not item.get("owner")]
    untestable_assumptions = [item for item in assumptions if not item.get("test_method") and item.get("status") not in {"supported", "refuted", "retired"}]
    if not claims:
        evidence_coverage = "not_assessed"
    elif len(linked_claims) == len(material_claims):
        evidence_coverage = "all_material_claims_linked"
    elif linked_claims:
        evidence_coverage = "some_material_claims_linked"
    else:
        evidence_coverage = "no_material_claims_linked"
    if not assumptions:
        assumption_exposure = "none_recorded"
    elif exposed_assumptions:
        assumption_exposure = "high_criticality_open"
    elif unowned_assumptions or untestable_assumptions:
        assumption_exposure = "ownership_or_test_gaps"
    else:
        assumption_exposure = "tracked"
    return {
        "source_count": len(sources),
        "evidence_count": len(evidence),
        "claim_count": len(claims),
        "assumption_count": len(assumptions),
        "research_question_count": len(questions),
        "claim_states": claim_states,
        "unsupported_or_disputed_count": claim_states.get("unsupported", 0) + claim_states.get("disputed", 0) + claim_states.get("outdated", 0),
        "open_high_criticality_assumption_count": len(exposed_assumptions),
        "unowned_assumption_count": len(unowned_assumptions),
        "untestable_assumption_count": len(untestable_assumptions),
        "evidence_coverage": evidence_coverage,
        "assumption_exposure": assumption_exposure,
        "indicator_note": "Coverage indicators describe recorded links and workflow gaps; they do not measure truth or research quality.",
        "generated_at": generated_at or _now(),
    }


def build_handoff_package(contract: Mapping[str, Any], target: str) -> Dict[str, Any]:
    target = _choice(target, {"knowledge_library", "research_librarian"}, "knowledge_library")
    return {
        "handoff_contract": "catalyst-canvas-research-handoff/1.0",
        "target": target,
        "canvas_context": {
            "schema_version": contract.get("schema_version"),
            "canvas_id": contract.get("canvas_id"),
            "revision_id": contract.get("revision_id"),
            "title": contract.get("title"),
            "challenge": contract.get("challenge"),
            "goal": contract.get("goal"),
            "audience": contract.get("audience"),
            "updated_at": contract.get("updated_at"),
        },
        "research": {
            "sources": contract.get("sources", []),
            "evidence": contract.get("evidence", []),
            "claims": contract.get("claims", []),
            "assumptions": contract.get("assumptions", []),
            "research_questions": contract.get("research_questions", []),
            "interview_guides": contract.get("interview_guides", []),
            "observation_notes": contract.get("observation_notes", []),
            "synthesis_tags": contract.get("synthesis_tags", []),
            "ledger_summary": contract.get("ledger_summary", {}),
        },
        "provenance": contract.get("provenance", {}),
        "generated_at": _text(contract.get("updated_at"), _now()),
    }
