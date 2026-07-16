import copy
import json
import tempfile
import unittest
from pathlib import Path

from app import create_app
from app.services.storage import create_project, init_db, list_research_assets, research_asset_counts
from catalyst_canvas.engine import generate_canvas
from catalyst_canvas.experiments import build_experiment_handoff_package
from catalyst_canvas.migrations import migrate_payload

ROOT = Path(__file__).resolve().parents[1]


class ExperimentContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads((ROOT / "fixtures" / "canvas_contract_1_5.input.json").read_text(encoding="utf-8"))
        cls.contract = generate_canvas(cls.source, source_surface="python")

    def test_contract_normalizes_prototypes_hypotheses_and_experiment_plans(self):
        prototype = self.contract["prototypes"][0]
        hypothesis = self.contract["hypotheses"][0]
        plan = self.contract["experiment_plans"][0]
        self.assertEqual(self.contract["schema_version"], "catalyst-canvas/1.5")
        self.assertEqual(prototype["prototype_type"], "paper")
        self.assertEqual(prototype["version"], "0.2")
        self.assertEqual(hypothesis["status"], "partially_supported")
        self.assertIn(prototype["prototype_id"], hypothesis["prototype_ids"])
        self.assertEqual(plan["participant_plan"]["target_count"], 5)
        self.assertEqual(len(plan["metrics"]), 2)
        self.assertTrue(plan["safeguards"]["stop_conditions"])

    def test_completed_run_and_learning_decision_create_learning_recorded_state(self):
        summary = self.contract["experiment_summary"]
        self.assertEqual(summary["readiness"], "learning_recorded")
        self.assertEqual(summary["completed_run_count"], 1)
        self.assertEqual(summary["learning_decision_count"], 1)
        self.assertEqual(summary["iteration_count"], 1)
        run = self.contract["experiment_runs"][0]
        self.assertEqual(run["result_state"], "partially_supported")
        self.assertTrue(run["metric_results"][0]["met_threshold"])
        self.assertFalse(run["metric_results"][1]["met_threshold"])

    def test_missing_metrics_and_safeguards_remain_visible(self):
        source = copy.deepcopy(self.source)
        source["experiment_plans"][0]["metrics"] = []
        source["experiment_plans"][0]["safeguards"] = {}
        source["experiment_plans"][0]["status"] = "planned"
        source["experiment_runs"] = []
        source["learning_decisions"] = []
        contract = generate_canvas(source, source_surface="python")
        self.assertEqual(contract["experiment_summary"]["readiness"], "planning")
        self.assertEqual(contract["experiment_summary"]["missing_metric_count"], 1)
        self.assertEqual(contract["experiment_summary"]["missing_safeguard_count"], 1)

    def test_contract_1_4_migrates_to_contract_1_5(self):
        legacy = json.loads((ROOT / "fixtures" / "canvas_contract_1_4.expected.json").read_text(encoding="utf-8"))
        result = migrate_payload(legacy)
        self.assertEqual(result.migrated_from, "catalyst-canvas/1.4")
        self.assertEqual(result.contract["schema_version"], "catalyst-canvas/1.5")
        self.assertIn("experiment_plans", result.contract)
        self.assertIn("experiment_summary", result.contract)
        self.assertIn("experiment fields", result.warnings[0])

    def test_research_lab_and_workbench_handoffs_preserve_execution_context(self):
        lab = build_experiment_handoff_package(self.contract, "research_lab")
        workbench = build_experiment_handoff_package(self.contract, "workbench")
        self.assertEqual(lab["handoff_contract"], "catalyst-canvas-experiment-handoff/1.0")
        self.assertEqual(lab["target"], "research_lab")
        self.assertEqual(lab["experiment_context"]["experiment_plans"][0]["experiment_id"], "experiment-001")
        self.assertEqual(lab["research_execution"]["participant_plans"][0]["target_count"], 5)
        self.assertIn("dataset://heat-brief-clarity-pilot", lab["research_execution"]["dataset_refs"])
        self.assertEqual(workbench["target"], "workbench")
        self.assertEqual(len(workbench["technical_validation"]["metric_definitions"]), 2)
        self.assertTrue(workbench["technical_validation"]["modeling_questions"])
        self.assertIn("artifact://heat-action-brief/v0.2", workbench["technical_validation"]["prototype_artifacts"])


class ExperimentStorageTests(unittest.TestCase):
    def test_workspace_indexes_experiment_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = str(Path(tmp) / "experiments.sqlite3")
            init_db(db)
            contract = json.loads((ROOT / "fixtures" / "canvas_contract_1_5.expected.json").read_text(encoding="utf-8"))
            create_project(db, contract, title="Experiment project")
            counts = research_asset_counts(db)
            for asset_type in ("prototype", "hypothesis", "experiment_plan", "experiment_run", "learning_decision", "iteration"):
                self.assertEqual(counts[asset_type], 1)
                assets = list_research_assets(db, asset_type=asset_type)
                self.assertEqual(len(assets), 1)


class ExperimentRouteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / "experiment-routes.sqlite3")
        self.app = create_app({"TESTING": True, "SECRET_KEY": "test-secret", "CANVAS_DB": self.db})
        self.client = self.app.test_client()
        contract = json.loads((ROOT / "fixtures" / "canvas_contract_1_5.expected.json").read_text(encoding="utf-8"))
        response = self.client.post("/api/canvas/import", json=contract)
        self.assertEqual(response.status_code, 201)
        self.project_id = response.get_json()["project_id"]

    def tearDown(self):
        self.tmp.cleanup()

    def test_experiment_api_run_creation_and_handoff_endpoints(self):
        payload = self.client.get("/api/experiments")
        self.assertEqual(payload.status_code, 200)
        self.assertEqual(payload.get_json()["experiment_summary"]["readiness"], "learning_recorded")

        created = self.client.post("/api/experiments/runs", json={
            "run_id": "experiment-run-002",
            "experiment_id": "experiment-001",
            "prototype_ids": ["prototype-001"],
            "status": "complete",
            "participant_count": 2,
            "result_state": "inconclusive",
            "summary": "A small follow-up run produced mixed results.",
            "metric_results": [],
        })
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.get_json()["run"]["run_id"], "experiment-run-002")

        lab = self.client.get(f"/projects/{self.project_id}/experiment-handoff/research_lab.json")
        self.assertEqual(lab.status_code, 200)
        self.assertEqual(lab.get_json()["target"], "research_lab")
        workbench = self.client.get(f"/projects/{self.project_id}/experiment-handoff/workbench.json")
        self.assertEqual(workbench.status_code, 200)
        self.assertIn("technical_validation", workbench.get_json())
        invalid = self.client.get(f"/projects/{self.project_id}/experiment-handoff/unknown.json")
        self.assertEqual(invalid.status_code, 404)

        missing = self.client.post("/api/experiments/runs", json={"summary": "Missing experiment"})
        self.assertEqual(missing.status_code, 400)


if __name__ == "__main__":
    unittest.main()
