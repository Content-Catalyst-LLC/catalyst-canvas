"""Canonical Catalyst Canvas repository version loader."""

from __future__ import annotations

from pathlib import Path

_VERSION_FILE = Path(__file__).resolve().parents[1] / "VERSION"


def read_version() -> str:
    """Return the canonical repository version."""
    version = _VERSION_FILE.read_text(encoding="utf-8").strip()
    if not version:
        raise RuntimeError(f"Catalyst Canvas version file is empty: {_VERSION_FILE}")
    return version


__version__ = read_version()
