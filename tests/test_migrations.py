import json
import unittest

from catalyst_canvas import generate_canvas

from catalyst_canvas import CONTRACT_VERSION
from catalyst_canvas.migrations import UnsupportedContractVersion, migrate_payload


class CanvasMigrationTests(unittest.TestCase):
    def test_migrates_legacy_core_export(self):
        legacy = {
            "version": "1.1.1",
            "generated_at": "2026-07-16T10:00:00+00:00",
            "challenge": "Legacy challenge",
            "audience": "Legacy audience",
            "goal": "Create a test",
            "constraint": "Limited evidence",
            "framework": "AIDA",
            "persona": {"name": "Legacy user", "description": "Legacy description"},
            "point_of_view": "Legacy POV",
            "how_might_we": ["How might we migrate safely?"],
            "prototype": {"title": "Legacy prototype", "description": "Legacy concept"},
            "test_plan": {"signal": "Signal", "method": "Method", "learning_goal": "Learn"},
            "assumptions": ["Legacy assumption"],
            "review_questions": ["What changed?"],
        }
        result = migrate_payload(legacy)
        self.assertEqual(result.contract["schema_version"], CONTRACT_VERSION)
        self.assertEqual(result.contract["challenge"], "Legacy challenge")
        self.assertEqual(result.migrated_from, "legacy-core/1.1.1")
        self.assertIn("Migrated", result.warnings[0])

    def test_migrates_legacy_wrapper_export(self):
        legacy = {
            "generated_at": "2026-07-16T10:00:00+00:00",
            "tool": "Catalyst Canvas Demo",
            "version": "1.1.0",
            "inputs": {
                "challenge": "Wrapper challenge",
                "audience": "Founder",
                "goal": "Prioritize experiments",
                "constraint": "Limited time",
                "framework": "JTBD",
            },
            "canvas": {
                "title": "Legacy wrapper",
                "persona_name": "Founder",
                "persona_body": "Needs clarity",
                "pov": "Founder needs clarity.",
                "hmw": ["How might we prioritize?"],
                "prototype_title": "Decision card",
                "prototype_body": "One card",
                "test_plan": {
                    "what_to_test": "Priority clarity",
                    "signal_to_watch": "Agreement",
                    "risk": "False consensus",
                    "next_iteration": "Review",
                },
            },
        }
        result = migrate_payload(legacy)
        self.assertEqual(result.contract["title"], "Legacy wrapper")
        self.assertEqual(result.contract["framework"]["key"], "JTBD")
        self.assertEqual(result.contract["provenance"]["migrated_from"], "legacy-wrapper/1.1.0")

    def test_future_contract_is_rejected_with_supported_version(self):
        with self.assertRaisesRegex(UnsupportedContractVersion, "catalyst-canvas/2.0"):
            migrate_payload({"schema_version": "catalyst-canvas/9.0"})

    def test_unknown_payload_is_rejected_with_expected_shape(self):
        with self.assertRaisesRegex(UnsupportedContractVersion, "challenge"):
            migrate_payload({"unrelated": True})


if __name__ == "__main__":
    unittest.main()

class ContractOneMigrationTests(unittest.TestCase):
    def test_contract_1_0_migrates_to_current_contract(self):
        current = generate_canvas({"challenge": "Upgrade a contract"})
        legacy = json.loads(json.dumps(current))
        legacy["schema_version"] = "catalyst-canvas/1.0"
        legacy.pop("journeys", None)
        legacy.pop("research_summary", None)
        for persona in legacy["personas"]:
            for key in ["context", "goals", "behaviors", "accessibility_needs", "preferred_channels", "quotes", "evidence_ids", "assumption_ids", "tags", "validation_status"]:
                persona.pop(key, None)
        for stakeholder in legacy["stakeholders"]:
            for key in ["stakeholder_type", "stance", "decision_role", "engagement_strategy", "evidence_ids", "dependencies", "tags"]:
                stakeholder.pop(key, None)
        result = migrate_payload(legacy)
        self.assertEqual(result.contract["schema_version"], "catalyst-canvas/2.0")
        self.assertEqual(result.migrated_from, "catalyst-canvas/1.0")
        self.assertIn("collaboration, publication, interoperability, and platform exchange fields", result.warnings[0])
        self.assertEqual(result.contract["personas"][0]["validation_status"], "hypothesis")
