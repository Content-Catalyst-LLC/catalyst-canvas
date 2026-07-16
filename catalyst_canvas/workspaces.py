"""Workspace and project records for Catalyst Canvas v1.5.0."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Mapping

from jsonschema import Draft202012Validator

from .contract import clean_list, clean_text, new_id, utc_now

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_SCHEMA_VERSION = "catalyst-canvas-workspace/1.0"
WORKSPACE_SCHEMA_PATH = ROOT / "schemas" / "catalyst_canvas_workspace_1_0.schema.json"
DEFAULT_WORKSPACE_ID = "workspace-local-default"


class WorkspaceValidationError(ValueError):
    """Raised when a workspace or project record is invalid."""


def load_workspace_schema() -> Dict[str, Any]:
    return json.loads(WORKSPACE_SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_project_record(record: Mapping[str, Any]) -> Dict[str, Any]:
    payload = deepcopy(dict(record))
    validator = Draft202012Validator(load_workspace_schema())
    errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.absolute_path))
    if errors:
        messages = []
        for error in errors:
            path = ".".join(str(part) for part in error.absolute_path) or "$"
            messages.append(f"{path}: {error.message}")
        raise WorkspaceValidationError("Workspace Project Contract 1.0 validation failed: " + "; ".join(messages))
    return payload


def new_workspace_record(
    name: str = "Local Workspace",
    *,
    workspace_id: str | None = None,
    owner_id: str = "local-user",
    description: str = "",
) -> Dict[str, Any]:
    now = utc_now()
    return {
        "workspace_id": clean_text(workspace_id, DEFAULT_WORKSPACE_ID),
        "name": clean_text(name, "Local Workspace"),
        "description": clean_text(description),
        "owner_id": clean_text(owner_id, "local-user"),
        "created_at": now,
        "updated_at": now,
    }


def project_record(
    *,
    workspace_id: str,
    project_id: str | None = None,
    title: str,
    description: str = "",
    status: str = "active",
    tags: Any = None,
    created_at: str | None = None,
    updated_at: str | None = None,
    archived_at: str = "",
    current_canvas_id: str,
    current_revision_id: str,
    revision_count: int = 1,
) -> Dict[str, Any]:
    created = clean_text(created_at, utc_now())
    updated = clean_text(updated_at, created)
    record = {
        "schema_version": WORKSPACE_SCHEMA_VERSION,
        "workspace_id": clean_text(workspace_id, DEFAULT_WORKSPACE_ID),
        "project_id": clean_text(project_id, new_id("project")),
        "title": clean_text(title, "Untitled Canvas Project"),
        "description": clean_text(description),
        "status": clean_text(status, "active"),
        "tags": clean_list(tags),
        "created_at": created,
        "updated_at": updated,
        "archived_at": clean_text(archived_at),
        "current_canvas_id": clean_text(current_canvas_id),
        "current_revision_id": clean_text(current_revision_id),
        "revision_count": int(revision_count),
    }
    return validate_project_record(record)
