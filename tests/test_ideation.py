import json
import tempfile
import unittest
from pathlib import Path

from app import create_app
from catalyst_canvas import generate_canvas
from catalyst_canvas.frameworks import export_framework_package, framework_record, import_framework_package
from catalyst_canvas.ideation import merge_idea_records
from catalyst_canvas.migrations import migrate_payload

ROOT = Path(__file__).resolve().parents[1]


class FrameworkRegistryTests(unittest.TestCase):
    def test_all_planned_framework_packs_are_available(self):
        keys = {"AIDA", "JTBD", "ValueProposition", "MessageHouse", "SWOT", "PESTLE", "FiveWOneH", "HeroGuide", "AssumptionMatrix", "ImpactEffort"}
        registry = json.loads((ROOT / "contracts" / "frameworks.json").read_text())
        self.assertTrue(keys.issubset(registry))
        for key in keys:
            record = framework_record(key)
            self.assertTrue(record["description"])
            self.assertTrue(record["intended_uses"])
            self.assertTrue(record["limitations"])
            self.assertTrue(record["required_inputs"])
            self.assertTrue(record["output_types"])
            self.assertTrue(record["prompts"])

    def test_custom_framework_round_trip_requires_no_code_change(self):
        custom = [{
            "key": "InstitutionalReview", "name": "Institutional Review", "category": "governance",
            "description": "Review authority and accountability.", "intended_uses": ["Governance review"],
            "limitations": ["Requires legal and operational review"], "required_inputs": ["Decision scope"],
            "output_types": ["review_questions"], "mode_support": ["convergent"],
            "prompts": [{"label": "Authority", "question": "Who has authority?", "purpose": "Clarify decision rights.", "output_type": "review_question"}],
            "organization": "Example Institution", "created_by": "Design lead", "tags": ["governance"]
        }]
        package = export_framework_package(custom, organization="Example Institution")
        imported = import_framework_package(package)
        self.assertEqual(imported[0]["key"], "InstitutionalReview")
        self.assertEqual(framework_record("InstitutionalReview", imported)["origin"], "custom")


class IdeationContractTests(unittest.TestCase):
    def test_idea_lineage_clustering_votes_and_summary(self):
        contract = generate_canvas({
            "framework": "ImpactEffort",
            "how_might_we": [{"hmw_id": "hmw-priority", "question": "How might we test the smallest useful change?", "status": "selected"}],
            "prototypes": [{"prototype_id": "prototype-001", "title": "Pilot card", "description": "A small pilot.", "status": "planned"}],
            "ideation_sessions": [{"session_id": "session-001", "title": "Workshop", "mode": "convergent", "framework_key": "ImpactEffort", "challenge_ids": ["challenge-primary"], "hmw_ids": ["hmw-priority"]}],
            "idea_clusters": [{"cluster_id": "cluster-001", "name": "Quick tests", "idea_ids": [], "sequence": 1}],
            "ideas": [{
                "idea_id": "idea-001", "title": "Pilot card", "session_id": "session-001", "challenge_id": "challenge-primary",
                "hmw_id": "hmw-priority", "prompt_id": "prompt-001", "author": "Facilitator", "rationale": "Small, reversible test.",
                "cluster_id": "cluster-001", "status": "selected", "vote_count": 4, "voter_ids": ["a", "b", "c", "d"],
                "prototype_ids": ["prototype-001"]
            }]
        })
        idea = contract["ideas"][0]
        self.assertEqual(idea["challenge_id"], contract["challenge_id"])
        self.assertEqual(idea["hmw_id"], "hmw-priority")
        self.assertEqual(idea["prototype_ids"], ["prototype-001"])
        self.assertIn("idea-001", contract["idea_clusters"][0]["idea_ids"])
        self.assertEqual(contract["ideation_summary"]["vote_count"], 4)
        self.assertEqual(contract["ideation_summary"]["selected_count"], 1)
        self.assertEqual(contract["ideation_summary"]["orphaned_lineage_count"], 0)

    def test_merge_preserves_parent_lineage(self):
        ideas = [
            {"idea_id": "idea-a", "title": "A", "status": "captured"},
            {"idea_id": "idea-b", "title": "B", "status": "captured"},
        ]
        merged = merge_idea_records(ideas, ["idea-a", "idea-b"], {"idea_id": "idea-c", "title": "Combined", "author": "Team", "rationale": "Combines compatible concepts."})
        self.assertEqual(merged[0]["merged_into_id"], "idea-c")
        self.assertEqual(merged[1]["status"], "merged")
        self.assertEqual(merged[-1]["parent_idea_ids"], ["idea-a", "idea-b"])

    def test_contract_1_2_migrates_to_1_3(self):
        payload = json.loads((ROOT / "fixtures" / "canvas_contract_1_2.expected.json").read_text())
        result = migrate_payload(payload)
        self.assertEqual(result.migrated_from, "catalyst-canvas/1.2")
        self.assertEqual(result.contract["schema_version"], "catalyst-canvas/1.5")
        self.assertIn("ideation_summary", result.contract)


class IdeationRouteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "test-secret", "CANVAS_DB": str(Path(self.tmp.name) / "ideation.sqlite3")})
        self.client = self.app.test_client()
        self.client.post("/projects", data={"title": "Ideation Project"})
        self.project_id = self.client.get("/api/projects").get_json()["projects"][0]["project_id"]

    def tearDown(self):
        self.tmp.cleanup()

    def test_ideation_form_saves_traceable_ideas(self):
        response = self.client.post("/ideate", data={
            "framework": "SWOT", "ideation_session_title": "Opportunity workshop", "ideation_mode": "divergent",
            "ideation_facilitator": "Design lead", "ideation_participants": "Research lead\nProgram lead",
            "idea_lines": "Shared evidence card | Keep gaps visible | Research lead | Reduces false certainty | hmw-001 | prompt-003 | evidence,brief | idea-cluster-001 | selected | 2 | prototype-001 | assumption-001 | evidence-001 |  | ",
            "cluster_lines": "Evidence transparency | Concepts that preserve limitations | idea-001 | evidence | Keeps gaps visible | 1",
        })
        self.assertEqual(response.status_code, 302)
        canvas = self.client.get(f"/api/projects/{self.project_id}").get_json()["canvas"]
        self.assertEqual(canvas["framework"]["key"], "SWOT")
        self.assertEqual(canvas["ideas"][0]["author"], "Research lead")
        self.assertEqual(canvas["ideas"][0]["rationale"], "Reduces false certainty")
        self.assertEqual(canvas["ideation_summary"]["idea_count"], 1)

    def test_framework_api_and_package_import(self):
        registry = self.client.get("/api/frameworks").get_json()
        self.assertGreaterEqual(len(registry["frameworks"]), 10)
        package = {
            "package_contract": "catalyst-canvas-framework-package/1.0",
            "organization": "Example",
            "frameworks": [{"key": "CustomOne", "name": "Custom One", "prompts": [{"label": "Prompt", "question": "What matters?"}]}],
        }
        response = self.client.post("/api/frameworks/import", json=package)
        self.assertEqual(response.status_code, 200)
        self.assertIn("CustomOne", response.get_json()["imported"])


if __name__ == "__main__":
    unittest.main()
