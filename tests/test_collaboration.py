import copy
import json
import tempfile
import unittest
from pathlib import Path

from app import create_app
from app.services.storage import (
    collaboration_record_counts,
    create_project,
    init_db,
    list_collaboration_records,
    list_workspace_members,
)
from catalyst_canvas.collaboration import (
    build_publication_package,
    member_can,
    publication_release_record,
)
from catalyst_canvas.engine import generate_canvas
from catalyst_canvas.migrations import migrate_payload

ROOT = Path(__file__).resolve().parents[1]


class CollaborationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads((ROOT / "fixtures/canvas_contract_1_6.input.json").read_text(encoding="utf-8"))
        cls.contract = generate_canvas(cls.source, source_surface="python")

    def test_contract_1_6_preserves_collaboration_and_readiness(self):
        self.assertEqual(self.contract["schema_version"], "catalyst-canvas/1.6")
        self.assertEqual(len(self.contract["workspace_members"]), 3)
        self.assertEqual(self.contract["collaboration_summary"]["readiness"], "ready_for_publication")
        self.assertEqual(self.contract["collaboration_summary"]["open_comment_count"], 1)
        self.assertEqual(self.contract["collaboration_summary"]["required_review_open_count"], 0)

    def test_contract_1_5_migrates_to_contract_1_6(self):
        legacy = json.loads((ROOT / "fixtures/canvas_contract_1_5.expected.json").read_text(encoding="utf-8"))
        result = migrate_payload(legacy)
        self.assertEqual(result.migrated_from, "catalyst-canvas/1.5")
        self.assertEqual(result.contract["schema_version"], "catalyst-canvas/1.6")
        self.assertIn("workspace_members", result.contract)
        self.assertIn("publication_records", result.contract)
        self.assertIn("collaboration, review, and publication", result.warnings[0])

    def test_public_safe_package_excludes_private_working_records(self):
        package = build_publication_package(self.contract, "public_api", "publication-001")
        self.assertEqual(package["publication_contract"], "catalyst-canvas-public-safe/1.0")
        self.assertEqual(package["source"]["revision_id"], self.contract["revision_id"])
        self.assertTrue(package["integrity"]["content_checksum"])
        serialized = json.dumps(package)
        for private_key in ("workspace_members", "comments", "approvals", "review_assignments"):
            self.assertNotIn(f'"{private_key}"', serialized)
        self.assertNotIn("participant_plan", package["content"])

    def test_role_capabilities_are_explicit(self):
        members = {item["role"]: item for item in self.contract["workspace_members"]}
        self.assertTrue(member_can(members["owner"], "publish"))
        self.assertTrue(member_can(members["editor"], "edit"))
        self.assertTrue(member_can(members["reviewer"], "approve"))
        self.assertFalse(member_can(members["reviewer"], "publish"))
        self.assertFalse(member_can({"role": "owner", "status": "suspended"}, "publish"))

    def test_blocking_approval_prevents_ready_state(self):
        source = copy.deepcopy(self.source)
        source["approvals"][0]["decision"] = "changes_requested"
        contract = generate_canvas(source, source_surface="python")
        self.assertEqual(contract["collaboration_summary"]["readiness"], "blocked")
        self.assertEqual(contract["collaboration_summary"]["changes_requested_count"], 1)

    def test_release_record_preserves_revision_and_checksum(self):
        release = publication_release_record(
            self.contract,
            "publication-001",
            published_by="member-owner",
            generated_at="2026-07-16T23:45:00+00:00",
        )
        self.assertEqual(release["source_revision_id"], self.contract["revision_id"])
        self.assertEqual(release["state"], "published")
        self.assertEqual(release["published_by"], "member-owner")
        self.assertEqual(len(release["checksum"]), 64)


class CollaborationStorageTests(unittest.TestCase):
    def test_workspace_indexes_members_and_collaboration_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = str(Path(tmp) / "collaboration.sqlite3")
            init_db(db)
            contract = json.loads((ROOT / "fixtures/canvas_contract_1_6.expected.json").read_text(encoding="utf-8"))
            project = create_project(db, contract, title="Collaboration project")
            members = list_workspace_members(db, project["workspace_id"])
            self.assertGreaterEqual(len(members), 3)
            counts = collaboration_record_counts(db, project["workspace_id"], project["project_id"])
            for record_type in ("review_assignment", "comment", "approval", "publication", "publication_handoff"):
                self.assertGreaterEqual(counts.get(record_type, 0), 1)
            records = list_collaboration_records(db, project["workspace_id"], project_id=project["project_id"])
            self.assertTrue(any(item["record_type"] == "publication" for item in records))


class CollaborationRouteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / "collaboration-routes.sqlite3")
        self.app = create_app({"TESTING": True, "SECRET_KEY": "test-secret", "CANVAS_DB": self.db})
        self.client = self.app.test_client()
        contract = json.loads((ROOT / "fixtures/canvas_contract_1_6.expected.json").read_text(encoding="utf-8"))
        response = self.client.post("/api/canvas/import", json=contract)
        self.assertEqual(response.status_code, 201)
        self.project_id = response.get_json()["project_id"]

    def tearDown(self):
        self.tmp.cleanup()

    def test_collaboration_apis_and_publication_release(self):
        overview = self.client.get("/api/collaboration")
        self.assertEqual(overview.status_code, 200)
        self.assertEqual(overview.get_json()["collaboration_summary"]["readiness"], "ready_for_publication")

        comment = self.client.post("/api/comments", json={"body": "Confirm the public source label.", "target_type": "publication", "target_id": "publication-001"})
        self.assertEqual(comment.status_code, 201)
        comment_id = comment.get_json()["comment"]["comment_id"]
        resolved = self.client.post(f"/api/comments/{comment_id}/resolve")
        self.assertEqual(resolved.status_code, 200)
        self.assertEqual(resolved.get_json()["comment"]["status"], "resolved")

        review = self.client.post("/api/reviews", json={"title": "Final source check", "status": "complete", "required": False})
        self.assertEqual(review.status_code, 201)
        approval = self.client.post("/api/approvals", json={"decision": "approved", "scope": "Final release"})
        self.assertEqual(approval.status_code, 201)

        released = self.client.post("/api/publications/publication-001/publish", json={"url": "https://example.test/brief"})
        self.assertEqual(released.status_code, 201)
        payload = released.get_json()
        self.assertEqual(payload["publication"]["state"], "published")
        self.assertEqual(payload["release"]["url"], "https://example.test/brief")
        self.assertEqual(payload["collaboration_summary"]["readiness"], "published")

        public = self.client.get(f"/projects/{self.project_id}/public.json?publication_id=publication-001")
        self.assertEqual(public.status_code, 200)
        self.assertEqual(public.get_json()["publication_contract"], "catalyst-canvas-public-safe/1.0")
        self.assertNotIn("comments", public.get_json()["content"])


if __name__ == "__main__":
    unittest.main()
