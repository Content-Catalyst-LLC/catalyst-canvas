import json
import re
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from catalyst_canvas import CONTRACT_VERSION, __version__
from catalyst_canvas.contract import load_schema
from catalyst_canvas.version import __version__ as package_version
from catalyst_canvas.workspaces import WORKSPACE_SCHEMA_VERSION, load_workspace_schema

ROOT = Path(__file__).resolve().parents[1]


class CatalystCanvasReleaseIntegrityTests(unittest.TestCase):
    def test_version_and_contract_markers_are_synchronized(self):
        manifest = json.loads((ROOT / "canvas_manifest.json").read_text(encoding="utf-8"))
        schema = load_schema()
        workspace_schema = load_workspace_schema()
        plugin = (ROOT / "wordpress" / "catalyst-canvas-demo" / "catalyst-canvas-demo.php").read_text(encoding="utf-8")
        contract_data = (ROOT / "wordpress" / "catalyst-canvas-demo" / "assets" / "catalyst-canvas-contract-data.js").read_text(encoding="utf-8")

        self.assertEqual((ROOT / "VERSION").read_text(encoding="utf-8").strip(), __version__)
        self.assertEqual(package_version, __version__)
        self.assertEqual(manifest["version"], __version__)
        self.assertEqual(manifest["contract_version"], CONTRACT_VERSION)
        self.assertEqual(schema["properties"]["schema_version"]["const"], CONTRACT_VERSION)
        self.assertEqual(schema["$defs"]["provenance"]["properties"]["generator_version"]["const"], __version__)
        self.assertEqual(manifest["workspace_contract_version"], WORKSPACE_SCHEMA_VERSION)
        self.assertEqual(workspace_schema["properties"]["schema_version"]["const"], WORKSPACE_SCHEMA_VERSION)
        self.assertRegex(plugin, rf"Version:\s*{re.escape(__version__)}")
        self.assertIn(f"private const VERSION = '{__version__}';", plugin)
        self.assertIn(f"private const CONTRACT_VERSION = '{CONTRACT_VERSION}';", plugin)
        self.assertIn(f'"releaseVersion":"{__version__}"', contract_data)
        self.assertIn(f'"contractVersion":"{CONTRACT_VERSION}"', contract_data)

    def test_canonical_schema_is_valid(self):
        Draft202012Validator.check_schema(load_schema())
        Draft202012Validator.check_schema(load_workspace_schema())

    def test_runtime_artifacts_are_ignored(self):
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("*.sqlite3", gitignore)
        self.assertIn("dist/", gitignore)
        self.assertIn("outputs/*", gitignore)
        self.assertFalse((ROOT / "outputs" / "catalyst-canvas-demo.zip").exists())

    def test_old_python_surfaces_are_classified_as_adapters(self):
        core = (ROOT / "python" / "catalyst_canvas_core.py").read_text(encoding="utf-8")
        wrapper = (ROOT / "python" / "catalyst_canvas_brief.py").read_text(encoding="utf-8")
        self.assertIn("Deprecated v1.x core adapter", core)
        self.assertIn("Deprecated v1.x compatibility adapter", wrapper)
        self.assertIn("generate_canvas", core)
        self.assertIn("generate_canvas", wrapper)

    def test_shared_fixture_files_exist(self):
        self.assertTrue((ROOT / "fixtures" / "canvas_contract_1_2.input.json").exists())
        self.assertTrue((ROOT / "fixtures" / "canvas_contract_1_2.expected.json").exists())
        self.assertTrue((ROOT / "tests" / "js" / "test_contract_fixture.js").exists())
        self.assertTrue((ROOT / "tests" / "js" / "test_workspace.js").exists())
        self.assertTrue((ROOT / "wordpress" / "catalyst-canvas-demo" / "assets" / "catalyst-canvas-workspace.js").exists())


if __name__ == "__main__":
    unittest.main()
