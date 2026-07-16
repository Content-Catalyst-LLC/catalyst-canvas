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
CONTRACT_VERSION = "catalyst-canvas/1.4"
WORKSPACE_CONTRACT_VERSION = "catalyst-canvas-workspace/1.0"


def run(*args: str, env: dict[str, str] | None = None) -> None:
    print("+", " ".join(args), flush=True)
    effective_env = os.environ.copy()
    if env:
        effective_env.update(env)
    subprocess.run(args, cwd=ROOT, check=True, env=effective_env, timeout=120)


def load_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def invoke_cli(*args: str) -> None:
    """Exercise the installed CLI parser without spawning another Python runtime."""
    from catalyst_canvas.cli import main as cli_main

    previous = sys.argv[:]
    try:
        sys.argv = ["catalyst-canvas", *args]
        result = cli_main()
    finally:
        sys.argv = previous
    if result:
        raise RuntimeError(f"CLI command failed with status {result}: {' '.join(args)}")


def verify_version_markers() -> None:
    if not re.fullmatch(r"\d+\.\d+\.\d+", VERSION):
        raise RuntimeError(f"Invalid semantic version: {VERSION!r}")

    manifest = load_json("canvas_manifest.json")
    schema = load_json("schemas/catalyst_canvas_contract_1_4.schema.json")
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
        raise RuntimeError("WordPress contract constant does not match Canvas Contract 1.4")
    if f'"releaseVersion":"{VERSION}"' not in contract_data:
        raise RuntimeError("Generated browser contract data has the wrong release version")
    if f'"contractVersion":"{CONTRACT_VERSION}"' not in contract_data:
        raise RuntimeError("Generated browser contract data has the wrong contract version")


def verify_generated_contract_asset(temp_dir: Path) -> None:
    from scripts.sync_contract_assets import render

    candidate = temp_dir / "catalyst-canvas-contract-data.js"
    candidate.write_text(render(), encoding="utf-8")
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
    schema = load_json("schemas/catalyst_canvas_contract_1_4.schema.json")
    workspace_schema = load_json("schemas/catalyst_canvas_workspace_1_0.schema.json")
    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(workspace_schema)
    return schema, workspace_schema


def validate_generated_contract(temp_dir: Path, schema: dict) -> None:
    from catalyst_canvas.engine import generate_canvas
    from catalyst_canvas.exporters import export_json, export_markdown, export_print_html
    from python.catalyst_canvas_core import generate_brief

    source = load_json("data/catalyst_canvas_sample_input.json")
    contract = generate_canvas(source, source_surface="cli")
    json_output = temp_dir / "sample.json"
    markdown_output = temp_dir / "sample.md"
    html_output = temp_dir / "sample.html"
    json_output.write_text(export_json(contract), encoding="utf-8")
    markdown_output.write_text(export_markdown(contract), encoding="utf-8")
    html_output.write_text(export_print_html(contract), encoding="utf-8")

    errors = sorted(Draft202012Validator(schema).iter_errors(contract), key=lambda error: list(error.path))
    if errors:
        raise RuntimeError("Generated sample failed schema validation: " + "; ".join(error.message for error in errors))
    if contract.get("schema_version") != CONTRACT_VERSION:
        raise RuntimeError("Generated JSON does not declare Canvas Contract 1.4")
    if f"Contract: {CONTRACT_VERSION}" not in markdown_output.read_text(encoding="utf-8"):
        raise RuntimeError("Generated Markdown does not declare Canvas Contract 1.4")
    if "<!doctype html>" not in html_output.read_text(encoding="utf-8").lower():
        raise RuntimeError("Generated print report is not standalone HTML")

    invoke_cli("validate", "--input", str(json_output))
    compatibility = generate_brief(source).contract
    if compatibility.get("schema_version") != CONTRACT_VERSION:
        raise RuntimeError("Legacy Python core adapter did not emit the canonical contract")

