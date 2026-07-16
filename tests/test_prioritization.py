import copy
import json
import unittest
import tempfile
from pathlib import Path

from app import create_app
from catalyst_canvas.engine import generate_canvas
from catalyst_canvas.migrations import migrate_payload
from catalyst_canvas.prioritization import (
    build_decision_handoff_package,
    normalize_sensitivity_views,
)

ROOT = Path(__file__).resolve().parents[1]


class PrioritizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads((ROOT / "fixtures/canvas_contract_1_5.input.json").read_text(encoding="utf-8"))
        cls.contract = generate_canvas(cls.source, source_surface="python")

    def test_score_inputs_preserve_basis_confidence_rationale_and_links(self):
        option = self.contract["decision_options"][0]
        for model_name in ("ice", "rice"):
            model = option[model_name]
            self.assertGreater(model["score"], 0)
            for score_input in model["inputs"]:
                self.assertIn(score_input["basis"], {"measured", "estimate", "opinion", "unknown"})
                self.assertIn(score_input["confidence"], {"low", "medium", "high", "unknown"})
                self.assertTrue(score_input["rationale"])
        for score in option["criterion_scores"]:
            self.assertTrue(score["rationale"])
            self.assertNotEqual(score["basis"], "unknown")
            self.assertNotEqual(score["confidence"], "unknown")

    def test_weight_changes_recalculate_rank_without_mutating_raw_values(self):
        options = copy.deepcopy(self.contract["decision_options"])
        raw_before = {
            option["option_id"]: [score["raw_value"] for score in option["criterion_scores"]]
            for option in options
        }
        views = normalize_sensitivity_views(
            [{
                "name": "Delivery constraint",
                "weight_overrides": [
                    {"criterion_id": "criterion-feasibility", "weight": 40},
                    {"criterion_id": "criterion-resource-efficiency", "weight": 35},
                    {"criterion_id": "criterion-impact", "weight": 10},
                ],
            }],
            options=options,
            criteria=self.contract["decision_criteria"],
            generated_at=self.contract["updated_at"],
        )
        baseline_order = [item["option_id"] for item in views[0]["rankings"]]
        scenario_order = [item["option_id"] for item in views[1]["rankings"]]
        self.assertNotEqual(baseline_order, scenario_order)
        raw_after = {
            option["option_id"]: [score["raw_value"] for score in option["criterion_scores"]]
            for option in options
        }
        self.assertEqual(raw_before, raw_after)

    def test_failed_ethical_gate_blocks_readiness(self):
        source = copy.deepcopy(self.source)
        source["decision_options"][0]["gate_results"] = [{
            "criterion_id": "criterion-equity-and-harm",
            "result": "fail",
            "rationale": "The option excludes a high-risk affected group.",
            "evidence_ids": ["evidence-001"],
        }]
        contract = generate_canvas(source, source_surface="python")
        self.assertEqual(contract["prioritization_summary"]["readiness"], "blocked_by_gate")
        self.assertEqual(contract["prioritization_summary"]["failed_gate_count"], 1)

    def test_handoffs_preserve_decision_context(self):
        for target in ("decision_studio", "workbench"):
            package = build_decision_handoff_package(self.contract, target)
            self.assertEqual(package["handoff_contract"], "catalyst-canvas-decision-handoff/1.0")
            self.assertEqual(package["target"], target)
            context = package["decision_context"]
            self.assertGreaterEqual(len(context["alternatives"]), 1)
            self.assertGreaterEqual(len(context["criteria"]), 1)
            self.assertGreaterEqual(len(context["assumptions"]), 1)
            self.assertGreaterEqual(len(context["evidence"]), 1)
            self.assertGreaterEqual(len(context["unresolved_questions"]), 1)
        self.assertIn("technical_validation", build_decision_handoff_package(self.contract, "workbench"))
        self.assertIn("governance", build_decision_handoff_package(self.contract, "decision_studio"))

    def test_contract_1_3_migrates_to_1_4(self):
        legacy = copy.deepcopy(self.contract)
        legacy["schema_version"] = "catalyst-canvas/1.3"
        for key in ["decision_criteria", "decision_options", "sensitivity_views", "decision_notes", "decision_handoffs", "prioritization_summary"]:
            legacy.pop(key, None)
        result = migrate_payload(legacy)
        self.assertEqual(result.contract["schema_version"], "catalyst-canvas/1.5")
        self.assertEqual(result.migrated_from, "catalyst-canvas/1.3")
        self.assertIn("prioritization", result.warnings[0])


class PrioritizationRouteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "test-secret", "CANVAS_DB": str(Path(self.tmp.name) / "prioritization.sqlite3")})
        self.client = self.app.test_client()
        source = json.loads((ROOT / "fixtures/canvas_contract_1_5.expected.json").read_text(encoding="utf-8"))
        response = self.client.post("/api/canvas/import", json=source)
        self.assertEqual(response.status_code, 201)
        self.project_id = response.get_json()["project_id"]

    def tearDown(self):
        self.tmp.cleanup()

    def test_prioritization_api_and_sensitivity_preview(self):
        response = self.client.get("/api/prioritization")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(len(payload["decision_options"]), 3)
        preview = self.client.post("/api/prioritization/sensitivity", json={
            "name": "Feasibility emphasis",
            "weight_overrides": [{"criterion_id": "criterion-feasibility", "weight": 50}],
        })
        self.assertEqual(preview.status_code, 200)
        preview_payload = preview.get_json()
        self.assertEqual(preview_payload["scenario"]["name"], "Feasibility emphasis")
        self.assertEqual(len(preview_payload["scenario"]["rankings"]), 3)

    def test_decision_handoff_endpoints_are_workspace_scoped(self):
        decision = self.client.get(f"/projects/{self.project_id}/decision-handoff/decision_studio.json")
        self.assertEqual(decision.status_code, 200)
        self.assertEqual(decision.get_json()["target"], "decision_studio")
        workbench = self.client.get(f"/projects/{self.project_id}/decision-handoff/workbench.json")
        self.assertEqual(workbench.status_code, 200)
        self.assertIn("technical_validation", workbench.get_json())
        invalid = self.client.get(f"/projects/{self.project_id}/decision-handoff/unknown.json")
        self.assertEqual(invalid.status_code, 404)


if __name__ == "__main__":
    unittest.main()
