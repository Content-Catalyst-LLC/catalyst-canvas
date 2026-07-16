#!/usr/bin/env python3
"""Deprecated v1.x core adapter over Canvas Contract 1.1.

New code should import ``catalyst_canvas.generate_canvas`` or use
``python -m catalyst_canvas.cli``. This module preserves the original dataclass
API and CLI flags for existing callers while delegating all generation to the
canonical shared engine.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import argparse
import json
from dataclasses import dataclass
from typing import Any, Dict, List

from catalyst_canvas import __version__, generate_canvas
from catalyst_canvas.exporters import export_json, export_markdown


@dataclass
class CatalystCanvasBrief:
    version: str
    generated_at: str
    challenge: str
    audience: str
    goal: str
    constraint: str
    framework: str
    persona: Dict[str, str]
    point_of_view: str
    how_might_we: List[str]
    ideation_prompts: List[str]
    prototype: Dict[str, str]
    test_plan: Dict[str, str]
    assumptions: List[str]
    review_questions: List[str]
    contract: Dict[str, Any]

    def to_markdown(self) -> str:
        return export_markdown(self.contract)


def generate_brief(payload: Dict[str, Any]) -> CatalystCanvasBrief:
    contract = generate_canvas(payload, source_surface="python")
    persona = contract["personas"][0]
    prototype = contract["prototypes"][0]
    test = contract["tests"][0]
    return CatalystCanvasBrief(
        version=__version__,
        generated_at=contract["updated_at"],
        challenge=contract["challenge"],
        audience=contract["audience"]["primary"],
        goal=contract["goal"],
        constraint=contract["constraints"][0]["statement"],
        framework=contract["framework"]["key"],
        persona={"name": persona["name"], "description": persona["description"]},
        point_of_view=contract["point_of_view"]["statement"],
        how_might_we=[item["question"] for item in contract["how_might_we"]],
        ideation_prompts=[f"{item['label']}: {item['question']}" for item in contract["framework"]["prompts"]],
        prototype={"title": prototype["title"], "description": prototype["description"]},
        test_plan={"signal": test["signal"], "method": test["method"], "learning_goal": test["learning_goal"]},
        assumptions=[item["statement"] for item in contract["assumptions"]],
        review_questions=[item["note"] for item in contract["review_notes"]],
        contract=contract,
    )


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a canonical Catalyst Canvas contract.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", help="Path to write Canvas Contract 1.1 JSON.")
    parser.add_argument("--markdown", help="Path to write Markdown.")
    args = parser.parse_args()
    contract = generate_canvas(load_json(Path(args.input)), source_surface="python")
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(export_json(contract), encoding="utf-8")
    if args.markdown:
        Path(args.markdown).parent.mkdir(parents=True, exist_ok=True)
        Path(args.markdown).write_text(export_markdown(contract), encoding="utf-8")
    if not args.output and not args.markdown:
        print(export_json(contract), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
