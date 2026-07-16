"""Transparent prioritization and decision-readiness models for Canvas Contract 1.6."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
CRITERIA_PATH = ROOT / "contracts" / "decision_criteria.json"
VALUE_BASES = {"measured", "estimate", "opinion", "unknown"}
CONFIDENCE_LEVELS = {"low", "medium", "high", "unknown"}
RECOMMENDATION_STATES = {"explore", "test", "defer", "reject", "escalate", "ready_for_decision_review"}
HANDOFF_TARGETS = {"decision_studio", "workbench"}
HANDOFF_STATUSES = {"draft", "ready", "sent", "accepted", "rejected"}
GATE_RESULTS = {"pass", "fail", "unknown", "not_applicable"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _text(value: Any, fallback: str = "") -> str:
    text = str(value or "").strip()
    return text if text else fallback


def _list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.splitlines() if item.strip()]
    if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray, Mapping)):
        return [_text(item) for item in value if _text(item)]
    return [_text(value)] if _text(value) else []


def _choice(value: Any, allowed: set[str], fallback: str) -> str:
    candidate = _text(value, fallback).lower()
    return candidate if candidate in allowed else fallback


def _number(value: Any, fallback: float = 0.0, *, minimum: float | None = None, maximum: float | None = None) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = fallback
    if minimum is not None:
        number = max(minimum, number)
    if maximum is not None:
        number = min(maximum, number)
    return round(number, 6)


def criteria_library() -> Dict[str, Dict[str, Any]]:
    return json.loads(CRITERIA_PATH.read_text(encoding="utf-8"))


def list_criteria_library() -> List[Dict[str, Any]]:
    return [deepcopy(item) for item in criteria_library().values()]


def normalize_criteria(value: Any) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if isinstance(value, Mapping) else [])
    if not raw:
        raw = list_criteria_library()
    records: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"name": item}
        criterion_id = _text(source.get("criterion_id"), f"criterion-{index:03d}")
        if criterion_id in seen:
            criterion_id = f"{criterion_id}-{index:03d}"
        seen.add(criterion_id)
        records.append({
            "criterion_id": criterion_id,
            "name": _text(source.get("name"), f"Criterion {index}"),
            "category": _text(source.get("category"), "custom"),
            "description": _text(source.get("description")),
            "weight": _number(source.get("weight", source.get("default_weight")), 10.0, minimum=0.0, maximum=1000.0),
            "direction": _choice(source.get("direction"), {"higher_better", "lower_better"}, "higher_better"),
            "is_gate": bool(source.get("is_gate", False)),
            "gate_requirement": _text(source.get("gate_requirement")),
            "limitations": _list(source.get("limitations")),
            "notes": _text(source.get("notes")),
        })
    return records


def normalize_score_inputs(value: Any, defaults: Sequence[tuple[str, str, float]], *, prefix: str) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else []
    by_key = {}
    for item in raw:
        if isinstance(item, Mapping):
            key = _text(item.get("key", item.get("label"))).lower().replace(" ", "_")
            if key:
                by_key[key] = item
    records: List[Dict[str, Any]] = []
    for index, (key, label, default_value) in enumerate(defaults, start=1):
        source = by_key.get(key, {})
        records.append({
            "input_id": _text(source.get("input_id"), f"{prefix}-{key}"),
            "key": key,
            "label": _text(source.get("label"), label),
            "value": _number(source.get("value"), default_value, minimum=0.0),
            "unit": _text(source.get("unit")),
            "basis": _choice(source.get("basis"), VALUE_BASES, "unknown"),
            "confidence": _choice(source.get("confidence"), CONFIDENCE_LEVELS, "unknown"),
            "rationale": _text(source.get("rationale")),
            "evidence_ids": _list(source.get("evidence_ids")),
            "assumption_ids": _list(source.get("assumption_ids")),
        })
    return records


def _input_map(inputs: Sequence[Mapping[str, Any]]) -> Dict[str, float]:
    return {str(item.get("key")): _number(item.get("value")) for item in inputs}


def normalize_score_model(value: Any, *, model: str) -> Dict[str, Any]:
    source = value if isinstance(value, Mapping) else {}
    if model == "ICE":
        defaults = (("impact", "Impact", 1.0), ("confidence", "Confidence", 1.0), ("ease", "Ease", 1.0))
        definition = "ICE = impact × confidence × ease. Definitions and scales remain editable and must be interpreted with the recorded rationale."
    else:
        defaults = (("reach", "Reach", 1.0), ("impact", "Impact", 1.0), ("confidence", "Confidence", 1.0), ("effort", "Effort", 1.0))
        definition = "RICE = reach × impact × confidence ÷ effort. Reach, confidence, and effort units must be stated for meaningful comparison."
    inputs = normalize_score_inputs(source.get("inputs"), defaults, prefix=model.lower())
    values = _input_map(inputs)
    if model == "ICE":
        score = values["impact"] * values["confidence"] * values["ease"]
    else:
        effort = values["effort"] if values["effort"] > 0 else 1.0
        score = values["reach"] * values["impact"] * values["confidence"] / effort
    return {
        "model": model,
        "definition": _text(source.get("definition"), definition),
        "inputs": inputs,
        "score": round(score, 6),
        "rationale": _text(source.get("rationale")),
        "confidence": _choice(source.get("confidence"), CONFIDENCE_LEVELS, "unknown"),
        "basis": _choice(source.get("basis"), VALUE_BASES, "unknown"),
    }


def normalize_criterion_scores(value: Any, criteria: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else []
    by_id = {str(item.get("criterion_id")): item for item in raw if isinstance(item, Mapping)}
    records = []
    for criterion in criteria:
        criterion_id = str(criterion["criterion_id"])
        source = by_id.get(criterion_id, {})
        raw_value = _number(source.get("raw_value", source.get("value")), 0.0, minimum=0.0, maximum=5.0)
        normalized_value = raw_value / 5.0
        weight = _number(criterion.get("weight"), 0.0, minimum=0.0)
        if criterion.get("direction") == "lower_better":
            normalized_value = 1.0 - normalized_value
        records.append({
            "criterion_id": criterion_id,
            "raw_value": raw_value,
            "normalized_value": round(normalized_value, 6),
            "weight": weight,
            "weighted_value": round(normalized_value * weight, 6),
            "basis": _choice(source.get("basis"), VALUE_BASES, "unknown"),
            "confidence": _choice(source.get("confidence"), CONFIDENCE_LEVELS, "unknown"),
            "rationale": _text(source.get("rationale")),
            "evidence_ids": _list(source.get("evidence_ids")),
            "assumption_ids": _list(source.get("assumption_ids")),
        })
    return records


def weighted_score(criterion_scores: Sequence[Mapping[str, Any]], weights: Mapping[str, float] | None = None) -> float:
    weights = weights or {}
    numerator = 0.0
    denominator = 0.0
    for item in criterion_scores:
        criterion_id = str(item.get("criterion_id"))
        weight = _number(weights.get(criterion_id, item.get("weight")), 0.0, minimum=0.0)
        normalized = _number(item.get("normalized_value"), 0.0, minimum=0.0, maximum=1.0)
        numerator += normalized * weight
        denominator += weight
    return round((numerator / denominator * 100.0) if denominator else 0.0, 6)


def _matrix_position(name: str, source: Mapping[str, Any], x_label: str, y_label: str) -> Dict[str, Any]:
    x_value = _number(source.get("x_value", source.get(x_label)), 3.0, minimum=1.0, maximum=5.0)
    y_value = _number(source.get("y_value", source.get(y_label)), 3.0, minimum=1.0, maximum=5.0)
    x_high = x_value >= 3.0
    y_high = y_value >= 3.0
    quadrants = {
        "impact_effort": {(False, True): "high_impact_low_effort", (True, True): "high_impact_high_effort", (False, False): "low_impact_low_effort", (True, False): "low_impact_high_effort"},
        "confidence_risk": {(False, True): "high_confidence_low_risk", (True, True): "high_confidence_high_risk", (False, False): "low_confidence_low_risk", (True, False): "low_confidence_high_risk"},
        "urgency_importance": {(False, True): "important_not_urgent", (True, True): "urgent_and_important", (False, False): "not_urgent_not_important", (True, False): "urgent_lower_importance"},
        "reversibility": {(False, True): "highly_reversible_low_commitment", (True, True): "highly_reversible_high_commitment", (False, False): "hard_to_reverse_low_commitment", (True, False): "hard_to_reverse_high_commitment"},
    }
    return {
        "matrix": name,
        "x_axis": x_label,
        "y_axis": y_label,
        "x_value": x_value,
        "y_value": y_value,
        "quadrant": quadrants[name][(x_high, y_high)],
        "basis": _choice(source.get("basis"), VALUE_BASES, "unknown"),
        "confidence": _choice(source.get("confidence"), CONFIDENCE_LEVELS, "unknown"),
        "rationale": _text(source.get("rationale")),
    }


def normalize_matrices(value: Any) -> Dict[str, Dict[str, Any]]:
    source = value if isinstance(value, Mapping) else {}
    return {
        "impact_effort": _matrix_position("impact_effort", source.get("impact_effort", {}) if isinstance(source.get("impact_effort"), Mapping) else {}, "effort", "impact"),
        "confidence_risk": _matrix_position("confidence_risk", source.get("confidence_risk", {}) if isinstance(source.get("confidence_risk"), Mapping) else {}, "risk", "confidence"),
        "urgency_importance": _matrix_position("urgency_importance", source.get("urgency_importance", {}) if isinstance(source.get("urgency_importance"), Mapping) else {}, "urgency", "importance"),
        "reversibility": _matrix_position("reversibility", source.get("reversibility", {}) if isinstance(source.get("reversibility"), Mapping) else {}, "commitment", "reversibility"),
    }


def normalize_gate_results(value: Any, criteria: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else []
    by_id = {str(item.get("criterion_id")): item for item in raw if isinstance(item, Mapping)}
    records = []
    for criterion in criteria:
        if not criterion.get("is_gate"):
            continue
        source = by_id.get(str(criterion["criterion_id"]), {})
        records.append({
            "criterion_id": str(criterion["criterion_id"]),
            "result": _choice(source.get("result"), GATE_RESULTS, "unknown"),
            "rationale": _text(source.get("rationale")),
            "evidence_ids": _list(source.get("evidence_ids")),
            "assumption_ids": _list(source.get("assumption_ids")),
            "reviewed_by": _text(source.get("reviewed_by")),
            "reviewed_at": _text(source.get("reviewed_at")),
        })
    return records


def normalize_decision_options(value: Any, *, criteria: Sequence[Mapping[str, Any]], ideas: Sequence[Mapping[str, Any]], prototypes: Sequence[Mapping[str, Any]], generated_at: str) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if isinstance(value, Mapping) else [])
    if not raw and ideas:
        raw = [
            {
                "option_id": f"option-{index:03d}",
                "title": idea.get("title"),
                "description": idea.get("description"),
                "idea_ids": [idea.get("idea_id")],
                "prototype_ids": idea.get("prototype_ids", []),
                "recommendation_state": "explore",
            }
            for index, idea in enumerate(ideas, start=1)
            if idea.get("status") in {"selected", "captured", "clustered"}
        ]
    if not raw and prototypes:
        raw = [{"title": item.get("title"), "description": item.get("description"), "prototype_ids": [item.get("prototype_id")]} for item in prototypes]
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"title": item}
        criterion_scores = normalize_criterion_scores(source.get("criterion_scores"), criteria)
        ice = normalize_score_model(source.get("ice"), model="ICE")
        rice = normalize_score_model(source.get("rice"), model="RICE")
        records.append({
            "option_id": _text(source.get("option_id"), f"option-{index:03d}"),
            "title": _text(source.get("title"), f"Option {index}"),
            "description": _text(source.get("description")),
            "idea_ids": _list(source.get("idea_ids")),
            "prototype_ids": _list(source.get("prototype_ids")),
            "owner": _text(source.get("owner")),
            "recommendation_state": _choice(source.get("recommendation_state"), RECOMMENDATION_STATES, "explore"),
            "decision_deadline": _text(source.get("decision_deadline")),
            "dependencies": _list(source.get("dependencies")),
            "blockers": _list(source.get("blockers")),
            "resource_needs": _list(source.get("resource_needs")),
            "assumption_ids": _list(source.get("assumption_ids")),
            "evidence_ids": _list(source.get("evidence_ids")),
            "research_question_ids": _list(source.get("research_question_ids")),
            "ice": ice,
            "rice": rice,
            "criterion_scores": criterion_scores,
            "weighted_score": weighted_score(criterion_scores),
            "matrices": normalize_matrices(source.get("matrices")),
            "gate_results": normalize_gate_results(source.get("gate_results"), criteria),
            "decision_rationale": _text(source.get("decision_rationale")),
            "confidence": _choice(source.get("confidence"), CONFIDENCE_LEVELS, "unknown"),
            "value_basis": _choice(source.get("value_basis"), VALUE_BASES, "unknown"),
            "created_at": _text(source.get("created_at"), generated_at),
            "updated_at": _text(source.get("updated_at"), generated_at),
        })
    return records


def _rank_options(options: Sequence[Mapping[str, Any]], weights: Mapping[str, float] | None = None) -> List[Dict[str, Any]]:
    ranked = sorted(
        ((str(option.get("option_id")), weighted_score(option.get("criterion_scores", []), weights)) for option in options),
        key=lambda item: (-item[1], item[0]),
    )
    return [{"option_id": option_id, "score": score, "rank": index} for index, (option_id, score) in enumerate(ranked, start=1)]


def normalize_sensitivity_views(value: Any, *, options: Sequence[Mapping[str, Any]], criteria: Sequence[Mapping[str, Any]], generated_at: str) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if isinstance(value, Mapping) else [])
    baseline = _rank_options(options)
    baseline_rank = {item["option_id"]: item["rank"] for item in baseline}
    views = [{
        "scenario_id": "sensitivity-baseline",
        "name": "Baseline weights",
        "description": "Ranking generated from the recorded criterion weights.",
        "weight_overrides": [],
        "rankings": [{**item, "delta_from_baseline": 0} for item in baseline],
        "generated_at": generated_at,
    }]
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"name": item}
        overrides_raw = source.get("weight_overrides") if isinstance(source.get("weight_overrides"), list) else []
        overrides = []
        weights = {}
        valid_ids = {str(criterion["criterion_id"]) for criterion in criteria}
        for override in overrides_raw:
            if not isinstance(override, Mapping):
                continue
            criterion_id = _text(override.get("criterion_id"))
            if criterion_id not in valid_ids:
                continue
            weight = _number(override.get("weight"), 0.0, minimum=0.0, maximum=1000.0)
            weights[criterion_id] = weight
            overrides.append({"criterion_id": criterion_id, "weight": weight})
        rankings = _rank_options(options, weights)
        views.append({
            "scenario_id": _text(source.get("scenario_id"), f"sensitivity-{index:03d}"),
            "name": _text(source.get("name"), f"Sensitivity scenario {index}"),
            "description": _text(source.get("description")),
            "weight_overrides": overrides,
            "rankings": [{**rank, "delta_from_baseline": baseline_rank.get(rank["option_id"], rank["rank"]) - rank["rank"]} for rank in rankings],
            "generated_at": _text(source.get("generated_at"), generated_at),
        })
    return views


def normalize_decision_notes(value: Any, *, generated_at: str) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if isinstance(value, Mapping) else [])
    records = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"note": item}
        if not _text(source.get("note")):
            continue
        records.append({
            "decision_note_id": _text(source.get("decision_note_id"), f"decision-note-{index:03d}"),
            "note_type": _choice(source.get("note_type"), {"comparison", "recommendation", "risk", "dependency", "question", "governance", "calculation", "other"}, "other"),
            "note": _text(source.get("note")),
            "option_ids": _list(source.get("option_ids")),
            "criterion_ids": _list(source.get("criterion_ids")),
            "evidence_ids": _list(source.get("evidence_ids")),
            "assumption_ids": _list(source.get("assumption_ids")),
            "author": _text(source.get("author")),
            "status": _choice(source.get("status"), {"open", "resolved", "accepted", "rejected"}, "open"),
            "created_at": _text(source.get("created_at"), generated_at),
        })
    return records


def normalize_decision_handoffs(value: Any, *, generated_at: str) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if isinstance(value, Mapping) else [])
    records = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"target": item}
        records.append({
            "handoff_id": _text(source.get("handoff_id"), f"decision-handoff-{index:03d}"),
            "target": _choice(source.get("target"), HANDOFF_TARGETS, "decision_studio"),
            "status": _choice(source.get("status"), HANDOFF_STATUSES, "draft"),
            "purpose": _text(source.get("purpose")),
            "option_ids": _list(source.get("option_ids")),
            "criterion_ids": _list(source.get("criterion_ids")),
            "assumption_ids": _list(source.get("assumption_ids")),
            "evidence_ids": _list(source.get("evidence_ids")),
            "research_question_ids": _list(source.get("research_question_ids")),
            "calculation_requirements": _list(source.get("calculation_requirements")),
            "modeling_questions": _list(source.get("modeling_questions")),
            "governance_questions": _list(source.get("governance_questions")),
            "created_at": _text(source.get("created_at"), generated_at),
            "created_by": _text(source.get("created_by")),
        })
    return records


def prioritization_summary(criteria: Sequence[Mapping[str, Any]], options: Sequence[Mapping[str, Any]], sensitivity_views: Sequence[Mapping[str, Any]], *, generated_at: str) -> Dict[str, Any]:
    baseline = sensitivity_views[0].get("rankings", []) if sensitivity_views else []
    top_option_id = baseline[0].get("option_id", "") if baseline else ""
    incomplete_scores = 0
    unknown_values = 0
    failed_gates = 0
    unresolved_gates = 0
    ready = 0
    deadlines = 0
    for option in options:
        if option.get("recommendation_state") == "ready_for_decision_review":
            ready += 1
        if option.get("decision_deadline"):
            deadlines += 1
        for score in option.get("criterion_scores", []):
            if not score.get("rationale") or score.get("confidence") == "unknown":
                incomplete_scores += 1
            if score.get("basis") == "unknown":
                unknown_values += 1
        for gate in option.get("gate_results", []):
            if gate.get("result") == "fail":
                failed_gates += 1
            elif gate.get("result") == "unknown":
                unresolved_gates += 1
    if not options:
        readiness = "no_options"
    elif failed_gates:
        readiness = "blocked_by_gate"
    elif unresolved_gates or incomplete_scores:
        readiness = "needs_review"
    elif ready:
        readiness = "ready_for_decision_review"
    else:
        readiness = "prioritized_not_ready"
    return {
        "criterion_count": len(criteria),
        "option_count": len(options),
        "sensitivity_view_count": len(sensitivity_views),
        "ready_option_count": ready,
        "decision_deadline_count": deadlines,
        "incomplete_score_count": incomplete_scores,
        "unknown_value_count": unknown_values,
        "failed_gate_count": failed_gates,
        "unresolved_gate_count": unresolved_gates,
        "top_option_id": top_option_id,
        "readiness": readiness,
        "indicator_note": "Scores and rankings summarize recorded inputs and weights. They do not remove judgment, resolve ethical constraints, or establish certainty.",
        "generated_at": generated_at or _now(),
    }


def build_decision_handoff_package(contract: Mapping[str, Any], target: str) -> Dict[str, Any]:
    target = _choice(target, HANDOFF_TARGETS, "decision_studio")
    handoffs = [item for item in contract.get("decision_handoffs", []) if item.get("target") == target]
    selected_option_ids = {option_id for item in handoffs for option_id in item.get("option_ids", [])}
    options = list(contract.get("decision_options", []))
    if selected_option_ids:
        options = [option for option in options if option.get("option_id") in selected_option_ids]
    package = {
        "handoff_contract": "catalyst-canvas-decision-handoff/1.0",
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
        "decision_context": {
            "alternatives": options,
            "criteria": contract.get("decision_criteria", []),
            "sensitivity_views": contract.get("sensitivity_views", []),
            "decision_notes": contract.get("decision_notes", []),
            "prioritization_summary": contract.get("prioritization_summary", {}),
            "assumptions": contract.get("assumptions", []),
            "evidence": contract.get("evidence", []),
            "unresolved_questions": [item for item in contract.get("research_questions", []) if item.get("status") not in {"answered", "closed"}],
            "handoff_records": handoffs,
        },
        "provenance": contract.get("provenance", {}),
        "generated_at": _text(contract.get("updated_at"), _now()),
    }
    if target == "workbench":
        package["technical_validation"] = {
            "calculation_requirements": [requirement for item in handoffs for requirement in item.get("calculation_requirements", [])],
            "modeling_questions": [question for item in handoffs for question in item.get("modeling_questions", [])],
            "inputs": [score_input for option in options for model in (option.get("ice", {}), option.get("rice", {})) for score_input in model.get("inputs", [])],
        }
    else:
        package["governance"] = {
            "questions": [question for item in handoffs for question in item.get("governance_questions", [])],
            "recommendation_states": {str(option.get("option_id")): option.get("recommendation_state") for option in options},
        }
    return package
