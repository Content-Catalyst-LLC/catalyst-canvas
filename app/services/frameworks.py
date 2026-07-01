"""Design-thinking prompts and framework helpers."""

from __future__ import annotations

FRAMEWORKS = {
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
    "HERO": [
        "Human: Who is experiencing the friction?",
        "Evidence: What do we know, and how do we know it?",
        "Risk: Where could the proposed solution fail or mislead?",
        "Outcome: What would a better state look like?",
    ],
    "Assumption Matrix": [
        "High impact / high uncertainty: What must be tested first?",
        "High impact / low uncertainty: What can be documented and monitored?",
        "Low impact / high uncertainty: What can wait?",
        "Low impact / low uncertainty: What should be simplified or ignored?",
    ],
}


def get_framework(name: str) -> list[str]:
    return FRAMEWORKS.get(name, FRAMEWORKS["HERO"])


def all_frameworks() -> dict[str, list[str]]:
    return dict(FRAMEWORKS)
