"""Workspace-aware SQLite persistence for Catalyst Canvas.

Version 1.9.0 stores immutable Canvas revisions beneath durable workspace
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
            CREATE TABLE IF NOT EXISTS research_assets (
              asset_key TEXT PRIMARY KEY,
              workspace_id TEXT NOT NULL,
              source_project_id TEXT NOT NULL,
              asset_type TEXT NOT NULL,
              source_record_id TEXT NOT NULL,
              name TEXT NOT NULL,
              payload TEXT NOT NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              archived_at TEXT NOT NULL DEFAULT '',
              FOREIGN KEY(workspace_id) REFERENCES workspaces(workspace_id),
              FOREIGN KEY(source_project_id) REFERENCES projects(project_id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS project_research_links (
              project_id TEXT NOT NULL,
              asset_key TEXT NOT NULL,
              relationship TEXT NOT NULL DEFAULT 'source',
              created_at TEXT NOT NULL,
              PRIMARY KEY(project_id, asset_key),
              FOREIGN KEY(project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
              FOREIGN KEY(asset_key) REFERENCES research_assets(asset_key) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS workspace_members (
              workspace_id TEXT NOT NULL,
              member_id TEXT NOT NULL,
              name TEXT NOT NULL,
              organization TEXT NOT NULL DEFAULT '',
              role TEXT NOT NULL,
              status TEXT NOT NULL,
              capabilities TEXT NOT NULL DEFAULT '[]',
              joined_at TEXT NOT NULL,
              last_active_at TEXT NOT NULL DEFAULT '',
              PRIMARY KEY(workspace_id, member_id),
              FOREIGN KEY(workspace_id) REFERENCES workspaces(workspace_id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS collaboration_records (
              record_key TEXT PRIMARY KEY,
              workspace_id TEXT NOT NULL,
              project_id TEXT NOT NULL,
              record_type TEXT NOT NULL,
              record_id TEXT NOT NULL,
              status TEXT NOT NULL DEFAULT '',
              assignee_id TEXT NOT NULL DEFAULT '',
              payload TEXT NOT NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              FOREIGN KEY(workspace_id) REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
              FOREIGN KEY(project_id) REFERENCES projects(project_id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_collaboration_workspace_type_updated
            ON collaboration_records(workspace_id, record_type, updated_at DESC)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_research_assets_workspace_type_updated
            ON research_assets(workspace_id, asset_type, updated_at DESC)
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
        _ensure_workspace_member_conn(conn, DEFAULT_WORKSPACE_ID, "local-user", name="Local owner", role="owner")
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


def _ensure_workspace_member_conn(
    conn: sqlite3.Connection, workspace_id: str, member_id: str, *, name: str = "Workspace member",
    organization: str = "", role: str = "viewer", status: str = "active", capabilities: Sequence[str] | None = None,
) -> str:
    from catalyst_canvas.collaboration import ROLE_CAPABILITIES
    selected_role = role if role in ROLE_CAPABILITIES else "viewer"
    now = utc_now()
    caps = list(capabilities) if capabilities is not None else list(ROLE_CAPABILITIES[selected_role])
    conn.execute(
        """INSERT INTO workspace_members
        (workspace_id, member_id, name, organization, role, status, capabilities, joined_at, last_active_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, '')
        ON CONFLICT(workspace_id, member_id) DO UPDATE SET
          name=excluded.name, organization=excluded.organization, role=excluded.role,
          status=excluded.status, capabilities=excluded.capabilities""",
        (workspace_id, member_id, name, organization, selected_role, status, json.dumps(caps), now),
    )
    return member_id


def ensure_workspace_member(db_path: str, workspace_id: str, member_id: str, **kwargs: Any) -> Dict[str, Any]:
    with closing(connect(db_path)) as conn:
        _ensure_workspace_conn(conn, workspace_id)
        _ensure_workspace_member_conn(conn, workspace_id, member_id, **kwargs)
        conn.commit()
    member = get_workspace_member(db_path, workspace_id, member_id)
    if not member:
        raise RuntimeError("Workspace member could not be created")
    return member


def get_workspace_member(db_path: str, workspace_id: str, member_id: str) -> Dict[str, Any] | None:
    with closing(connect(db_path)) as conn:
        row = conn.execute("SELECT * FROM workspace_members WHERE workspace_id=? AND member_id=?", (workspace_id, member_id)).fetchone()
    if not row:
        return None
    record = dict(row)
    record["capabilities"] = json.loads(record.get("capabilities") or "[]")
    return record


def list_workspace_members(db_path: str, workspace_id: str) -> List[Dict[str, Any]]:
    with closing(connect(db_path)) as conn:
        rows = conn.execute("SELECT * FROM workspace_members WHERE workspace_id=? ORDER BY role, name", (workspace_id,)).fetchall()
    records=[]
    for row in rows:
        item=dict(row); item["capabilities"]=json.loads(item.get("capabilities") or "[]"); records.append(item)
    return records


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
        _ensure_workspace_member_conn(conn, identifier, owner_id, name="Workspace owner", role="owner")
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


def _research_asset_key(project_id: str, asset_type: str, record_id: str) -> str:
    return f"{project_id}:{asset_type}:{record_id}"


def _sync_research_assets_conn(
    conn: sqlite3.Connection, project_id: str, payload: Mapping[str, Any]
) -> None:
    project = _project_row(conn, project_id)
    if not project:
        return
    workspace_id = str(project["workspace_id"])
    now = str(payload.get("updated_at") or utc_now())
    collections = {
        "persona": (payload.get("personas", []), "persona_id"),
        "stakeholder": (payload.get("stakeholders", []), "stakeholder_id"),
        "journey": (payload.get("journeys", []), "journey_id"),
        "source": (payload.get("sources", []), "source_id"),
        "evidence": (payload.get("evidence", []), "evidence_id"),
        "claim": (payload.get("claims", []), "claim_id"),
        "assumption": (payload.get("assumptions", []), "assumption_id"),
        "research_question": (payload.get("research_questions", []), "research_question_id"),
        "interview_guide": (payload.get("interview_guides", []), "interview_guide_id"),
        "observation_note": (payload.get("observation_notes", []), "observation_note_id"),
        "prototype": (payload.get("prototypes", []), "prototype_id"),
        "hypothesis": (payload.get("hypotheses", []), "hypothesis_id"),
        "experiment_plan": (payload.get("experiment_plans", []), "experiment_id"),
        "experiment_run": (payload.get("experiment_runs", []), "run_id"),
        "learning_decision": (payload.get("learning_decisions", []), "learning_decision_id"),
        "iteration": (payload.get("iteration_history", []), "iteration_id"),
    }
    active_keys: set[str] = set()
    for asset_type, collection in collections.items():
        records, id_key = collection
        for record in records if isinstance(records, list) else []:
            if not isinstance(record, Mapping):
                continue
            record_id = str(record.get(id_key) or "").strip()
            if not record_id:
                continue
            asset_key = _research_asset_key(project_id, asset_type, record_id)
            active_keys.add(asset_key)
            name = str(record.get("name") or record.get("title") or record.get("statement") or record.get("question") or record.get("note") or f"Untitled {asset_type}").strip()
            existing = conn.execute(
                "SELECT created_at FROM research_assets WHERE asset_key=?", (asset_key,)
            ).fetchone()
            created_at = str(existing["created_at"]) if existing else now
            conn.execute(
                """
                INSERT INTO research_assets
                  (asset_key, workspace_id, source_project_id, asset_type, source_record_id, name, payload, created_at, updated_at, archived_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, '')
                ON CONFLICT(asset_key) DO UPDATE SET
                  name=excluded.name, payload=excluded.payload, updated_at=excluded.updated_at, archived_at=''
                """,
                (asset_key, workspace_id, project_id, asset_type, record_id, name, json.dumps(record, ensure_ascii=False), created_at, now),
            )
            conn.execute(
                """
                INSERT INTO project_research_links (project_id, asset_key, relationship, created_at)
                VALUES (?, ?, 'source', ?)
                ON CONFLICT(project_id, asset_key) DO NOTHING
                """,
                (project_id, asset_key, now),
            )
    rows = conn.execute(
        "SELECT asset_key FROM research_assets WHERE source_project_id=? AND archived_at=''",
        (project_id,),
    ).fetchall()
    stale = [str(row["asset_key"]) for row in rows if str(row["asset_key"]) not in active_keys]
    for asset_key in stale:
        conn.execute("UPDATE research_assets SET archived_at=?, updated_at=? WHERE asset_key=?", (now, now, asset_key))


def _sync_collaboration_records_conn(conn: sqlite3.Connection, project_id: str, payload: Mapping[str, Any]) -> None:
    project = _project_row(conn, project_id)
    if not project:
        return
    workspace_id = str(project["workspace_id"])
    now = str(payload.get("updated_at") or utc_now())
    collections = {
        "review_assignment": (payload.get("review_assignments", []), "assignment_id", "status", "assignee_ids"),
        "comment": (payload.get("comments", []), "comment_id", "status", "author_id"),
        "approval": (payload.get("approvals", []), "approval_id", "decision", "reviewer_id"),
        "publication": (payload.get("publication_records", []), "publication_id", "state", "owner_id"),
        "publication_release": (payload.get("release_history", []), "release_id", "state", "published_by"),
        "publication_handoff": (payload.get("publication_handoffs", []), "handoff_id", "status", "created_by"),
    }
    active=set()
    for record_type,(records,id_key,status_key,assignee_key) in collections.items():
        for record in records if isinstance(records,list) else []:
            if not isinstance(record,Mapping): continue
            record_id=str(record.get(id_key) or '').strip()
            if not record_id: continue
            key=f"{project_id}:{record_type}:{record_id}"; active.add(key)
            assignee=record.get(assignee_key, '')
            if isinstance(assignee,list): assignee=','.join(str(x) for x in assignee)
            created=str(record.get('created_at') or record.get('published_at') or now)
            conn.execute(
                """INSERT INTO collaboration_records
                (record_key,workspace_id,project_id,record_type,record_id,status,assignee_id,payload,created_at,updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(record_key) DO UPDATE SET status=excluded.status, assignee_id=excluded.assignee_id, payload=excluded.payload, updated_at=excluded.updated_at""",
                (key,workspace_id,project_id,record_type,record_id,str(record.get(status_key) or ''),str(assignee or ''),json.dumps(record,ensure_ascii=False),created,now),
            )
    rows=conn.execute("SELECT record_key FROM collaboration_records WHERE project_id=?",(project_id,)).fetchall()
    stale=[str(row['record_key']) for row in rows if str(row['record_key']) not in active]
    if stale:
        conn.executemany("DELETE FROM collaboration_records WHERE record_key=?",[(key,) for key in stale])
    for member in payload.get('workspace_members', []) if isinstance(payload.get('workspace_members'),list) else []:
        if isinstance(member,Mapping) and member.get('member_id'):
            _ensure_workspace_member_conn(conn, workspace_id, str(member['member_id']), name=str(member.get('name') or 'Workspace member'), organization=str(member.get('organization') or ''), role=str(member.get('role') or 'viewer'), status=str(member.get('status') or 'active'), capabilities=member.get('capabilities') if isinstance(member.get('capabilities'),list) else None)


def list_collaboration_records(db_path: str, workspace_id: str, *, project_id: str = "", record_type: str = "all") -> List[Dict[str, Any]]:
    clauses=['workspace_id=?']; params: List[Any]=[workspace_id]
    if project_id: clauses.append('project_id=?'); params.append(project_id)
    if record_type!='all': clauses.append('record_type=?'); params.append(record_type)
    with closing(connect(db_path)) as conn:
        rows=conn.execute(f"SELECT * FROM collaboration_records WHERE {' AND '.join(clauses)} ORDER BY updated_at DESC",params).fetchall()
    records=[]
    for row in rows:
        item=dict(row); item['payload']=json.loads(item['payload']); records.append(item)
    return records


def collaboration_record_counts(db_path: str, workspace_id: str, project_id: str = "") -> Dict[str,int]:
    clauses=['workspace_id=?']; params: List[Any]=[workspace_id]
    if project_id: clauses.append('project_id=?'); params.append(project_id)
    with closing(connect(db_path)) as conn:
        rows=conn.execute(f"SELECT record_type, COUNT(*) AS total FROM collaboration_records WHERE {' AND '.join(clauses)} GROUP BY record_type",params).fetchall()
    return {str(row['record_type']):int(row['total']) for row in rows}


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
    _sync_research_assets_conn(conn, project_id, payload)
    _sync_collaboration_records_conn(conn, project_id, payload)
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
            "schema_version": payload_schema_version(db_path, item["project_id"]),
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


def payload_schema_version(db_path: str, project_id: str) -> str:
    canvas = get_project_canvas(db_path, project_id)
    return str(canvas.get("schema_version", "")) if canvas else ""


def list_research_assets(
    db_path: str,
    *,
    workspace_id: str = DEFAULT_WORKSPACE_ID,
    asset_type: str = "all",
    query: str = "",
    include_archived: bool = False,
) -> List[Dict[str, Any]]:
    clauses = ["workspace_id=?"]
    params: List[Any] = [workspace_id]
    if asset_type in {"persona", "stakeholder", "journey", "source", "evidence", "claim", "assumption", "research_question", "interview_guide", "observation_note", "prototype", "hypothesis", "experiment_plan", "experiment_run", "learning_decision", "iteration"}:
        clauses.append("asset_type=?")
        params.append(asset_type)
    if not include_archived:
        clauses.append("archived_at=''")
    if query.strip():
        clauses.append("(LOWER(name) LIKE ? OR LOWER(payload) LIKE ?)")
        needle = f"%{query.strip().lower()}%"
        params.extend([needle, needle])
    with closing(connect(db_path)) as conn:
        rows = conn.execute(
            f"SELECT * FROM research_assets WHERE {' AND '.join(clauses)} ORDER BY updated_at DESC, name ASC",
            params,
        ).fetchall()
    result: List[Dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        item["payload"] = json.loads(item["payload"])
        result.append(item)
    return result


def get_research_asset(db_path: str, asset_key: str) -> Dict[str, Any] | None:
    with closing(connect(db_path)) as conn:
        row = conn.execute("SELECT * FROM research_assets WHERE asset_key=?", (asset_key,)).fetchone()
    if not row:
        return None
    item = dict(row)
    item["payload"] = json.loads(item["payload"])
    return item


def research_asset_counts(db_path: str, workspace_id: str = DEFAULT_WORKSPACE_ID) -> Dict[str, int]:
    result = {kind: 0 for kind in ["persona", "stakeholder", "journey", "source", "evidence", "claim", "assumption", "research_question", "interview_guide", "observation_note", "prototype", "hypothesis", "experiment_plan", "experiment_run", "learning_decision", "iteration"]}
    result["total"] = 0
    with closing(connect(db_path)) as conn:
        rows = conn.execute(
            """SELECT asset_type, COUNT(*) AS total FROM research_assets
               WHERE workspace_id=? AND archived_at='' GROUP BY asset_type""",
            (workspace_id,),
        ).fetchall()
    for row in rows:
        kind = str(row["asset_type"])
        result[kind] = int(row["total"])
        result["total"] += int(row["total"])
    return result


def reuse_research_asset(
    db_path: str, project_id: str, asset_key: str, *, workspace_id: str = DEFAULT_WORKSPACE_ID
) -> int:
    asset = get_research_asset(db_path, asset_key)
    if not asset or asset["workspace_id"] != workspace_id or asset["archived_at"]:
        raise ValueError("Research asset not found in this workspace.")
    canvas = get_project_canvas(db_path, project_id)
    if not canvas or canvas.get("_workspace_id") != workspace_id:
        raise ValueError("Project not found in this workspace.")
    payload = strip_internal_fields(canvas)
    payload["revision_id"] = new_id("revision")
    payload["updated_at"] = utc_now()
    kind = str(asset["asset_type"])
    collection_map = {
        "persona": "personas", "stakeholder": "stakeholders", "journey": "journeys",
        "source": "sources", "evidence": "evidence", "claim": "claims", "assumption": "assumptions",
        "research_question": "research_questions", "interview_guide": "interview_guides", "observation_note": "observation_notes",
        "prototype": "prototypes", "hypothesis": "hypotheses", "experiment_plan": "experiment_plans",
        "experiment_run": "experiment_runs", "learning_decision": "learning_decisions", "iteration": "iteration_history",
    }
    if kind not in collection_map:
        raise ValueError("Unsupported research asset type.")
    collection = collection_map[kind]
    record = json.loads(json.dumps(asset["payload"]))
    id_key = {
        "experiment_plan": "experiment_id", "experiment_run": "run_id", "iteration": "iteration_id",
    }.get(kind, f"{kind}_id")
    existing_ids = {str(item.get(id_key, "")) for item in payload.get(collection, [])}
    if str(record.get(id_key, "")) in existing_ids:
        record[id_key] = new_id(kind)
    if kind == "journey":
        persona_ids = {item.get("persona_id") for item in payload.get("personas", [])}
        if record.get("persona_id") not in persona_ids and payload.get("personas"):
            record["persona_id"] = payload["personas"][0]["persona_id"]
    payload.setdefault(collection, []).append(record)
    from catalyst_canvas.engine import generate_canvas
    payload = generate_canvas(payload, source_surface="workspace-reuse")
    return save_canvas(
        db_path, payload, project_id=project_id, workspace_id=workspace_id,
        change_note=f"Reused {kind} from workspace research library",
    )


def archive_research_asset(db_path: str, asset_key: str, *, workspace_id: str = DEFAULT_WORKSPACE_ID) -> bool:
    with closing(connect(db_path)) as conn:
        cursor = conn.execute(
            "UPDATE research_assets SET archived_at=?, updated_at=? WHERE asset_key=? AND workspace_id=?",
            (utc_now(), utc_now(), asset_key, workspace_id),
        )
        conn.commit()
        return bool(cursor.rowcount)
