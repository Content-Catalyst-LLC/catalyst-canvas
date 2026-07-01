"""Point-of-view and How Might We helpers."""

from __future__ import annotations


def clean(value: str | None) -> str:
    return " ".join((value or "").strip().split())


def build_point_of_view(persona: str, need: str, insight: str) -> str:
    persona = clean(persona) or "A defined audience"
    need = clean(need) or "needs a clearer way to make progress"
    insight = clean(insight) or "because the current situation creates uncertainty and friction"
    return f"{persona} needs {need} because {insight}."


def build_hmw(challenge: str, audience: str, goal: str, constraint: str = "") -> str:
    challenge = clean(challenge) or "the current challenge"
    audience = clean(audience) or "the intended audience"
    goal = clean(goal) or "make meaningful progress"
    constraint = clean(constraint)
    if constraint:
        return f"How might we help {audience} {goal} while working within {constraint}?"
    return f"How might we help {audience} {goal} in response to {challenge}?"
