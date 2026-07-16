"""Collaboration, review, approval, and publication records for Catalyst Canvas.

Canvas Contract 2.0 retains collaboration metadata inside each immutable revision
while the Flask storage layer indexes the same records for workspace views.
Publication helpers deliberately create a reduced public-safe package instead of
publishing the complete working contract.
"""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from typing import Any, Dict, Iterable, List, Mapping, Sequence

ROLE_CAPABILITIES: Dict[str, List[str]] = {
    "owner": ["view", "comment", "edit", "assign_review", "approve", "publish", "manage_members"],
    "editor": ["view", "comment", "edit", "assign_review", "approve", "publish"],
    "contributor": ["view", "comment", "edit"],
    "reviewer": ["view", "comment", "approve"],
    "viewer": ["view"],
}

PUBLICATION_CONTRACT = "catalyst-canvas-publication/1.0"
PUBLIC_SAFE_CONTRACT = "catalyst-canvas-public-safe/1.0"


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


def _choice(value: Any, allowed: Sequence[str], fallback: str) -> str:
    selected = _text(value, fallback).lower()
    return selected if selected in allowed else fallback


def _records(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, Mapping):
        return [value]
    return []


def normalize_workspace_members(value: Any, *, owner_context: Mapping[str, Any], generated_at: str) -> List[Dict[str, Any]]:
    raw = _records(value)
    if not raw:
        raw = [{
            "member_id": _text(owner_context.get("owner_id"), "local-user"),
            "name": _text(owner_context.get("name"), "Workspace owner"),
            "organization": _text(owner_context.get("organization")),
            "role": "owner",
            "status": "active",
        }]
    records: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"name": item}
        member_id = _text(source.get("member_id"), f"member-{index:03d}")
        if member_id in seen:
            continue
        seen.add(member_id)
        role = _choice(source.get("role"), tuple(ROLE_CAPABILITIES), "viewer")
        records.append({
            "member_id": member_id,
            "name": _text(source.get("name"), f"Workspace member {index}"),
            "organization": _text(source.get("organization")),
            "role": role,
            "status": _choice(source.get("status"), ("invited", "active", "suspended", "removed"), "active"),
            "capabilities": list(ROLE_CAPABILITIES[role]),
            "joined_at": _text(source.get("joined_at"), generated_at),
            "last_active_at": _text(source.get("last_active_at")),
        })
    if not any(item["role"] == "owner" and item["status"] == "active" for item in records):
        records.insert(0, {
            "member_id": _text(owner_context.get("owner_id"), "local-user"),
            "name": _text(owner_context.get("name"), "Workspace owner"),
            "organization": _text(owner_context.get("organization")),
            "role": "owner",
            "status": "active",
            "capabilities": list(ROLE_CAPABILITIES["owner"]),
            "joined_at": generated_at,
            "last_active_at": "",
        })
    return records


def normalize_review_assignments(value: Any, *, generated_at: str) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(_records(value), start=1):
        source = item if isinstance(item, Mapping) else {"title": item}
        records.append({
            "assignment_id": _text(source.get("assignment_id"), f"review-assignment-{index:03d}"),
            "title": _text(source.get("title"), f"Review assignment {index}"),
            "review_type": _choice(source.get("review_type"), ("content", "evidence", "ethics", "accessibility", "legal", "security", "publication", "other"), "content"),
            "status": _choice(source.get("status"), ("draft", "assigned", "in_progress", "complete", "cancelled"), "assigned"),
            "required": bool(source.get("required", True)),
            "requested_by": _text(source.get("requested_by")),
            "assignee_ids": _list(source.get("assignee_ids")),
            "scope": _text(source.get("scope"), "Entire Canvas revision"),
            "target_ids": _list(source.get("target_ids")),
            "instructions": _text(source.get("instructions")),
            "due_at": _text(source.get("due_at")),
            "created_at": _text(source.get("created_at"), generated_at),
            "completed_at": _text(source.get("completed_at")),
        })
    return records


