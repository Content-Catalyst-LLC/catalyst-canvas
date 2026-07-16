"""Validated SQLite persistence for Canvas Contract 1.0 records."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any, Dict, List, Mapping

from catalyst_canvas.contract import strip_internal_fields, validate_contract
from catalyst_canvas.exporters import export_json
from catalyst_canvas.migrations import migrate_payload


def connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str) -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with closing(connect(db_path)) as conn:
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
        conn.commit()


def save_canvas(db_path: str, canvas: Mapping[str, Any], canvas_id: int | None = None) -> int:
    payload = validate_contract(strip_internal_fields(canvas))
    serialized = export_json(payload)
    title = payload["title"]
    with closing(connect(db_path)) as conn:
        if canvas_id:
            existing = conn.execute("SELECT id FROM canvas_briefs WHERE id=?", (canvas_id,)).fetchone()
            if existing:
                conn.execute(
                    "UPDATE canvas_briefs SET title=?, payload=?, created_at=?, updated_at=? WHERE id=?",
                    (title, serialized, payload["created_at"], payload["updated_at"], canvas_id),
                )
                conn.commit()
                return canvas_id
        cursor = conn.execute(
            "INSERT INTO canvas_briefs (title, payload, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (title, serialized, payload["created_at"], payload["updated_at"]),
        )
        conn.commit()
        return int(cursor.lastrowid)


def _row_to_contract(row: sqlite3.Row) -> Dict[str, Any]:
    raw = json.loads(row["payload"])
    result = migrate_payload(raw, source_surface="migration")
    contract = result.contract
    contract["_storage_id"] = int(row["id"])
    return contract


def get_canvas(db_path: str, canvas_id: int) -> Dict[str, Any] | None:
    with closing(connect(db_path)) as conn:
        row = conn.execute("SELECT * FROM canvas_briefs WHERE id=?", (canvas_id,)).fetchone()
    return _row_to_contract(row) if row else None


def latest_canvas(db_path: str) -> Dict[str, Any] | None:
    with closing(connect(db_path)) as conn:
        row = conn.execute(
            "SELECT * FROM canvas_briefs ORDER BY updated_at DESC, id DESC LIMIT 1"
        ).fetchone()
    return _row_to_contract(row) if row else None


def list_canvases(db_path: str, limit: int = 12) -> List[Dict[str, Any]]:
    with closing(connect(db_path)) as conn:
        rows = conn.execute(
            "SELECT id, title, payload, created_at, updated_at FROM canvas_briefs ORDER BY updated_at DESC, id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    records: List[Dict[str, Any]] = []
    for row in rows:
        try:
            contract = migrate_payload(json.loads(row["payload"]), source_surface="migration").contract
            records.append({
                "id": int(row["id"]),
                "canvas_id": contract["canvas_id"],
                "schema_version": contract["schema_version"],
                "title": contract["title"],
                "status": contract["status"],
                "created_at": contract["created_at"],
                "updated_at": contract["updated_at"],
            })
        except (ValueError, TypeError, json.JSONDecodeError):
            records.append({
                "id": int(row["id"]),
                "canvas_id": "unreadable",
                "schema_version": "unknown",
                "title": row["title"],
                "status": "draft",
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            })
    return records
