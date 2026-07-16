"""Flask presentation adapter for the canonical framework registry."""

from catalyst_canvas.frameworks import FRAMEWORKS, framework_prompt_strings, normalize_framework_key


def all_frameworks():
    return {key: value["name"] for key, value in FRAMEWORKS.items()}


def get_framework(name: str):
    return framework_prompt_strings(normalize_framework_key(name))
