# Changelog

All notable changes to Catalyst Canvas are documented here.

## 1.2.0 — 2026-07-16

### Canvas Contract 1.0

- Added the canonical `catalyst_canvas/` package for normalization, generation, JSON Schema validation, migrations, surface adapters, and stable exporters.
- Introduced `catalyst-canvas/1.0` with Canvas and revision IDs, lifecycle and owner metadata, structured audiences, personas, stakeholders, POV/HMW records, framework prompts, evidence, assumptions, prototypes, tests, review notes, and provenance.
- Added the authoritative `schemas/catalyst_canvas_contract_1_0.schema.json` schema and archived the v1.1 brief schema under `schemas/legacy/`.
- Added explicit migration paths for legacy Python core exports, legacy wrapper exports, and Flask flat records, with useful rejection messages for unknown or future contracts.

### Shared engines and adapters

- Replaced the Flask-specific generation engine with a form/view adapter over the canonical package.
- Converted the legacy Python core and brief modules into compatibility adapters over the canonical engine.
- Added a WordPress browser engine that creates canonical contracts and exports contract-aware JSON and Markdown locally.
- Moved framework definitions into `contracts/frameworks.json` and added deterministic generation of the browser contract-data asset.
- Removed the unused Flask POV/HMW engine to eliminate a remaining divergent generation path.

### Persistence, exports, and validation

- Enforced Contract 1.0 validation on Flask saves, reads, imports, and exports.
- Added the Flask `POST /api/canvas/import` migration endpoint and JSON Schema endpoint.
- Added stable JSON, Markdown, and standalone print-HTML exporters.
- Added deterministic Python/Flask/WordPress fixtures and Node conformance tests.
- Expanded the release suite to 31 pytest and 31 unittest checks plus browser, CLI migration, syntax, generated-asset, schema, and package validation.

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
