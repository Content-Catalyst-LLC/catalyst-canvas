"""Canvas Contract 2.0 normalization and JSON Schema validation."""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping
from uuid import uuid4

from jsonschema import Draft202012Validator

from .version import CONTRACT_VERSION, __version__
from .ledger import (
    ledger_summary,
    normalize_assumptions as normalize_ledger_assumptions,
    normalize_claims,
    normalize_evidence as normalize_ledger_evidence,
    normalize_handoffs,
    normalize_interview_guides,
    normalize_observation_notes,
    normalize_research_questions,
    normalize_sources,
)
from .ideation import (
    ideation_summary,
    normalize_custom_frameworks,
    normalize_idea_clusters,
    normalize_ideas,
    normalize_ideation_sessions,
    normalize_prompt_packs,
)
from .prioritization import (
    normalize_criteria,
    normalize_decision_options,
    normalize_sensitivity_views,
    normalize_decision_notes,
    normalize_decision_handoffs,
    prioritization_summary,
)
from .experiments import (
    experiment_summary,
    normalize_experiment_handoffs,
    normalize_experiment_plans,
    normalize_experiment_runs,
    normalize_hypotheses,
    normalize_iteration_history,
    normalize_learning_decisions,
    normalize_prototypes as normalize_managed_prototypes,
)
from .research import (
    normalize_behavioral_signals,
    normalize_journeys,
    normalize_personas as normalize_research_personas,
    normalize_stakeholders as normalize_research_stakeholders,
    research_summary,
)
from .platform import (
    normalize_platform_connections,
    normalize_interoperability_profiles,
    normalize_workflow_links,
    normalize_exchange_records,
    normalize_platform_events,
    platform_summary,
)
from .collaboration import (
    collaboration_summary,
    normalize_approvals,
    normalize_comments,
    normalize_publication_handoffs,
    normalize_publication_records,
    normalize_release_history,
    normalize_review_assignments,
    normalize_workspace_members,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "catalyst_canvas_contract_2_0.schema.json"


class CanvasContractError(ValueError):
    """Base error for contract normalization and validation failures."""


class CanvasValidationError(CanvasContractError):
    """Raised when a payload does not satisfy the active Canvas contract."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4()}"


def clean_text(value: Any, fallback: str = "") -> str:
    text = str(value or "").strip()
    return text if text else fallback


def clean_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.splitlines() if item.strip()]
    if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray, Mapping)):
        return [clean_text(item) for item in value if clean_text(item)]
    return [clean_text(value)] if clean_text(value) else []


def strip_internal_fields(contract: Mapping[str, Any]) -> Dict[str, Any]:
    """Return a deep copy without adapter/storage keys prefixed by an underscore."""
    return {
        key: deepcopy(value)
        for key, value in contract.items()
        if not str(key).startswith("_")
    }


def load_schema() -> Dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def validation_errors(contract: Mapping[str, Any]) -> List[str]:
    payload = strip_internal_fields(contract)
    validator = Draft202012Validator(load_schema())
    errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.absolute_path))
    messages: List[str] = []
    for error in errors:
        path = ".".join(str(part) for part in error.absolute_path) or "$"
        messages.append(f"{path}: {error.message}")
    return messages


def validate_contract(contract: Mapping[str, Any]) -> Dict[str, Any]:
    payload = strip_internal_fields(contract)
    errors = validation_errors(payload)
    if errors:
        raise CanvasValidationError(f"{CONTRACT_VERSION} validation failed: " + "; ".join(errors))
    return payload


def normalize_owner_context(value: Any) -> Dict[str, str]:
    source = value if isinstance(value, Mapping) else {}
    return {
        "owner_id": clean_text(source.get("owner_id")),
        "name": clean_text(source.get("name")),
        "organization": clean_text(source.get("organization")),
        "role": clean_text(source.get("role")),
    }


def normalize_audience(value: Any) -> Dict[str, Any]:
    if isinstance(value, Mapping):
        return {
            "primary": clean_text(value.get("primary"), "A stakeholder who needs a clearer path forward."),
            "secondary": clean_list(value.get("secondary")),
            "affected": clean_list(value.get("affected")),
            "excluded": clean_list(value.get("excluded")),
        }
    return {
        "primary": clean_text(value, "A stakeholder who needs a clearer path forward."),
        "secondary": [],
        "affected": [],
        "excluded": [],
    }


def normalize_constraints(value: Any) -> List[Dict[str, str]]:
    raw: List[Any]
    if isinstance(value, list):
        raw = value
    elif value is None:
        raw = []
    else:
        raw = [value]
    if not raw:
        raw = ["Limited time, limited evidence, and competing priorities."]
    records: List[Dict[str, str]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"statement": item}
        records.append({
            "constraint_id": clean_text(source.get("constraint_id"), f"constraint-{index:03d}"),
            "statement": clean_text(source.get("statement"), "Limited time, limited evidence, and competing priorities."),
            "source": clean_text(source.get("source"), "input"),
        })
    return records


def normalize_personas(value: Any, *, audience: Dict[str, Any], challenge: str, goal: str, constraint: str) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if isinstance(value, Mapping) else [])
    if not raw:
        name = audience["primary"].split(",")[0].strip() or "Primary user"
        raw = [{
            "name": name,
            "description": (
                f"Needs help addressing: {challenge}. The user wants {goal.lower()} "
                f"while navigating {constraint.lower()}."
            ),
            "needs": [goal],
            "pains": [constraint],
            "source_type": "assumption",
            "confidence": "low",
        }]
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"name": item}
        records.append({
            "persona_id": clean_text(source.get("persona_id"), f"persona-{index:03d}"),
            "name": clean_text(source.get("name"), "Primary user"),
            "role": clean_text(source.get("role")),
            "description": clean_text(source.get("description")),
            "needs": clean_list(source.get("needs")),
            "pains": clean_list(source.get("pains")),
            "source_type": clean_text(source.get("source_type"), "assumption"),
            "confidence": clean_text(source.get("confidence"), "low"),
        })
    return records


def normalize_stakeholders(value: Any) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else []
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"name": item}
        records.append({
            "stakeholder_id": clean_text(source.get("stakeholder_id"), f"stakeholder-{index:03d}"),
            "name": clean_text(source.get("name"), "Unnamed stakeholder"),
            "relationship": clean_text(source.get("relationship"), "affected"),
            "influence": clean_text(source.get("influence"), "unknown"),
            "interest": clean_text(source.get("interest"), "unknown"),
            "notes": clean_text(source.get("notes")),
        })
    return records


def normalize_evidence(value: Any) -> List[Dict[str, str]]:
    raw = value if isinstance(value, list) else ([value] if clean_text(value) else [])
    records: List[Dict[str, str]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"summary": item}
        records.append({
            "evidence_id": clean_text(source.get("evidence_id"), f"evidence-{index:03d}"),
            "type": clean_text(source.get("type"), "note"),
            "title": clean_text(source.get("title"), "Available evidence"),
            "summary": clean_text(source.get("summary")),
            "citation": clean_text(source.get("citation")),
            "confidence": clean_text(source.get("confidence"), "medium"),
        })
    return records


def normalize_assumptions(value: Any) -> List[Dict[str, str]]:
    defaults = [
        "The stated audience is the right primary user for the first iteration.",
        "The goal is specific enough to test with a small prototype.",
        "The constraint is material and should remain visible in the design process.",
        "A lightweight brief can reduce ambiguity before heavier implementation work begins.",
    ]
    raw = value if isinstance(value, list) else ([value] if clean_text(value) else defaults)
    records: List[Dict[str, str]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"statement": item}
        records.append({
            "assumption_id": clean_text(source.get("assumption_id"), f"assumption-{index:03d}"),
            "statement": clean_text(source.get("statement")),
            "status": clean_text(source.get("status"), "untested"),
            "criticality": clean_text(source.get("criticality"), "medium"),
        })
    return records


def normalize_prototypes(value: Any) -> List[Dict[str, str]]:
    raw = value if isinstance(value, list) else ([value] if value else [])
    if not raw:
        raw = [{
            "title": "Reviewable Canvas Brief",
            "description": (
                "A one-page working artifact that captures the challenge, audience, goal, constraints, "
                "point of view, HMW prompts, prototype concept, assumptions, and test plan."
            ),
        }]
    records: List[Dict[str, str]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"description": item}
        records.append({
            "prototype_id": clean_text(source.get("prototype_id"), f"prototype-{index:03d}"),
            "title": clean_text(source.get("title"), "Prototype concept"),
            "description": clean_text(source.get("description")),
            "status": clean_text(source.get("status"), "concept"),
        })
    return records


def normalize_tests(value: Any) -> List[Dict[str, str]]:
    raw = value if isinstance(value, list) else ([value] if value else [])
    if not raw:
        raw = [{
            "title": "Stakeholder clarity review",
            "signal": "A stakeholder can explain the problem, proposed next step, and key assumption in their own words.",
            "method": "Share the brief with 3–5 users or reviewers and capture confusion, objections, missing evidence, and next-step clarity.",
            "learning_goal": "Determine whether the framing is clear enough to guide a real prototype or decision.",
        }]
    records: List[Dict[str, str]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"method": item}
        records.append({
            "test_id": clean_text(source.get("test_id"), f"test-{index:03d}"),
            "title": clean_text(source.get("title"), "Learning test"),
            "signal": clean_text(source.get("signal")),
            "method": clean_text(source.get("method")),
            "learning_goal": clean_text(source.get("learning_goal")),
            "status": clean_text(source.get("status"), "planned"),
        })
    return records


def normalize_review_notes(value: Any) -> List[Dict[str, str]]:
    defaults = [
        {"type": "review_question", "note": "What claim in this brief needs stronger evidence?"},
        {"type": "review_question", "note": "What assumption would most change the next step if it proved false?"},
        {"type": "review_question", "note": "What user signal would show that the prototype is worth continuing?"},
        {"type": "review_question", "note": "What should be rewritten to avoid overpromising?"},
    ]
    raw = value if isinstance(value, list) else ([value] if clean_text(value) else defaults)
    records: List[Dict[str, str]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"note": item}
        records.append({
            "review_note_id": clean_text(source.get("review_note_id"), f"review-{index:03d}"),
            "type": clean_text(source.get("type"), "note"),
            "note": clean_text(source.get("note")),
            "status": clean_text(source.get("status"), "open"),
        })
    return records


def normalize_provenance(value: Any, *, source_surface: str, migrated_from: str = "") -> Dict[str, Any]:
    source = value if isinstance(value, Mapping) else {}
    warnings = clean_list(source.get("warnings"))
    return {
        "generator": "catalyst-canvas",
        "generator_version": __version__,
        "source_surface": clean_text(source.get("source_surface"), source_surface),
        "source_version": clean_text(source.get("source_version"), __version__),
        "migrated_from": clean_text(source.get("migrated_from"), migrated_from),
        "warnings": warnings,
    }


def build_contract(payload: Mapping[str, Any] | None = None, *, source_surface: str = "python") -> Dict[str, Any]:
    """Normalize a compact or partially structured payload into Canvas Contract 2.0."""
    from .frameworks import framework_record

    source: Mapping[str, Any] = payload or {}
    challenge = clean_text(
        source.get("challenge"),
        "A team is working through an unclear sustainability or systems problem.",
    )
    audience = normalize_audience(source.get("audience"))
    goal = clean_text(source.get("goal"), "Create a more useful, testable, and reviewable next step.")
    constraints = normalize_constraints(source.get("constraints", source.get("constraint")))
    constraint_text = constraints[0]["statement"]
    personas = normalize_research_personas(
        source.get("personas", source.get("persona")),
        audience=audience,
        challenge=challenge,
        goal=goal,
        constraint=constraint_text,
    )
    primary_persona = personas[0]
    stakeholders = normalize_research_stakeholders(source.get("stakeholders"))
    journeys = normalize_journeys(source.get("journeys", source.get("journey")), personas=personas, goal=goal)
    behavioral_signals = normalize_behavioral_signals(source.get("behavioral_signals"))
    point_of_view = source.get("point_of_view")
    if isinstance(point_of_view, Mapping):
        pov = {
            "statement": clean_text(point_of_view.get("statement")),
            "persona_id": clean_text(point_of_view.get("persona_id"), primary_persona["persona_id"]),
        }
    else:
        pov = {
            "statement": clean_text(
                point_of_view,
                (
                    f"{primary_persona['name']} needs a practical way to address '{challenge}' so they can "
                    f"{goal.lower().rstrip('.')} without ignoring the constraint: {constraint_text.rstrip('.')}."
                ),
            ),
            "persona_id": primary_persona["persona_id"],
        }

    raw_hmw = source.get("how_might_we")
    if isinstance(raw_hmw, list) and raw_hmw:
        hmw_items = raw_hmw
    elif clean_text(raw_hmw):
        hmw_items = [raw_hmw]
    else:
        hmw_items = [
            f"How might we help {primary_persona['name']} make the challenge concrete enough to act on?",
            f"How might we turn the goal — {goal.rstrip('.')} — into a small testable experiment?",
            f"How might we make the constraint visible without letting it stop progress?",
            "How might we document assumptions so the next decision can be reviewed?",
        ]
    hmw_records: List[Dict[str, str]] = []
    for index, item in enumerate(hmw_items, start=1):
        item_source = item if isinstance(item, Mapping) else {"question": item}
        hmw_records.append({
            "hmw_id": clean_text(item_source.get("hmw_id"), f"hmw-{index:03d}"),
            "question": clean_text(item_source.get("question")),
            "status": clean_text(item_source.get("status"), "candidate"),
        })

    custom_frameworks = normalize_custom_frameworks(source.get("custom_frameworks"))
    prompt_packs = normalize_prompt_packs(source.get("prompt_packs"))
    framework_value = source.get("framework", "AIDA")
    if isinstance(framework_value, Mapping):
        framework_value = framework_value.get("key", "AIDA")
    framework = framework_record(framework_value, custom_frameworks)

    created_at = clean_text(source.get("created_at"), utc_now())
    updated_at = clean_text(source.get("updated_at"), created_at)
    canvas_id = clean_text(source.get("canvas_id"), new_id("canvas"))
    revision_id = clean_text(source.get("revision_id"), new_id("revision"))
    title = clean_text(source.get("title"), "Catalyst Canvas Brief")
    sources = normalize_sources(source.get("sources", source.get("source_records")))
    evidence = normalize_ledger_evidence(source.get("evidence"))
    assumptions = normalize_ledger_assumptions(source.get("assumptions", source.get("assumption")))
    claims = normalize_claims(source.get("claims"))
    research_questions = normalize_research_questions(source.get("research_questions"))
    interview_guides = normalize_interview_guides(source.get("interview_guides"))
    observation_notes = normalize_observation_notes(source.get("observation_notes"))
    handoffs = normalize_handoffs(source.get("handoffs"))
    prototypes = normalize_managed_prototypes(source.get("prototypes", source.get("prototype")), generated_at=updated_at)
    sessions = normalize_ideation_sessions(source.get("ideation_sessions"), framework_key=framework["key"], created_at=created_at)
    clusters = normalize_idea_clusters(source.get("idea_clusters"))
    ideas = normalize_ideas(
        source.get("ideas"),
        sessions=sessions,
        hmw_ids=[item["hmw_id"] for item in hmw_records],
        framework_prompts=framework["prompts"],
        prototypes=prototypes,
        created_at=created_at,
    )
    cluster_map = {cluster["cluster_id"]: cluster for cluster in clusters}
    for idea in ideas:
        cluster_id = idea.get("cluster_id")
        if cluster_id and cluster_id in cluster_map and idea["idea_id"] not in cluster_map[cluster_id]["idea_ids"]:
            cluster_map[cluster_id]["idea_ids"].append(idea["idea_id"])

    decision_criteria = normalize_criteria(source.get("decision_criteria", source.get("criteria_library")))
    decision_options = normalize_decision_options(
        source.get("decision_options", source.get("prioritization_evaluations")),
        criteria=decision_criteria,
        ideas=ideas,
        prototypes=prototypes,
        generated_at=updated_at,
    )
    sensitivity_views = normalize_sensitivity_views(
        source.get("sensitivity_views"),
        options=decision_options,
        criteria=decision_criteria,
        generated_at=updated_at,
    )
    decision_notes = normalize_decision_notes(source.get("decision_notes"), generated_at=updated_at)
    decision_handoffs = normalize_decision_handoffs(source.get("decision_handoffs"), generated_at=updated_at)
    hypotheses = normalize_hypotheses(source.get("hypotheses"), assumptions=assumptions, prototypes=prototypes, generated_at=updated_at)
    experiment_plans = normalize_experiment_plans(
        source.get("experiment_plans"),
        legacy_tests=source.get("tests", source.get("test_plan")),
        hypotheses=hypotheses,
        prototypes=prototypes,
        generated_at=updated_at,
    )
    experiment_runs = normalize_experiment_runs(source.get("experiment_runs"), generated_at=updated_at)
    learning_decisions = normalize_learning_decisions(source.get("learning_decisions"), generated_at=updated_at)
    iteration_history = normalize_iteration_history(source.get("iteration_history"), generated_at=updated_at)
    experiment_handoffs = normalize_experiment_handoffs(source.get("experiment_handoffs"), generated_at=updated_at)
    owner_context = normalize_owner_context(source.get("owner_context"))
    workspace_members = normalize_workspace_members(source.get("workspace_members"), owner_context=owner_context, generated_at=updated_at)
    review_assignments = normalize_review_assignments(source.get("review_assignments"), generated_at=updated_at)
    comments = normalize_comments(source.get("comments"), generated_at=updated_at)
    approvals = normalize_approvals(source.get("approvals"), generated_at=updated_at)
    publication_records = normalize_publication_records(
        source.get("publication_records"), revision_id=revision_id, title=title, generated_at=updated_at
    )
    release_history = normalize_release_history(source.get("release_history"), generated_at=updated_at)
    publication_handoffs = normalize_publication_handoffs(source.get("publication_handoffs"), generated_at=updated_at)
    platform_connections = normalize_platform_connections(source.get("platform_connections"), generated_at=updated_at)
    interoperability_profiles = normalize_interoperability_profiles(source.get("interoperability_profiles"), generated_at=updated_at)
    workflow_links = normalize_workflow_links(source.get("workflow_links"), generated_at=updated_at)
    exchange_records = normalize_exchange_records(source.get("exchange_records"), generated_at=updated_at)
    platform_events = normalize_platform_events(source.get("platform_events"), generated_at=updated_at)
    subsystem_readiness = {
        "research": str(research_summary(personas, stakeholders, journeys, behavioral_signals, generated_at=updated_at).get("readiness", "")),
        "evidence": str(ledger_summary(sources, evidence, claims, assumptions, research_questions, generated_at=updated_at).get("evidence_coverage", "")),
        "ideation": str(ideation_summary(sessions, ideas, list(cluster_map.values()), generated_at=updated_at).get("readiness", "")),
        "decision": str(prioritization_summary(decision_criteria, decision_options, sensitivity_views, generated_at=updated_at).get("readiness", "")),
        "experiment": str(experiment_summary(prototypes, hypotheses, experiment_plans, experiment_runs, learning_decisions, iteration_history, generated_at=updated_at).get("readiness", "")),
        "collaboration": str(collaboration_summary(workspace_members, review_assignments, comments, approvals, publication_records, release_history, generated_at=updated_at).get("readiness", "")),
    }

    contract = {
        "schema_version": CONTRACT_VERSION,
        "canvas_id": canvas_id,
        "challenge_id": clean_text(source.get("challenge_id"), "challenge-primary"),
        "revision_id": revision_id,
        "title": title,
        "status": clean_text(source.get("status"), "draft"),
        "owner_context": owner_context,
        "created_at": created_at,
        "updated_at": updated_at,
        "challenge": challenge,
        "audience": audience,
        "goal": goal,
        "constraints": constraints,
        "personas": personas,
        "stakeholders": stakeholders,
        "journeys": journeys,
        "behavioral_signals": behavioral_signals,
        "research_summary": research_summary(personas, stakeholders, journeys, behavioral_signals, generated_at=updated_at),
        "point_of_view": pov,
        "how_might_we": hmw_records,
        "framework": framework,
        "custom_frameworks": custom_frameworks,
        "prompt_packs": prompt_packs,
        "ideation_sessions": sessions,
        "ideas": ideas,
        "idea_clusters": list(cluster_map.values()),
        "ideation_summary": ideation_summary(sessions, ideas, list(cluster_map.values()), generated_at=updated_at),
        "decision_criteria": decision_criteria,
        "decision_options": decision_options,
        "sensitivity_views": sensitivity_views,
        "decision_notes": decision_notes,
        "decision_handoffs": decision_handoffs,
        "prioritization_summary": prioritization_summary(decision_criteria, decision_options, sensitivity_views, generated_at=updated_at),
        "sources": sources,
        "evidence": evidence,
        "claims": claims,
        "assumptions": assumptions,
        "research_questions": research_questions,
        "interview_guides": interview_guides,
        "observation_notes": observation_notes,
        "synthesis_tags": clean_list(source.get("synthesis_tags")),
        "ledger_summary": ledger_summary(sources, evidence, claims, assumptions, research_questions, generated_at=updated_at),
        "handoffs": handoffs,
        "prototypes": prototypes,
        "hypotheses": hypotheses,
        "experiment_plans": experiment_plans,
        "experiment_runs": experiment_runs,
        "learning_decisions": learning_decisions,
        "iteration_history": iteration_history,
        "experiment_handoffs": experiment_handoffs,
        "experiment_summary": experiment_summary(
            prototypes, hypotheses, experiment_plans, experiment_runs, learning_decisions, iteration_history, generated_at=updated_at
        ),
        "workspace_members": workspace_members,
        "review_assignments": review_assignments,
        "comments": comments,
        "approvals": approvals,
        "publication_records": publication_records,
        "release_history": release_history,
        "publication_handoffs": publication_handoffs,
        "collaboration_summary": collaboration_summary(
            workspace_members, review_assignments, comments, approvals, publication_records, release_history, generated_at=updated_at
        ),
        "platform_connections": platform_connections,
        "interoperability_profiles": interoperability_profiles,
        "workflow_links": workflow_links,
        "exchange_records": exchange_records,
        "platform_events": platform_events,
        "platform_summary": platform_summary(
            platform_connections, interoperability_profiles, workflow_links, exchange_records, platform_events,
            subsystem_readiness=subsystem_readiness, generated_at=updated_at
        ),
        "tests": normalize_tests(source.get("tests", source.get("test_plan"))),
        "review_notes": normalize_review_notes(source.get("review_notes", source.get("review_note"))),
        "provenance": normalize_provenance(source.get("provenance"), source_surface=source_surface),
    }
    return validate_contract(contract)
