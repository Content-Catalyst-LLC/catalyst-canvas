"""Framework and ideation normalization for Canvas Contract 1.3."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping

IDEATION_MODES = {"divergent", "convergent"}
IDEA_STATUSES = {"captured", "clustered", "merged", "selected", "parked", "rejected"}
SESSION_STATUSES = {"planned", "active", "complete", "archived"}


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


def _count(value: Any, fallback: int = 0) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return fallback


def normalize_prompt(prompt: Any, index: int, *, prefix: str = "prompt") -> Dict[str, str]:
    source = prompt if isinstance(prompt, Mapping) else {"question": prompt}
    return {
        "prompt_id": _text(source.get("prompt_id"), f"{prefix}-{index:03d}"),
        "label": _text(source.get("label"), f"Prompt {index}"),
        "question": _text(source.get("question"), "What should the team explore?"),
        "purpose": _text(source.get("purpose")),
        "output_type": _text(source.get("output_type"), "idea"),
    }


def normalize_custom_frameworks(value: Any) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if isinstance(value, Mapping) else [])
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"name": item}
        key = _text(source.get("key"), f"custom-{index:03d}")
        prompts = [normalize_prompt(prompt, prompt_index) for prompt_index, prompt in enumerate(source.get("prompts") or [], start=1)]
        if not prompts:
            prompts = [normalize_prompt({"label": "Explore", "question": "What should the team explore?"}, 1)]
        records.append({
            "key": key,
            "name": _text(source.get("name"), f"Custom Framework {index}"),
            "category": _text(source.get("category"), "custom"),
            "description": _text(source.get("description")),
            "intended_uses": _list(source.get("intended_uses")),
            "limitations": _list(source.get("limitations")),
            "required_inputs": _list(source.get("required_inputs")),
            "output_types": _list(source.get("output_types")) or ["idea"],
            "mode_support": [mode for mode in _list(source.get("mode_support")) if mode in IDEATION_MODES] or ["divergent", "convergent"],
            "prompts": prompts,
            "origin": "custom",
            "organization": _text(source.get("organization")),
            "created_by": _text(source.get("created_by")),
            "version": _text(source.get("version"), "1.0"),
            "tags": _list(source.get("tags")),
        })
    return records


def normalize_prompt_packs(value: Any) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if isinstance(value, Mapping) else [])
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"name": item}
        prompts = [normalize_prompt(prompt, prompt_index, prefix=f"pack-{index:03d}-prompt") for prompt_index, prompt in enumerate(source.get("prompts") or [], start=1)]
        if not prompts:
            continue
        records.append({
            "prompt_pack_id": _text(source.get("prompt_pack_id"), f"prompt-pack-{index:03d}"),
            "name": _text(source.get("name"), f"Prompt Pack {index}"),
            "description": _text(source.get("description")),
            "organization": _text(source.get("organization")),
            "created_by": _text(source.get("created_by")),
            "prompts": prompts,
            "tags": _list(source.get("tags")),
        })
    return records


def normalize_ideation_sessions(value: Any, *, framework_key: str, created_at: str) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if isinstance(value, Mapping) else [])
    if not raw:
        raw = [{
            "title": "Primary ideation session",
            "mode": "divergent",
            "framework_key": framework_key,
            "challenge_ids": ["challenge-primary"],
            "status": "planned",
        }]
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"title": item}
        session_created = _text(source.get("created_at"), created_at)
        records.append({
            "session_id": _text(source.get("session_id"), f"ideation-session-{index:03d}"),
            "title": _text(source.get("title"), f"Ideation Session {index}"),
            "mode": _choice(source.get("mode"), IDEATION_MODES, "divergent"),
            "framework_key": _text(source.get("framework_key"), framework_key),
            "prompt_pack_ids": _list(source.get("prompt_pack_ids")),
            "challenge_ids": _list(source.get("challenge_ids")) or ["challenge-primary"],
            "hmw_ids": _list(source.get("hmw_ids")),
            "facilitator": _text(source.get("facilitator")),
            "participants": _list(source.get("participants")),
            "status": _choice(source.get("status"), SESSION_STATUSES, "planned"),
            "notes": _text(source.get("notes")),
            "created_at": session_created,
            "updated_at": _text(source.get("updated_at"), session_created),
        })
    return records


def normalize_idea_clusters(value: Any) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if isinstance(value, Mapping) else [])
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"name": item}
        records.append({
            "cluster_id": _text(source.get("cluster_id"), f"idea-cluster-{index:03d}"),
            "name": _text(source.get("name"), f"Cluster {index}"),
            "description": _text(source.get("description")),
            "idea_ids": _list(source.get("idea_ids")),
            "tags": _list(source.get("tags")),
            "rationale": _text(source.get("rationale")),
            "sequence": max(1, _count(source.get("sequence"), index)),
        })
    return records


def normalize_ideas(
    value: Any,
    *,
    sessions: List[Dict[str, Any]],
    hmw_ids: List[str],
    framework_prompts: List[Dict[str, Any]],
    prototypes: List[Dict[str, Any]],
    created_at: str,
) -> List[Dict[str, Any]]:
    raw = value if isinstance(value, list) else ([value] if isinstance(value, Mapping) else [])
    session_id = sessions[0]["session_id"] if sessions else "ideation-session-001"
    default_hmw = hmw_ids[0] if hmw_ids else "hmw-001"
    default_prompt = framework_prompts[0]["prompt_id"] if framework_prompts else "prompt-001"
    records: List[Dict[str, Any]] = []
    for index, item in enumerate(raw, start=1):
        source = item if isinstance(item, Mapping) else {"title": item}
        title = _text(source.get("title"), f"Idea {index}")
        idea_created = _text(source.get("created_at"), created_at)
        status = _choice(source.get("status"), IDEA_STATUSES, "captured")
        records.append({
            "idea_id": _text(source.get("idea_id"), f"idea-{index:03d}"),
            "title": title,
            "description": _text(source.get("description")),
            "session_id": _text(source.get("session_id"), session_id),
            "challenge_id": _text(source.get("challenge_id"), "challenge-primary"),
            "hmw_id": _text(source.get("hmw_id"), default_hmw),
            "prompt_id": _text(source.get("prompt_id"), default_prompt),
            "author": _text(source.get("author"), "Unassigned author"),
            "rationale": _text(source.get("rationale"), "Captured for review; rationale not yet expanded."),
            "tags": _list(source.get("tags")),
            "cluster_id": _text(source.get("cluster_id")),
            "status": status,
            "vote_count": _count(source.get("vote_count")),
            "voter_ids": _list(source.get("voter_ids")),
            "parent_idea_ids": _list(source.get("parent_idea_ids")),
            "merged_into_id": _text(source.get("merged_into_id")),
            "prototype_ids": _list(source.get("prototype_ids")),
            "assumption_ids": _list(source.get("assumption_ids")),
            "evidence_ids": _list(source.get("evidence_ids")),
            "created_at": idea_created,
            "updated_at": _text(source.get("updated_at"), idea_created),
        })
    # Repair cluster memberships from idea records without deleting explicit membership.
    return records


def ideation_summary(
    sessions: List[Dict[str, Any]],
    ideas: List[Dict[str, Any]],
    clusters: List[Dict[str, Any]],
    *,
    generated_at: str,
) -> Dict[str, Any]:
    lineage_missing = sum(
        1 for idea in ideas
        if not idea.get("challenge_id") or not idea.get("hmw_id") or not idea.get("prompt_id") or not idea.get("author") or not idea.get("rationale")
    )
    return {
        "session_count": len(sessions),
        "idea_count": len(ideas),
        "cluster_count": len(clusters),
        "vote_count": sum(_count(idea.get("vote_count")) for idea in ideas),
        "selected_count": sum(1 for idea in ideas if idea.get("status") == "selected"),
        "merged_count": sum(1 for idea in ideas if idea.get("status") == "merged" or idea.get("merged_into_id")),
        "prototype_link_count": sum(len(idea.get("prototype_ids") or []) for idea in ideas),
        "orphaned_lineage_count": lineage_missing,
        "modes_used": sorted({session.get("mode", "divergent") for session in sessions}),
        "indicator_note": "Ideation indicators describe recorded activity and lineage. Votes and selections represent participant judgment, not objective quality.",
        "generated_at": generated_at,
    }


def merge_idea_records(ideas: List[Mapping[str, Any]], source_ids: List[str], target: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Return a normalized idea list with source ideas merged into a target idea."""
    target_id = _text(target.get("idea_id"), "idea-merged")
    source_set = set(source_ids)
    result: List[Dict[str, Any]] = []
    parents: List[str] = []
    for item in ideas:
        record = deepcopy(dict(item))
        if record.get("idea_id") in source_set:
            record["status"] = "merged"
            record["merged_into_id"] = target_id
            parents.append(record["idea_id"])
        result.append(record)
    merged = deepcopy(dict(target))
    merged["idea_id"] = target_id
    merged["parent_idea_ids"] = sorted(set(_list(merged.get("parent_idea_ids")) + parents))
    merged["status"] = _choice(merged.get("status"), IDEA_STATUSES, "captured")
    result.append(merged)
    return result
