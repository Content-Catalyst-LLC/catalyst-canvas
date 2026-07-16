#!/usr/bin/env python3
"""Deprecated v1.x compatibility adapter over Canvas Contract 2.0."""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import argparse
import json
from dataclasses import asdict, dataclass
from typing import Dict, List

from catalyst_canvas import __version__, generate_canvas


@dataclass(frozen=True)
class CanvasInput:
    challenge: str
    audience: str
    goal: str
    constraint: str
    framework: str = "AIDA"


@dataclass(frozen=True)
class CanvasBrief:
    title: str
    summary: str
    persona_name: str
    persona_body: str
    pov: str
    hmw: List[str]
    ideas: List[str]
    prototype_title: str
    prototype_body: str
    test_plan: Dict[str, str]
    boundary: str


def build_canvas_brief(data: CanvasInput) -> CanvasBrief:
    contract = generate_canvas(asdict(data), source_surface="python")
    persona = contract["personas"][0]
    prototype = contract["prototypes"][0]
    test = contract["tests"][0]
    return CanvasBrief(
        title=f"Catalyst Canvas draft for {contract['audience']['primary']}",
        summary=(
            f"This canvas frames a design challenge for {contract['audience']['primary']}: "
            f"{contract['challenge']}. The working goal is to {contract['goal'].lower()} "
            f"while accounting for {contract['constraints'][0]['statement'].lower()}."
        ),
        persona_name=persona["name"],
        persona_body=persona["description"],
        pov=contract["point_of_view"]["statement"],
        hmw=[item["question"] for item in contract["how_might_we"]],
        ideas=[f"{item['label']}: {item['question']}" for item in contract["framework"]["prompts"]],
        prototype_title=prototype["title"],
        prototype_body=prototype["description"],
        test_plan={
            "what_to_test": test["learning_goal"],
            "signal_to_watch": test["signal"],
            "risk": "The prototype may overstate confidence if assumptions and evidence gaps are not explicit.",
            "next_iteration": test["method"],
        },
        boundary="Structured design-thinking support only. Review before relying on this output.",
    )


def export_payload(data: CanvasInput) -> Dict[str, object]:
    contract = generate_canvas(asdict(data), source_surface="python")
    return {
        "generated_at": contract["updated_at"],
        "tool": "Catalyst Canvas Demo",
        "version": __version__,
        "inputs": asdict(data),
        "canvas": asdict(build_canvas_brief(data)),
        "canonical_contract": contract,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a legacy-compatible Canvas wrapper.")
    parser.add_argument("--challenge", required=True)
    parser.add_argument("--audience", required=True)
    parser.add_argument("--goal", required=True)
    parser.add_argument("--constraint", required=True)
    parser.add_argument("--framework", default="AIDA", choices=("AIDA", "Hero", "JTBD", "Matrix"))
    parser.add_argument("--output", default="-")
    args = parser.parse_args()
    payload = export_payload(CanvasInput(args.challenge, args.audience, args.goal, args.constraint, args.framework))
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.output == "-":
        print(text)
    else:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
