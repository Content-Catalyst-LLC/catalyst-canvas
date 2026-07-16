"""Prototype and experiment management for Canvas Contract 2.0."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Mapping, Sequence

PROTOTYPE_TYPES = {
    "concept", "paper", "wireframe", "storyboard", "service_blueprint",
    "interactive", "technical", "data", "policy", "operational", "other",
}
PROTOTYPE_STATUSES = {
    "concept", "planned", "building", "ready_for_test", "testing",
    "iterating", "validated", "retired",
}
FIDELITY_LEVELS = {"low", "medium", "high", "production_candidate"}
HYPOTHESIS_TYPES = {"desirability", "usability", "feasibility", "viability", "equity", "safety", "adoption", "impact", "other"}
HYPOTHESIS_STATUSES = {"draft", "active", "supported", "partially_supported", "not_supported", "inconclusive", "retired"}
EXPERIMENT_STATUSES = {"draft", "planned", "ready", "running", "complete", "cancelled", "blocked"}
RUN_STATUSES = {"planned", "running", "complete", "cancelled", "invalid"}
RESULT_STATES = {"supported", "partially_supported", "not_supported", "inconclusive", "not_evaluated"}
LEARNING_OUTCOMES = {"continue", "iterate", "pivot", "stop", "escalate", "retest"}
HANDOFF_TARGETS = {"research_lab", "workbench"}
CONFIDENCE_LEVELS = {"low", "medium", "high", "unknown"}
VALUE_BASES = {"measured", "estimate", "opinion", "unknown"}


def _text(value: Any, fallback: str = "") -> str:
    text = str(value or "").strip()
    return text or fallback


def _list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.replace(";", "\n").splitlines() if item.strip()]
    if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray, Mapping)):
        return [_text(item) for item in value if _text(item)]
    return [_text(value)] if _text(value) else []


def _choice(value: Any, allowed: set[str], fallback: str) -> str:
    candidate = _text(value, fallback).lower()
    return candidate if candidate in allowed else fallback


def _number(value: Any, fallback: float = 0.0, *, minimum: float | None = None) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = fallback
    if minimum is not None:
        number = max(minimum, number)
    return number


def normalize_prototypes(value: Any, *, generated_at: str) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if value else [])
    if not raw:
        raw = [{
            "title": "Reviewable Canvas Brief",
            "description": "A low-fidelity working artifact that makes the challenge, evidence, assumptions, option rationale, and proposed learning test reviewable.",
            "prototype_type": "concept",
            "fidelity": "low",
            "status": "ready_for_test",
            "version": "0.1",
        }]
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"description": item}
        records.append({
            "prototype_id": _text(source.get("prototype_id"), f"prototype-{index:03d}"),
            "title": _text(source.get("title"), "Prototype concept"),
            "description": _text(source.get("description")),
            "prototype_type": _choice(source.get("prototype_type", source.get("type")), PROTOTYPE_TYPES, "concept"),
            "fidelity": _choice(source.get("fidelity"), FIDELITY_LEVELS, "low"),
            "status": _choice(source.get("status"), PROTOTYPE_STATUSES, "concept"),
            "version": _text(source.get("version"), "0.1"),
            "owner": _text(source.get("owner")),
            "idea_ids": _list(source.get("idea_ids")),
            "option_ids": _list(source.get("option_ids")),
            "assumption_ids": _list(source.get("assumption_ids")),
            "evidence_ids": _list(source.get("evidence_ids")),
            "artifact_refs": _list(source.get("artifact_refs")),
            "success_definition": _text(source.get("success_definition")),
            "known_limitations": _list(source.get("known_limitations")),
            "created_at": _text(source.get("created_at"), generated_at),
            "updated_at": _text(source.get("updated_at"), generated_at),
        })
    return records


def normalize_hypotheses(value: Any, *, assumptions: Sequence[Mapping[str, Any]], prototypes: Sequence[Mapping[str, Any]], generated_at: str) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if isinstance(value, Mapping) else [])
    if not raw:
        assumption_ids = [str(item.get("assumption_id")) for item in assumptions[:1] if item.get("assumption_id")]
        raw = [{
            "statement": "A representative reviewer can use the prototype to identify the next testable action and the most material unsupported assumption.",
            "hypothesis_type": "usability",
            "status": "active",
            "prototype_ids": [str(item.get("prototype_id")) for item in prototypes[:1] if item.get("prototype_id")],
            "assumption_ids": assumption_ids,
            "falsification_condition": "Reviewers cannot identify either the next action or the unsupported assumption without facilitator interpretation.",
            "confidence": "low",
        }]
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"statement": item}
        records.append({
            "hypothesis_id": _text(source.get("hypothesis_id"), f"hypothesis-{index:03d}"),
            "statement": _text(source.get("statement"), "A testable outcome is expected."),
            "hypothesis_type": _choice(source.get("hypothesis_type", source.get("type")), HYPOTHESIS_TYPES, "other"),
            "status": _choice(source.get("status"), HYPOTHESIS_STATUSES, "draft"),
            "confidence": _choice(source.get("confidence"), CONFIDENCE_LEVELS, "unknown"),
            "owner": _text(source.get("owner")),
            "prototype_ids": _list(source.get("prototype_ids")),
            "assumption_ids": _list(source.get("assumption_ids")),
            "evidence_ids": _list(source.get("evidence_ids")),
            "falsification_condition": _text(source.get("falsification_condition")),
            "limitations": _list(source.get("limitations")),
            "created_at": _text(source.get("created_at"), generated_at),
            "updated_at": _text(source.get("updated_at"), generated_at),
        })
    return records


def _participant_plan(value: Any) -> Dict[str, Any]:
    source = value if isinstance(value, Mapping) else {}
    return {
        "target_count": int(_number(source.get("target_count"), 0, minimum=0)),
        "segments": _list(source.get("segments")),
        "recruitment_method": _text(source.get("recruitment_method")),
        "inclusion_criteria": _list(source.get("inclusion_criteria")),
        "exclusion_criteria": _list(source.get("exclusion_criteria")),
        "consent_required": bool(source.get("consent_required", True)),
        "compensation": _text(source.get("compensation")),
        "accessibility_accommodations": _list(source.get("accessibility_accommodations")),
    }


def _metric(value: Any, index: int) -> Dict[str, Any]:
    source = value if isinstance(value, Mapping) else {"name": value}
    return {
        "metric_id": _text(source.get("metric_id"), f"metric-{index:03d}"),
        "name": _text(source.get("name"), f"Metric {index}"),
        "metric_type": _choice(source.get("metric_type"), {"quantitative", "qualitative", "guardrail"}, "qualitative"),
        "success_threshold": _text(source.get("success_threshold")),
        "unit": _text(source.get("unit")),
        "collection_method": _text(source.get("collection_method")),
        "baseline": _text(source.get("baseline")),
        "target": _text(source.get("target")),
        "basis": _choice(source.get("basis"), VALUE_BASES, "unknown"),
        "confidence": _choice(source.get("confidence"), CONFIDENCE_LEVELS, "unknown"),
        "evidence_ids": _list(source.get("evidence_ids")),
    }


def _safeguards(value: Any) -> Dict[str, Any]:
    source = value if isinstance(value, Mapping) else {}
    return {
        "risks": _list(source.get("risks")),
        "mitigations": _list(source.get("mitigations")),
        "stop_conditions": _list(source.get("stop_conditions")),
        "data_handling": _text(source.get("data_handling")),
        "ethics_review_status": _choice(source.get("ethics_review_status"), {"not_required", "not_started", "in_review", "approved", "changes_required"}, "not_started"),
    }


def normalize_experiment_plans(value: Any, *, legacy_tests: Any, hypotheses: Sequence[Mapping[str, Any]], prototypes: Sequence[Mapping[str, Any]], generated_at: str) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if isinstance(value, Mapping) else [])
    if not raw:
        tests = legacy_tests if isinstance(legacy_tests, list) else ([legacy_tests] if legacy_tests else [])
        if tests:
            raw = []
            for item in tests:
                source = item if isinstance(item, Mapping) else {"method": item}
                raw.append({
                    "title": source.get("title", "Learning test"),
                    "objective": source.get("learning_goal", "Learn whether the prototype is useful enough to continue."),
                    "method": source.get("method", "Conduct a structured review."),
                    "metrics": [{"name": "Success signal", "metric_type": "qualitative", "success_threshold": source.get("signal", "A useful learning signal is observed."), "collection_method": source.get("method", "Structured review")}],
                    "status": source.get("status", "planned"),
                })
        else:
            raw = [{
                "title": "Stakeholder clarity experiment",
                "objective": "Determine whether the prototype makes the next action and the most material uncertainty understandable.",
                "method": "Run a structured review with representative users and capture task completion, confusion, objections, and unsupported claims.",
                "status": "planned",
                "participant_plan": {"target_count": 5, "segments": ["primary audience"], "consent_required": True},
                "metrics": [
                    {"name": "Next-action clarity", "metric_type": "quantitative", "success_threshold": "At least 4 of 5 participants identify the intended next action", "unit": "participants", "collection_method": "Post-task question", "basis": "estimate", "confidence": "low"},
                    {"name": "Unsupported-assumption identification", "metric_type": "qualitative", "success_threshold": "Participants identify at least one material uncertainty without prompting", "collection_method": "Facilitated debrief", "basis": "estimate", "confidence": "low"},
                ],
                "safeguards": {"risks": ["Participants may interpret a prototype as a final commitment"], "mitigations": ["Label the artifact as provisional and explain the learning purpose"], "stop_conditions": ["Stop if sensitive personal information is disclosed"], "data_handling": "Store only de-identified notes.", "ethics_review_status": "not_required"},
            }]
    default_prototype_ids = [str(item.get("prototype_id")) for item in prototypes[:1] if item.get("prototype_id")]
    default_hypothesis_ids = [str(item.get("hypothesis_id")) for item in hypotheses[:1] if item.get("hypothesis_id")]
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"method": item}
        metrics_raw = source.get("metrics") if isinstance(source.get("metrics"), list) else []
        if not metrics_raw and _text(source.get("signal")):
            metrics_raw = [{"name": "Success signal", "metric_type": "qualitative", "success_threshold": source.get("signal"), "collection_method": source.get("method")}]
        records.append({
            "experiment_id": _text(source.get("experiment_id"), f"experiment-{index:03d}"),
            "title": _text(source.get("title"), f"Experiment {index}"),
            "objective": _text(source.get("objective", source.get("learning_goal")), "Learn whether the prototype is useful enough to continue."),
            "method": _text(source.get("method"), "Conduct a structured learning test."),
            "status": _choice(source.get("status"), EXPERIMENT_STATUSES, "planned"),
            "owner": _text(source.get("owner")),
            "prototype_ids": _list(source.get("prototype_ids")) or deepcopy(default_prototype_ids),
            "hypothesis_ids": _list(source.get("hypothesis_ids")) or deepcopy(default_hypothesis_ids),
            "assumption_ids": _list(source.get("assumption_ids")),
            "evidence_ids": _list(source.get("evidence_ids")),
            "research_question_ids": _list(source.get("research_question_ids")),
            "participant_plan": _participant_plan(source.get("participant_plan")),
            "metrics": [_metric(metric, metric_index) for metric_index, metric in enumerate(metrics_raw, start=1)],
            "safeguards": _safeguards(source.get("safeguards")),
            "start_date": _text(source.get("start_date")),
            "end_date": _text(source.get("end_date")),
            "dependencies": _list(source.get("dependencies")),
            "blockers": _list(source.get("blockers")),
            "artifact_refs": _list(source.get("artifact_refs")),
            "created_at": _text(source.get("created_at"), generated_at),
            "updated_at": _text(source.get("updated_at"), generated_at),
        })
    return records


def _metric_result(value: Any, index: int) -> Dict[str, Any]:
    source = value if isinstance(value, Mapping) else {"observed_value": value}
    return {
        "metric_id": _text(source.get("metric_id"), f"metric-{index:03d}"),
        "observed_value": _text(source.get("observed_value")),
        "met_threshold": source.get("met_threshold") if isinstance(source.get("met_threshold"), bool) else None,
        "sample_size": int(_number(source.get("sample_size"), 0, minimum=0)),
        "analysis_note": _text(source.get("analysis_note")),
        "confidence": _choice(source.get("confidence"), CONFIDENCE_LEVELS, "unknown"),
        "evidence_ids": _list(source.get("evidence_ids")),
    }


def normalize_experiment_runs(value: Any, *, generated_at: str) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if isinstance(value, Mapping) else [])
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"summary": item}
        results_raw = source.get("metric_results") if isinstance(source.get("metric_results"), list) else []
        records.append({
            "run_id": _text(source.get("run_id"), f"experiment-run-{index:03d}"),
            "experiment_id": _text(source.get("experiment_id"), "experiment-001"),
            "prototype_ids": _list(source.get("prototype_ids")),
            "status": _choice(source.get("status"), RUN_STATUSES, "planned"),
            "started_at": _text(source.get("started_at")),
            "completed_at": _text(source.get("completed_at")),
            "participant_count": int(_number(source.get("participant_count"), 0, minimum=0)),
            "result_state": _choice(source.get("result_state"), RESULT_STATES, "not_evaluated"),
            "summary": _text(source.get("summary")),
            "metric_results": [_metric_result(result, result_index) for result_index, result in enumerate(results_raw, start=1)],
            "observations": _list(source.get("observations")),
            "evidence_ids": _list(source.get("evidence_ids")),
            "limitations": _list(source.get("limitations")),
            "incidents": _list(source.get("incidents")),
            "artifact_refs": _list(source.get("artifact_refs")),
            "recorded_by": _text(source.get("recorded_by")),
            "recorded_at": _text(source.get("recorded_at"), generated_at),
        })
    return records


def normalize_learning_decisions(value: Any, *, generated_at: str) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if isinstance(value, Mapping) else [])
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"rationale": item}
        records.append({
            "learning_decision_id": _text(source.get("learning_decision_id"), f"learning-decision-{index:03d}"),
            "experiment_id": _text(source.get("experiment_id")),
            "run_ids": _list(source.get("run_ids")),
            "outcome": _choice(source.get("outcome"), LEARNING_OUTCOMES, "iterate"),
            "rationale": _text(source.get("rationale")),
            "hypothesis_ids": _list(source.get("hypothesis_ids")),
            "assumption_ids": _list(source.get("assumption_ids")),
            "evidence_ids": _list(source.get("evidence_ids")),
            "next_actions": _list(source.get("next_actions")),
            "owner": _text(source.get("owner")),
            "decided_at": _text(source.get("decided_at"), generated_at),
        })
    return records


def normalize_iteration_history(value: Any, *, generated_at: str) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if isinstance(value, Mapping) else [])
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"change_summary": item}
        records.append({
            "iteration_id": _text(source.get("iteration_id"), f"iteration-{index:03d}"),
            "prototype_id": _text(source.get("prototype_id"), "prototype-001"),
            "from_version": _text(source.get("from_version")),
            "to_version": _text(source.get("to_version")),
            "change_summary": _text(source.get("change_summary")),
            "reason": _text(source.get("reason")),
            "experiment_run_ids": _list(source.get("experiment_run_ids")),
            "learning_decision_id": _text(source.get("learning_decision_id")),
            "author": _text(source.get("author")),
            "created_at": _text(source.get("created_at"), generated_at),
        })
    return records


def normalize_experiment_handoffs(value: Any, *, generated_at: str) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if isinstance(value, Mapping) else [])
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"purpose": item}
        records.append({
            "experiment_handoff_id": _text(source.get("experiment_handoff_id"), f"experiment-handoff-{index:03d}"),
            "target": _choice(source.get("target"), HANDOFF_TARGETS, "research_lab"),
            "status": _choice(source.get("status"), {"draft", "ready", "sent", "accepted", "closed"}, "draft"),
            "purpose": _text(source.get("purpose")),
            "prototype_ids": _list(source.get("prototype_ids")),
            "experiment_ids": _list(source.get("experiment_ids")),
            "run_ids": _list(source.get("run_ids")),
            "dataset_refs": _list(source.get("dataset_refs")),
            "calculation_requirements": _list(source.get("calculation_requirements")),
            "modeling_questions": _list(source.get("modeling_questions")),
            "compute_requirements": _list(source.get("compute_requirements")),
            "created_by": _text(source.get("created_by")),
            "created_at": _text(source.get("created_at"), generated_at),
        })
    return records


def experiment_summary(
    prototypes: Sequence[Mapping[str, Any]],
    hypotheses: Sequence[Mapping[str, Any]],
    plans: Sequence[Mapping[str, Any]],
    runs: Sequence[Mapping[str, Any]],
    decisions: Sequence[Mapping[str, Any]],
    iterations: Sequence[Mapping[str, Any]],
    *, generated_at: str,
) -> Dict[str, Any]:
    active = sum(1 for item in plans if item.get("status") in {"ready", "running"})
    blocked = sum(1 for item in plans if item.get("status") == "blocked" or item.get("blockers"))
    completed = sum(1 for item in runs if item.get("status") == "complete")
    untested_hypotheses = sum(1 for item in hypotheses if item.get("status") in {"draft", "active"})
    missing_metrics = sum(1 for item in plans if not item.get("metrics"))
    missing_safeguards = sum(1 for item in plans if not item.get("safeguards", {}).get("risks") and not item.get("safeguards", {}).get("stop_conditions"))
    if blocked:
        readiness = "blocked"
    elif any(item.get("status") == "running" for item in plans) or any(item.get("status") == "running" for item in runs):
        readiness = "running"
    elif completed and decisions:
        readiness = "learning_recorded"
    elif plans and not missing_metrics and not missing_safeguards:
        readiness = "ready_to_test"
    else:
        readiness = "planning"
    return {
        "prototype_count": len(prototypes),
        "hypothesis_count": len(hypotheses),
        "experiment_count": len(plans),
        "active_experiment_count": active,
        "completed_run_count": completed,
        "learning_decision_count": len(decisions),
        "iteration_count": len(iterations),
        "untested_hypothesis_count": untested_hypotheses,
        "missing_metric_count": missing_metrics,
        "missing_safeguard_count": missing_safeguards,
        "blocked_experiment_count": blocked,
        "readiness": readiness,
        "indicator_note": "Experiment readiness is a workflow coverage indicator. It does not establish safety, causal validity, statistical power, desirability, feasibility, or impact.",
        "generated_at": generated_at,
    }


def build_experiment_handoff_package(contract: Mapping[str, Any], target: str) -> Dict[str, Any]:
    selected_target = _choice(target, HANDOFF_TARGETS, "research_lab")
    handoffs = [item for item in contract.get("experiment_handoffs", []) if item.get("target") == selected_target]
    selected_experiment_ids = {value for item in handoffs for value in item.get("experiment_ids", [])}
    plans = [item for item in contract.get("experiment_plans", []) if not selected_experiment_ids or item.get("experiment_id") in selected_experiment_ids]
    selected_prototype_ids = {value for item in handoffs for value in item.get("prototype_ids", [])}
    selected_prototype_ids.update(value for plan in plans for value in plan.get("prototype_ids", []))
    package: Dict[str, Any] = {
        "handoff_contract": "catalyst-canvas-experiment-handoff/1.0",
        "target": selected_target,
        "canvas_context": {
            "schema_version": contract.get("schema_version"),
            "canvas_id": contract.get("canvas_id"),
            "revision_id": contract.get("revision_id"),
            "title": contract.get("title"),
            "challenge": contract.get("challenge"),
            "goal": contract.get("goal"),
            "updated_at": contract.get("updated_at"),
        },
        "experiment_context": {
            "prototypes": [item for item in contract.get("prototypes", []) if not selected_prototype_ids or item.get("prototype_id") in selected_prototype_ids],
            "hypotheses": contract.get("hypotheses", []),
            "experiment_plans": plans,
            "experiment_runs": contract.get("experiment_runs", []),
            "learning_decisions": contract.get("learning_decisions", []),
            "iteration_history": contract.get("iteration_history", []),
            "summary": contract.get("experiment_summary", {}),
            "assumptions": contract.get("assumptions", []),
            "evidence": contract.get("evidence", []),
            "handoff_records": handoffs,
        },
        "provenance": contract.get("provenance", {}),
        "generated_at": contract.get("updated_at"),
    }
    if selected_target == "research_lab":
        package["research_execution"] = {
            "participant_plans": [plan.get("participant_plan", {}) for plan in plans],
            "safeguards": [plan.get("safeguards", {}) for plan in plans],
            "dataset_refs": [value for item in handoffs for value in item.get("dataset_refs", [])],
            "compute_requirements": [value for item in handoffs for value in item.get("compute_requirements", [])],
        }
    else:
        package["technical_validation"] = {
            "calculation_requirements": [value for item in handoffs for value in item.get("calculation_requirements", [])],
            "modeling_questions": [value for item in handoffs for value in item.get("modeling_questions", [])],
            "metric_definitions": [metric for plan in plans for metric in plan.get("metrics", [])],
            "prototype_artifacts": [value for item in contract.get("prototypes", []) for value in item.get("artifact_refs", [])],
        }
    return package
