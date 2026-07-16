#!/usr/bin/env python3
"""Create fresh Catalyst Canvas demo databases using Canvas Contract 1.0."""

from __future__ import annotations

from contextlib import closing

import argparse
import csv
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from catalyst_canvas.adapters.flask import default_contract
from app.services.storage import init_db, save_canvas

DEFAULT_DATABASES = [ROOT / "catalyst.sqlite3", ROOT / "demo" / "catalyst_seed.sqlite3"]


def seed(path: Path) -> None:
    if path.exists():
        path.unlink()
    path.parent.mkdir(parents=True, exist_ok=True)
    init_db(str(path))
    save_canvas(str(path), default_contract())

    csv_path = ROOT / "demo" / "ga4_sample.csv"
    if csv_path.exists():
        with closing(sqlite3.connect(path)) as conn, csv_path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                conn.execute(
                    "INSERT INTO demo_events (event_date, source, event_name, persona_hint, page_path, count) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        row["event_date"],
                        row["source"],
                        row["event_name"],
                        row["persona_hint"],
                        row["page_path"],
                        int(row["count"]),
                    ),
                )
            conn.commit()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--database",
        action="append",
        type=Path,
        help="Database path to replace. Repeat for multiple databases; defaults to the two local demo paths.",
    )
    args = parser.parse_args()
    paths = [path.resolve() for path in args.database] if args.database else DEFAULT_DATABASES
    for path in paths:
        seed(path)
        print(f"seeded {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
