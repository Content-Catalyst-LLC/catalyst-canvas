"""Flask presentation adapter for the canonical framework registry."""

from catalyst_canvas.frameworks import framework_prompt_strings, framework_record, framework_registry, normalize_framework_key


def all_frameworks(custom_frameworks=None):
    return framework_registry(custom_frameworks)


def get_framework(name: str, custom_frameworks=None):
    return framework_prompt_strings(normalize_framework_key(name, custom_frameworks), custom_frameworks)


def get_framework_record(name: str, custom_frameworks=None):
    return framework_record(name, custom_frameworks)