def normalize_comments(value: Any, *, generated_at: str) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(_records(value), start=1):
        source = item if isinstance(item, Mapping) else {"body": item}
        body = _text(source.get("body"))
        if not body:
            continue
        comment_id = _text(source.get("comment_id"), f"comment-{index:03d}")
        records.append({
            "comment_id": comment_id,
            "thread_id": _text(source.get("thread_id"), comment_id),
            "parent_comment_id": _text(source.get("parent_comment_id")),
            "target_type": _choice(source.get("target_type"), ("canvas", "section", "claim", "assumption", "idea", "decision_option", "prototype", "experiment", "publication", "other"), "canvas"),
            "target_id": _text(source.get("target_id")),
            "section_path": _text(source.get("section_path")),
            "author_id": _text(source.get("author_id"), "anonymous"),
            "body": body,
            "visibility": _choice(source.get("visibility"), ("internal", "reviewers", "public"), "internal"),
            "status": _choice(source.get("status"), ("open", "resolved", "dismissed"), "open"),
            "mentions": _list(source.get("mentions")),
            "tags": _list(source.get("tags")),
            "created_at": _text(source.get("created_at"), generated_at),
            "updated_at": _text(source.get("updated_at"), generated_at),
            "resolved_by": _text(source.get("resolved_by")),
            "resolved_at": _text(source.get("resolved_at")),
        })
    return records


def normalize_approvals(value: Any, *, generated_at: str) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(_records(value), start=1):
        source = item if isinstance(item, Mapping) else {"rationale": item}
        records.append({
            "approval_id": _text(source.get("approval_id"), f"approval-{index:03d}"),
            "stage": _choice(source.get("stage"), ("research", "evidence", "decision", "experiment", "publication", "release"), "publication"),
            "reviewer_id": _text(source.get("reviewer_id")),
            "decision": _choice(source.get("decision"), ("pending", "approved", "changes_requested", "rejected", "abstained"), "pending"),
            "scope": _text(source.get("scope"), "Current Canvas revision"),
            "target_ids": _list(source.get("target_ids")),
            "rationale": _text(source.get("rationale")),
            "conditions": _list(source.get("conditions")),
            "created_at": _text(source.get("created_at"), generated_at),
            "decided_at": _text(source.get("decided_at")),
            "expires_at": _text(source.get("expires_at")),
        })
    return records


def normalize_publication_records(value: Any, *, revision_id: str, title: str, generated_at: str) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(_records(value), start=1):
        source = item if isinstance(item, Mapping) else {"title": item}
        state = _choice(source.get("state"), ("draft", "in_review", "approved", "scheduled", "published", "withdrawn", "archived"), "draft")
        records.append({
            "publication_id": _text(source.get("publication_id"), f"publication-{index:03d}"),
            "title": _text(source.get("title"), title),
            "publication_type": _choice(source.get("publication_type"), ("public_brief", "internal_report", "knowledge_document", "decision_brief", "web_page", "data_package"), "public_brief"),
            "channel": _choice(source.get("channel"), ("wordpress", "knowledge_library", "public_api", "download", "internal"), "download"),
            "audience": _text(source.get("audience"), "Public readers"),
            "state": state,
            "version": _text(source.get("version"), "1.0"),
            "slug": _text(source.get("slug")),
            "owner_id": _text(source.get("owner_id")),
            "source_revision_id": _text(source.get("source_revision_id"), revision_id),
            "selected_sections": _list(source.get("selected_sections")) or [
                "challenge", "audience", "goal", "constraints", "personas", "point_of_view",
                "how_might_we", "ideas", "decision_options", "prototypes", "claims", "sources",
            ],
            "redaction_notes": _list(source.get("redaction_notes")),
            "release_notes": _text(source.get("release_notes")),
            "review_assignment_ids": _list(source.get("review_assignment_ids")),
            "approval_ids": _list(source.get("approval_ids")),
            "url": _text(source.get("url")),
            "scheduled_at": _text(source.get("scheduled_at")),
            "published_at": _text(source.get("published_at")),
            "withdrawn_at": _text(source.get("withdrawn_at")),
            "created_at": _text(source.get("created_at"), generated_at),
            "updated_at": _text(source.get("updated_at"), generated_at),
        })
    return records


def normalize_release_history(value: Any, *, generated_at: str) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(_records(value), start=1):
        source = item if isinstance(item, Mapping) else {"summary": item}
        records.append({
            "release_id": _text(source.get("release_id"), f"publication-release-{index:03d}"),
            "publication_id": _text(source.get("publication_id")),
            "version": _text(source.get("version"), "1.0"),
            "state": _choice(source.get("state"), ("published", "withdrawn", "superseded", "archived"), "published"),
            "source_revision_id": _text(source.get("source_revision_id")),
            "summary": _text(source.get("summary")),
            "published_by": _text(source.get("published_by")),
            "published_at": _text(source.get("published_at"), generated_at),
            "url": _text(source.get("url")),
            "checksum": _text(source.get("checksum")),
        })
    return records


