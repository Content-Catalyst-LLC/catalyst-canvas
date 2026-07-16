"""Workspace-aware SQLite persistence for Catalyst Canvas.

Version 1.3.0 stores immutable Canvas revisions beneath durable workspace
projects. The legacy ``canvas_briefs`` table remains readable and is migrated
into the default workspace during initialization.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence

from catalyst_canvas.contract import new_id, strip_internal_fields, utc_now, validate_contract
from catalyst_canvas.exporters import export_json
from catalyst_canvas.migrations import migrate_payload
from catalyst_canvas.workspaces import (
    DEFAULT_WORKSPACE_ID,
    project_record,
    validate_project_record,
)

AUTOSAVE_RETENTION = 20


def connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: str) -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with closing(connect(db_path)) as conn:
        # v1.2 compatibility table. Kept so existing repositories can be upgraded
        # in place; all new writes go to workspace/project/revision tables.
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS canvas_briefs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              title TEXT NOT NULL,
              payload TEXT NOT NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS demo_events (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              event_date TEXT NOT NULL,
              source TEXT NOT NULL,
              event_name TEXT NOT NULL,
              persona_hint TEXT,
              page_path TEXT,
              count INTEGER NOT NULL DEFAULT 1
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS workspaces (
              workspace_id TEXT PRIMARY KEY,
              name TEXT NOT NULL,
              description TEXT NOT NULL DEFAULT '',
              owner_id TEXT NOT NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
              project_id TEXT PRIMARY KEY,
              workspace_id TEXT NOT NULL,
              title TEXT NOT NULL,
              description TEXT NOT NULL DEFAULT '',
              status TEXT NOT NULL DEFAULT 'active',
              tags TEXT NOT NULL DEFAULT '[]',
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              archived_at TEXT NOT NULL DEFAULT '',
              current_revision_storage_id INTEGER,
              legacy_storage_id INTEGER UNIQUE,
              FOREIGN KEY(workspace_id) REFERENCES workspaces(workspace_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS canvas_revisions (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              revision_id TEXT NOT NULL UNIQUE,
              project_id TEXT NOT NULL,
              canvas_id TEXT NOT NULL,
              payload TEXT NOT NULL,
              created_at TEXT NOT NULL,
              autosave INTEGER NOT NULL DEFAULT 0,
              change_note TEXT NOT NULL DEFAULT '',
              restored_from_revision_id TEXT NOT NULL DEFAULT '',
              FOREIGN KEY(project_id) REFERENCES projects(project_id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_projects_workspace_status_updated
            ON projects(workspace_id, status, updated_at DESC)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_revisions_project_created
            ON canvas_revisions(project_id, created_at DESC, id DESC)
            """
        )
        _ensure_workspace_conn(conn)
        _migrate_legacy_rows_conn(conn)
        conn.commit()


