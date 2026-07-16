#!/usr/bin/env python3
"""Run the authoritative Catalyst Canvas release validation suite."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def run(*args: str) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=ROOT, check=True)


def verify_version_markers() -> None:
    if not re.fullmatch(r"\d+\.\d+\.\d+", VERSION):
        raise RuntimeError(f"Invalid semantic version: {VERSION!r}")

    manifest = json.loads((ROOT / "canvas_manifest.json").read_text(encoding="utf-8"))
    schema = json.loads(
        (ROOT / "schemas" / "catalyst_canvas_brief.schema.json").read_text(encoding="utf-8")
    )
    plugin = (
        ROOT / "wordpress" / "catalyst-canvas-demo" / "catalyst-canvas-demo.php"
    ).read_text(encoding="utf-8")

    checks = {
        "manifest": manifest.get("version"),
        "schema": schema.get("properties", {}).get("version", {}).get("const"),
    }
    for label, value in checks.items():
        if value != VERSION:
            raise RuntimeError(f"{label} version {value!r} does not match VERSION {VERSION}")
    if not re.search(rf"Version:\s*{re.escape(VERSION)}(?:\s|$)", plugin):
        raise RuntimeError("WordPress plugin header does not match VERSION")
    if f"private const VERSION = '{VERSION}';" not in plugin:
        raise RuntimeError("WordPress plugin constant does not match VERSION")


def verify_source_tree() -> None:
    forbidden_files = [
        ROOT / "outputs" / "catalyst-canvas-demo.zip",
        ROOT / ".github" / "workflows" / "python-tests.yml",
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


def validate_generated_brief(temp_dir: Path) -> None:
    json_output = temp_dir / "sample.json"
    markdown_output = temp_dir / "sample.md"
    run(
        sys.executable,
        "python/catalyst_canvas_core.py",
        "--input",
        "data/catalyst_canvas_sample_input.json",
        "--output",
        str(json_output),
        "--markdown",
        str(markdown_output),
    )

    schema = json.loads(
        (ROOT / "schemas" / "catalyst_canvas_brief.schema.json").read_text(encoding="utf-8")
    )
    payload = json.loads(json_output.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(payload),
        key=lambda error: list(error.path),
    )
    if errors:
        messages = "; ".join(error.message for error in errors)
        raise RuntimeError(f"Generated sample failed schema validation: {messages}")
    if f"Version: {VERSION}" not in markdown_output.read_text(encoding="utf-8"):
        raise RuntimeError("Generated Markdown does not contain the canonical version")


def validate_optional_syntax_tools() -> None:
    php = shutil.which("php")
    if php:
        run(php, "-l", "wordpress/catalyst-canvas-demo/catalyst-canvas-demo.php")
    else:
        print("SKIP: PHP is unavailable; plugin syntax check not run locally.")

    node = shutil.which("node")
    if node:
        run(node, "--check", "wordpress/catalyst-canvas-demo/assets/catalyst-canvas-demo.js")
    else:
        print("SKIP: Node.js is unavailable; JavaScript syntax check not run locally.")


def validate_plugin_package(temp_dir: Path) -> None:
    output = temp_dir / f"catalyst-canvas-demo-v{VERSION}.zip"
    run(sys.executable, "scripts/build_plugin.py", "--output", str(output))
    with ZipFile(output) as archive:
        names = set(archive.namelist())
    required = {
        "catalyst-canvas-demo/catalyst-canvas-demo.php",
        "catalyst-canvas-demo/assets/catalyst-canvas-demo.css",
        "catalyst-canvas-demo/assets/catalyst-canvas-demo.js",
    }
    missing = sorted(required - names)
    if missing:
        raise RuntimeError(f"Plugin ZIP is missing required entries: {missing}")


def main() -> int:
    verify_version_markers()
    verify_source_tree()
    run(sys.executable, "-m", "compileall", "-q", "app", "python", "demo", "scripts")
    run(sys.executable, "-m", "pytest", "tests")
    run(sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v")
    with tempfile.TemporaryDirectory(prefix="catalyst-canvas-release-") as tmp:
        temp_dir = Path(tmp)
        validate_generated_brief(temp_dir)
        validate_optional_syntax_tools()
        validate_plugin_package(temp_dir)
    print(f"PASS: Catalyst Canvas v{VERSION} release validation completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
