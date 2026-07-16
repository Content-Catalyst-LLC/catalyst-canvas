"""Command-line interface for Canvas Contract 1.5."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from .engine import generate_canvas
from .exporters import export_json, export_markdown, export_print_html
from .migrations import migrate_payload
from .contract import validate_contract
from .frameworks import export_framework_package, import_framework_package
from .prioritization import build_decision_handoff_package


def load_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Canvas input must be a JSON object.")
    return payload


def write(path: Path | None, content: str) -> None:
    if path is None:
        print(content, end="")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def command_generate(args: argparse.Namespace) -> int:
    payload = load_json(args.input)
    contract = generate_canvas(payload, source_surface="cli")
    outputs = [args.json_output, args.markdown, args.html]
    if not any(outputs):
        write(None, export_json(contract))
    if args.json_output:
        write(args.json_output, export_json(contract))
    if args.markdown:
        write(args.markdown, export_markdown(contract))
    if args.html:
        write(args.html, export_print_html(contract))
    return 0


def command_validate(args: argparse.Namespace) -> int:
    payload = load_json(args.input)
    validate_contract(payload)
    print(f"PASS: {args.input} is a valid Canvas Contract 1.5 payload.")
    return 0


def command_migrate(args: argparse.Namespace) -> int:
    payload = load_json(args.input)
    result = migrate_payload(payload, source_surface="migration")
    write(args.output, export_json(result.contract))
    if result.migrated_from:
        print(f"Migrated {result.migrated_from} to {result.contract['schema_version']}.")
    return 0



def command_framework_export(args: argparse.Namespace) -> int:
    payload = load_json(args.input)
    contract = migrate_payload(payload, source_surface="cli").contract
    package = export_framework_package(
        contract.get("custom_frameworks"),
        organization=args.organization or contract.get("metadata", {}).get("organization", ""),
    )
    write(args.output, json.dumps(package, indent=2, ensure_ascii=False) + "\n")
    return 0


def command_framework_import(args: argparse.Namespace) -> int:
    payload = load_json(args.input)
    contract = migrate_payload(payload, source_surface="cli").contract
    package = load_json(args.package)
    incoming = import_framework_package(package)
    merged = {record["key"]: record for record in contract.get("custom_frameworks", [])}
    merged.update({record["key"]: record for record in incoming})
    updated = generate_canvas(
        {**contract, "custom_frameworks": list(merged.values())},
        source_surface="cli",
    )
    write(args.output, export_json(updated))
    return 0

def command_decision_handoff(args: argparse.Namespace) -> int:
    payload = load_json(args.input)
    contract = migrate_payload(payload, source_surface="cli").contract
    package = build_decision_handoff_package(contract, args.target)
    write(args.output, json.dumps(package, indent=2, ensure_ascii=False) + "\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate, validate, migrate, and export Catalyst Canvas contracts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate", help="Generate Canvas Contract 1.5 from compact JSON input.")
    generate.add_argument("--input", type=Path, required=True)
    generate.add_argument("--json", dest="json_output", type=Path)
    generate.add_argument("--markdown", type=Path)
    generate.add_argument("--html", type=Path)
    generate.set_defaults(func=command_generate)

    validate = subparsers.add_parser("validate", help="Validate a Canvas Contract 1.5 JSON document.")
    validate.add_argument("--input", type=Path, required=True)
    validate.set_defaults(func=command_validate)

    migrate = subparsers.add_parser("migrate", help="Migrate a recognized legacy or Canvas Contract 1.0-1.3 export.")
    migrate.add_argument("--input", type=Path, required=True)
    migrate.add_argument("--output", type=Path, required=True)
    migrate.set_defaults(func=command_migrate)

    framework_export = subparsers.add_parser("framework-export", help="Export custom frameworks as a portable framework package.")
    framework_export.add_argument("--input", type=Path, required=True, help="Canvas Contract JSON containing custom frameworks.")
    framework_export.add_argument("--output", type=Path, required=True)
    framework_export.add_argument("--organization", default="")
    framework_export.set_defaults(func=command_framework_export)

    framework_import = subparsers.add_parser("framework-import", help="Import a portable framework package into a Canvas Contract.")
    framework_import.add_argument("--input", type=Path, required=True, help="Canvas Contract JSON to update.")
    framework_import.add_argument("--package", type=Path, required=True)
    framework_import.add_argument("--output", type=Path, required=True)
    framework_import.set_defaults(func=command_framework_import)

    decision_handoff = subparsers.add_parser("decision-handoff", help="Export a Decision Studio or Workbench handoff package.")
    decision_handoff.add_argument("--input", type=Path, required=True)
    decision_handoff.add_argument("--target", choices=["decision_studio", "workbench"], required=True)
    decision_handoff.add_argument("--output", type=Path, required=True)
    decision_handoff.set_defaults(func=command_decision_handoff)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
