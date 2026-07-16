#!/usr/bin/env python3
"""Run the authoritative Catalyst Canvas release validation suite."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
CONTRACT_VERSION = "catalyst-canvas/1.1"
WORKSPACE_CONTRACT_VERSION = "catalyst-canvas-workspace/1.0"


def run(*args: str, env: dict[str, str] | None = None) -> None:
    print("+", " ".join(args), flush=True)
    effective_env = os.environ.copy()
    if env:
        effective_env.update(env)
    subprocess.run(args, cwd=ROOT, check=True, env=effective_env)


def load_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def verify_version_markers() -> None:
    if not re.fullmatch(r"\d+\.\d+\.\d+", VERSION):
        raise RuntimeError(f"Invalid semantic version: {VERSION!r}")

    manifest = load_json("canvas_manifest.json")
    schema = load_json("schemas/catalyst_canvas_contract_1_1.schema.json")
    workspace_schema = load_json("schemas/catalyst_canvas_workspace_1_0.schema.json")
    plugin = (ROOT / "wordpress/catalyst-canvas-demo/catalyst-canvas-demo.php").read_text(encoding="utf-8")
    package_version = (ROOT / "catalyst_canvas/version.py").read_text(encoding="utf-8")
    contract_data = (ROOT / "wordpress/catalyst-canvas-demo/assets/catalyst-canvas-contract-data.js").read_text(encoding="utf-8")

    checks = {
        "manifest release": manifest.get("version"),
        "manifest contract": manifest.get("contract_version"),
        "schema contract": schema.get("properties", {}).get("schema_version", {}).get("const"),
        "schema generator": schema.get("$defs", {}).get("provenance", {}).get("properties", {}).get("generator_version", {}).get("const"),
        "workspace contract": manifest.get("workspace_contract_version"),
        "workspace schema": workspace_schema.get("properties", {}).get("schema_version", {}).get("const"),
    }
    expected = {
        "manifest release": VERSION,
        "manifest contract": CONTRACT_VERSION,
        "schema contract": CONTRACT_VERSION,
        "schema generator": VERSION,
        "workspace contract": WORKSPACE_CONTRACT_VERSION,
        "workspace schema": WORKSPACE_CONTRACT_VERSION,
    }
    for label, value in checks.items():
        if value != expected[label]:
            raise RuntimeError(f"{label} {value!r} does not match {expected[label]!r}")

    if f'__version__ = "{VERSION}"' not in package_version:
        raise RuntimeError("Canonical package version does not match VERSION")
    if f'CONTRACT_VERSION = "{CONTRACT_VERSION}"' not in package_version:
        raise RuntimeError("Canonical package contract version is not synchronized")
    if not re.search(rf"Version:\s*{re.escape(VERSION)}(?:\s|$)", plugin):
        raise RuntimeError("WordPress plugin header does not match VERSION")
    if f"private const VERSION = '{VERSION}';" not in plugin:
        raise RuntimeError("WordPress plugin release constant does not match VERSION")
    if f"private const CONTRACT_VERSION = '{CONTRACT_VERSION}';" not in plugin:
        raise RuntimeError("WordPress contract constant does not match Canvas Contract 1.1")
    if f'"releaseVersion":"{VERSION}"' not in contract_data:
        raise RuntimeError("Generated browser contract data has the wrong release version")
    if f'"contractVersion":"{CONTRACT_VERSION}"' not in contract_data:
        raise RuntimeError("Generated browser contract data has the wrong contract version")


def verify_generated_contract_asset(temp_dir: Path) -> None:
    candidate = temp_dir / "catalyst-canvas-contract-data.js"
    run(sys.executable, "scripts/sync_contract_assets.py", "--output", str(candidate))
    canonical = ROOT / "wordpress/catalyst-canvas-demo/assets/catalyst-canvas-contract-data.js"
    if candidate.read_bytes() != canonical.read_bytes():
        raise RuntimeError("WordPress contract-data asset is stale; run scripts/sync_contract_assets.py")


def verify_source_tree() -> None:
    forbidden_files = [
        ROOT / "outputs/catalyst-canvas-demo.zip",
        ROOT / ".github/workflows/python-tests.yml",
    ]
    present = [str(path.relative_to(ROOT)) for path in forbidden_files if path.exists()]
    if present:
        raise RuntimeError(f"Generated or superseded files remain in source: {present}")

    runtime_databases = ["catalyst.sqlite3", "demo/catalyst_seed.sqlite3"]
    if (ROOT / ".git").exists() and shutil.which("git"):
        tracked = []
        for relative_path in runtime_databases:
            result = subprocess.run(
                ["git", "ls-files", "--error-unmatch", relative_path],
                cwd=ROOT,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            if result.returncode == 0:
                tracked.append(relative_path)
        if tracked:
            raise RuntimeError(f"Runtime databases are still tracked by Git: {tracked}")


def validate_schemas() -> tuple[dict, dict]:
    schema = load_json("schemas/catalyst_canvas_contract_1_1.schema.json")
    workspace_schema = load_json("schemas/catalyst_canvas_workspace_1_0.schema.json")
    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(workspace_schema)
    return schema, workspace_schema


def validate_generated_contract(temp_dir: Path, schema: dict) -> None:
    json_output = temp_dir / "sample.json"
    markdown_output = temp_dir / "sample.md"
    html_output = temp_dir / "sample.html"
    run(
        sys.executable,
        "-m",
        "catalyst_canvas.cli",
        "generate",
        "--input",
        "data/catalyst_canvas_sample_input.json",
        "--json",
        str(json_output),
        "--markdown",
        str(markdown_output),
        "--html",
        str(html_output),
    )
    payload = json.loads(json_output.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(payload), key=lambda error: list(error.path))
    if errors:
        raise RuntimeError("Generated sample failed schema validation: " + "; ".join(error.message for error in errors))
    if payload.get("schema_version") != CONTRACT_VERSION:
        raise RuntimeError("Generated JSON does not declare Canvas Contract 1.1")
    if f"Contract: {CONTRACT_VERSION}" not in markdown_output.read_text(encoding="utf-8"):
        raise RuntimeError("Generated Markdown does not declare Canvas Contract 1.1")
    if "<!doctype html>" not in html_output.read_text(encoding="utf-8").lower():
        raise RuntimeError("Generated print report is not standalone HTML")
    run(sys.executable, "-m", "catalyst_canvas.cli", "validate", "--input", str(json_output))

    compatibility_output = temp_dir / "compatibility.json"
    run(
        sys.executable,
        "python/catalyst_canvas_core.py",
        "--input",
        "data/catalyst_canvas_sample_input.json",
        "--output",
        str(compatibility_output),
    )
    if json.loads(compatibility_output.read_text(encoding="utf-8"))["schema_version"] != CONTRACT_VERSION:
        raise RuntimeError("Legacy Python core adapter did not emit the canonical contract")


def validate_demo_seed(temp_dir: Path) -> None:
    from app.services.storage import get_canvas

    database = temp_dir / "seed.sqlite3"
    run(sys.executable, "demo/seed_demo.py", "--database", str(database))
    canvas = get_canvas(str(database), 1)
    if not canvas or canvas.get("schema_version") != CONTRACT_VERSION:
        raise RuntimeError("Demo seed did not create a Canvas Contract 1.1 record")



def validate_workspace_operations(temp_dir: Path, workspace_schema: dict) -> None:
    from catalyst_canvas import generate_canvas
    from app.services.storage import (
        archive_project, create_project, duplicate_project, get_project_canvas,
        init_db, list_projects, list_revisions, restore_project, save_canvas,
        list_research_assets, research_asset_counts,
    )

    database = str(temp_dir / "workspace-validation.sqlite3")
    init_db(database)
    canvas = generate_canvas({"title": "Release workspace", "challenge": "Validate persistence"})
    project = create_project(database, canvas, title="Release workspace", tags="release,workspace")
    errors = list(Draft202012Validator(workspace_schema).iter_errors({key: value for key, value in project.items() if not key.startswith("_")}))
    if errors:
        raise RuntimeError("Project record failed Workspace Contract 1.0 validation")
    current = get_project_canvas(database, project["project_id"])
    current["revision_id"] = "revision-release-autosave"
    current["updated_at"] = "2026-07-16T22:00:00+00:00"
    save_canvas(database, current, project_id=project["project_id"], autosave=True)
    if len(list_revisions(database, project["project_id"])) != 2:
        raise RuntimeError("Workspace revision ledger did not retain both revisions")
    if len(list_projects(database, query="release")) != 1:
        raise RuntimeError("Workspace project search failed")
    archive_project(database, project["project_id"])
    if list_projects(database, status="active"):
        raise RuntimeError("Archived project remained in active registry")
    restore_project(database, project["project_id"])
    duplicate = duplicate_project(database, project["project_id"])
    if not duplicate or duplicate["current_canvas_id"] == project["current_canvas_id"]:
        raise RuntimeError("Project duplication did not create independent Canvas identity")
    research_canvas = get_project_canvas(database, project["project_id"])
    research_canvas["revision_id"] = "revision-release-research"
    research_canvas["updated_at"] = "2026-07-16T22:10:00+00:00"
    research_canvas["stakeholders"] = [{
        "stakeholder_id": "stakeholder-release", "name": "Release reviewer", "stakeholder_type": "advisor",
        "relationship": "reviewer", "influence": 4, "interest": 5, "stance": "supportive",
        "decision_role": "advisor", "engagement_strategy": "Review contract conformance", "notes": "",
        "evidence_ids": [], "dependencies": [], "tags": ["release"],
    }]
    # normalize through the shared engine to add a journey and recompute summary.
    from catalyst_canvas.engine import generate_canvas
    research_canvas = generate_canvas({**{k:v for k,v in research_canvas.items() if not k.startswith("_")},
        "revision_id": "revision-release-research", "updated_at": "2026-07-16T22:10:00+00:00",
        "journeys": [{"journey_id":"journey-release","title":"Release journey","persona_id":research_canvas["personas"][0]["persona_id"],"stages":[{"name":"Validate","actions":["Run release gate"]}]}],
    })
    save_canvas(database, research_canvas, project_id=project["project_id"], change_note="Research validation")
    counts = research_asset_counts(database)
    if counts["persona"] < 1 or counts["stakeholder"] < 1 or counts["journey"] < 1:
        raise RuntimeError("Research asset library did not index personas, stakeholders, and journeys")
    if not list_research_assets(database, asset_type="journey"):
        raise RuntimeError("Journey research asset was not queryable")

def validate_migration_cli(temp_dir: Path, schema: dict) -> None:
    legacy = {
        "version": "1.1.1",
        "generated_at": "2026-07-16T10:00:00+00:00",
        "challenge": "Migrate a legacy export",
        "audience": "Maintainer",
        "goal": "Produce Canvas Contract 1.1",
        "constraint": "Flat fields",
        "framework": "AIDA",
        "persona": {"name": "Maintainer", "description": "Needs safe migration."},
        "prototype": {"title": "Migration test", "description": "A deterministic fixture."},
        "test_plan": {"signal": "Valid output", "method": "Run CLI", "learning_goal": "Verify migration"},
    }
    source = temp_dir / "legacy.json"
    output = temp_dir / "migrated.json"
    source.write_text(json.dumps(legacy), encoding="utf-8")
    run(sys.executable, "-m", "catalyst_canvas.cli", "migrate", "--input", str(source), "--output", str(output))
    payload = json.loads(output.read_text(encoding="utf-8"))
    errors = list(Draft202012Validator(schema).iter_errors(payload))
    if errors:
        raise RuntimeError("Migrated CLI output failed Canvas Contract 1.1 validation")
    if payload["provenance"]["migrated_from"] != "legacy-core/1.1.1":
        raise RuntimeError("Migration provenance was not recorded")


def validate_cross_surface_fixture() -> None:
    from catalyst_canvas.adapters.flask import compact_to_contract
    from catalyst_canvas.engine import generate_canvas

    source = load_json("fixtures/canvas_contract_1_1.input.json")
    expected = load_json("fixtures/canvas_contract_1_1.expected.json")
    if generate_canvas(source, source_surface="python") != expected:
        raise RuntimeError("Python engine diverges from the shared fixture")
    if compact_to_contract(source) != expected:
        raise RuntimeError("Flask adapter diverges from the shared fixture")

    node = shutil.which("node")
    if node:
        run(node, "tests/js/test_contract_fixture.js")
        run(node, "tests/js/test_workspace.js")
        run(node, "tests/js/test_research_studio.js")
    else:
        print("SKIP: Node.js is unavailable; browser fixture conformance will run in CI.")


def validate_optional_syntax_tools() -> None:
    php = shutil.which("php")
    if php:
        run(php, "-l", "wordpress/catalyst-canvas-demo/catalyst-canvas-demo.php")
    else:
        print("SKIP: PHP is unavailable; plugin syntax check not run locally.")

    node = shutil.which("node")
    if node:
        for relative in [
            "wordpress/catalyst-canvas-demo/assets/catalyst-canvas-contract-data.js",
            "wordpress/catalyst-canvas-demo/assets/catalyst-canvas-engine.js",
            "wordpress/catalyst-canvas-demo/assets/catalyst-canvas-workspace.js",
            "wordpress/catalyst-canvas-demo/assets/catalyst-canvas-demo.js",
        ]:
            run(node, "--check", relative)
    else:
        print("SKIP: Node.js is unavailable; JavaScript syntax checks not run locally.")


def validate_plugin_package(temp_dir: Path) -> None:
    output = temp_dir / f"catalyst-canvas-demo-v{VERSION}.zip"
    run(sys.executable, "scripts/build_plugin.py", "--output", str(output))
    with ZipFile(output) as archive:
        names = set(archive.namelist())
    required = {
        "catalyst-canvas-demo/catalyst-canvas-demo.php",
        "catalyst-canvas-demo/assets/catalyst-canvas-demo.css",
        "catalyst-canvas-demo/assets/catalyst-canvas-contract-data.js",
        "catalyst-canvas-demo/assets/catalyst-canvas-engine.js",
        "catalyst-canvas-demo/assets/catalyst-canvas-workspace.js",
        "catalyst-canvas-demo/assets/catalyst-canvas-demo.js",
    }
    missing = sorted(required - names)
    if missing:
        raise RuntimeError(f"Plugin ZIP is missing required entries: {missing}")


def main() -> int:
    verify_version_markers()
    verify_source_tree()
    schema, workspace_schema = validate_schemas()
    run(sys.executable, "-m", "compileall", "-q", "app", "catalyst_canvas", "python", "demo", "scripts")
    run(sys.executable, "-m", "pytest", "tests", env={"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"})
    run(sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v")
    with tempfile.TemporaryDirectory(prefix="catalyst-canvas-release-") as tmp:
        temp_dir = Path(tmp)
        verify_generated_contract_asset(temp_dir)
        validate_generated_contract(temp_dir, schema)
        validate_demo_seed(temp_dir)
        validate_workspace_operations(temp_dir, workspace_schema)
        validate_migration_cli(temp_dir, schema)
        validate_cross_surface_fixture()
        validate_optional_syntax_tools()
        validate_plugin_package(temp_dir)
    print(f"PASS: Catalyst Canvas v{VERSION} / {CONTRACT_VERSION} / {WORKSPACE_CONTRACT_VERSION} release validation completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
