import json
import re
import unittest
from dataclasses import asdict
from pathlib import Path

from jsonschema import Draft202012Validator

from python.catalyst_canvas_core import generate_brief
from python.catalyst_canvas_version import __version__

ROOT = Path(__file__).resolve().parents[1]


class CatalystCanvasReleaseIntegrityTests(unittest.TestCase):
    def test_version_markers_are_synchronized(self):
        manifest = json.loads((ROOT / "canvas_manifest.json").read_text(encoding="utf-8"))
        schema = json.loads(
            (ROOT / "schemas" / "catalyst_canvas_brief.schema.json").read_text(encoding="utf-8")
        )
        plugin = (
            ROOT / "wordpress" / "catalyst-canvas-demo" / "catalyst-canvas-demo.php"
        ).read_text(encoding="utf-8")

        self.assertEqual((ROOT / "VERSION").read_text(encoding="utf-8").strip(), __version__)
        self.assertEqual(manifest["version"], __version__)
        self.assertEqual(schema["properties"]["version"]["const"], __version__)
        self.assertRegex(plugin, rf"Version:\s*{re.escape(__version__)}")
        self.assertIn(f"private const VERSION = '{__version__}';", plugin)

    def test_generated_brief_validates_against_schema(self):
        schema = json.loads(
            (ROOT / "schemas" / "catalyst_canvas_brief.schema.json").read_text(encoding="utf-8")
        )
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        errors = sorted(
            validator.iter_errors(asdict(generate_brief({"challenge": "Validate release"}))),
            key=lambda error: list(error.path),
        )
        self.assertEqual(errors, [])

    def test_runtime_artifacts_are_ignored_and_release_zip_is_absent(self):
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("*.sqlite3", gitignore)
        self.assertIn("dist/", gitignore)
        self.assertIn("outputs/*", gitignore)
        self.assertFalse((ROOT / "outputs" / "catalyst-canvas-demo.zip").exists())

    def test_legacy_engine_is_classified_as_compatibility_adapter(self):
        source = (ROOT / "python" / "catalyst_canvas_brief.py").read_text(encoding="utf-8")
        self.assertIn("Deprecated v1.x compatibility adapter", source)
        self.assertIn("generate_brief", source)


if __name__ == "__main__":
    unittest.main()