def _ensure_workspace_conn(
    conn: sqlite3.Connection,
    workspace_id: str = DEFAULT_WORKSPACE_ID,
    *,
    name: str = "Local Workspace",
    owner_id: str = "local-user",
    description: str = "Private local Catalyst Canvas workspace.",
) -> str:
    existing = conn.execute(
        "SELECT workspace_id FROM workspaces WHERE workspace_id=?", (workspace_id,)
    ).fetchone()
    if existing:
        return workspace_id
    now = utc_now()
    conn.execute(
        """
        INSERT INTO workspaces (workspace_id, name, description, owner_id, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (workspace_id, name, description, owner_id, now, now),
    )
    return workspace_id


def ensure_workspace(
    db_path: str,
    workspace_id: str = DEFAULT_WORKSPACE_ID,
    *,
    name: str = "Local Workspace",
    owner_id: str = "local-user",
    description: str = "Private local Catalyst Canvas workspace.",
) -> str:
    with closing(connect(db_path)) as conn:
        result = _ensure_workspace_conn(
            conn,
            workspace_id,
            name=name,
            owner_id=owner_id,
            description=description,
        )
        conn.commit()
        return result


def create_workspace(
    db_path: str,
    name: str,
    *,
    owner_id: str = "local-user",
    description: str = "",
    workspace_id: str | None = None,
) -> Dict[str, Any]:
    identifier = workspace_id or new_id("workspace")
    with closing(connect(db_path)) as conn:
        _ensure_workspace_conn(
            conn,
            identifier,
            name=name,
            owner_id=owner_id,
            description=description,
        )
        conn.commit()
    workspace = get_workspace(db_path, identifier)
    if not workspace:
        raise RuntimeError("Workspace creation failed")
    return workspace


def get_workspace(db_path: str, workspace_id: str = DEFAULT_WORKSPACE_ID) -> Dict[str, Any] | None:
    with closing(connect(db_path)) as conn:
        row = conn.execute("SELECT * FROM workspaces WHERE workspace_id=?", (workspace_id,)).fetchone()
    return dict(row) if row else None


def list_workspaces(db_path: str) -> List[Dict[str, Any]]:
    with closing(connect(db_path)) as conn:
        rows = conn.execute(
            """
            SELECT w.*, COUNT(p.project_id) AS project_count,
                   SUM(CASE WHEN p.status='active' THEN 1 ELSE 0 END) AS active_project_count
            FROM workspaces w
            LEFT JOIN projects p ON p.workspace_id=w.workspace_id
            GROUP BY w.workspace_id
            ORDER BY w.updated_at DESC, w.name ASC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def _migrate_legacy_rows_conn(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        """
        SELECT b.* FROM canvas_briefs b
        LEFT JOIN projects p ON p.legacy_storage_id=b.id
        WHERE p.project_id IS NULL
        ORDER BY b.id ASC
        """
    ).fetchall()
    for row in rows:
        try:
            contract = migrate_payload(json.loads(row["payload"]), source_surface="migration").contract
        except (ValueError, TypeError, json.JSONDecodeError):
            continue
        project_id = new_id("project")
        serialized = export_json(contract)
        conn.execute(
            """
            INSERT INTO projects
              (project_id, workspace_id, title, description, status, tags, created_at,
               updated_at, archived_at, current_revision_storage_id, legacy_storage_id)
            VALUES (?, ?, ?, '', 'active', '[]', ?, ?, '', NULL, ?)
            """,
            (
                project_id,
                DEFAULT_WORKSPACE_ID,
                contract["title"],
                contract["created_at"],
                contract["updated_at"],
                int(row["id"]),
            ),
        )
        cursor = conn.execute(
            """
            INSERT INTO canvas_revisions
              (revision_id, project_id, canvas_id, payload, created_at, autosave, change_note)
            VALUES (?, ?, ?, ?, ?, 0, ?)
            """,
            (
                contract["revision_id"],
                project_id,
                contract["canvas_id"],
                serialized,
                contract["updated_at"],
                "Migrated from Catalyst Canvas v1.2 storage",
            ),
        )
        revision_storage_id = int(cursor.lastrowid)
        conn.execute(
            "UPDATE projects SET current_revision_storage_id=? WHERE project_id=?",
            (revision_storage_id, project_id),
        )


def _project_row(conn: sqlite3.Connection, project_id: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM projects WHERE project_id=?", (project_id,)).fetchone()


def _project_for_revision_storage(conn: sqlite3.Connection, revision_storage_id: int) -> sqlite3.Row | None:
    return conn.execute(
        """
        SELECT p.* FROM projects p
        JOIN canvas_revisions r ON r.project_id=p.project_id
        WHERE r.id=?
        """,
        (revision_storage_id,),
    ).fetchone()


def _insert_revision_conn(
    conn: sqlite3.Connection,
    project_id: str,
    contract: Mapping[str, Any],
    *,
    autosave: bool,
    change_note: str,
    restored_from_revision_id: str = "",
) -> int:
    payload = validate_contract(strip_internal_fields(contract))
    cursor = conn.execute(
        """
        INSERT INTO canvas_revisions
          (revision_id, project_id, canvas_id, payload, created_at, autosave, change_note, restored_from_revision_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload["revision_id"],
            project_id,
            payload["canvas_id"],
            export_json(payload),
            payload["updated_at"],
            1 if autosave else 0,
            str(change_note or "").strip(),
            str(restored_from_revision_id or "").strip(),
        ),
    )
    revision_storage_id = int(cursor.lastrowid)
    conn.execute(
        """
        UPDATE projects
        SET title=?, updated_at=?, current_revision_storage_id=?
        WHERE project_id=?
        """,
        (payload["title"], payload["updated_at"], revision_storage_id, project_id),
    )
    if autosave:
        _prune_autosaves_conn(conn, project_id)
    return revision_storage_id


def _prune_autosaves_conn(conn: sqlite3.Connection, project_id: str) -> None:
    rows = conn.execute(
        """
        SELECT id FROM canvas_revisions
        WHERE project_id=? AND autosave=1
        ORDER BY created_at DESC, id DESC
        LIMIT -1 OFFSET ?
        """,
        (project_id, AUTOSAVE_RETENTION),
    ).fetchall()
    if not rows:
        return
    current = conn.execute(
        "SELECT current_revision_storage_id FROM projects WHERE project_id=?", (project_id,)
    ).fetchone()
    current_id = int(current[0]) if current and current[0] else None
    removable = [int(row["id"]) for row in rows if int(row["id"]) != current_id]
    if removable:
        placeholders = ",".join("?" for _ in removable)
        conn.execute(f"DELETE FROM canvas_revisions WHERE id IN ({placeholders})", removable)


def create_project(
    db_path: str,
    canvas: Mapping[str, Any],
    *,
    workspace_id: str = DEFAULT_WORKSPACE_ID,
    title: str | None = None,
    description: str = "",
    tags: Sequence[str] | str | None = None,
    project_id: str | None = None,
    change_note: str = "Project created",
) -> Dict[str, Any]:
    payload = validate_contract(strip_internal_fields(canvas))
    identifier = project_id or new_id("project")
    with closing(connect(db_path)) as conn:
        _ensure_workspace_conn(conn, workspace_id)
        now = payload["updated_at"]
        conn.execute(
            """
            INSERT INTO projects
              (project_id, workspace_id, title, description, status, tags, created_at,
               updated_at, archived_at, current_revision_storage_id, legacy_storage_id)
            VALUES (?, ?, ?, ?, 'active', ?, ?, ?, '', NULL, NULL)
            """,
            (
                identifier,
                workspace_id,
                str(title or payload["title"]).strip() or "Untitled Canvas Project",
                str(description or "").strip(),
                json.dumps(list(tags) if tags and not isinstance(tags, str) else ([item.strip() for item in tags.split(",") if item.strip()] if isinstance(tags, str) else [])),
                payload["created_at"],
                now,
            ),
        )
        revision_storage_id = _insert_revision_conn(
            conn, identifier, payload, autosave=False, change_note=change_note
        )
        conn.commit()
    project = get_project(db_path, identifier)
    if not project:
        raise RuntimeError("Project creation failed")
    project["_current_revision_storage_id"] = revision_storage_id
    return project


def save_canvas(
    db_path: str,
    canvas: Mapping[str, Any],
    canvas_id: int | None = None,
    *,
    project_id: str | None = None,
    workspace_id: str = DEFAULT_WORKSPACE_ID,
    autosave: bool = False,
    change_note: str = "",
) -> int:
    payload = validate_contract(strip_internal_fields(canvas))
    with closing(connect(db_path)) as conn:
        _ensure_workspace_conn(conn, workspace_id)
        project = _project_row(conn, project_id) if project_id else None
        if not project and canvas_id:
            project = _project_for_revision_storage(conn, int(canvas_id))
        if not project:
            identifier = project_id or new_id("project")
            conn.execute(
                """
                INSERT INTO projects
                  (project_id, workspace_id, title, description, status, tags, created_at,
                   updated_at, archived_at, current_revision_storage_id, legacy_storage_id)
                VALUES (?, ?, ?, '', 'active', '[]', ?, ?, '', NULL, NULL)
                """,
                (
                    identifier,
                    workspace_id,
                    payload["title"],
                    payload["created_at"],
                    payload["updated_at"],
                ),
            )
            project_id = identifier
        else:
            project_id = str(project["project_id"])
            if project["status"] == "archived":
                raise ValueError("Archived projects must be restored before they can be edited.")
        revision_storage_id = _insert_revision_conn(
            conn,
            project_id,
            payload,
            autosave=autosave,
            change_note=change_note or ("Autosave" if autosave else "Canvas updated"),
        )
        conn.commit()
        return revision_storage_id


def _revision_to_contract(row: sqlite3.Row) -> Dict[str, Any]:
    raw = json.loads(row["payload"])
    contract = migrate_payload(raw, source_surface="migration").contract
    contract["_storage_id"] = int(row["id"])
    contract["_project_id"] = str(row["project_id"])
    contract["_workspace_id"] = str(row["workspace_id"])
    contract["_autosave"] = bool(row["autosave"])
    contract["_change_note"] = str(row["change_note"] or "")
    return contract


def get_canvas(db_path: str, canvas_id: int) -> Dict[str, Any] | None:
    with closing(connect(db_path)) as conn:
        row = conn.execute(
            """
            SELECT r.*, p.workspace_id FROM canvas_revisions r
            JOIN projects p ON p.project_id=r.project_id
            WHERE r.id=?
            """,
            (canvas_id,),
        ).fetchone()
        if not row:
            legacy = conn.execute("SELECT * FROM canvas_briefs WHERE id=?", (canvas_id,)).fetchone()
            if legacy:
                project = conn.execute(
                    "SELECT current_revision_storage_id FROM projects WHERE legacy_storage_id=?",
                    (canvas_id,),
                ).fetchone()
                if not project:
                    _migrate_legacy_rows_conn(conn)
                    conn.commit()
                    project = conn.execute(
                        "SELECT current_revision_storage_id FROM projects WHERE legacy_storage_id=?",
                        (canvas_id,),
                    ).fetchone()
                if project and project["current_revision_storage_id"]:
                    row = conn.execute(
                        """
                        SELECT r.*, p.workspace_id FROM canvas_revisions r
                        JOIN projects p ON p.project_id=r.project_id
                        WHERE r.id=?
                        """,
                        (int(project["current_revision_storage_id"]),),
                    ).fetchone()
    return _revision_to_contract(row) if row else None


def get_project_canvas(
    db_path: str,
    project_id: str,
    *,
    revision_id: str | None = None,
) -> Dict[str, Any] | None:
    with closing(connect(db_path)) as conn:
        if revision_id:
            row = conn.execute(
                """
                SELECT r.*, p.workspace_id FROM canvas_revisions r
                JOIN projects p ON p.project_id=r.project_id
                WHERE r.project_id=? AND r.revision_id=?
                """,
                (project_id, revision_id),
            ).fetchone()
        else:
            row = conn.execute(
                """
                SELECT r.*, p.workspace_id FROM projects p
                JOIN canvas_revisions r ON r.id=p.current_revision_storage_id
                WHERE p.project_id=?
                """,
                (project_id,),
            ).fetchone()
    return _revision_to_contract(row) if row else None


def latest_canvas(
    db_path: str,
    *,
    workspace_id: str = DEFAULT_WORKSPACE_ID,
    include_archived: bool = False,
) -> Dict[str, Any] | None:
    status_clause = "" if include_archived else "AND p.status='active'"
    with closing(connect(db_path)) as conn:
        row = conn.execute(
            f"""
            SELECT r.*, p.workspace_id FROM projects p
            JOIN canvas_revisions r ON r.id=p.current_revision_storage_id
            WHERE p.workspace_id=? {status_clause}
            ORDER BY p.updated_at DESC, p.project_id DESC LIMIT 1
            """,
            (workspace_id,),
        ).fetchone()
    return _revision_to_contract(row) if row else None


def _row_to_project_record(conn: sqlite3.Connection, row: sqlite3.Row) -> Dict[str, Any]:
    current = conn.execute(
        "SELECT revision_id, canvas_id FROM canvas_revisions WHERE id=?",
        (row["current_revision_storage_id"],),
    ).fetchone()
    count = conn.execute(
        "SELECT COUNT(*) AS total FROM canvas_revisions WHERE project_id=?",
        (row["project_id"],),
    ).fetchone()
    if not current:
        raise RuntimeError(f"Project {row['project_id']} has no current revision")
    return project_record(
        workspace_id=row["workspace_id"],
        project_id=row["project_id"],
        title=row["title"],
        description=row["description"],
        status=row["status"],
        tags=json.loads(row["tags"] or "[]"),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        archived_at=row["archived_at"],
        current_canvas_id=current["canvas_id"],
        current_revision_id=current["revision_id"],
        revision_count=int(count["total"]),
    )


def get_project(db_path: str, project_id: str) -> Dict[str, Any] | None:
    with closing(connect(db_path)) as conn:
        row = _project_row(conn, project_id)
        if not row:
            return None
        record = _row_to_project_record(conn, row)
        record["_current_revision_storage_id"] = int(row["current_revision_storage_id"])
        return record


def list_projects(
    db_path: str,
    *,
    workspace_id: str = DEFAULT_WORKSPACE_ID,
    query: str = "",
    status: str = "active",
    limit: int = 50,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    clauses = ["workspace_id=?"]
    params: List[Any] = [workspace_id]
    if status in {"active", "archived"}:
        clauses.append("status=?")
        params.append(status)
    if query.strip():
        clauses.append("(LOWER(title) LIKE ? OR LOWER(description) LIKE ? OR LOWER(tags) LIKE ?)")
        needle = f"%{query.strip().lower()}%"
        params.extend([needle, needle, needle])
    params.extend([max(1, min(int(limit), 200)), max(0, int(offset))])
    sql = f"""
        SELECT * FROM projects
        WHERE {' AND '.join(clauses)}
        ORDER BY updated_at DESC, project_id DESC
        LIMIT ? OFFSET ?
    """
    records: List[Dict[str, Any]] = []
    with closing(connect(db_path)) as conn:
        rows = conn.execute(sql, params).fetchall()
        for row in rows:
            record = _row_to_project_record(conn, row)
            record["_current_revision_storage_id"] = int(row["current_revision_storage_id"])
            records.append(record)
    return records


def list_canvases(db_path: str, limit: int = 12) -> List[Dict[str, Any]]:
    """Compatibility project listing used by the v1.2 dashboard."""
    records = list_projects(db_path, limit=limit, status="active")
    return [
        {
            "id": item["_current_revision_storage_id"],
            "project_id": item["project_id"],
            "canvas_id": item["current_canvas_id"],
            "schema_version": "catalyst-canvas/1.0",
            "title": item["title"],
            "status": item["status"],
            "created_at": item["created_at"],
            "updated_at": item["updated_at"],
            "revision_count": item["revision_count"],
        }
        for item in records
    ]


def update_project_metadata(
    db_path: str,
    project_id: str,
    *,
    title: str | None = None,
    description: str | None = None,
    tags: Sequence[str] | str | None = None,
) -> Dict[str, Any] | None:
    updates: List[str] = []
    params: List[Any] = []
    if title is not None:
        updates.append("title=?")
        params.append(str(title).strip() or "Untitled Canvas Project")
    if description is not None:
        updates.append("description=?")
        params.append(str(description).strip())
    if tags is not None:
        normalized = list(tags) if not isinstance(tags, str) else [item.strip() for item in tags.split(",") if item.strip()]
        updates.append("tags=?")
        params.append(json.dumps(normalized))
    if not updates:
        return get_project(db_path, project_id)
    updates.append("updated_at=?")
    params.append(utc_now())
    params.append(project_id)
    with closing(connect(db_path)) as conn:
        conn.execute(f"UPDATE projects SET {', '.join(updates)} WHERE project_id=?", params)
        conn.commit()
    return get_project(db_path, project_id)


def archive_project(db_path: str, project_id: str) -> Dict[str, Any] | None:
    now = utc_now()
    with closing(connect(db_path)) as conn:
        conn.execute(
            "UPDATE projects SET status='archived', archived_at=?, updated_at=? WHERE project_id=?",
            (now, now, project_id),
        )
        conn.commit()
    return get_project(db_path, project_id)


def restore_project(db_path: str, project_id: str) -> Dict[str, Any] | None:
    now = utc_now()
    with closing(connect(db_path)) as conn:
        conn.execute(
            "UPDATE projects SET status='active', archived_at='', updated_at=? WHERE project_id=?",
            (now, project_id),
        )
        conn.commit()
    return get_project(db_path, project_id)


def duplicate_project(
    db_path: str,
    project_id: str,
    *,
    title: str | None = None,
) -> Dict[str, Any] | None:
    source_project = get_project(db_path, project_id)
    source_canvas = get_project_canvas(db_path, project_id)
    if not source_project or not source_canvas:
        return None
    payload = strip_internal_fields(source_canvas)
    payload["canvas_id"] = new_id("canvas")
    payload["revision_id"] = new_id("revision")
    payload["title"] = str(title or f"{source_project['title']} Copy").strip()
    payload["created_at"] = utc_now()
    payload["updated_at"] = payload["created_at"]
    payload["provenance"] = {
        **payload["provenance"],
        "source_surface": "flask",
        "warnings": list(payload["provenance"].get("warnings", []))
        + [f"Duplicated from project {project_id}."],
    }
    return create_project(
        db_path,
        payload,
        workspace_id=source_project["workspace_id"],
        title=payload["title"],
        description=source_project["description"],
        tags=source_project["tags"],
        change_note=f"Duplicated from {project_id}",
    )


def list_revisions(db_path: str, project_id: str, *, limit: int = 100) -> List[Dict[str, Any]]:
    with closing(connect(db_path)) as conn:
        rows = conn.execute(
            """
            SELECT id, revision_id, canvas_id, created_at, autosave, change_note,
                   restored_from_revision_id
            FROM canvas_revisions
            WHERE project_id=?
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (project_id, max(1, min(int(limit), 500))),
        ).fetchall()
    return [
        {
            "storage_id": int(row["id"]),
            "revision_id": row["revision_id"],
            "canvas_id": row["canvas_id"],
            "created_at": row["created_at"],
            "autosave": bool(row["autosave"]),
            "change_note": row["change_note"],
            "restored_from_revision_id": row["restored_from_revision_id"],
        }
        for row in rows
    ]


def restore_revision(db_path: str, project_id: str, revision_id: str) -> int | None:
    historical = get_project_canvas(db_path, project_id, revision_id=revision_id)
    if not historical:
        return None
    payload = strip_internal_fields(historical)
    payload["revision_id"] = new_id("revision")
    payload["updated_at"] = utc_now()
    with closing(connect(db_path)) as conn:
        project = _project_row(conn, project_id)
        if not project:
            return None
        if project["status"] == "archived":
            raise ValueError("Archived projects must be restored before a revision can be restored.")
        storage_id = _insert_revision_conn(
            conn,
            project_id,
            payload,
            autosave=False,
            change_note=f"Restored revision {revision_id}",
            restored_from_revision_id=revision_id,
        )
        conn.commit()
        return storage_id


def project_counts(db_path: str, workspace_id: str = DEFAULT_WORKSPACE_ID) -> Dict[str, int]:
    with closing(connect(db_path)) as conn:
        rows = conn.execute(
            "SELECT status, COUNT(*) AS total FROM projects WHERE workspace_id=? GROUP BY status",
            (workspace_id,),
        ).fetchall()
    counts = {"active": 0, "archived": 0}
    for row in rows:
        counts[str(row["status"])] = int(row["total"])
    return counts
