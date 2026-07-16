"""SQLite persistence for the local Catalyst Canvas Flask demo."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def save_canvas(db_path: str, canvas: Dict[str, Any], canvas_id: int | None = None) -> int:
    created_at = canvas.get("created_at") or now()
    updated_at = now()
    canvas["created_at"] = created_at
    canvas["updated_at"] = updated_at
    payload = json.dumps(canvas, ensure_ascii=False, indent=2)
    title = canvas.get("title") or "Untitled Catalyst Canvas Brief"
    with closing(connect(db_path)) as conn:
        if canvas_id:
            conn.execute(
                "UPDATE canvas_briefs SET title=?, payload=?, updated_at=? WHERE id=?",
                (title, payload, updated_at, canvas_id),
            )
            existing = conn.execute("SELECT id FROM canvas_briefs WHERE id=?", (canvas_id,)).fetchone()
            if existing:
                conn.commit()
                return canvas_id
        cur = conn.execute(
            "INSERT INTO canvas_briefs (title, payload, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (title, payload, created_at, updated_at),
        )
        conn.commit()
        return int(cur.lastrowid)


def get_canvas(db_path: str, canvas_id: int) -> Dict[str, Any] | None:
    with closing(connect(db_path)) as conn:
        row = conn.execute("SELECT * FROM canvas_briefs WHERE id=?", (canvas_id,)).fetchone()
    if not row:
        return None
    data = json.loads(row["payload"])
    data["id"] = row["id"]
    return data


def latest_canvas(db_path: str) -> Dict[str, Any] | None:
    with closing(connect(db_path)) as conn:
        row = conn.execute("SELECT * FROM canvas_briefs ORDER BY updated_at DESC, id DESC LIMIT 1").fetchone()
    if not row:
        return None
    data = json.loads(row["payload"])
    data["id"] = row["id"]
    return data


def list_canvases(db_path: str, limit: int = 12) -> List[Dict[str, Any]]:
    with closing(connect(db_path)) as conn:
        rows = conn.execute(
            "SELECT id, title, created_at, updated_at FROM canvas_briefs ORDER BY updated_at DESC, id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]
