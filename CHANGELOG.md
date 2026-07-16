# Changelog

All notable changes to Catalyst Canvas are documented here.

## 1.1.1 — 2026-07-16

### Repository integrity

- Added `VERSION` as the canonical release version source.
- Synchronized the project manifest, Python exports, JSON Schema, WordPress plugin header, WordPress asset version, documentation, and package naming to v1.1.1.
- Added the MIT `LICENSE` file.
- Added `.env.example` and required `CATALYST_CANVAS_SECRET` outside development, local, and test environments.
- Removed committed SQLite runtime databases and the generated WordPress ZIP.
- Expanded `.gitignore` for environments, caches, runtime databases, and generated release artifacts.

### Python and tests

- Made the `python/` utilities importable as a package from the repository root.
- Reclassified `catalyst_canvas_brief.py` as a deprecated v1.x compatibility adapter over `catalyst_canvas_core.py`.
- Added the canonical version to core JSON and Markdown outputs.
- Rebuilt the tests so both `python -m pytest tests` and `python -m unittest discover -s tests -v` execute the same integrity suite.
- Added application secret configuration, schema validation, version synchronization, and source-tree hygiene tests.
- Closed SQLite connections deterministically to prevent resource leaks during application and test initialization.

### CI and packaging

- Consolidated the two competing workflows into one authoritative GitHub Actions release-validation workflow.
- Added `scripts/validate_release.py` for repeatable local and CI validation.
- Added `scripts/build_plugin.py` for deterministic, versioned WordPress plugin packaging.
- Added PHP syntax, JavaScript syntax, JSON Schema, sample generation, and plugin-content validation gates.

## 1.1.0 — 2026-07-01

- Added the WordPress shortcode demo plugin for the Catalyst Canvas page.
- Added the dependency-light Python core generator and CLI.
- Added JSON Schema, sample input, example output notes, and documentation.
- Added the review checklist, repository architecture, export specification, and WordPress installation instructions.
- Added the initial Python tests and GitHub Actions workflows.
