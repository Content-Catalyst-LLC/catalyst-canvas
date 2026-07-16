import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import create_app


class CatalystCanvasAppConfigTests(unittest.TestCase):
    def test_production_requires_secret(self):
        with patch.dict(
            os.environ,
            {"CATALYST_CANVAS_ENV": "production"},
            clear=True,
        ):
            with self.assertRaisesRegex(RuntimeError, "CATALYST_CANVAS_SECRET"):
                create_app()

    def test_local_test_app_uses_explicit_database(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.sqlite3"
            with patch.dict(
                os.environ,
                {"CATALYST_CANVAS_ENV": "test"},
                clear=True,
            ):
                app = create_app({
                    "TESTING": True,
                    "SECRET_KEY": "test-secret",
                    "CANVAS_DB": str(db_path),
                })
            self.assertTrue(app.config["TESTING"])
            self.assertEqual(app.config["CATALYST_CANVAS_ENV"], "test")
            self.assertTrue(db_path.exists())


if __name__ == "__main__":
    unittest.main()
