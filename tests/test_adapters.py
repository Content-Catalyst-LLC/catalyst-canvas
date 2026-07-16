import json
import unittest
from pathlib import Path

from catalyst_canvas.adapters.flask import compact_to_contract, contract_to_form, form_to_contract

ROOT = Path(__file__).resolve().parents[1]


class CanvasAdapterTests(unittest.TestCase):
    def test_flask_adapter_matches_shared_fixture(self):
        source = json.loads((ROOT / "fixtures" / "canvas_contract_1_2.input.json").read_text(encoding="utf-8"))
        expected = json.loads((ROOT / "fixtures" / "canvas_contract_1_2.expected.json").read_text(encoding="utf-8"))
        self.assertEqual(compact_to_contract(source), expected)

    def test_form_update_preserves_canvas_and_changes_revision(self):
        original = compact_to_contract({
            "challenge": "Original challenge",
            "audience": "Program lead",
            "goal": "Choose an experiment",
            "constraint": "Limited time",
        })
        updated = form_to_contract({
            "challenge": "Updated challenge",
            "persona_name": "Delivery lead",
            "framework": "Matrix",
        }, original)
        self.assertEqual(updated["canvas_id"], original["canvas_id"])
        self.assertNotEqual(updated["revision_id"], original["revision_id"])
        self.assertEqual(updated["challenge"], "Updated challenge")
        self.assertEqual(updated["personas"][0]["name"], "Delivery lead")
        self.assertEqual(updated["framework"]["key"], "Matrix")

    def test_contract_to_form_exposes_legacy_template_fields(self):
        contract = compact_to_contract({
            "challenge": "Template challenge",
            "audience": "Reviewer",
            "goal": "Review",
            "constraint": "Time",
        })
        form = contract_to_form(contract, storage_id=8)
        self.assertEqual(form["id"], 8)
        self.assertEqual(form["challenge"], "Template challenge")
        self.assertEqual(form["audience"], "Reviewer")
        self.assertEqual(form["schema_version"], "catalyst-canvas/1.2")


if __name__ == "__main__":
    unittest.main()
