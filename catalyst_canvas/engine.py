"""Authoritative Canvas Contract 1.5 generation engine."""

from __future__ import annotations

from typing import Any, Dict, Mapping

from .contract import build_contract


def generate_canvas(payload: Mapping[str, Any] | None = None, *, source_surface: str = "python") -> Dict[str, Any]:
    """Generate a validated canonical Canvas contract."""
    return build_contract(payload, source_surface=source_surface)
