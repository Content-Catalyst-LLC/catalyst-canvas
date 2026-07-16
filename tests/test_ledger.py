import json
import tempfile
import unittest
from pathlib import Path

from app import create_app
from app.services.storage import list_research_assets
from catalyst_canvas import generate_canvas
from catalyst_canvas.exporters import export_markdown
from catalyst_canvas.ledger import build_handoff_package
from catalyst_canvas.migrations import migrate_payload


class LedgerContractTests(unittest.TestCase):
    def test_claim_states_and_coverage_are_descriptive(self):
        contract = generate_canvas({
            "sources": [{"source_id": "source-001", "source_type": "interview", "title": "Interview"}],
            "evidence": [{"evidence_id": "evidence-001", "source_id": "source-001", "title": "Excerpt", "summary": "Observed friction"}],
            "claims": [
                {"claim_id": "claim-001", "statement": "The workflow causes friction.", "state": "supported", "evidence_ids": ["evidence-001"]},
                {"claim_id": "claim-002", "statement": "The redesign will solve the problem.", "state": "unsupported"},
            ],
            "assumptions": [{"statement": "Users will adopt the redesign.", "criticality": "high", "status": "planned", "owner": "Product lead", "test_method": "Prototype test"}],
        })
        summary = contract["ledger_summary"]
        self.assertEqual(summary["claim_states"]["supported"], 1)
        self.assertEqual(summary["claim_states"]["unsupported"], 1)
        self.assertEqual(summary["unsupported_or_disputed_count"], 1)
        self.assertEqual(summary["evidence_coverage"], "some_material_claims_linked")
        self.assertIn("do not measure truth", summary["indicator_note"])

    def test_assumption_links_to_experiment_and_evidence(self):
        contract = generate_canvas({"assumptions": [{
            "assumption_id": "assumption-001", "statement": "A short brief improves clarity.",
            "owner": "Research lead", "confidence": "low", "criticality": "high",
            "consequence": "The format may add work.", "test_method": "Compare comprehension.",
            "status": "testing", "experiment_ids": ["test-001"], "evidence_ids": ["evidence-001"],
        }]})
        assumption = contract["assumptions"][0]
        self.assertEqual(assumption["experiment_ids"], ["test-001"])
        self.assertEqual(assumption["evidence_ids"], ["evidence-001"])
        self.assertEqual(contract["ledger_summary"]["open_high_criticality_assumption_count"], 1)

    def test_markdown_surfaces_unsupported_claims_before_publication(self):
        contract = generate_canvas({"claims": [{"claim_id": "claim-risk", "statement": "A causal outcome is guaranteed.", "state": "unsupported"}]})
        markdown = export_markdown(contract)
        self.assertIn("## Publication and Review Warning", markdown)
        self.assertIn("claim-risk: A causal outcome is guaranteed. [unsupported]", markdown)
        self.assertLess(markdown.index("## Publication and Review Warning"), markdown.index("## Challenge"))

    def test_handoff_preserves_context_research_and_provenance(self):
        contract = generate_canvas({
            "canvas_id": "canvas-handoff", "revision_id": "revision-handoff", "title": "Handoff Canvas",
            "sources": [{"source_id": "source-001", "source_type": "document", "title": "Source"}],
            "claims": [{"claim_id": "claim-001", "statement": "Review this claim.", "state": "unsupported"}],
        })
        package = build_handoff_package(contract, "research_librarian")
        self.assertEqual(package["handoff_contract"], "catalyst-canvas-research-handoff/1.0")
        self.assertEqual(package["target"], "research_librarian")
        self.assertEqual(package["canvas_context"]["canvas_id"], "canvas-handoff")
        self.assertEqual(package["research"]["claims"][0]["claim_id"], "claim-001")
        self.assertEqual(package["provenance"]["generator"], "catalyst-canvas")

    def test_contract_1_1_migrates_to_1_2(self):
        payload = json.loads((Path(__file__).parents[1] / "fixtures" / "canvas_contract_1_1.expected.json").read_text())
        result = migrate_payload(payload)
        self.assertEqual(result.migrated_from, "catalyst-canvas/1.1")
        self.assertEqual(result.contract["schema_version"], "catalyst-canvas/1.4")
        self.assertIn("ledger_summary", result.contract)


class LedgerRouteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / "ledger.sqlite3")
        self.app = create_app({"TESTING": True, "SECRET_KEY": "test-secret", "CANVAS_DB": self.db})
        self.client = self.app.test_client()
        self.client.post("/projects", data={"title": "Ledger Project"})
        self.project_id = self.client.get("/api/projects").get_json()["projects"][0]["project_id"]

    def tearDown(self):
        self.tmp.cleanup()

    def test_ledger_route_saves_and_indexes_records(self):
        response = self.client.post("/ledger", data={
            "source_lines": "interview | Partner interview | Researcher | 2026-07-10 |  | Research lead | One participant | partner |  | Planning interview",
            "evidence_lines": "Partner quote | quote | source-001 | Partner wants visible gaps | Show the gap | note 4 | Interview note | medium | Single participant | partner",
            "claim_lines": "partially_supported | A shared brief improves clarity | Product lead | low | evidence-001 | assumption-001 | Small sample | One interview |  | Baseline measure | review | clarity",
            "assumption_lines": "high | Teams will use the shared brief | Product lead | low | Adoption may fail | Prototype session | planned | test-001 | evidence-001 | 2026-08-15 | Small sample | adoption",
            "research_question_lines": "high | Where does decision clarity break down? | Research lead | investigating | source-001 | evidence-001 | Interview more teams | clarity",
            "synthesis_tags": "decision clarity\nevidence gaps",
            "handoff_lines": "knowledge_library | ready | Register source | Preserve claim context | source-001 | evidence-001 | claim-001 | assumption-001 | Research lead",
        })
        self.assertEqual(response.status_code, 302)
        canvas = self.client.get(f"/api/projects/{self.project_id}").get_json()["canvas"]
        self.assertEqual(canvas["ledger_summary"]["source_count"], 1)
        self.assertEqual(canvas["ledger_summary"]["claim_count"], 1)
        self.assertEqual(canvas["claims"][0]["state"], "partially_supported")
        self.assertEqual(canvas["assumptions"][0]["experiment_ids"], ["test-001"])
        types = {item["asset_type"] for item in list_research_assets(self.db)}
        self.assertTrue({"source", "evidence", "claim", "assumption", "research_question"}.issubset(types))

    def test_handoff_export_endpoint_is_workspace_scoped(self):
        response = self.client.get(f"/projects/{self.project_id}/research-handoff/knowledge_library.json")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["target"], "knowledge_library")
        self.assertEqual(payload["canvas_context"]["title"], "Ledger Project")
        invalid = self.client.get(f"/projects/{self.project_id}/research-handoff/unknown.json")
        self.assertEqual(invalid.status_code, 404)


if __name__ == "__main__":
    unittest.main()
