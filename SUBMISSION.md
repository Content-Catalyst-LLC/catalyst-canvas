# Catalyst Canvas v1.2.0 Submission Notes

## Release

**Catalyst Canvas v1.2.0 — Canonical Canvas Contract and Shared Engine**

This release establishes one authoritative data and generation model for Python, CLI, Flask, and WordPress.

## Included

- Canvas Contract 1.0 and strict JSON Schema;
- canonical generation, normalization, validation, migration, and export package;
- Flask and WordPress adapters;
- validated SQLite save/read/import/export boundaries;
- stable JSON, Markdown, and print HTML exports;
- legacy v1.0/v1.1 migration support;
- deterministic Python, Flask, and browser conformance fixtures;
- 31 pytest and 31 unittest checks plus Node conformance and package validation.

## Validate

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/validate_release.py
```

## Build WordPress

```bash
python scripts/build_plugin.py
```

Expected artifact:

```text
dist/catalyst-canvas-demo-v1.2.0.zip
```
