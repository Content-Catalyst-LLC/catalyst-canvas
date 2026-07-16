import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import create_app


class CatalystCanvasAppConfigTests(unittest.TestCase):
    def test_production_requires_secret(self):
        with patch.dict(os.environ, {"CATALYST_CANVAS_ENV": "production"}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "CATALYST_CANVAS_SECRET"):
                create_app()

    def test_local_test_app_uses_explicit_database(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.sqlite3"
            with patch.dict(os.environ, {"CATALYST_CANVAS_ENV": "test"}, clear=True):
                app = create_app({
                    "TESTING": True,
                    "SECRET_KEY": "test-secret",
                    "CANVAS_DB": str(db_path),
                })
            self.assertTrue(app.config["TESTING"])
            self.assertEqual(app.config["CATALYST_CANVAS_ENV"], "test")
            self.assertTrue(db_path.exists())

    def test_import_api_migrates_legacy_payload(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.sqlite3"
            with patch.dict(os.environ, {"CATALYST_CANVAS_ENV": "test"}, clear=True):
                app = create_app({"TESTING": True, "SECRET_KEY": "test", "CANVAS_DB": str(db_path)})
            response = app.test_client().post("/api/canvas/import", json={
                "title": "Imported legacy Canvas",
                "challenge": "Import old data",
                "audience": "Maintainer",
                "goal": "Create a canonical record",
                "constraint": "Flat fields",
            })
            self.assertEqual(response.status_code, 201)
            payload = response.get_json()
            self.assertEqual(payload["schema_version"], "catalyst-canvas/1.5")
            self.assertEqual(payload["migrated_from"], "legacy-flask/1.x")

    def test_import_api_rejects_unknown_payload(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.sqlite3"
            with patch.dict(os.environ, {"CATALYST_CANVAS_ENV": "test"}, clear=True):
                app = create_app({"TESTING": True, "SECRET_KEY": "test", "CANVAS_DB": str(db_path)})
            response = app.test_client().post("/api/canvas/import", data=json.dumps({"bad": True}), content_type="application/json")
            self.assertEqual(response.status_code, 422)
            self.assertIn("Unable to identify", response.get_json()["error"])


if __name__ == "__main__":
    unittest.main()
