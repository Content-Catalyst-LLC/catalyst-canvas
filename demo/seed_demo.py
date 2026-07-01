#!/usr/bin/env python3
"""Create fresh Catalyst Canvas demo SQLite databases."""

from __future__ import annotations

import csv
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATHS = [ROOT / "catalyst.sqlite3", ROOT / "demo" / "catalyst_seed.sqlite3"]
SAMPLE = {
    "title": "Sample Catalyst Canvas Brief",
    "challenge": "A sustainability team needs to turn broad impact goals into testable work.",
    "audience": "sustainability managers and cross-functional project leads",
    "goal": "create a reviewable experiment plan",
    "constraint": "limited data quality and competing stakeholder expectations",
    "persona_name": "Sustainability Manager",
    "persona_role": "Owner of measurement and reporting workflows",
    "persona_needs": "a clearer way to connect goals, evidence, experiments, and reporting outputs",
    "persona_pains": "fragmented data, unclear ownership, and pressure to communicate before evidence is ready",
    "evidence": "Stakeholder interviews, current reporting artifacts, available indicators, and known data gaps.",
    "assumption": "A lightweight Canvas workflow can reduce ambiguity before heavier analytics work begins.",
    "how_might_we": "How might we help sustainability managers create a reviewable experiment plan while working within limited data quality and competing stakeholder expectations?",
    "point_of_view": "Sustainability Manager needs a clearer way to connect goals, evidence, experiments, and reporting outputs because fragmented data, unclear ownership, and pressure to communicate before evidence is ready.",
    "prototype": "A one-page decision brief with claim, source, assumption, experiment, and review sections.",
    "test_plan": "Run the Canvas with one project team and compare clarity before and after the workshop.",
    "success_signal": "The team can identify one testable next step and one unsupported claim to revise.",
    "risk_note": "Do not convert workshop confidence into proof of impact.",
    "review_note": "Require evidence notes before moving from prototype to public claim.",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_one(path: Path) -> None:
    if path.exists():
        path.unlink()
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE canvas_briefs (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)")
        conn.execute("CREATE TABLE demo_events (id INTEGER PRIMARY KEY AUTOINCREMENT, event_date TEXT NOT NULL, source TEXT NOT NULL, event_name TEXT NOT NULL, persona_hint TEXT, page_path TEXT, count INTEGER NOT NULL DEFAULT 1)")
        timestamp = now()
        sample = dict(SAMPLE, created_at=timestamp, updated_at=timestamp)
        conn.execute("INSERT INTO canvas_briefs (title, payload, created_at, updated_at) VALUES (?, ?, ?, ?)", (sample["title"], json.dumps(sample, indent=2), timestamp, timestamp))
        csv_path = ROOT / "demo" / "ga4_sample.csv"
        if csv_path.exists():
            with csv_path.open(newline="", encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    conn.execute("INSERT INTO demo_events (event_date, source, event_name, persona_hint, page_path, count) VALUES (?, ?, ?, ?, ?, ?)", (row["event_date"], row["source"], row["event_name"], row["persona_hint"], row["page_path"], int(row["count"])))
        conn.commit()


if __name__ == "__main__":
    for db in DB_PATHS:
        init_one(db)
        print(f"seeded {db}")
