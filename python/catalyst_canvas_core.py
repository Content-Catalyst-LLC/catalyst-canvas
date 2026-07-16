#!/usr/bin/env python3
"""Catalyst Canvas core brief generator.

This module intentionally avoids external runtime dependencies. It turns a compact
problem-framing input into a structured Canvas brief that can be exported as JSON
or Markdown and reviewed over time.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

try:
    from .catalyst_canvas_version import __version__
except ImportError:  # Direct script execution.
    from catalyst_canvas_version import __version__

FRAMEWORK_PROMPTS: Dict[str, List[str]] = {
    "AIDA": [
        "Attention: What concrete tension should the audience notice first?",
        "Interest: What evidence or story makes the problem worth caring about?",
        "Desire: What better state becomes imaginable and credible?",
        "Action: What small next step can be tested?",
    ],
    "JTBD": [
        "When situation: What situation creates the need?",
        "I want to: What progress is the user trying to make?",
        "So I can: What outcome matters?",
        "Constraint: What prevents the user from making progress today?",
    ],
    "Hero": [
        "Ordinary world: What is the current operating reality?",
        "Call: What pressure or opportunity forces change?",
        "Guide: What support helps the user move forward?",
        "Return: What measurable improvement should be visible?",
    ],
    "Matrix": [
        "Audience need: What question does this audience need answered?",
        "Evidence type: What proof would make the answer credible?",
        "Format: What artifact should carry the answer?",
        "Review signal: What would show that the artifact worked?",
    ],
}


@dataclass
class CatalystCanvasInput:
    challenge: str
    audience: str
    goal: str
    constraint: str
    framework: str = "AIDA"


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

    def to_markdown(self) -> str:
        hmw = "\n".join(f"- {item}" for item in self.how_might_we)
        prompts = "\n".join(f"- {item}" for item in self.ideation_prompts)
        assumptions = "\n".join(f"- {item}" for item in self.assumptions)
        review = "\n".join(f"- {item}" for item in self.review_questions)
        return f"""# Catalyst Canvas Brief

Version: {self.version}  
Generated: {self.generated_at}

## Challenge

{self.challenge}

## Audience

{self.audience}

## Goal

{self.goal}

## Constraint

{self.constraint}

## Persona

**{self.persona['name']}** — {self.persona['description']}

## Point of View

{self.point_of_view}

## How Might We

{hmw}

## Ideation Framework: {self.framework}

{prompts}

## Prototype Concept

**{self.prototype['title']}** — {self.prototype['description']}

## Test Plan

- **Signal:** {self.test_plan['signal']}
- **Method:** {self.test_plan['method']}
- **Learning goal:** {self.test_plan['learning_goal']}

## Assumptions

{assumptions}

## Review Questions

{review}
"""


def _clean(value: Any, fallback: str) -> str:
    text = str(value or "").strip()
    return text if text else fallback


def generate_brief(payload: Dict[str, Any]) -> CatalystCanvasBrief:
    """Generate a structured Catalyst Canvas brief from a dictionary payload."""

    inp = CatalystCanvasInput(
        challenge=_clean(payload.get("challenge"), "A team is working through an unclear sustainability or systems problem."),
        audience=_clean(payload.get("audience"), "A stakeholder who needs a clearer path forward."),
        goal=_clean(payload.get("goal"), "Create a more useful, testable, and reviewable next step."),
        constraint=_clean(payload.get("constraint"), "Limited time, limited evidence, and competing priorities."),
        framework=_clean(payload.get("framework"), "AIDA"),
    )

    framework = inp.framework if inp.framework in FRAMEWORK_PROMPTS else "AIDA"

    persona_name = inp.audience.split(",")[0].strip() or "Primary user"
    persona = {
        "name": persona_name,
        "description": (
            f"Needs help addressing: {inp.challenge}. The user wants {inp.goal.lower()} "
            f"while navigating {inp.constraint.lower()}."
        ),
    }

    pov = (
        f"{persona_name} needs a practical way to address '{inp.challenge}' so they can "
        f"{inp.goal.lower()} without ignoring the constraint: {inp.constraint}."
    )

    hmw = [
        f"How might we help {persona_name} make the challenge concrete enough to act on?",
        f"How might we turn the goal — {inp.goal} — into a small testable experiment?",
        f"How might we make the constraint visible without letting it stop progress?",
        "How might we document assumptions so the next decision can be reviewed?",
    ]

    prototype = {
        "title": "Reviewable Canvas Brief",
        "description": (
            "A one-page working artifact that captures the challenge, audience, goal, constraint, "
            "point of view, HMW prompts, prototype concept, assumptions, and test plan."
        ),
    }

    test_plan = {
        "signal": "A stakeholder can explain the problem, proposed next step, and key assumption in their own words.",
        "method": "Share the brief with 3–5 users or reviewers and capture confusion, objections, missing evidence, and next-step clarity.",
        "learning_goal": "Determine whether the framing is clear enough to guide a real prototype or decision.",
    }

    assumptions = [
        "The stated audience is the right primary user for the first iteration.",
        "The goal is specific enough to test with a small prototype.",
        "The constraint is material and should remain visible in the design process.",
        "A lightweight brief can reduce ambiguity before heavier implementation work begins.",
    ]

    review_questions = [
        "What claim in this brief needs stronger evidence?",
        "What assumption would most change the next step if it proved false?",
        "What user signal would show that the prototype is worth continuing?",
        "What should be rewritten to avoid overpromising?",
    ]

    return CatalystCanvasBrief(
        version=__version__,
        generated_at=datetime.now(timezone.utc).isoformat(),
        challenge=inp.challenge,
        audience=inp.audience,
        goal=inp.goal,
        constraint=inp.constraint,
        framework=framework,
        persona=persona,
        point_of_view=pov,
        how_might_we=hmw,
        ideation_prompts=FRAMEWORK_PROMPTS[framework],
        prototype=prototype,
        test_plan=test_plan,
        assumptions=assumptions,
        review_questions=review_questions,
    )


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, brief: CatalystCanvasBrief) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(asdict(brief), f, indent=2, ensure_ascii=False)
        f.write("\n")


def write_markdown(path: Path, brief: CatalystCanvasBrief) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(brief.to_markdown(), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a Catalyst Canvas brief.")
    parser.add_argument("--input", required=True, help="Path to input JSON file.")
    parser.add_argument("--output", help="Path to write output JSON brief.")
    parser.add_argument("--markdown", help="Path to write output Markdown brief.")
    args = parser.parse_args()

    payload = load_json(Path(args.input))
    brief = generate_brief(payload)

    if not args.output and not args.markdown:
        print(json.dumps(asdict(brief), indent=2, ensure_ascii=False))
        return 0

    if args.output:
        write_json(Path(args.output), brief)
        print(f"Wrote JSON brief: {args.output}")
    if args.markdown:
        write_markdown(Path(args.markdown), brief)
        print(f"Wrote Markdown brief: {args.markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
