#!/usr/bin/env python3
"""Catalyst Canvas brief generator.

A dependency-free companion to the WordPress demo. It turns a design-thinking
prompt into a reviewable JSON brief with persona, POV, HMW prompts, ideas,
prototype concept, and test plan.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, List

FRAMEWORK_IDEAS: Dict[str, List[str]] = {
    "AIDA": [
        "Lead with the audience's urgent problem",
        "Show the evidence behind the program claim",
        "Translate impact into a concrete stakeholder benefit",
        "Close with a low-friction next action",
    ],
    "JTBD": [
        "Name the functional job the user needs done",
        "Address the emotional anxiety behind the decision",
        "Reduce switching costs with a simple first step",
        "Identify what current habit the prototype must replace",
    ],
    "Hero": [
        "Frame the user as the protagonist",
        "Name the obstacle that makes progress difficult",
        "Introduce the tool as a guide, not the hero",
        "Show the transformed future state after the work is reviewed",
    ],
    "Matrix": [
        "Create one evergreen explainer",
        "Create one timely update",
        "Create one practical worksheet",
        "Create one stakeholder-facing proof point",
    ],
}


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


def _clean(value: str, fallback: str) -> str:
    value = (value or "").strip()
    return value if value else fallback


def _sentence(value: str) -> str:
    value = " ".join((value or "").strip().split())
    if not value:
        return ""
    return value[:1].upper() + value[1:].rstrip(".!?") + "."


def build_canvas_brief(data: CanvasInput) -> CanvasBrief:
    challenge = _clean(data.challenge, "A team needs a clearer way to turn a messy problem into structured action")
    audience = _clean(data.audience, "Project lead")
    goal = _clean(data.goal, "build a reviewable plan")
    constraint = _clean(data.constraint, "limited time, limited data, and stakeholder pressure")
    framework = data.framework if data.framework in FRAMEWORK_IDEAS else "AIDA"

    hmw = [
        f"How might we help {audience} make progress without hiding uncertainty?",
        "How might we turn the challenge into a testable workflow?",
        "How might we make evidence, assumptions, and next steps visible?",
        f"How might we reduce friction created by {constraint}?",
    ]

    return CanvasBrief(
        title=f"Catalyst Canvas draft for {audience}",
        summary=_sentence(
            f"This canvas frames a design challenge for {audience}: {challenge} "
            f"The working goal is to {goal} while accounting for {constraint}"
        ),
        persona_name=audience,
        persona_body=_sentence(
            f"{audience} is trying to {goal} but faces {constraint} "
            "The persona needs clear evidence, usable structure, and a next step that does not overpromise"
        ),
        pov=_sentence(
            f"{audience} needs a way to {goal} because {challenge} The solution must respect {constraint}"
        ),
        hmw=hmw,
        ideas=list(FRAMEWORK_IDEAS[framework]),
        prototype_title=f"{framework} concept card",
        prototype_body=_sentence(
            f"Build a lightweight prototype that helps {audience} {goal} "
            "It should expose sources, assumptions, and decision points before a final recommendation is made"
        ),
        test_plan={
            "what_to_test": "Whether the draft canvas helps the user explain the problem, evidence, and next step more clearly.",
            "signal_to_watch": "A reviewer can identify the claim, source, assumption, and recommended next action without extra explanation.",
            "risk": "The prototype may still overstate confidence if data quality and uncertainty are not made explicit.",
            "next_iteration": "Run the canvas with one real stakeholder and revise the claim, indicator, and prototype before publishing.",
        },
        boundary="Structured design-thinking support only. Review before relying on this output.",
    )


def export_payload(data: CanvasInput) -> Dict[str, object]:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tool": "Catalyst Canvas Demo",
        "version": "1.0.0",
        "inputs": asdict(data),
        "canvas": asdict(build_canvas_brief(data)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a Catalyst Canvas JSON brief.")
    parser.add_argument("--challenge", required=True)
    parser.add_argument("--audience", required=True)
    parser.add_argument("--goal", required=True)
    parser.add_argument("--constraint", required=True)
    parser.add_argument("--framework", default="AIDA", choices=sorted(FRAMEWORK_IDEAS))
    parser.add_argument("--output", default="-")
    args = parser.parse_args()

    payload = export_payload(CanvasInput(
        challenge=args.challenge,
        audience=args.audience,
        goal=args.goal,
        constraint=args.constraint,
        framework=args.framework,
    ))
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.output == "-":
        print(text)
    else:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