def normalize_publication_handoffs(value: Any, *, generated_at: str) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(_records(value), start=1):
        source = item if isinstance(item, Mapping) else {"purpose": item}
        records.append({
            "handoff_id": _text(source.get("handoff_id"), f"publication-handoff-{index:03d}"),
            "target": _choice(source.get("target"), ("wordpress", "knowledge_library", "public_api"), "wordpress"),
            "status": _choice(source.get("status"), ("draft", "ready", "sent", "accepted", "rejected"), "draft"),
            "publication_ids": _list(source.get("publication_ids")),
            "purpose": _text(source.get("purpose")),
            "instructions": _list(source.get("instructions")),
            "created_by": _text(source.get("created_by")),
            "created_at": _text(source.get("created_at"), generated_at),
        })
    return records


def collaboration_summary(
    members: Sequence[Mapping[str, Any]],
    assignments: Sequence[Mapping[str, Any]],
    comments: Sequence[Mapping[str, Any]],
    approvals: Sequence[Mapping[str, Any]],
    publications: Sequence[Mapping[str, Any]],
    release_history: Sequence[Mapping[str, Any]],
    *,
    generated_at: str,
) -> Dict[str, Any]:
    open_comments = sum(item.get("status") == "open" for item in comments)
    required_reviews = sum(bool(item.get("required")) and item.get("status") != "complete" for item in assignments)
    pending_approvals = sum(item.get("decision") == "pending" for item in approvals)
    changes_requested = sum(item.get("decision") == "changes_requested" for item in approvals)
    rejected = sum(item.get("decision") == "rejected" for item in approvals)
    approved = sum(item.get("decision") == "approved" for item in approvals)
    published = sum(item.get("state") == "published" for item in publications)
    approved_publications = sum(item.get("state") in {"approved", "scheduled", "published"} for item in publications)
    redaction_reviews = sum(not item.get("redaction_notes") for item in publications if item.get("publication_type") != "internal_report")
    if published:
        readiness = "published"
    elif rejected or changes_requested:
        readiness = "blocked"
    elif required_reviews or pending_approvals:
        readiness = "in_review"
    elif approved_publications and not redaction_reviews:
        readiness = "ready_for_publication"
    elif publications:
        readiness = "publication_draft"
    else:
        readiness = "collaboration_draft"
    return {
        "member_count": len(members),
        "active_member_count": sum(item.get("status") == "active" for item in members),
        "review_assignment_count": len(assignments),
        "required_review_open_count": required_reviews,
        "comment_count": len(comments),
        "open_comment_count": open_comments,
        "approval_count": len(approvals),
        "approved_count": approved,
        "pending_approval_count": pending_approvals,
        "changes_requested_count": changes_requested,
        "rejected_count": rejected,
        "publication_count": len(publications),
        "approved_publication_count": approved_publications,
        "published_count": published,
        "release_count": len(release_history),
        "redaction_review_open_count": redaction_reviews,
        "readiness": readiness,
        "indicator_note": (
            "Collaboration readiness describes recorded assignments, comments, approvals, redaction notes, "
            "and publication state. It does not establish legal clearance, factual accuracy, accessibility, "
            "security, ethical acceptability, or institutional authorization."
        ),
        "generated_at": generated_at,
    }


def member_can(member: Mapping[str, Any] | None, capability: str) -> bool:
    if not member or member.get("status") != "active":
        return False
    return capability in set(member.get("capabilities") or ROLE_CAPABILITIES.get(str(member.get("role")), []))


def _public_persona(item: Mapping[str, Any]) -> Dict[str, Any]:
    allowed = ("persona_id", "name", "role", "description", "context", "jobs", "goals", "needs", "pains", "gains", "behaviors", "barriers", "motivations", "accessibility_needs", "preferred_channels", "empathy_map", "validation_status")
    return {key: deepcopy(item.get(key)) for key in allowed if key in item}


def _public_stakeholder(item: Mapping[str, Any]) -> Dict[str, Any]:
    allowed = ("stakeholder_id", "name", "stakeholder_type", "relationship", "impact", "stance", "decision_role", "engagement_strategy", "responsibilities")
    return {key: deepcopy(item.get(key)) for key in allowed if key in item}