def validate_demo_seed(temp_dir: Path) -> None:
    from app.services.storage import get_canvas
    from demo.seed_demo import seed

    database = temp_dir / "seed.sqlite3"
    seed(database)
    canvas = get_canvas(str(database), 1)
    if not canvas or canvas.get("schema_version") != CONTRACT_VERSION:
        raise RuntimeError("Demo seed did not create a Canvas Contract 1.4 record")

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
        "sources": [{"source_id":"source-release","source_type":"document","title":"Release evidence source"}],
        "evidence": [{"evidence_id":"evidence-release","source_id":"source-release","evidence_type":"summary","title":"Release evidence","summary":"The release gate completed."}],
        "claims": [{"claim_id":"claim-release","statement":"The release gate completed.","state":"supported","evidence_ids":["evidence-release"],"source_ids":["source-release"]}],
        "assumptions": [{"assumption_id":"assumption-release","statement":"Installer preservation will remain reliable.","owner":"Maintainer","criticality":"high","status":"planned","test_method":"Run disposable installer test","experiment_ids":["test-release"]}],
        "research_questions": [{"research_question_id":"research-question-release","question":"Does the upgrade preserve existing runtime data?","owner":"Maintainer","status":"investigating","priority":"high"}],
        "how_might_we": [{"hmw_id":"hmw-release","question":"How might we preserve release lineage across ideation and prototype decisions?","status":"selected"}],
        "framework": "ReleaseLens",
        "custom_frameworks": [{"key":"ReleaseLens","name":"Release Lens","description":"Review release integrity through a portable custom framework.","prompts":[{"label":"Integrity","question":"What must remain traceable after installation?"}]}],
        "prompt_packs": [{"prompt_pack_id":"prompt-pack-release","name":"Release prompts","prompts":[{"label":"Smallest check","question":"What is the smallest check that protects the upgrade?"}]}],
        "ideation_sessions": [{"session_id":"ideation-session-release","title":"Release ideation","mode":"convergent","framework_key":"ReleaseLens","prompt_pack_ids":["prompt-pack-release"],"challenge_ids":["challenge-primary"],"hmw_ids":["hmw-release"],"facilitator":"Maintainer","participants":["Reviewer"],"status":"complete"}],
        "ideas": [{"idea_id":"idea-release","title":"Preservation manifest","description":"Record data-preservation evidence with the release.","session_id":"ideation-session-release","challenge_id":"challenge-primary","hmw_id":"hmw-release","prompt_id":"prompt-001","author":"Maintainer","rationale":"Makes installer evidence reviewable.","status":"selected","vote_count":1,"voter_ids":["reviewer-001"],"prototype_ids":["prototype-001"],"assumption_ids":["assumption-release"],"evidence_ids":["evidence-release"]}],
        "idea_clusters": [{"cluster_id":"idea-cluster-release","name":"Release integrity","idea_ids":["idea-release"],"rationale":"Groups safeguards around traceable installation."}],
    })
    save_canvas(database, research_canvas, project_id=project["project_id"], change_note="Research validation")
    counts = research_asset_counts(database)
    required_counts = ["persona", "stakeholder", "journey", "source", "evidence", "claim", "assumption", "research_question"]
    if any(counts.get(asset_type, 0) < 1 for asset_type in required_counts):
        raise RuntimeError("Research asset library did not index the complete research and ledger record set")
    if not list_research_assets(database, asset_type="journey"):
        raise RuntimeError("Journey research asset was not queryable")
    from catalyst_canvas.ledger import build_handoff_package
    handoff = build_handoff_package(research_canvas, "knowledge_library")
    if handoff["handoff_contract"] != "catalyst-canvas-research-handoff/1.0" or not handoff["research"]["claims"]:
        raise RuntimeError("Research handoff package did not preserve ledger context")
    if research_canvas["ideation_summary"]["idea_count"] != 1 or research_canvas["ideation_summary"]["prototype_link_count"] != 1:
        raise RuntimeError("Ideation lineage and prototype links were not preserved")
    if research_canvas["framework"]["key"] != "ReleaseLens":
        raise RuntimeError("Custom framework did not resolve through the shared registry")
    if len(research_canvas.get("decision_criteria", [])) != 8 or len(research_canvas.get("decision_options", [])) != 1:
        raise RuntimeError("Prioritization records were not generated from the selected release idea")
    if research_canvas.get("prioritization_summary", {}).get("readiness") not in {"needs_review", "prioritized_not_ready"}:
        raise RuntimeError("Decision readiness did not preserve incomplete review state")

