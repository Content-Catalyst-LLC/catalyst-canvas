"""Flask form and view adapters for Canvas Contract 2.0."""

from __future__ import annotations

from copy import deepcopy
import json
from typing import Any, Dict, Mapping

from ..contract import build_contract, clean_text, new_id, strip_internal_fields, utc_now, validate_contract
from ..frameworks import framework_record
from ..persona_templates import persona_template
from ..research import (normalize_behavioral_signals, normalize_journeys, normalize_stakeholders, parse_behavioral_signal_csv, research_summary)
from ..ledger import ledger_summary


def compact_to_contract(payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Generate a canonical contract through the Flask surface adapter."""
    return build_contract(payload, source_surface="flask")


def default_contract() -> Dict[str, Any]:
    return build_contract({
        "title": "Sample Catalyst Canvas Brief",
        "challenge": "A sustainability team needs to turn broad impact goals into testable work.",
        "audience": "sustainability managers and cross-functional project leads",
        "goal": "create a reviewable experiment plan",
        "constraint": "limited data quality and competing stakeholder expectations",
        "persona": {
            "name": "Sustainability Manager",
            "role": "Turns broad climate and impact commitments into measurable work.",
            "description": "Needs a clearer way to connect goals, evidence, experiments, and reporting outputs.",
            "needs": ["A clearer way to connect goals, evidence, experiments, and reporting outputs."],
            "pains": ["Fragmented data, unclear ownership, and pressure to communicate before evidence is ready."],
            "source_type": "assumption",
            "confidence": "low"
        },
        "evidence": "Stakeholder interviews, current reporting artifacts, available indicators, and known data gaps.",
        "assumption": "A lightweight Canvas workflow can reduce ambiguity before heavier analytics work begins.",
        "prototype": "A one-page decision brief with claim, source, assumption, experiment, and review sections.",
        "test_plan": {
            "title": "Project-team clarity review",
            "method": "Run the Canvas with one project team and compare clarity before and after the workshop.",
            "signal": "The team can identify one testable next step and one unsupported claim to revise.",
            "learning_goal": "Determine whether the Canvas reduces ambiguity enough to guide the next experiment."
        },
        "review_notes": [
            {"type": "risk", "note": "Do not convert workshop confidence into proof of impact."},
            {"type": "note", "note": "Require evidence notes before moving from prototype to public claim."}
        ],
    }, source_surface="flask")


def _first(records: list[dict[str, Any]]) -> dict[str, Any]:
    return records[0] if records else {}


def _lines(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.splitlines() if item.strip()]
    if isinstance(value, list):
        return [clean_text(item) for item in value if clean_text(item)]
    return [clean_text(value)] if clean_text(value) else []


def _parse_stakeholder_lines(value: Any) -> list[dict[str, Any]]:
    records = []
    for index, line in enumerate(_lines(value), start=1):
        parts = [part.strip() for part in line.split("|")]
        parts += [""] * (11 - len(parts))
        records.append({
            "stakeholder_id": f"stakeholder-{index:03d}",
            "name": parts[0] or f"Stakeholder {index}",
            "stakeholder_type": parts[1] or "other",
            "influence": parts[2] or 3,
            "interest": parts[3] or 3,
            "impact": parts[4] or 3,
            "stance": parts[5] or "unknown",
            "decision_role": parts[6] or "affected",
            "engagement_strategy": parts[7],
            "responsibilities": _lines(parts[8].replace(";", "\n")),
            "tensions": _lines(parts[9].replace(";", "\n")),
            "notes": parts[10],
        })
    return records

def _parse_stage_lines(value: Any) -> list[dict[str, Any]]:
    stages = []
    for index, line in enumerate(_lines(value), start=1):
        parts = [part.strip() for part in line.split("|")]
        parts += [""] * (12 - len(parts))
        stages.append({
            "stage_id": f"stage-{index:03d}",
            "name": parts[0] or f"Stage {index}",
            "actions": _lines(parts[1].replace(";", "\n")),
            "questions": _lines(parts[2].replace(";", "\n")),
            "emotion": parts[3] or 0,
            "frictions": _lines(parts[4].replace(";", "\n")),
            "opportunities": _lines(parts[5].replace(";", "\n")),
            "touchpoints": _lines(parts[6].replace(";", "\n")),
            "channels": _lines(parts[7].replace(";", "\n")),
            "metrics": _lines(parts[8].replace(";", "\n")),
            "owner": parts[9],
            "evidence_ids": _lines(parts[10].replace(",", "\n")),
            "experiment_ids": _lines(parts[11].replace(",", "\n")),
        })
    return stages

def _parse_pipe_records(value: Any, fields: list[str]) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for line in _lines(value):
        parts = [part.strip() for part in line.split("|")]
        parts += [""] * max(0, len(fields) - len(parts))
        records.append(dict(zip(fields, parts[:len(fields)])))
    return records


def _csv_list(value: str) -> list[str]:
    return [item.strip() for item in str(value or "").replace(";", ",").split(",") if item.strip()]


def contract_to_form(contract: Mapping[str, Any], *, storage_id: int | None = None) -> Dict[str, Any]:
    data = validate_contract(contract)
    persona = _first(data["personas"])
    prototype = _first(data["prototypes"])
    test = _first(data["tests"])
    risk = next((item for item in data["review_notes"] if item["type"] == "risk"), {})
    review = next((item for item in data["review_notes"] if item["type"] != "risk"), {})
    evidence = _first(data["evidence"])
    assumption = _first(data["assumptions"])
    result = {
        "id": storage_id,
        "schema_version": data["schema_version"],
        "canvas_id": data["canvas_id"],
        "revision_id": data["revision_id"],
        "title": data["title"],
        "status": data["status"],
        "challenge": data["challenge"],
        "audience": data["audience"]["primary"],
        "audience_secondary": "\n".join(data["audience"].get("secondary", [])),
        "audience_affected": "\n".join(data["audience"].get("affected", [])),
        "audience_excluded": "\n".join(data["audience"].get("excluded", [])),
        "goal": data["goal"],
        "constraint": _first(data["constraints"]).get("statement", ""),
        "persona_name": persona.get("name", ""),
        "persona_role": persona.get("role", ""),
        "persona_context": persona.get("context", ""),
        "persona_jobs": "\n".join(persona.get("jobs", [])),
        "persona_goals": "\n".join(persona.get("goals", [])),
        "persona_needs": "\n".join(persona.get("needs", [])),
        "persona_pains": "\n".join(persona.get("pains", [])),
        "persona_gains": "\n".join(persona.get("gains", [])),
        "persona_behaviors": "\n".join(persona.get("behaviors", [])),
        "persona_barriers": "\n".join(persona.get("barriers", [])),
        "persona_motivations": "\n".join(persona.get("motivations", [])),
        "persona_accessibility": "\n".join(persona.get("accessibility_needs", [])),
        "persona_channels": "\n".join(persona.get("preferred_channels", [])),
        "persona_quotes": "\n".join(persona.get("quotes", [])),
        "persona_empathy_says": "\n".join(persona.get("empathy_map", {}).get("says", [])),
        "persona_empathy_thinks": "\n".join(persona.get("empathy_map", {}).get("thinks", [])),
        "persona_empathy_does": "\n".join(persona.get("empathy_map", {}).get("does", [])),
        "persona_empathy_feels": "\n".join(persona.get("empathy_map", {}).get("feels", [])),
        "persona_empathy_sees": "\n".join(persona.get("empathy_map", {}).get("sees", [])),
        "persona_empathy_hears": "\n".join(persona.get("empathy_map", {}).get("hears", [])),
        "persona_attribute_lines": "\n".join(" | ".join([item.get("category", "other"), item.get("statement", ""), item.get("basis", "assumed"), item.get("confidence", "low"), ", ".join(item.get("evidence_ids", [])), item.get("notes", "")]) for item in persona.get("attributes", [])),
        "persona_evidence_ids": "\n".join(persona.get("evidence_ids", [])),
        "persona_assumption_ids": "\n".join(persona.get("assumption_ids", [])),
        "persona_tags": "\n".join(persona.get("tags", [])),
        "persona_source_type": persona.get("source_type", "assumption"),
        "persona_source_notes": persona.get("source_notes", ""),
        "persona_confidence": persona.get("confidence", "low"),
        "persona_confidence_notes": persona.get("confidence_notes", ""),
        "persona_validation_status": persona.get("validation_status", "hypothesis"),
        "stakeholder_lines": "\n".join(
            " | ".join([item.get("name", ""), item.get("stakeholder_type", "other"), str(item.get("influence", 3)), str(item.get("interest", 3)), str(item.get("impact", 3)), item.get("stance", "unknown"), item.get("decision_role", "affected"), item.get("engagement_strategy", ""), "; ".join(item.get("responsibilities", [])), "; ".join(item.get("tensions", [])), item.get("notes", "")])
            for item in data.get("stakeholders", [])
        ),
        "journey_title": _first(data.get("journeys", [])).get("title", ""),
        "journey_scenario": _first(data.get("journeys", [])).get("scenario", ""),
        "journey_outcome": _first(data.get("journeys", [])).get("desired_outcome", ""),
        "journey_status": _first(data.get("journeys", [])).get("status", "draft"),
        "journey_stages": "\n".join(
            " | ".join([stage.get("name", ""), "; ".join(stage.get("actions", [])), "; ".join(stage.get("questions", [])), str(stage.get("emotion", 0)), "; ".join(stage.get("frictions", [])), "; ".join(stage.get("opportunities", [])), "; ".join(stage.get("touchpoints", [])), "; ".join(stage.get("channels", [])), "; ".join(stage.get("metrics", [])), stage.get("owner", ""), ", ".join(stage.get("evidence_ids", [])), ", ".join(stage.get("experiment_ids", []))])
            for stage in _first(data.get("journeys", [])).get("stages", [])
        ),
        "behavioral_signal_csv": "metric,segment,value,period,interpretation,limitation,evidence_ids,tags\n" + "\n".join(
            ",".join([item.get("metric", ""), item.get("segment", ""), item.get("value", ""), item.get("period", ""), item.get("interpretation", ""), item.get("limitation", ""), ";".join(item.get("evidence_ids", [])), ";".join(item.get("tags", []))])
            for item in data.get("behavioral_signals", [])
        ) if data.get("behavioral_signals") else "",
        "behavioral_signal_source_type": data.get("behavioral_signals", [{}])[0].get("source_type", "analytics_csv") if data.get("behavioral_signals") else "analytics_csv",
        "source_lines": "\n".join(" | ".join([item.get("source_type", "other"), item.get("title", ""), item.get("creator", ""), item.get("source_date", ""), item.get("url", ""), item.get("owner", ""), "; ".join(item.get("limitations", [])), ", ".join(item.get("tags", [])), item.get("knowledge_library_record_id", ""), item.get("description", "")]) for item in data.get("sources", [])),
        "evidence_lines": "\n".join(" | ".join([item.get("title", ""), item.get("evidence_type", "note"), item.get("source_id", ""), item.get("summary", ""), item.get("quote", ""), item.get("locator", ""), item.get("citation", ""), item.get("confidence", "unknown"), "; ".join(item.get("limitations", [])), ", ".join(item.get("tags", []))]) for item in data.get("evidence", [])),
        "claim_lines": "\n".join(" | ".join([item.get("state", "unsupported"), item.get("statement", ""), item.get("owner", ""), item.get("confidence", "unknown"), ", ".join(item.get("evidence_ids", [])), ", ".join(item.get("assumption_ids", [])), item.get("uncertainty", ""), "; ".join(item.get("limitations", [])), "; ".join(item.get("contradictions", [])), "; ".join(item.get("missing_data", [])), item.get("review_status", "draft"), ", ".join(item.get("tags", []))]) for item in data.get("claims", [])),
        "assumption_lines": "\n".join(" | ".join([item.get("criticality", "medium"), item.get("statement", ""), item.get("owner", ""), item.get("confidence", "unknown"), item.get("consequence", ""), item.get("test_method", ""), item.get("status", "untested"), ", ".join(item.get("experiment_ids", [])), ", ".join(item.get("evidence_ids", [])), item.get("due_date", ""), "; ".join(item.get("limitations", [])), ", ".join(item.get("tags", []))]) for item in data.get("assumptions", [])),
        "research_question_lines": "\n".join(" | ".join([item.get("priority", "medium"), item.get("question", ""), item.get("owner", ""), item.get("status", "open"), ", ".join(item.get("source_ids", [])), ", ".join(item.get("evidence_ids", [])), item.get("notes", ""), ", ".join(item.get("tags", []))]) for item in data.get("research_questions", [])),
        "interview_guide_lines": "\n".join(" | ".join([item.get("title", ""), item.get("purpose", ""), item.get("audience", ""), "; ".join(item.get("questions", [])), item.get("owner", ""), item.get("status", "draft"), ", ".join(item.get("source_ids", [])), ", ".join(item.get("tags", []))]) for item in data.get("interview_guides", [])),
        "observation_note_lines": "\n".join(" | ".join([item.get("title", ""), item.get("note", ""), item.get("observed_at", ""), item.get("observer", ""), item.get("context", ""), item.get("source_id", ""), ", ".join(item.get("evidence_ids", [])), "; ".join(item.get("limitations", [])), ", ".join(item.get("tags", []))]) for item in data.get("observation_notes", [])),
        "synthesis_tags": "\n".join(data.get("synthesis_tags", [])),
        "handoff_lines": "\n".join(" | ".join([item.get("target", "knowledge_library"), item.get("status", "draft"), item.get("purpose", ""), item.get("context_note", ""), ", ".join(item.get("source_ids", [])), ", ".join(item.get("evidence_ids", [])), ", ".join(item.get("claim_ids", [])), ", ".join(item.get("assumption_ids", [])), item.get("created_by", "")]) for item in data.get("handoffs", [])),
        "ideation_session_title": _first(data.get("ideation_sessions", [])).get("title", ""),
        "ideation_mode": _first(data.get("ideation_sessions", [])).get("mode", "divergent"),
        "ideation_facilitator": _first(data.get("ideation_sessions", [])).get("facilitator", ""),
        "ideation_participants": "\n".join(_first(data.get("ideation_sessions", [])).get("participants", [])),
        "ideation_status": _first(data.get("ideation_sessions", [])).get("status", "planned"),
        "ideation_notes": _first(data.get("ideation_sessions", [])).get("notes", ""),
        "idea_lines": "\n".join(" | ".join([item.get("title", ""), item.get("description", ""), item.get("author", ""), item.get("rationale", ""), item.get("hmw_id", ""), item.get("prompt_id", ""), ", ".join(item.get("tags", [])), item.get("cluster_id", ""), item.get("status", "captured"), str(item.get("vote_count", 0)), ", ".join(item.get("prototype_ids", [])), ", ".join(item.get("assumption_ids", [])), ", ".join(item.get("evidence_ids", [])), ", ".join(item.get("parent_idea_ids", [])), item.get("merged_into_id", "")]) for item in data.get("ideas", [])),
        "cluster_lines": "\n".join(" | ".join([item.get("name", ""), item.get("description", ""), ", ".join(item.get("idea_ids", [])), ", ".join(item.get("tags", [])), item.get("rationale", ""), str(item.get("sequence", 1))]) for item in data.get("idea_clusters", [])),
        "custom_frameworks_json": json.dumps(data.get("custom_frameworks", []), ensure_ascii=False, indent=2),
        "prompt_packs_json": json.dumps(data.get("prompt_packs", []), ensure_ascii=False, indent=2),
        "decision_criteria_json": json.dumps(data.get("decision_criteria", []), ensure_ascii=False, indent=2),
        "decision_options_json": json.dumps(data.get("decision_options", []), ensure_ascii=False, indent=2),
        "sensitivity_views_json": json.dumps(data.get("sensitivity_views", [])[1:], ensure_ascii=False, indent=2),
        "decision_notes_json": json.dumps(data.get("decision_notes", []), ensure_ascii=False, indent=2),
        "decision_handoffs_json": json.dumps(data.get("decision_handoffs", []), ensure_ascii=False, indent=2),
        "prototypes_json": json.dumps(data.get("prototypes", []), ensure_ascii=False, indent=2),
        "hypotheses_json": json.dumps(data.get("hypotheses", []), ensure_ascii=False, indent=2),
        "experiment_plans_json": json.dumps(data.get("experiment_plans", []), ensure_ascii=False, indent=2),
        "experiment_runs_json": json.dumps(data.get("experiment_runs", []), ensure_ascii=False, indent=2),
        "learning_decisions_json": json.dumps(data.get("learning_decisions", []), ensure_ascii=False, indent=2),
        "iteration_history_json": json.dumps(data.get("iteration_history", []), ensure_ascii=False, indent=2),
        "experiment_handoffs_json": json.dumps(data.get("experiment_handoffs", []), ensure_ascii=False, indent=2),
        "workspace_members_json": json.dumps(data.get("workspace_members", []), ensure_ascii=False, indent=2),
        "review_assignments_json": json.dumps(data.get("review_assignments", []), ensure_ascii=False, indent=2),
        "comments_json": json.dumps(data.get("comments", []), ensure_ascii=False, indent=2),
        "approvals_json": json.dumps(data.get("approvals", []), ensure_ascii=False, indent=2),
        "publication_records_json": json.dumps(data.get("publication_records", []), ensure_ascii=False, indent=2),
        "release_history_json": json.dumps(data.get("release_history", []), ensure_ascii=False, indent=2),
        "publication_handoffs_json": json.dumps(data.get("publication_handoffs", []), ensure_ascii=False, indent=2),
        "research_readiness": data.get("research_summary", {}).get("readiness", "hypothesis"),
        "evidence": evidence.get("summary", ""),
        "assumption": assumption.get("statement", ""),
        "point_of_view": data["point_of_view"]["statement"],
        "how_might_we": _first(data["how_might_we"]).get("question", ""),
        "framework": data["framework"]["key"],
        "prototype": prototype.get("description", ""),
        "test_plan": test.get("method", ""),
        "success_signal": test.get("signal", ""),
        "risk_note": risk.get("note", ""),
        "review_note": review.get("note", ""),
        "created_at": data["created_at"],
        "updated_at": data["updated_at"],
    }
    return result


def form_to_contract(form: Mapping[str, Any], existing: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    if existing is None:
        compact = {key: form.get(key) for key in form.keys()}
        compact["audience"] = {
            "primary": form.get("audience"),
            "secondary": _lines(form.get("audience_secondary")),
            "affected": _lines(form.get("audience_affected")),
            "excluded": _lines(form.get("audience_excluded")),
        }
        template = {}
        if clean_text(form.get("persona_template")):
            try:
                template = persona_template(clean_text(form.get("persona_template")))
            except KeyError:
                template = {}
        compact["persona"] = {
            "name": form.get("persona_name") or template.get("name"),
            "role": form.get("persona_role") or template.get("role"),
            "context": form.get("persona_context") or template.get("context"),
            "jobs": _lines(form.get("persona_jobs")) or template.get("jobs", []),
            "goals": _lines(form.get("persona_goals")) or template.get("goals", []),
            "needs": _lines(form.get("persona_needs")),
            "pains": _lines(form.get("persona_pains")) or template.get("pains", []),
            "gains": _lines(form.get("persona_gains")) or template.get("gains", []),
            "behaviors": _lines(form.get("persona_behaviors")) or template.get("behaviors", []),
            "barriers": _lines(form.get("persona_barriers")) or template.get("barriers", []),
            "motivations": _lines(form.get("persona_motivations")) or template.get("motivations", []),
            "accessibility_needs": _lines(form.get("persona_accessibility")),
            "preferred_channels": _lines(form.get("persona_channels")),
            "quotes": _lines(form.get("persona_quotes")),
            "empathy_map": {
                "says": _lines(form.get("persona_empathy_says")), "thinks": _lines(form.get("persona_empathy_thinks")),
                "does": _lines(form.get("persona_empathy_does")), "feels": _lines(form.get("persona_empathy_feels")),
                "sees": _lines(form.get("persona_empathy_sees")), "hears": _lines(form.get("persona_empathy_hears")),
            },
            "attributes": [
                {"category": parts[0] or "other", "statement": parts[1], "basis": parts[2] or "assumed", "confidence": parts[3] or "low", "evidence_ids": _lines(parts[4].replace(",", "\n")), "notes": parts[5]}
                for line in _lines(form.get("persona_attribute_lines"))
                for parts in [[part.strip() for part in line.split("|")] + [""] * 6]
                if parts[1]
            ],
            "evidence_ids": _lines(form.get("persona_evidence_ids")),
            "assumption_ids": _lines(form.get("persona_assumption_ids")),
            "tags": _lines(form.get("persona_tags")),
            "source_type": form.get("persona_source_type") or "assumption",
            "source_notes": form.get("persona_source_notes"),
            "confidence": form.get("persona_confidence") or "low",
            "confidence_notes": form.get("persona_confidence_notes"),
            "validation_status": form.get("persona_validation_status") or "hypothesis",
        }
        compact["stakeholders"] = _parse_stakeholder_lines(form.get("stakeholder_lines"))
        stages = _parse_stage_lines(form.get("journey_stages"))
        if clean_text(form.get("journey_title")) or stages:
            compact["journeys"] = [{
                "title": form.get("journey_title") or "Primary experience journey",
                "persona_id": "persona-001",
                "scenario": form.get("journey_scenario"),
                "desired_outcome": form.get("journey_outcome"),
                "status": form.get("journey_status") or "draft",
                "stages": stages,
            }]
        compact["behavioral_signals"] = parse_behavioral_signal_csv(
            clean_text(form.get("behavioral_signal_csv")),
            source_type=clean_text(form.get("behavioral_signal_source_type"), "analytics_csv"),
        )
        return build_contract(compact, source_surface="flask")

    data = strip_internal_fields(existing)
    validate_contract(data)
    updated = deepcopy(data)
    updated["revision_id"] = new_id("revision")
    updated["updated_at"] = utc_now()
    updated["provenance"] = {
        **updated["provenance"],
        "generator_version": updated["provenance"]["generator_version"],
        "source_surface": "flask",
        "source_version": updated["provenance"]["generator_version"],
    }

    text_fields = ["title", "challenge", "goal"]
    for key in text_fields:
        if key in form:
            updated[key] = clean_text(form.get(key), updated[key])
    if "audience" in form:
        updated["audience"]["primary"] = clean_text(form.get("audience"), updated["audience"]["primary"])
    for form_key, audience_key in (("audience_secondary", "secondary"), ("audience_affected", "affected"), ("audience_excluded", "excluded")):
        if form_key in form:
            updated["audience"][audience_key] = _lines(form.get(form_key))
    if "constraint" in form:
        updated["constraints"][0]["statement"] = clean_text(form.get("constraint"), updated["constraints"][0]["statement"])

    persona = updated["personas"][0]
    for form_key, contract_key in (("persona_name", "name"), ("persona_role", "role"), ("persona_context", "context")):
        if form_key in form:
            persona[contract_key] = clean_text(form.get(form_key), persona.get(contract_key, ""))
    for form_key, contract_key in (
        ("persona_jobs", "jobs"), ("persona_goals", "goals"), ("persona_needs", "needs"), ("persona_pains", "pains"),
        ("persona_gains", "gains"), ("persona_behaviors", "behaviors"), ("persona_barriers", "barriers"),
        ("persona_motivations", "motivations"), ("persona_accessibility", "accessibility_needs"),
        ("persona_channels", "preferred_channels"), ("persona_quotes", "quotes"),
        ("persona_evidence_ids", "evidence_ids"), ("persona_assumption_ids", "assumption_ids"),
        ("persona_tags", "tags"),
    ):
        if form_key in form:
            persona[contract_key] = _lines(form.get(form_key))
    for form_key, contract_key in (("persona_source_type", "source_type"), ("persona_source_notes", "source_notes"), ("persona_confidence", "confidence"), ("persona_confidence_notes", "confidence_notes"), ("persona_validation_status", "validation_status")):
        if form_key in form:
            persona[contract_key] = clean_text(form.get(form_key), persona.get(contract_key, ""))

    if any(key in form for key in ("persona_empathy_says", "persona_empathy_thinks", "persona_empathy_does", "persona_empathy_feels", "persona_empathy_sees", "persona_empathy_hears")):
        persona["empathy_map"] = {
            "says": _lines(form.get("persona_empathy_says")), "thinks": _lines(form.get("persona_empathy_thinks")),
            "does": _lines(form.get("persona_empathy_does")), "feels": _lines(form.get("persona_empathy_feels")),
            "sees": _lines(form.get("persona_empathy_sees")), "hears": _lines(form.get("persona_empathy_hears")),
            "pains": persona.get("pains", []), "gains": persona.get("gains", []),
        }
    if "persona_attribute_lines" in form:
        persona["attributes"] = [
            {"attribute_id": f"attribute-{index:03d}", "category": parts[0] or "other", "statement": parts[1], "basis": parts[2] or "assumed", "confidence": parts[3] or "low", "evidence_ids": _lines(parts[4].replace(",", "\n")), "notes": parts[5]}
            for index, line in enumerate(_lines(form.get("persona_attribute_lines")), start=1)
            for parts in [[part.strip() for part in line.split("|")] + [""] * 6]
            if parts[1]
        ]

    if "stakeholder_lines" in form:
        updated["stakeholders"] = normalize_stakeholders(_parse_stakeholder_lines(form.get("stakeholder_lines")))
    if any(key in form for key in ("journey_title", "journey_scenario", "journey_outcome", "journey_status", "journey_stages")):
        existing_journey = _first(updated.get("journeys", []))
        journey_source = {
            **existing_journey,
            "title": form.get("journey_title", existing_journey.get("title", "Primary experience journey")),
            "persona_id": persona["persona_id"],
            "scenario": form.get("journey_scenario", existing_journey.get("scenario", "")),
            "desired_outcome": form.get("journey_outcome", existing_journey.get("desired_outcome", updated["goal"])),
            "status": form.get("journey_status", existing_journey.get("status", "draft")),
            "stages": _parse_stage_lines(form.get("journey_stages")) if "journey_stages" in form else existing_journey.get("stages", []),
        }
        updated["journeys"] = normalize_journeys([journey_source], personas=updated["personas"], goal=updated["goal"])

    if any(key in form for key in ("challenge", "audience", "goal", "constraint", "persona_name", "persona_needs", "persona_pains")):
        name = persona["name"] or updated["audience"]["primary"]
        constraint = updated["constraints"][0]["statement"]
        updated["point_of_view"] = {
            "persona_id": persona["persona_id"],
            "statement": f"{name} needs a practical way to address '{updated['challenge']}' so they can {updated['goal'].lower()} without ignoring the constraint: {constraint}.",
        }

    if "how_might_we" in form:
        updated["how_might_we"][0]["question"] = clean_text(form.get("how_might_we"), updated["how_might_we"][0]["question"])
    if "framework" in form:
        updated["framework"] = framework_record(form.get("framework"))
    if "evidence" in form:
        summary = clean_text(form.get("evidence"))
        if updated["evidence"]:
            updated["evidence"][0]["summary"] = summary
        elif summary:
            updated["evidence"] = [{
                "evidence_id": "evidence-001", "source_id": "", "evidence_type": "note", "title": "Available evidence",
                "summary": summary, "quote": "", "locator": "", "citation": "", "url": "", "captured_at": "", "captured_by": "",
                "confidence": "medium", "limitations": [], "contradiction_ids": [], "tags": []
            }]
    if "assumption" in form:
        statement = clean_text(form.get("assumption"))
        if updated["assumptions"]:
            updated["assumptions"][0]["statement"] = statement
        elif statement:
            updated["assumptions"] = [{
                "assumption_id": "assumption-001", "statement": statement, "owner": "", "confidence": "unknown",
                "status": "untested", "criticality": "medium", "consequence": "", "test_method": "",
                "experiment_ids": [], "evidence_ids": [], "due_date": "", "limitations": [], "tags": []
            }]
    if "source_lines" in form:
        updated["sources"] = []
        for index, row in enumerate(_parse_pipe_records(form.get("source_lines"), ["source_type","title","creator","source_date","url","owner","limitations","tags","knowledge_library_record_id","description"]), start=1):
            if row["title"]:
                updated["sources"].append({**row, "source_id": f"source-{index:03d}", "publisher":"", "accessed_at":"", "rights":"", "limitations":_csv_list(row["limitations"]), "tags":_csv_list(row["tags"]), "provenance_note":""})
    if "evidence_lines" in form:
        updated["evidence"] = []
        for index, row in enumerate(_parse_pipe_records(form.get("evidence_lines"), ["title","evidence_type","source_id","summary","quote","locator","citation","confidence","limitations","tags"]), start=1):
            if row["title"] or row["summary"] or row["quote"]:
                updated["evidence"].append({**row, "evidence_id":f"evidence-{index:03d}", "url":"", "captured_at":"", "captured_by":"", "limitations":_csv_list(row["limitations"]), "contradiction_ids":[], "tags":_csv_list(row["tags"])})
    if "claim_lines" in form:
        updated["claims"] = []
        for index, row in enumerate(_parse_pipe_records(form.get("claim_lines"), ["state","statement","owner","confidence","evidence_ids","assumption_ids","uncertainty","limitations","contradictions","missing_data","review_status","tags"]), start=1):
            if row["statement"]:
                updated["claims"].append({**row, "claim_id":f"claim-{index:03d}", "evidence_ids":_csv_list(row["evidence_ids"]), "assumption_ids":_csv_list(row["assumption_ids"]), "source_ids":[], "limitations":_csv_list(row["limitations"]), "contradictions":_csv_list(row["contradictions"]), "missing_data":_csv_list(row["missing_data"]), "reviewed_by":"", "reviewed_at":"", "updated_at":updated["updated_at"], "tags":_csv_list(row["tags"])})
    if "assumption_lines" in form:
        updated["assumptions"] = []
        for index, row in enumerate(_parse_pipe_records(form.get("assumption_lines"), ["criticality","statement","owner","confidence","consequence","test_method","status","experiment_ids","evidence_ids","due_date","limitations","tags"]), start=1):
            if row["statement"]:
                updated["assumptions"].append({**row, "assumption_id":f"assumption-{index:03d}", "experiment_ids":_csv_list(row["experiment_ids"]), "evidence_ids":_csv_list(row["evidence_ids"]), "limitations":_csv_list(row["limitations"]), "tags":_csv_list(row["tags"])})
    if "research_question_lines" in form:
        updated["research_questions"] = []
        for index, row in enumerate(_parse_pipe_records(form.get("research_question_lines"), ["priority","question","owner","status","source_ids","evidence_ids","notes","tags"]), start=1):
            if row["question"]:
                updated["research_questions"].append({**row, "research_question_id":f"research-question-{index:03d}", "source_ids":_csv_list(row["source_ids"]), "evidence_ids":_csv_list(row["evidence_ids"]), "tags":_csv_list(row["tags"])})
    if "interview_guide_lines" in form:
        updated["interview_guides"] = []
        for index, row in enumerate(_parse_pipe_records(form.get("interview_guide_lines"), ["title","purpose","audience","questions","owner","status","source_ids","tags"]), start=1):
            if row["title"]:
                updated["interview_guides"].append({**row, "interview_guide_id":f"interview-guide-{index:03d}", "questions":_csv_list(row["questions"]), "source_ids":_csv_list(row["source_ids"]), "tags":_csv_list(row["tags"])})
    if "observation_note_lines" in form:
        updated["observation_notes"] = []
        for index, row in enumerate(_parse_pipe_records(form.get("observation_note_lines"), ["title","note","observed_at","observer","context","source_id","evidence_ids","limitations","tags"]), start=1):
            if row["note"]:
                updated["observation_notes"].append({**row, "observation_note_id":f"observation-{index:03d}", "evidence_ids":_csv_list(row["evidence_ids"]), "limitations":_csv_list(row["limitations"]), "tags":_csv_list(row["tags"])})
    if "synthesis_tags" in form:
        updated["synthesis_tags"] = _lines(form.get("synthesis_tags"))
    if "handoff_lines" in form:
        updated["handoffs"] = []
        for index, row in enumerate(_parse_pipe_records(form.get("handoff_lines"), ["target","status","purpose","context_note","source_ids","evidence_ids","claim_ids","assumption_ids","created_by"]), start=1):
            if row["purpose"] or row["context_note"]:
                updated["handoffs"].append({**row, "handoff_id":f"handoff-{index:03d}", "source_ids":_csv_list(row["source_ids"]), "evidence_ids":_csv_list(row["evidence_ids"]), "claim_ids":_csv_list(row["claim_ids"]), "assumption_ids":_csv_list(row["assumption_ids"]), "created_at":updated["updated_at"]})

    if any(key in form for key in ("ideation_session_title", "ideation_mode", "ideation_facilitator", "ideation_participants", "ideation_status", "ideation_notes")):
        session = _first(updated.get("ideation_sessions", []))
        updated["ideation_sessions"] = [{
            **session,
            "title": form.get("ideation_session_title", session.get("title", "Primary ideation session")),
            "mode": form.get("ideation_mode", session.get("mode", "divergent")),
            "framework_key": updated.get("framework", {}).get("key", "AIDA"),
            "challenge_ids": [updated.get("challenge_id", "challenge-primary")],
            "hmw_ids": [item.get("hmw_id", "") for item in updated.get("how_might_we", []) if item.get("hmw_id")],
            "facilitator": form.get("ideation_facilitator", session.get("facilitator", "")),
            "participants": _lines(form.get("ideation_participants")) if "ideation_participants" in form else session.get("participants", []),
            "status": form.get("ideation_status", session.get("status", "planned")),
            "notes": form.get("ideation_notes", session.get("notes", "")),
            "updated_at": updated["updated_at"],
        }]
    if "idea_lines" in form:
        updated["ideas"] = []
        for index, row in enumerate(_parse_pipe_records(form.get("idea_lines"), ["title","description","author","rationale","hmw_id","prompt_id","tags","cluster_id","status","vote_count","prototype_ids","assumption_ids","evidence_ids","parent_idea_ids","merged_into_id"]), start=1):
            if row["title"]:
                updated["ideas"].append({**row, "idea_id":f"idea-{index:03d}", "session_id":_first(updated.get("ideation_sessions", [])).get("session_id", "ideation-session-001"), "challenge_id":updated.get("challenge_id", "challenge-primary"), "tags":_csv_list(row["tags"]), "vote_count":row["vote_count"] or 0, "voter_ids":[], "prototype_ids":_csv_list(row["prototype_ids"]), "assumption_ids":_csv_list(row["assumption_ids"]), "evidence_ids":_csv_list(row["evidence_ids"]), "parent_idea_ids":_csv_list(row["parent_idea_ids"]), "created_at":updated["updated_at"], "updated_at":updated["updated_at"]})
    if "cluster_lines" in form:
        updated["idea_clusters"] = []
        for index, row in enumerate(_parse_pipe_records(form.get("cluster_lines"), ["name","description","idea_ids","tags","rationale","sequence"]), start=1):
            if row["name"]:
                updated["idea_clusters"].append({**row, "cluster_id":f"idea-cluster-{index:03d}", "idea_ids":_csv_list(row["idea_ids"]), "tags":_csv_list(row["tags"])})
    for form_key, contract_key in (
        ("custom_frameworks_json", "custom_frameworks"),
        ("prompt_packs_json", "prompt_packs"),
        ("decision_criteria_json", "decision_criteria"),
        ("decision_options_json", "decision_options"),
        ("sensitivity_views_json", "sensitivity_views"),
        ("decision_notes_json", "decision_notes"),
        ("decision_handoffs_json", "decision_handoffs"),
        ("prototypes_json", "prototypes"),
        ("hypotheses_json", "hypotheses"),
        ("experiment_plans_json", "experiment_plans"),
        ("experiment_runs_json", "experiment_runs"),
        ("learning_decisions_json", "learning_decisions"),
        ("iteration_history_json", "iteration_history"),
        ("experiment_handoffs_json", "experiment_handoffs"),
        ("workspace_members_json", "workspace_members"),
        ("review_assignments_json", "review_assignments"),
        ("comments_json", "comments"),
        ("approvals_json", "approvals"),
        ("publication_records_json", "publication_records"),
        ("release_history_json", "release_history"),
        ("publication_handoffs_json", "publication_handoffs"),
    ):
        if form_key in form:
            raw_json = clean_text(form.get(form_key), "[]")
            try:
                value = json.loads(raw_json)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{form_key} must contain valid JSON.") from exc
            updated[contract_key] = value if isinstance(value, list) else [value]

    if "prototype" in form:
        updated["prototypes"][0]["description"] = clean_text(form.get("prototype"), updated["prototypes"][0]["description"])
    if "test_plan" in form:
        updated["tests"][0]["method"] = clean_text(form.get("test_plan"), updated["tests"][0]["method"])
    if "success_signal" in form:
        updated["tests"][0]["signal"] = clean_text(form.get("success_signal"), updated["tests"][0]["signal"])

    def upsert_review(note_type: str, form_key: str) -> None:
        if form_key not in form:
            return
        note = clean_text(form.get(form_key))
        target = next((item for item in updated["review_notes"] if item["type"] == note_type), None)
        if target:
            target["note"] = note or target["note"]
        elif note:
            updated["review_notes"].append({
                "review_note_id": f"review-{len(updated['review_notes']) + 1:03d}",
                "type": note_type,
                "note": note,
                "status": "open",
            })

    upsert_review("risk", "risk_note")
    upsert_review("note", "review_note")
    if "behavioral_signal_csv" in form:
        updated["behavioral_signals"] = parse_behavioral_signal_csv(
            clean_text(form.get("behavioral_signal_csv")),
            source_type=clean_text(form.get("behavioral_signal_source_type"), "analytics_csv"),
        )
    updated["research_summary"] = research_summary(
        updated["personas"], updated["stakeholders"], updated.get("journeys", []), updated.get("behavioral_signals", []), generated_at=updated["updated_at"]
    )
    return build_contract(updated, source_surface="flask")
