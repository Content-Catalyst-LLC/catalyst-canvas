import tempfile
import unittest
from pathlib import Path

from app import create_app


class WorkspaceRouteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "CANVAS_DB": str(Path(self.tmp.name) / "routes.sqlite3"),
            "CANVAS_WORKSPACE_ID": "workspace-local-default",
        })
        self.client = self.app.test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def test_project_lifecycle_and_autosave_api(self):
        response = self.client.post("/projects", data={"title": "Route Project", "tags": "route,test"})
        self.assertEqual(response.status_code, 302)
        projects = self.client.get("/api/projects").get_json()["projects"]
        self.assertEqual(len(projects), 1)
        project_id = projects[0]["project_id"]
        detail = self.client.get(f"/api/projects/{project_id}").get_json()
        self.assertEqual(detail["project"]["title"], "Route Project")
        autosave = self.client.post(
            f"/api/projects/{project_id}/autosave",
            json={"challenge": "Autosaved route challenge", "title": "Route Project"},
        )
        self.assertEqual(autosave.status_code, 201)
        revisions = self.client.get(f"/api/projects/{project_id}/revisions").get_json()["revisions"]
        self.assertEqual(len(revisions), 2)
        self.assertTrue(revisions[0]["autosave"])

    def test_workspace_boundary_hides_project_from_other_workspace(self):
        self.client.post("/projects", data={"title": "Private Project"})
        project_id = self.client.get("/api/projects").get_json()["projects"][0]["project_id"]
        other = self.client.post("/workspaces", data={"name": "Other Workspace"})
        self.assertEqual(other.status_code, 302)
        self.assertEqual(self.client.get(f"/api/projects/{project_id}").status_code, 404)


if __name__ == "__main__":
    unittest.main()

class ResearchStudioRouteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "CANVAS_DB": str(Path(self.tmp.name) / "research-routes.sqlite3"),
            "CANVAS_WORKSPACE_ID": "workspace-local-default",
        })
        self.client = self.app.test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def test_research_studio_saves_and_indexes_records(self):
        self.client.post("/projects", data={"title": "Research Project"})
        project_id = self.client.get("/api/projects").get_json()["projects"][0]["project_id"]
        response = self.client.post("/research", data={
            "persona_name": "Program Lead",
            "persona_context": "Coordinates a cross-agency pilot",
            "persona_goals": "Align partners",
            "persona_confidence": "medium",
            "persona_validation_status": "researching",
            "stakeholder_lines": "Sponsor | sponsor | 5 | 4 | supportive | approver | Review evidence |",
            "journey_title": "Pilot journey",
            "journey_stages": "Discover | Review evidence | -1 | Missing data | Show gaps | Dashboard | Web | evidence-001",
        })
        self.assertEqual(response.status_code, 302)
        detail = self.client.get(f"/api/projects/{project_id}").get_json()["canvas"]
        self.assertEqual(detail["research_summary"]["stakeholder_count"], 1)
        self.assertEqual(detail["research_summary"]["journey_count"], 1)
        assets = self.client.get("/api/research/assets").get_json()
        self.assertEqual(assets["counts"]["persona"], 1)
        self.assertEqual(assets["counts"]["stakeholder"], 1)
        self.assertEqual(assets["counts"]["journey"], 1)