def validate_framework_package_cli(temp_dir: Path) -> None:
    contract_source = ROOT / "fixtures/canvas_contract_1_4.expected.json"
    package = temp_dir / "framework-package.json"
    imported = temp_dir / "framework-imported.json"
    invoke_cli("framework-export", "--input", str(contract_source), "--output", str(package), "--organization", "Release validation")
    package_payload = json.loads(package.read_text(encoding="utf-8"))
    if package_payload.get("package_contract") != "catalyst-canvas-framework-package/1.0" or not package_payload.get("frameworks"):
        raise RuntimeError("Framework package export omitted custom framework records")
    invoke_cli("framework-import", "--input", str(contract_source), "--package", str(package), "--output", str(imported))
    imported_payload = json.loads(imported.read_text(encoding="utf-8"))
    if not any(record.get("key") == "EquityLens" for record in imported_payload.get("custom_frameworks", [])):
        raise RuntimeError("Framework package import did not preserve the custom framework")

def validate_decision_handoff_cli(temp_dir: Path) -> None:
    # Validate the same package builder used by the CLI without spawning two
    # additional jsonschema-heavy Python interpreters inside the release gate.
    from catalyst_canvas.prioritization import build_decision_handoff_package

    contract = load_json("fixtures/canvas_contract_1_4.expected.json")
    decision = build_decision_handoff_package(contract, "decision_studio")
    workbench = build_decision_handoff_package(contract, "workbench")
    (temp_dir / "decision-studio-handoff.json").write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")
    (temp_dir / "workbench-handoff.json").write_text(json.dumps(workbench, indent=2) + "\n", encoding="utf-8")
    if decision.get("handoff_contract") != "catalyst-canvas-decision-handoff/1.0":
        raise RuntimeError("Decision Studio handoff contract marker is missing")
    context = decision.get("decision_context", {})
    if not context.get("alternatives") or not context.get("criteria") or not context.get("assumptions") or not context.get("evidence") or not context.get("unresolved_questions"):
        raise RuntimeError("Decision Studio handoff omitted required decision context")
    technical = workbench.get("technical_validation", {})
    if not technical.get("calculation_requirements") or not technical.get("modeling_questions") or not technical.get("inputs"):
        raise RuntimeError("Workbench handoff omitted technical-validation context")


def validate_migration_cli(temp_dir: Path, schema: dict) -> None:
    legacy = {
        "version": "1.1.1",
        "generated_at": "2026-07-16T10:00:00+00:00",
        "challenge": "Migrate a legacy export",
        "audience": "Maintainer",
        "goal": "Produce Canvas Contract 1.4",
        "constraint": "Flat fields",
        "framework": "AIDA",
        "persona": {"name": "Maintainer", "description": "Needs safe migration."},
        "prototype": {"title": "Migration test", "description": "A deterministic fixture."},
        "test_plan": {"signal": "Valid output", "method": "Run CLI", "learning_goal": "Verify migration"},
    }
    source = temp_dir / "legacy.json"
    output = temp_dir / "migrated.json"
    source.write_text(json.dumps(legacy), encoding="utf-8")
    invoke_cli("migrate", "--input", str(source), "--output", str(output))
    payload = json.loads(output.read_text(encoding="utf-8"))
    errors = list(Draft202012Validator(schema).iter_errors(payload))
    if errors:
        raise RuntimeError("Migrated CLI output failed Canvas Contract 1.4 validation")
    if payload["provenance"]["migrated_from"] != "legacy-core/1.1.1":
        raise RuntimeError("Migration provenance was not recorded")


def validate_cross_surface_fixture() -> None:
    from catalyst_canvas.adapters.flask import compact_to_contract
    from catalyst_canvas.engine import generate_canvas

    source = load_json("fixtures/canvas_contract_1_4.input.json")
    expected = load_json("fixtures/canvas_contract_1_4.expected.json")
    if generate_canvas(source, source_surface="python") != expected:
        raise RuntimeError("Python engine diverges from the shared fixture")
    if compact_to_contract(source) != expected:
        raise RuntimeError("Flask adapter diverges from the shared fixture")

    node = shutil.which("node")
    if node:
        run(node, "tests/js/test_contract_fixture.js")
        run(node, "tests/js/test_workspace.js")
        run(node, "tests/js/test_research_studio.js")
        run(node, "tests/js/test_ledger.js")
        run(node, "tests/js/test_ideation.js")
        run(node, "tests/js/test_prioritization.js")
    else:
        print("SKIP: Node.js is unavailable; browser fixture conformance will run in CI.")



