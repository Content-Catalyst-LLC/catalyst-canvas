from contextlib import closing
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from catalyst_canvas import generate_canvas
from app.services.storage import (
    archive_project,
    create_project,
    duplicate_project,
    get_project,
    get_project_canvas,
    init_db,
    list_projects,
    list_revisions,
    restore_project,
    restore_revision,
    save_canvas,
)


class WorkspaceStorageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / "workspace.sqlite3")
        init_db(self.db)

    def tearDown(self):
        self.tmp.cleanup()

    def test_project_revisions_are_immutable_and_current_pointer_advances(self):
        canvas = generate_canvas({"title": "Project A", "challenge": "First"})
        project = create_project(self.db, canvas, title="Project A")
        original = get_project_canvas(self.db, project["project_id"])
        updated = generate_canvas({
            **{key: value for key, value in original.items() if not key.startswith("_")},
            "revision_id": "revision-second",
            "challenge": "Second",
            "updated_at": "2026-07-16T18:00:00+00:00",
        })
        save_canvas(self.db, updated, project_id=project["project_id"], change_note="Challenge revised")
        revisions = list_revisions(self.db, project["project_id"])
        self.assertEqual(len(revisions), 2)
        self.assertEqual(get_project_canvas(self.db, project["project_id"])["challenge"], "Second")
        historical = get_project_canvas(self.db, project["project_id"], revision_id=original["revision_id"])
        self.assertEqual(historical["challenge"], "First")

    def test_archive_restore_search_and_duplicate(self):
        canvas = generate_canvas({"title": "Evidence Project", "challenge": "Trace evidence"})
        project = create_project(self.db, canvas, title="Evidence Project", tags="evidence, review")
        self.assertEqual(len(list_projects(self.db, query="evidence")), 1)
        archived = archive_project(self.db, project["project_id"])
        self.assertEqual(archived["status"], "archived")
        self.assertEqual(len(list_projects(self.db, status="active")), 0)
        restored = restore_project(self.db, project["project_id"])
        self.assertEqual(restored["status"], "active")
        duplicate = duplicate_project(self.db, project["project_id"])
        self.assertNotEqual(duplicate["project_id"], project["project_id"])
        self.assertNotEqual(duplicate["current_canvas_id"], project["current_canvas_id"])

    def test_restore_revision_creates_a_new_revision(self):
        canvas = generate_canvas({"title": "Restore Test", "challenge": "Original"})
        project = create_project(self.db, canvas)
        original_revision = project["current_revision_id"]
        current = get_project_canvas(self.db, project["project_id"])
        changed = generate_canvas({
            **{key: value for key, value in current.items() if not key.startswith("_")},
            "revision_id": "revision-changed",
            "challenge": "Changed",
            "updated_at": "2026-07-16T19:00:00+00:00",
        })
        save_canvas(self.db, changed, project_id=project["project_id"])
        restored_storage_id = restore_revision(self.db, project["project_id"], original_revision)
        self.assertIsNotNone(restored_storage_id)
        self.assertEqual(get_project_canvas(self.db, project["project_id"])["challenge"], "Original")
        self.assertEqual(len(list_revisions(self.db, project["project_id"])), 3)

    def test_v12_rows_migrate_into_default_workspace(self):
        legacy_db = str(Path(self.tmp.name) / "legacy.sqlite3")
        with closing(sqlite3.connect(legacy_db)) as conn:
            conn.execute("""
                CREATE TABLE canvas_briefs (
                  id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, payload TEXT NOT NULL,
                  created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                )
            """)
            contract = generate_canvas({"title": "Legacy Project", "challenge": "Upgrade storage"})
            conn.execute(
                "INSERT INTO canvas_briefs (title,payload,created_at,updated_at) VALUES (?,?,?,?)",
                (contract["title"], json.dumps(contract), contract["created_at"], contract["updated_at"]),
            )
            conn.commit()
        init_db(legacy_db)
        projects = list_projects(legacy_db)
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]["title"], "Legacy Project")
        self.assertEqual(projects[0]["revision_count"], 1)


if __name__ == "__main__":
    unittest.main()
