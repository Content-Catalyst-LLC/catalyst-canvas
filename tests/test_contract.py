import json
import unittest
from pathlib import Path

from catalyst_canvas import CONTRACT_VERSION, generate_canvas
from catalyst_canvas.contract import CanvasValidationError, validate_contract

ROOT = Path(__file__).resolve().parents[1]


class CanvasContractTests(unittest.TestCase):
    def test_generation_returns_valid_contract(self):
        contract = generate_canvas({
            "challenge": "Improve impact reporting",
            "audience": "Program director",
            "goal": "Create a reviewable brief",
            "constraint": "Limited data",
            "framework": "JTBD",
        })
        self.assertEqual(contract["schema_version"], CONTRACT_VERSION)
        self.assertEqual(contract["framework"]["key"], "JTBD")
        self.assertTrue(contract["canvas_id"].startswith("canvas-"))
        self.assertTrue(contract["revision_id"].startswith("revision-"))
        self.assertEqual(validate_contract(contract), contract)

    def test_python_engine_matches_shared_fixture(self):
        source = json.loads((ROOT / "fixtures" / "canvas_contract_1_6.input.json").read_text(encoding="utf-8"))
        expected = json.loads((ROOT / "fixtures" / "canvas_contract_1_6.expected.json").read_text(encoding="utf-8"))
        self.assertEqual(generate_canvas(source, source_surface="python"), expected)

    def test_unknown_framework_falls_back_to_aida(self):
        contract = generate_canvas({"framework": "Unknown"})
        self.assertEqual(contract["framework"]["key"], "AIDA")

    def test_invalid_contract_has_useful_path(self):
        contract = generate_canvas({"challenge": "Test validation"})
        contract["personas"] = []
        with self.assertRaisesRegex(CanvasValidationError, "personas"):
            validate_contract(contract)


if __name__ == "__main__":
    unittest.main()

class ResearchContractTests(unittest.TestCase):
    def test_research_records_are_normalized_and_summarized(self):
        contract = generate_canvas({
            "challenge": "Coordinate a community pilot",
            "audience": "Program lead",
            "goal": "Reach a reviewable decision",
            "constraint": "Uneven evidence",
            "persona": {
                "name": "Program Lead",
                "goals": ["Align partners"],
                "behaviors": ["Reviews evidence before workshops"],
                "evidence_ids": ["evidence-001"],
                "validation_status": "researching",
                "confidence": "medium",
            },
            "stakeholders": [{
                "name": "Funding sponsor", "influence": "high", "interest": "medium",
                "stance": "supportive", "decision_role": "approver",
            }],
            "journeys": [{
                "title": "Pilot decision journey",
                "stages": [{"name": "Review", "emotion": -9}, {"name": "Commit", "emotion": 8}],
            }],
        })
        self.assertEqual(contract["schema_version"], "catalyst-canvas/1.6")
        self.assertEqual(contract["stakeholders"][0]["influence"], 5)
        self.assertEqual(contract["stakeholders"][0]["interest"], 3)
        self.assertEqual(contract["journeys"][0]["stages"][0]["emotion"], -2)
        self.assertEqual(contract["journeys"][0]["stages"][1]["emotion"], 2)
        self.assertEqual(contract["research_summary"]["journey_count"], 1)
        self.assertEqual(contract["research_summary"]["evidence_link_count"], 1)
        self.assertEqual(contract["research_summary"]["readiness"], "review_ready")
