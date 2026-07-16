"""Connected platform exchange, interoperability, and readiness helpers.

Catalyst Canvas v2.0.0 records integrations as explicit contracts. It does not
claim a remote system is available merely because a connection record exists.
Exchange packages are deterministic, checksum-protected, and can be signed with
HMAC-SHA256 when a caller supplies an institutional signing key.
"""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import hmac
import json
from typing import Any, Dict, Iterable, List, Mapping, Sequence

EXCHANGE_CONTRACT = "catalyst-canvas-exchange/2.0"
EVENT_CONTRACT = "catalyst-canvas-event/1.0"
CAPABILITY_CONTRACT = "catalyst-canvas-capabilities/1.0"
PLATFORM_PRODUCTS = (
    "knowledge_library",
    "research_librarian",
    "site_intelligence",
    "workbench",
    "decision_studio",
    "research_lab",
    "feature_support",
    "contact_engagement",
    "wordpress",
    "public_api",
)


def _text(value: Any, fallback: str = "") -> str:
    text = str(value or "").strip()
    return text if text else fallback


def _list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.replace(";", "\n").splitlines() if item.strip()]
    if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray, Mapping)):
        return [_text(item) for item in value if _text(item)]
    return [_text(value)] if _text(value) else []


def _records(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, Mapping):
        return [value]
    return []


def _choice(value: Any, allowed: Sequence[str], fallback: str) -> str:
    selected = _text(value, fallback).lower()
    return selected if selected in allowed else fallback


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def normalize_platform_connections(value: Any, *, generated_at: str) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(_records(value), start=1):
        source = item if isinstance(item, Mapping) else {"product": item}
        product = _choice(source.get("product"), PLATFORM_PRODUCTS, "public_api")
        connection_id = _text(source.get("connection_id"), f"connection-{index:03d}")
        if connection_id in seen:
            continue
        seen.add(connection_id)
        records.append({
            "connection_id": connection_id,
            "product": product,
            "display_name": _text(source.get("display_name"), product.replace("_", " ").title()),
            "direction": _choice(source.get("direction"), ("inbound", "outbound", "bidirectional"), "outbound"),
            "status": _choice(source.get("status"), ("planned", "configured", "verified", "degraded", "disabled"), "planned"),
            "endpoint": _text(source.get("endpoint")),
            "auth_mode": _choice(source.get("auth_mode"), ("none", "api_key", "hmac", "oauth2", "service_account", "session"), "none"),
            "capabilities": _list(source.get("capabilities")),
            "data_classes": _list(source.get("data_classes")),
            "accepted_contracts": _list(source.get("accepted_contracts")),
            "retention_policy": _text(source.get("retention_policy")),
            "owner": _text(source.get("owner")),
            "last_verified_at": _text(source.get("last_verified_at")),
            "verification_note": _text(source.get("verification_note")),
            "created_at": _text(source.get("created_at"), generated_at),
            "updated_at": _text(source.get("updated_at"), generated_at),
        })
    return records


def normalize_interoperability_profiles(value: Any, *, generated_at: str) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(_records(value), start=1):
        source = item if isinstance(item, Mapping) else {"name": item}
        records.append({
            "profile_id": _text(source.get("profile_id"), f"profile-{index:03d}"),
            "name": _text(source.get("name"), f"Interoperability profile {index}"),
            "version": _text(source.get("version"), "1.0"),
            "status": _choice(source.get("status"), ("draft", "active", "deprecated"), "draft"),
            "supported_contracts": _list(source.get("supported_contracts")),
            "export_formats": _list(source.get("export_formats")) or ["json"],
            "identity_modes": _list(source.get("identity_modes")) or ["stable_ids"],
            "event_types": _list(source.get("event_types")),
            "required_fields": _list(source.get("required_fields")),
            "redaction_rules": _list(source.get("redaction_rules")),
            "retention_policy": _text(source.get("retention_policy")),
            "notes": _text(source.get("notes")),
            "created_at": _text(source.get("created_at"), generated_at),
            "updated_at": _text(source.get("updated_at"), generated_at),
        })
    return records


