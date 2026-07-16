"""Migration support for legacy exports and Canvas Contracts 1.0 through 1.3."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping

from .contract import CanvasContractError, build_contract, clean_text, validate_contract
from .version import CONTRACT_VERSION


class UnsupportedContractVersion(CanvasContractError):
    """Raised when an unknown future or incompatible contract is supplied."""


@dataclass(frozen=True)
class MigrationResult:
    contract: Dict[str, Any]
    migrated_from: str
    warnings: List[str]


def detect_payload_version(payload: Mapping[str, Any]) -> str:
    schema_version = clean_text(payload.get("schema_version"))
    if schema_version:
        return schema_version
    if "inputs" in payload and "canvas" in payload:
        return f"legacy-wrapper/{clean_text(payload.get('version'), 'unknown')}"
    if "version" in payload and "generated_at" in payload and "persona" in payload:
        return f"legacy-core/{clean_text(payload.get('version'), 'unknown')}"
    flask_keys = {"challenge", "audience", "goal", "constraint"}
    if flask_keys.issubset(payload.keys()):
        return "legacy-flask/1.x"
    return "unknown"


def _legacy_wrapper_input(payload: Mapping[str, Any]) -> Dict[str, Any]:
    inputs = payload.get("inputs") if isinstance(payload.get("inputs"), Mapping) else {}
    canvas = payload.get("canvas") if isinstance(payload.get("canvas"), Mapping) else {}
    return {
        **dict(inputs),
        "title": clean_text(canvas.get("title"), "Catalyst Canvas Brief"),
        "point_of_view": canvas.get("pov"),
        "how_might_we": canvas.get("hmw"),
        "persona": {
            "name": canvas.get("persona_name"),
            "description": canvas.get("persona_body"),
            "source_type": "assumption",
            "confidence": "low",
        },
        "prototype": {
            "title": canvas.get("prototype_title"),
            "description": canvas.get("prototype_body"),
        },
        "test_plan": {
            "title": "Legacy learning test",
            "signal": (canvas.get("test_plan") or {}).get("signal_to_watch", "") if isinstance(canvas.get("test_plan"), Mapping) else "",
            "method": (canvas.get("test_plan") or {}).get("next_iteration", "") if isinstance(canvas.get("test_plan"), Mapping) else "",
            "learning_goal": (canvas.get("test_plan") or {}).get("what_to_test", "") if isinstance(canvas.get("test_plan"), Mapping) else "",
        },
        "review_notes": [
            {"type": "risk", "note": (canvas.get("test_plan") or {}).get("risk", "Review migrated claims before use.") if isinstance(canvas.get("test_plan"), Mapping) else "Review migrated claims before use."}
        ],
        "created_at": payload.get("generated_at"),
    }


def _legacy_core_input(payload: Mapping[str, Any]) -> Dict[str, Any]:
    persona = payload.get("persona") if isinstance(payload.get("persona"), Mapping) else {}
    prototype = payload.get("prototype") if isinstance(payload.get("prototype"), Mapping) else {}
    test_plan = payload.get("test_plan") if isinstance(payload.get("test_plan"), Mapping) else {}
    return {
        "title": payload.get("title", "Catalyst Canvas Brief"),
        "challenge": payload.get("challenge"),
        "audience": payload.get("audience"),
        "goal": payload.get("goal"),
        "constraint": payload.get("constraint"),
        "framework": payload.get("framework"),
        "persona": {
            "name": persona.get("name"),
            "description": persona.get("description"),
            "source_type": "assumption",
            "confidence": "low",
        },
        "point_of_view": payload.get("point_of_view"),
        "how_might_we": payload.get("how_might_we"),
        "prototype": prototype,
        "test_plan": test_plan,
        "assumptions": payload.get("assumptions"),
        "review_notes": [
            {"type": "review_question", "note": item}
            for item in (payload.get("review_questions") or [])
        ],
        "created_at": payload.get("generated_at"),
    }


def _legacy_flask_input(payload: Mapping[str, Any]) -> Dict[str, Any]:
    review_notes: List[Dict[str, str]] = []
    if clean_text(payload.get("risk_note")):
        review_notes.append({"type": "risk", "note": payload.get("risk_note")})
    if clean_text(payload.get("review_note")):
        review_notes.append({"type": "note", "note": payload.get("review_note")})
    return {
        "canvas_id": payload.get("canvas_id"),
        "revision_id": payload.get("revision_id"),
        "title": payload.get("title"),
        "status": payload.get("status", "draft"),
        "created_at": payload.get("created_at"),
        "updated_at": payload.get("updated_at"),
        "challenge": payload.get("challenge"),
        "audience": payload.get("audience"),
        "goal": payload.get("goal"),
        "constraint": payload.get("constraint"),
        "framework": payload.get("framework", "AIDA"),
        "persona": {
            "name": payload.get("persona_name"),
            "role": payload.get("persona_role"),
            "description": "",
            "needs": [payload.get("persona_needs")] if clean_text(payload.get("persona_needs")) else [],
            "pains": [payload.get("persona_pains")] if clean_text(payload.get("persona_pains")) else [],
            "source_type": "assumption",
            "confidence": "low",
        },
        "point_of_view": payload.get("point_of_view"),
        "how_might_we": payload.get("how_might_we"),
        "evidence": payload.get("evidence"),
        "assumption": payload.get("assumption"),
        "prototype": payload.get("prototype"),
        "test_plan": {
            "title": "Learning test",
            "signal": payload.get("success_signal", ""),
            "method": payload.get("test_plan", ""),
            "learning_goal": "Learn whether the proposed framing and prototype are useful enough to continue.",
        },
        "review_notes": review_notes,
    }


def migrate_payload(payload: Mapping[str, Any], *, source_surface: str = "migration") -> MigrationResult:
    """Return a validated current contract or a useful incompatibility error."""
    detected = detect_payload_version(payload)
    if detected == CONTRACT_VERSION:
        return MigrationResult(validate_contract(payload), "", [])
    if detected in {"catalyst-canvas/1.0", "catalyst-canvas/1.1", "catalyst-canvas/1.2", "catalyst-canvas/1.3"}:
        compact = dict(payload)
        warning = f"Migrated {detected} to {CONTRACT_VERSION}; research, ideation, and prioritization fields were normalized and should be reviewed."
        compact["schema_version"] = CONTRACT_VERSION
        compact["provenance"] = {
            **(dict(payload.get("provenance")) if isinstance(payload.get("provenance"), Mapping) else {}),
            "source_surface": source_surface,
            "source_version": detected,
            "migrated_from": detected,
            "warnings": [warning],
        }
        contract = build_contract(compact, source_surface=source_surface)
        return MigrationResult(contract, detected, [warning])
    if detected.startswith("catalyst-canvas/"):
        raise UnsupportedContractVersion(
            f"Unsupported Canvas contract {detected!r}. This release accepts {CONTRACT_VERSION!r} and migrates 'catalyst-canvas/1.0', 'catalyst-canvas/1.1', 'catalyst-canvas/1.2', and 'catalyst-canvas/1.3'. "
            "Export through a compatible Catalyst Canvas release before importing."
        )

    if detected.startswith("legacy-wrapper/"):
        compact = _legacy_wrapper_input(payload)
    elif detected.startswith("legacy-core/"):
        compact = _legacy_core_input(payload)
    elif detected == "legacy-flask/1.x":
        compact = _legacy_flask_input(payload)
    else:
        raise UnsupportedContractVersion(
            "Unable to identify this Canvas payload. Expected Canvas Contract 1.4, Canvas Contract 1.3, Canvas Contract 1.2, Canvas Contract 1.1, Canvas Contract 1.0, or a v1.0/v1.1 "
            "Python, Flask, or WordPress export containing challenge, audience, goal, and constraint fields."
        )

    warning = f"Migrated {detected} to {CONTRACT_VERSION}; review assumptions, evidence, and generated identifiers."
    compact["provenance"] = {
        "source_surface": source_surface,
        "source_version": detected,
        "migrated_from": detected,
        "warnings": [warning],
    }
    contract = build_contract(compact, source_surface=source_surface)
    return MigrationResult(contract, detected, [warning])
