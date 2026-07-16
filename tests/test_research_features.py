import io
import tempfile
import unittest
from pathlib import Path
from werkzeug.datastructures import FileStorage

from app import create_app
from app.routes import read_behavioral_signal_upload
from catalyst_canvas import generate_canvas
from catalyst_canvas.persona_templates import list_persona_templates
from catalyst_canvas.research import parse_behavioral_signal_csv


class ResearchFeatureContractTests(unittest.TestCase):
    def test_persona_templates_cover_supported_contexts(self):
        templates = list_persona_templates()
        self.assertEqual(
            set(templates),
            {"civic", "sustainability", "research", "technical_content", "institutional", "public_interest"},
        )
        for template in templates.values():
            self.assertTrue(template["name"])
            self.assertTrue(template["jobs"])
            self.assertTrue(template["needs"])
            self.assertTrue(template["barriers"])
            self.assertTrue(template["motivations"])

    def test_persona_empathy_attributes_and_journey_experiment_links_are_canonical(self):
        contract = generate_canvas({
            "challenge": "Coordinate an evidence-aware pilot",
            "audience": {"primary": "Program lead", "affected": ["Residents"], "excluded": ["Individual targeting"]},
            "persona": {
                "name": "Program Lead",
                "jobs": ["Coordinate the pilot"],
                "needs": ["Traceable evidence"],
                "pains": ["Fragmented ownership"],
                "gains": ["Shared accountability"],
                "barriers": ["Uneven data"],
                "motivations": ["Defensible decisions"],
                "empathy_map": {"says": ["Show me the evidence gap."], "does": ["Reviews source notes"]},
                "attributes": [
                    {"category": "behavior", "statement": "Reviews source notes", "basis": "observed", "confidence": "high", "evidence_ids": ["evidence-001"]},
                    {"category": "motivation", "statement": "Prefers certainty", "basis": "assumed", "confidence": "low"},
                ],
                "source_type": "mixed",
                "confidence": "medium",
                "validation_status": "researching",
            },
            "journeys": [{
                "title": "Pilot journey",
                "stages": [{
                    "name": "Review",
                    "questions": ["What is supported?"],
                    "frictions": ["Evidence gap"],
                    "opportunities": ["Show source confidence"],
                    "evidence_ids": ["evidence-001"],
                    "experiment_ids": ["test-001"],
                    "owner": "Program lead",
                }],
            }],
        })
        persona = contract["personas"][0]
        self.assertEqual(persona["empathy_map"]["says"], ["Show me the evidence gap."])
        self.assertEqual(persona["attributes"][0]["basis"], "observed")
        self.assertEqual(persona["attributes"][1]["basis"], "assumed")
        stage = contract["journeys"][0]["stages"][0]
        self.assertEqual(stage["questions"], ["What is supported?"])
        self.assertEqual(stage["frictions"], ["Evidence gap"])
        self.assertEqual(stage["experiment_ids"], ["test-001"])
        self.assertEqual(contract["audience"]["affected"], ["Residents"])
        self.assertEqual(contract["audience"]["excluded"], ["Individual targeting"])

    def test_behavioral_csv_stays_a_hint_and_ignores_identity_columns(self):
        csv_text = (
            "metric,segment,value,period,interpretation,limitation,evidence_ids,tags,age,gender,intent\n"
            "brief_downloads,all visitors,42,2026-06,Investigate format use,,evidence-001,brief,35-44,woman,high\n"
        )
        signals = parse_behavioral_signal_csv(csv_text, source_type="ga4_export")
        self.assertEqual(len(signals), 1)
        signal = signals[0]
        self.assertEqual(signal["evidence_status"], "hint")
        self.assertIn("do not prove intent", signal["limitation"])
        self.assertNotIn("age", signal)
        self.assertNotIn("gender", signal)
        self.assertNotIn("intent", signal)


class ResearchFeatureRouteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "CANVAS_DB": str(Path(self.tmp.name) / "research-features.sqlite3"),
            "CANVAS_WORKSPACE_ID": "workspace-local-default",
        })
        self.client = self.app.test_client()
        self.client.post("/projects", data={"title": "Research Feature Project"})
        self.project_id = self.client.get("/api/projects").get_json()["projects"][0]["project_id"]

    def tearDown(self):
        self.tmp.cleanup()

    def test_csv_file_upload_and_comparison_surface(self):
        csv_bytes = (
            b"metric,segment,value,period,interpretation,limitation,evidence_ids,tags,demographic\n"
            b"journey_completion,all visitors,64%,2026-Q2,Investigate journey friction,,evidence-001,journey,ignored\n"
        )
        response = self.client.post(
            "/research",
            data={
                "persona_name": "Program Lead",
                "persona_jobs": "Coordinate a pilot",
                "persona_source_type": "research",
                "persona_confidence": "medium",
                "persona_validation_status": "researching",
                "journey_title": "Pilot journey",
                "journey_stages": "Review | Inspect evidence | What is supported? | -1 | Evidence gap | Show confidence | Dashboard | Web | Review time | Program Lead | evidence-001 | test-001",
                "behavioral_signal_source_type": "ga4_export",
                "behavioral_signal_file": (io.BytesIO(csv_bytes), "ga4-export.csv"),
            },
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 302)
        response.close()
        canvas = self.client.get(f"/api/projects/{self.project_id}").get_json()["canvas"]
        self.assertEqual(canvas["research_summary"]["behavioral_signal_count"], 1)
        self.assertEqual(canvas["behavioral_signals"][0]["evidence_status"], "hint")
        self.assertEqual(canvas["journeys"][0]["stages"][0]["experiment_ids"], ["test-001"])
        comparison = self.client.get("/research/compare?type=persona")
        self.assertEqual(comparison.status_code, 200)
        self.assertIn(b"Research Feature Project", comparison.data)
        templates = self.client.get("/api/research/persona-templates").get_json()["templates"]
        self.assertEqual(len(templates), 6)

    def test_csv_upload_rejects_non_csv_and_oversize_files(self):
        invalid = self.client.post(
            "/research",
            data={"behavioral_signal_file": (io.BytesIO(b"not csv"), "signals.txt")},
            content_type="multipart/form-data",
        )
        self.assertEqual(invalid.status_code, 400)
        self.assertIn(b"must be CSV", invalid.data)
        invalid.close()
        upload = FileStorage(stream=io.BytesIO(b"x" * 2_000_001), filename="signals.csv")
        try:
            with self.assertRaisesRegex(ValueError, "2 MB"):
                read_behavioral_signal_upload(upload)
        finally:
            upload.close()


if __name__ == "__main__":
    unittest.main()