def normalize_workflow_links(value: Any, *, generated_at: str) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(_records(value), start=1):
        source = item if isinstance(item, Mapping) else {"relation": item}
        records.append({
            "link_id": _text(source.get("link_id"), f"workflow-link-{index:03d}"),
            "from_product": _choice(source.get("from_product"), PLATFORM_PRODUCTS, "public_api"),
            "from_record_id": _text(source.get("from_record_id")),
            "to_product": _choice(source.get("to_product"), PLATFORM_PRODUCTS, "public_api"),
            "to_record_id": _text(source.get("to_record_id")),
            "relation": _choice(source.get("relation"), ("derived_from", "references", "validates", "implements", "publishes", "supersedes", "requests", "responds_to"), "references"),
            "status": _choice(source.get("status"), ("planned", "active", "complete", "broken", "archived"), "planned"),
            "correlation_id": _text(source.get("correlation_id")),
            "notes": _text(source.get("notes")),
            "created_at": _text(source.get("created_at"), generated_at),
            "updated_at": _text(source.get("updated_at"), generated_at),
        })
    return records


def normalize_platform_events(value: Any, *, generated_at: str) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(_records(value), start=1):
        source = item if isinstance(item, Mapping) else {"event_type": item}
        metadata = source.get("metadata") if isinstance(source.get("metadata"), Mapping) else {}
        payload_checksum = _text(source.get("payload_checksum"))
        if not payload_checksum and metadata:
            payload_checksum = sha256(_canonical_json(metadata).encode("utf-8")).hexdigest()
        records.append({
            "event_contract": EVENT_CONTRACT,
            "event_id": _text(source.get("event_id"), f"platform-event-{index:03d}"),
            "event_type": _text(source.get("event_type"), "canvas.updated"),
            "producer": _choice(source.get("producer"), ("catalyst_canvas",) + PLATFORM_PRODUCTS, "catalyst_canvas"),
            "subject_id": _text(source.get("subject_id")),
            "correlation_id": _text(source.get("correlation_id")),
            "occurred_at": _text(source.get("occurred_at"), generated_at),
            "payload_checksum": payload_checksum,
            "metadata": dict(metadata),
        })
    return records


def normalize_exchange_records(value: Any, *, generated_at: str) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(_records(value), start=1):
        source = item if isinstance(item, Mapping) else {"target_product": item}
        records.append({
            "exchange_id": _text(source.get("exchange_id"), f"exchange-{index:03d}"),
            "exchange_contract": EXCHANGE_CONTRACT,
            "target_product": _choice(source.get("target_product"), PLATFORM_PRODUCTS, "public_api"),
            "payload_type": _choice(source.get("payload_type"), ("full_canvas", "research", "decision", "experiment", "publication", "support", "engagement", "event"), "full_canvas"),
            "status": _choice(source.get("status"), ("draft", "ready", "sent", "accepted", "rejected", "expired"), "draft"),
            "source_revision_id": _text(source.get("source_revision_id")),
            "related_record_ids": _list(source.get("related_record_ids")),
            "profile_id": _text(source.get("profile_id")),
            "checksum": _text(source.get("checksum")),
            "signature_algorithm": _choice(source.get("signature_algorithm"), ("none", "hmac-sha256"), "none"),
            "signature": _text(source.get("signature")),
            "created_by": _text(source.get("created_by")),
            "created_at": _text(source.get("created_at"), generated_at),
            "expires_at": _text(source.get("expires_at")),
            "acknowledged_at": _text(source.get("acknowledged_at")),
            "notes": _text(source.get("notes")),
        })
    return records


