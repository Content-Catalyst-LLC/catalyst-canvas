import copy
import json
import tempfile
import unittest
from pathlib import Path

from app import create_app
from app.services.storage import create_project, init_db, list_platform_records, platform_record_counts
from catalyst_canvas.engine import generate_canvas
from catalyst_canvas.migrations import migrate_payload
from catalyst_canvas.platform import build_exchange_package, capability_manifest, verify_exchange_package

ROOT = Path(__file__).resolve().parents[1]


class ConnectedPlatformContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads((ROOT / "fixtures/canvas_contract_2_0.input.json").read_text(encoding="utf-8"))
        cls.contract = generate_canvas(cls.source, source_surface="python")

    def test_contract_2_0_preserves_platform_records(self):
        self.assertEqual(self.contract["schema_version"], "catalyst-canvas/2.0")
        self.assertEqual(self.contract["platform_summary"]["connection_count"], 3)
        self.assertEqual(self.contract["platform_summary"]["verified_connection_count"], 2)
        self.assertEqual(self.contract["platform_summary"]["readiness"], "connected_but_not_ready")
        self.assertEqual(self.contract["platform_events"][0]["event_contract"], "catalyst-canvas-event/1.0")

    def test_contract_1_6_migrates_to_contract_2_0(self):
        legacy = json.loads((ROOT / "fixtures/canvas_contract_1_6.expected.json").read_text(encoding="utf-8"))
        result = migrate_payload(legacy)
        self.assertEqual(result.migrated_from, "catalyst-canvas/1.6")
        self.assertEqual(result.contract["schema_version"], "catalyst-canvas/2.0")
        self.assertIn("platform_connections", result.contract)
        self.assertIn("platform exchange", result.warnings[0])

    def test_signed_exchange_verifies_and_detects_tampering(self):
        package = build_exchange_package(
            self.contract,
            "decision_studio",
            payload_type="decision",
            profile_id="profile-institutional-v1",
            signing_key="test-signing-key",
            created_by="member-owner",
        )
        result = verify_exchange_package(package, "test-signing-key")
        self.assertTrue(result["valid"])
        self.assertTrue(result["checksum_valid"])
        self.assertTrue(result["signature_valid"])
        tampered = copy.deepcopy(package)
        tampered["payload"]["goal"] = "Tampered goal"
        invalid = verify_exchange_package(tampered, "test-signing-key")
        self.assertFalse(invalid["valid"])
        self.assertFalse(invalid["checksum_valid"])

    def test_capability_manifest_describes_supported_contracts(self):
        manifest = capability_manifest(self.contract)
        self.assertEqual(manifest["capability_contract"], "catalyst-canvas-capabilities/1.0")
        self.assertEqual(manifest["canvas_contract"], "catalyst-canvas/2.0")
        self.assertEqual(manifest["exchange_contract"], "catalyst-canvas-exchange/2.0")
        self.assertIn("signed_exchange", manifest["capabilities"])


class ConnectedPlatformStorageTests(unittest.TestCase):
    def test_workspace_indexes_platform_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = str(Path(tmp) / "platform.sqlite3")
            init_db(db)
            contract = json.loads((ROOT / "fixtures/canvas_contract_2_0.expected.json").read_text(encoding="utf-8"))
            project = create_project(db, contract, title="Connected platform")
            counts = platform_record_counts(db, project["workspace_id"], project["project_id"])
            for record_type in ("connection", "interoperability_profile", "workflow_link", "exchange", "platform_event"):
                self.assertGreaterEqual(counts.get(record_type, 0), 1)
            records = list_platform_records(db, project["workspace_id"], project_id=project["project_id"])
            self.assertTrue(any(item["record_type"] == "connection" for item in records))


class ConnectedPlatformRouteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / "platform-routes.sqlite3")
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "CANVAS_DB": self.db,
            "CANVAS_EXCHANGE_SIGNING_KEY": "test-signing-key",
        })
        self.client = self.app.test_client()
        contract = json.loads((ROOT / "fixtures/canvas_contract_2_0.expected.json").read_text(encoding="utf-8"))
        response = self.client.post("/api/canvas/import", json=contract)
        self.assertEqual(response.status_code, 201)
        self.project_id = response.get_json()["project_id"]

    def tearDown(self):
        self.tmp.cleanup()

    def test_platform_overview_and_capabilities(self):
        overview = self.client.get("/api/platform")
        self.assertEqual(overview.status_code, 200)
        self.assertEqual(overview.get_json()["platform_summary"]["connection_count"], 3)
        capabilities = self.client.get("/api/capabilities")
        self.assertEqual(capabilities.status_code, 200)
        self.assertEqual(capabilities.get_json()["canvas_contract"], "catalyst-canvas/2.0")
        studio = self.client.get("/platform")
        self.assertEqual(studio.status_code, 200)
        self.assertIn(b"Connected Strategic Design Platform", studio.data)

    def test_exchange_export_and_verification(self):
        response = self.client.get(
            f"/projects/{self.project_id}/exchange/decision_studio.json?payload_type=decision&profile_id=profile-institutional-v1"
        )
        self.assertEqual(response.status_code, 200)
        package = response.get_json()
        self.assertEqual(package["exchange_contract"], "catalyst-canvas-exchange/2.0")
        self.assertEqual(package["target"]["product"], "decision_studio")
        self.assertEqual(package["integrity"]["signature_algorithm"], "hmac-sha256")
        verified = self.client.post("/api/exchange/verify", json=package)
        self.assertEqual(verified.status_code, 200)
        self.assertTrue(verified.get_json()["valid"])


if __name__ == "__main__":
    unittest.main()
