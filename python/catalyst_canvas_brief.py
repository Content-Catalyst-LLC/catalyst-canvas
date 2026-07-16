#!/usr/bin/env python3
"""Deprecated v1.x compatibility adapter for Catalyst Canvas briefs.

New code should use :mod:`catalyst_canvas_core`. This module remains available
through the v1.x line so existing imports and command-line workflows continue
to work, but it delegates generation to the maintained core engine rather than
carrying a second independent implementation.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from typing import Dict, List

try:
    from .catalyst_canvas_core import generate_brief
    from .catalyst_canvas_version import __version__
except ImportError:  # Direct script execution.
    from catalyst_canvas_core import generate_brief
    from catalyst_canvas_version import __version__


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
    """Return the legacy brief shape using the maintained core generator."""
    core = generate_brief(asdict(data))
    return CanvasBrief(
        title=f"Catalyst Canvas draft for {core.audience}",
        summary=(
            f"This canvas frames a design challenge for {core.audience}: "
            f"{core.challenge}. The working goal is to {core.goal.lower()} "
            f"while accounting for {core.constraint.lower()}."
        ),
        persona_name=core.persona["name"],
        persona_body=core.persona["description"],
        pov=core.point_of_view,
        hmw=list(core.how_might_we),
        ideas=list(core.ideation_prompts),
        prototype_title=core.prototype["title"],
        prototype_body=core.prototype["description"],
        test_plan={
            "what_to_test": core.test_plan["learning_goal"],
            "signal_to_watch": core.test_plan["signal"],
            "risk": "The prototype may overstate confidence if assumptions and evidence gaps are not explicit.",
            "next_iteration": core.test_plan["method"],
        },
        boundary="Structured design-thinking support only. Review before relying on this output.",
    )


def export_payload(data: CanvasInput) -> Dict[str, object]:
    """Export the legacy wrapper with the canonical repository version."""
    core = generate_brief(asdict(data))
    return {
        "generated_at": core.generated_at,
        "tool": "Catalyst Canvas Demo",
        "version": __version__,
        "inputs": asdict(data),
        "canvas": asdict(build_canvas_brief(data)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a legacy-compatible Catalyst Canvas JSON brief."
    )
    parser.add_argument("--challenge", required=True)
    parser.add_argument("--audience", required=True)
    parser.add_argument("--goal", required=True)
    parser.add_argument("--constraint", required=True)
    parser.add_argument("--framework", default="AIDA", choices=("AIDA", "Hero", "JTBD", "Matrix"))
    parser.add_argument("--output", default="-")
    args = parser.parse_args()

    payload = export_payload(
        CanvasInput(
            challenge=args.challenge,
            audience=args.audience,
            goal=args.goal,
            constraint=args.constraint,
            framework=args.framework,
        )
    )
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.output == "-":
        print(text)
    else:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
