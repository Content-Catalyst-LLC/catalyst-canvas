"""Flask compatibility facade over the canonical Canvas Contract 1.0 package."""

from __future__ import annotations

from typing import Any, Dict, Mapping

from catalyst_canvas.adapters.flask import contract_to_form, default_contract, form_to_contract
from catalyst_canvas.exporters import export_json, export_markdown, export_print_html


def normalize_form(form: Mapping[str, Any], existing: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    return form_to_contract(form, existing)


def to_form(contract: Mapping[str, Any], storage_id: int | None = None) -> Dict[str, Any]:
    return contract_to_form(contract, storage_id=storage_id)


def new_canvas() -> Dict[str, Any]:
    return default_contract()


def to_markdown(canvas: Mapping[str, Any]) -> str:
    return export_markdown(canvas)


def to_pretty_json(canvas: Mapping[str, Any]) -> str:
    return export_json(canvas)


def to_print_html(canvas: Mapping[str, Any]) -> str:
    return export_print_html(canvas)