def platform_summary(
    connections: Sequence[Mapping[str, Any]],
    profiles: Sequence[Mapping[str, Any]],
    links: Sequence[Mapping[str, Any]],
    exchanges: Sequence[Mapping[str, Any]],
    events: Sequence[Mapping[str, Any]],
    *,
    subsystem_readiness: Mapping[str, str],
    generated_at: str,
) -> Dict[str, Any]:
    verified = sum(item.get("status") == "verified" for item in connections)
    degraded = sum(item.get("status") == "degraded" for item in connections)
    broken_links = sum(item.get("status") == "broken" for item in links)
    rejected = sum(item.get("status") == "rejected" for item in exchanges)
    unsigned_ready = sum(item.get("status") == "ready" and not item.get("signature") for item in exchanges)
    blocking_states = {"blocked", "needs_evidence", "needs_review", "not_ready"}
    blocked_subsystems = sorted(name for name, status in subsystem_readiness.items() if status in blocking_states)
    if degraded or broken_links or rejected:
        readiness = "degraded"
    elif blocked_subsystems:
        readiness = "connected_but_not_ready"
    elif connections and verified == len(connections) and not unsigned_ready:
        readiness = "connected"
    elif connections:
        readiness = "configuration_incomplete"
    else:
        readiness = "platform_draft"
    return {
        "connection_count": len(connections),
        "verified_connection_count": verified,
        "degraded_connection_count": degraded,
        "profile_count": len(profiles),
        "workflow_link_count": len(links),
        "broken_link_count": broken_links,
        "exchange_count": len(exchanges),
        "ready_exchange_count": sum(item.get("status") == "ready" for item in exchanges),
        "rejected_exchange_count": rejected,
        "unsigned_ready_exchange_count": unsigned_ready,
        "event_count": len(events),
        "blocked_subsystems": blocked_subsystems,
        "subsystem_readiness": dict(subsystem_readiness),
        "readiness": readiness,
        "indicator_note": (
            "Platform readiness describes recorded contracts, connection verification, workflow links, exchange status, "
            "and subsystem workflow states. It does not prove remote availability, authorization, security, delivery, "
            "legal interoperability, or institutional acceptance."
        ),
        "generated_at": generated_at,
    }


def capability_manifest(contract: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "capability_contract": CAPABILITY_CONTRACT,
        "product": "catalyst_canvas",
        "release_version": contract.get("provenance", {}).get("generator_version", ""),
        "canvas_contract": contract.get("schema_version"),
        "exchange_contract": EXCHANGE_CONTRACT,
        "event_contract": EVENT_CONTRACT,
        "capabilities": [
            "problem_framing", "research_ledger", "persona_stakeholder_journey", "ideation",
            "prioritization", "prototype_experiments", "collaboration_review", "public_safe_publication",
            "signed_exchange", "workflow_links", "event_envelopes", "immutable_revisions",
        ],
        "supported_targets": list(PLATFORM_PRODUCTS),
        "supported_payload_types": ["full_canvas", "research", "decision", "experiment", "publication", "support", "engagement", "event"],
        "integrity_modes": ["sha256", "hmac-sha256"],
        "api_routes": [
            "GET /api/platform",
            "GET /api/capabilities",
            "GET /projects/<project_id>/exchange/<target>.json",
            "POST /api/exchange/verify",
        ],
        "generated_at": contract.get("updated_at"),
    }


def _payload_for_type(contract: Mapping[str, Any], payload_type: str) -> Dict[str, Any]:
    common = {
        "schema_version": contract.get("schema_version"),
        "canvas_id": contract.get("canvas_id"),
        "revision_id": contract.get("revision_id"),
        "title": contract.get("title"),
        "challenge": contract.get("challenge"),
        "goal": contract.get("goal"),
        "provenance": deepcopy(contract.get("provenance", {})),
    }
    sections = {
        "research": ("audience", "personas", "stakeholders", "journeys", "sources", "evidence", "claims", "assumptions", "research_questions", "ledger_summary"),
        "decision": ("decision_criteria", "decision_options", "sensitivity_views", "decision_notes", "prioritization_summary"),
        "experiment": ("prototypes", "hypotheses", "experiment_plans", "experiment_runs", "learning_decisions", "iteration_history", "experiment_summary"),
        "publication": ("publication_records", "release_history", "collaboration_summary"),
        "support": ("review_notes", "comments", "claims", "assumptions", "publication_records"),
        "engagement": ("owner_context", "workspace_members", "decision_options", "publication_records"),
        "event": ("platform_events",),
    }
    if payload_type == "full_canvas":
        return deepcopy(dict(contract))
    payload = dict(common)
    for key in sections.get(payload_type, ()):  # pragma: no branch - normalized earlier
        payload[key] = deepcopy(contract.get(key))
    return payload


