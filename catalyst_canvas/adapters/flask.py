"""Flask form and view adapters for Canvas Contract 1.0."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Mapping

from ..contract import build_contract, clean_text, new_id, strip_internal_fields, utc_now, validate_contract
from ..frameworks import framework_record


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
        "goal": data["goal"],
        "constraint": _first(data["constraints"]).get("statement", ""),
        "persona_name": persona.get("name", ""),
        "persona_role": persona.get("role", ""),
        "persona_needs": "\n".join(persona.get("needs", [])),
        "persona_pains": "\n".join(persona.get("pains", [])),
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
        compact["persona"] = {
            "name": form.get("persona_name"),
            "role": form.get("persona_role"),
            "needs": [form.get("persona_needs")] if clean_text(form.get("persona_needs")) else [],
            "pains": [form.get("persona_pains")] if clean_text(form.get("persona_pains")) else [],
            "source_type": "assumption",
            "confidence": "low",
        }
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
    if "constraint" in form:
        updated["constraints"][0]["statement"] = clean_text(form.get("constraint"), updated["constraints"][0]["statement"])

    persona = updated["personas"][0]
    for form_key, contract_key in (("persona_name", "name"), ("persona_role", "role")):
        if form_key in form:
            persona[contract_key] = clean_text(form.get(form_key), persona[contract_key])
    if "persona_needs" in form:
        persona["needs"] = [clean_text(form.get("persona_needs"))] if clean_text(form.get("persona_needs")) else []
    if "persona_pains" in form:
        persona["pains"] = [clean_text(form.get("persona_pains"))] if clean_text(form.get("persona_pains")) else []

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
                "evidence_id": "evidence-001", "type": "note", "title": "Available evidence",
                "summary": summary, "citation": "", "confidence": "medium"
            }]
    if "assumption" in form:
        statement = clean_text(form.get("assumption"))
        if updated["assumptions"]:
            updated["assumptions"][0]["statement"] = statement
        elif statement:
            updated["assumptions"] = [{
                "assumption_id": "assumption-001", "statement": statement,
                "status": "untested", "criticality": "medium"
            }]
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
    return validate_contract(updated)
