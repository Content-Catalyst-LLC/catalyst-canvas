import json
import unittest

from catalyst_canvas import generate_canvas
from catalyst_canvas.exporters import export_json, export_markdown, export_print_html


class CanvasExportTests(unittest.TestCase):
    def setUp(self):
        self.contract = generate_canvas({
            "canvas_id": "canvas-export-001",
            "revision_id": "revision-export-001",
            "created_at": "2026-07-16T12:00:00+00:00",
            "updated_at": "2026-07-16T12:00:00+00:00",
            "challenge": "Export a stable Canvas",
            "audience": "Reviewer",
            "goal": "Inspect the same fields",
            "constraint": "Multiple surfaces",
        })

    def test_json_export_is_canonical_and_newline_terminated(self):
        text = export_json(self.contract)
        self.assertTrue(text.endswith("\n"))
        self.assertEqual(json.loads(text)["schema_version"], "catalyst-canvas/1.3")

    def test_markdown_export_contains_contract_identity(self):
        text = export_markdown(self.contract)
        self.assertIn("Contract: catalyst-canvas/1.3", text)
        self.assertIn("Canvas ID: canvas-export-001", text)
        self.assertIn("## Provenance", text)

    def test_print_export_is_standalone_html(self):
        text = export_print_html(self.contract)
        self.assertIn("<!doctype html>", text.lower())
        self.assertIn("canvas-export-001", text)
        self.assertIn("@media print", text)


if __name__ == "__main__":
    unittest.main()