def build_exchange_package(
    contract: Mapping[str, Any],
    target_product: str,
    *,
    payload_type: str = "full_canvas",
    profile_id: str = "",
    related_record_ids: Sequence[str] | None = None,
    signing_key: str | bytes | None = None,
    created_by: str = "",
) -> Dict[str, Any]:
    target = _choice(target_product, PLATFORM_PRODUCTS, "public_api")
    payload_type = _choice(payload_type, ("full_canvas", "research", "decision", "experiment", "publication", "support", "engagement", "event"), "full_canvas")
    payload = _payload_for_type(contract, payload_type)
    payload_checksum = sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    source = {
        "product": "catalyst_canvas",
        "canvas_id": contract.get("canvas_id"),
        "revision_id": contract.get("revision_id"),
        "contract": contract.get("schema_version"),
    }
    unsigned = {
        "exchange_contract": EXCHANGE_CONTRACT,
        "exchange_id": f"exchange-{target}-{str(contract.get('revision_id') or 'revision')}",
        "source": source,
        "target": {"product": target, "profile_id": _text(profile_id)},
        "payload_type": payload_type,
        "related_record_ids": list(related_record_ids or []),
        "payload": payload,
        "integrity": {"algorithm": "sha256", "payload_checksum": payload_checksum},
        "created_by": _text(created_by),
        "created_at": contract.get("updated_at"),
        "boundary": (
            "This package proves only deterministic serialization and optional HMAC possession. The receiving system "
            "must independently authorize the sender, validate the contract, enforce retention and redaction rules, "
            "and acknowledge acceptance."
        ),
    }
    signature = ""
    algorithm = "none"
    if signing_key:
        key = signing_key.encode("utf-8") if isinstance(signing_key, str) else signing_key
        signature = hmac.new(key, _canonical_json(unsigned).encode("utf-8"), "sha256").hexdigest()
        algorithm = "hmac-sha256"
    unsigned["integrity"]["signature_algorithm"] = algorithm
    unsigned["integrity"]["signature"] = signature
    return unsigned


def verify_exchange_package(package: Mapping[str, Any], signing_key: str | bytes | None = None) -> Dict[str, Any]:
    payload = package.get("payload")
    integrity = package.get("integrity") if isinstance(package.get("integrity"), Mapping) else {}
    expected_checksum = _text(integrity.get("payload_checksum"))
    actual_checksum = sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    checksum_valid = bool(expected_checksum) and hmac.compare_digest(expected_checksum, actual_checksum)
    algorithm = _text(integrity.get("signature_algorithm"), "none")
    signature_valid: bool | None = None
    if algorithm == "hmac-sha256":
        if signing_key is None:
            signature_valid = None
        else:
            key = signing_key.encode("utf-8") if isinstance(signing_key, str) else signing_key
            unsigned = deepcopy(dict(package))
            unsigned_integrity = dict(unsigned.get("integrity") or {})
            signature = _text(unsigned_integrity.pop("signature", ""))
            unsigned_integrity.pop("signature_algorithm", None)
            unsigned["integrity"] = unsigned_integrity
            expected_signature = hmac.new(key, _canonical_json(unsigned).encode("utf-8"), "sha256").hexdigest()
            signature_valid = bool(signature) and hmac.compare_digest(signature, expected_signature)
    elif algorithm == "none":
        signature_valid = True
    return {
        "exchange_contract_valid": package.get("exchange_contract") == EXCHANGE_CONTRACT,
        "checksum_valid": checksum_valid,
        "signature_algorithm": algorithm,
        "signature_valid": signature_valid,
        "valid": package.get("exchange_contract") == EXCHANGE_CONTRACT and checksum_valid and signature_valid is not False,
    }