def validate_prioritization_and_handoffs() -> None:
    from copy import deepcopy
    from catalyst_canvas.engine import generate_canvas
    from catalyst_canvas.prioritization import build_decision_handoff_package, normalize_sensitivity_views

    source = load_json("fixtures/canvas_contract_1_4.input.json")
    contract = generate_canvas(source, source_surface="release-validation")
    summary = contract.get("prioritization_summary", {})
    if summary.get("option_count") != 3 or summary.get("criterion_count", 0) < 8:
        raise RuntimeError("Prioritization fixture omitted alternatives or criteria")
    if not all(
        score.get("rationale") and score.get("basis") != "unknown" and score.get("confidence") != "unknown"
        for option in contract.get("decision_options", [])
        for score in option.get("criterion_scores", [])
    ):
        raise RuntimeError("Prioritization scores do not preserve rationale, basis, and confidence")

    options = deepcopy(contract["decision_options"])
    raw_before = {item["option_id"]: [score["raw_value"] for score in item["criterion_scores"]] for item in options}
    views = normalize_sensitivity_views(
        [{"name": "Release feasibility emphasis", "weight_overrides": [
            {"criterion_id": "criterion-feasibility", "weight": 50},
            {"criterion_id": "criterion-resource-efficiency", "weight": 40},
            {"criterion_id": "criterion-impact", "weight": 10},
        ]}],
        options=options,
        criteria=contract["decision_criteria"],
        generated_at=contract["updated_at"],
    )
    if [item["option_id"] for item in views[0]["rankings"]] == [item["option_id"] for item in views[1]["rankings"]]:
        raise RuntimeError("Sensitivity weighting did not change the release-fixture ranking")
    raw_after = {item["option_id"]: [score["raw_value"] for score in item["criterion_scores"]] for item in options}
    if raw_before != raw_after:
        raise RuntimeError("Sensitivity weighting overwrote raw criterion values")

    for target in ("decision_studio", "workbench"):
        package = build_decision_handoff_package(contract, target)
        context = package.get("decision_context", {})
        if package.get("handoff_contract") != "catalyst-canvas-decision-handoff/1.0":
            raise RuntimeError("Decision handoff contract marker is missing")
        for required in ("alternatives", "criteria", "assumptions", "evidence", "unresolved_questions"):
            if not context.get(required):
                raise RuntimeError(f"Decision handoff omitted {required}")
    if not build_decision_handoff_package(contract, "workbench").get("technical_validation", {}).get("inputs"):
        raise RuntimeError("Workbench handoff omitted calculation inputs")
    if "governance" not in build_decision_handoff_package(contract, "decision_studio"):
        raise RuntimeError("Decision Studio handoff omitted governance context")

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
    from scripts.build_plugin import build

    output = temp_dir / f"catalyst-canvas-demo-v{VERSION}.zip"
    build(output)
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
        phases = [
            ("generated browser assets", lambda: verify_generated_contract_asset(temp_dir)),
            ("sample generation", lambda: validate_generated_contract(temp_dir, schema)),
            ("demo seed", lambda: validate_demo_seed(temp_dir)),
            ("workspace persistence", lambda: validate_workspace_operations(temp_dir, workspace_schema)),
            ("legacy migration", lambda: validate_migration_cli(temp_dir, schema)),
            ("framework package", lambda: validate_framework_package_cli(temp_dir)),
            ("decision handoffs", lambda: validate_decision_handoff_cli(temp_dir)),
            ("cross-surface conformance", validate_cross_surface_fixture),
            ("prioritization invariants", validate_prioritization_and_handoffs),
            ("optional syntax tools", validate_optional_syntax_tools),
            ("WordPress package", lambda: validate_plugin_package(temp_dir)),
        ]
        for label, phase in phases:
            print(f"==> Validating {label}", flush=True)
            phase()
    print(f"PASS: Catalyst Canvas v{VERSION} / {CONTRACT_VERSION} / {WORKSPACE_CONTRACT_VERSION} release validation completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