def public_safe_content(contract: Mapping[str, Any], publication: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    selected = set((publication or {}).get("selected_sections") or [])
    if not selected:
        selected = {"challenge", "audience", "goal", "constraints", "personas", "point_of_view", "how_might_we", "ideas", "decision_options", "prototypes", "claims", "sources"}
    content: Dict[str, Any] = {}
    simple_sections = ("challenge", "audience", "goal", "constraints", "point_of_view", "how_might_we", "research_summary", "ideation_summary", "prioritization_summary", "experiment_summary")
    for section in simple_sections:
        if section in selected and section in contract:
            content[section] = deepcopy(contract[section])
    if "personas" in selected:
        content["personas"] = [_public_persona(item) for item in contract.get("personas", [])]
    if "stakeholders" in selected:
        content["stakeholders"] = [_public_stakeholder(item) for item in contract.get("stakeholders", [])]
    for section in ("journeys", "ideas", "decision_options", "prototypes", "hypotheses", "claims"):
        if section in selected:
            content[section] = deepcopy(contract.get(section, []))
    if "sources" in selected:
        content["sources"] = [
            {key: deepcopy(item.get(key)) for key in ("source_id", "source_type", "title", "creator", "publisher", "source_date", "url", "description", "rights", "limitations")}
            for item in contract.get("sources", [])
        ]
    if "evidence" in selected:
        content["evidence"] = [
            {key: deepcopy(item.get(key)) for key in ("evidence_id", "source_id", "evidence_type", "title", "summary", "quote", "locator", "citation", "url", "confidence", "limitations")}
            for item in contract.get("evidence", [])
        ]
    return content


def build_publication_package(contract: Mapping[str, Any], target: str = "public_api", publication_id: str = "") -> Dict[str, Any]:
    target = _choice(target, ("wordpress", "knowledge_library", "public_api", "download"), "public_api")
    publications = list(contract.get("publication_records", []))
    publication = next((item for item in publications if item.get("publication_id") == publication_id), None) if publication_id else None
    if publication is None:
        publication = publications[0] if publications else {
            "publication_id": "publication-preview",
            "title": contract.get("title", "Catalyst Canvas publication"),
            "publication_type": "public_brief",
            "channel": target,
            "audience": "Public readers",
            "state": "draft",
            "version": "preview",
            "selected_sections": [],
            "redaction_notes": ["Preview generated without an approved publication record."],
            "release_notes": "",
            "url": "",
        }
    content = public_safe_content(contract, publication)
    canonical = json.dumps(content, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return {
        "publication_contract": PUBLIC_SAFE_CONTRACT,
        "target": target,
        "source": {
            "schema_version": contract.get("schema_version"),
            "canvas_id": contract.get("canvas_id"),
            "revision_id": contract.get("revision_id"),
            "publication_id": publication.get("publication_id"),
        },
        "publication": {
            key: deepcopy(publication.get(key))
            for key in ("publication_id", "title", "publication_type", "channel", "audience", "state", "version", "slug", "release_notes", "redaction_notes", "url", "published_at")
        },
        "content": content,
        "integrity": {
            "algorithm": "sha256",
            "content_checksum": sha256(canonical.encode("utf-8")).hexdigest(),
            "source_revision_id": contract.get("revision_id"),
        },
        "provenance": deepcopy(contract.get("provenance", {})),
        "generated_at": contract.get("updated_at"),
        "boundary": (
            "This package omits workspace members, internal comments, review assignments, approvals, participant details, "
            "private notes, and other working records. Human review is still required before publication."
        ),
    }


def publication_release_record(contract: Mapping[str, Any], publication_id: str, *, published_by: str, generated_at: str, url: str = "") -> Dict[str, Any]:
    package = build_publication_package(contract, publication_id=publication_id)
    publication = package["publication"]
    return {
        "release_id": f"release-{publication_id}-{_text(publication.get('version'), '1.0')}",
        "publication_id": publication_id,
        "version": _text(publication.get("version"), "1.0"),
        "state": "published",
        "source_revision_id": _text(contract.get("revision_id")),
        "summary": _text(publication.get("release_notes")),
        "published_by": _text(published_by),
        "published_at": generated_at,
        "url": _text(url, _text(publication.get("url"))),
        "checksum": package["integrity"]["content_checksum"],
    }
