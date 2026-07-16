from contextlib import closing
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from catalyst_canvas import generate_canvas
from catalyst_canvas.contract import CanvasValidationError
from app.services.storage import get_canvas, init_db, save_canvas


class CanvasStorageTests(unittest.TestCase):
    def test_save_and_read_validate_canonical_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = str(Path(tmp) / "canvas.sqlite3")
            init_db(db)
            contract = generate_canvas({"challenge": "Persist this Canvas"})
            storage_id = save_canvas(db, contract)
            loaded = get_canvas(db, storage_id)
            self.assertEqual(loaded["canvas_id"], contract["canvas_id"])
            self.assertEqual(loaded["schema_version"], "catalyst-canvas/2.0")
            self.assertEqual(loaded["_storage_id"], storage_id)

    def test_save_rejects_invalid_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = str(Path(tmp) / "canvas.sqlite3")
            init_db(db)
            contract = generate_canvas({"challenge": "Invalid before save"})
            contract["constraints"] = []
            with self.assertRaises(CanvasValidationError):
                save_canvas(db, contract)

    def test_read_migrates_legacy_flask_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = str(Path(tmp) / "canvas.sqlite3")
            init_db(db)
            legacy = {
                "title": "Legacy local brief",
                "challenge": "Migrate a local record",
                "audience": "Facilitator",
                "goal": "Keep old data usable",
                "constraint": "Old flat fields",
                "created_at": "2026-07-15T12:00:00+00:00",
                "updated_at": "2026-07-15T12:00:00+00:00",
            }
            with closing(sqlite3.connect(db)) as conn:
                cursor = conn.execute(
                    "INSERT INTO canvas_briefs (title, payload, created_at, updated_at) VALUES (?, ?, ?, ?)",
                    (legacy["title"], json.dumps(legacy), legacy["created_at"], legacy["updated_at"]),
                )
                storage_id = cursor.lastrowid
                conn.commit()
            loaded = get_canvas(db, storage_id)
            self.assertEqual(loaded["schema_version"], "catalyst-canvas/2.0")
            self.assertEqual(loaded["challenge"], "Migrate a local record")
            self.assertEqual(loaded["provenance"]["migrated_from"], "legacy-flask/1.x")


if __name__ == "__main__":
    unittest.main()
