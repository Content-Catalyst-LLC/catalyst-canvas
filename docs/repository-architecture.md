# Repository Architecture

Catalyst Canvas v1.4.0 is organized around one canonical domain package, explicit surface adapters, and workspace-scoped persistence.

- `VERSION` is the canonical release version.
- `catalyst_canvas/contract.py` owns Contract 1.1 normalization and validation.
- `catalyst_canvas/research.py` owns persona, stakeholder, journey, stage, and readiness normalization.
- `catalyst_canvas/migrations.py` upgrades Contract 1.0 and recognized legacy formats.
- `catalyst_canvas/exporters.py` produces stable JSON, Markdown, and print HTML.
- `contracts/frameworks.json` is the authoritative framework registry.
- `schemas/catalyst_canvas_contract_1_1.schema.json` is the current Canvas schema.
- `schemas/catalyst_canvas_workspace_1_0.schema.json` is the project-registry schema.
- `app/services/storage.py` owns projects, immutable revisions, research assets, and project links.
- `fixtures/` supplies deterministic cross-surface conformance records.
- `wordpress/catalyst-canvas-demo/` provides the browser-local workspace and research surface.
- `scripts/sync_contract_assets.py` derives browser contract data from repository sources.
- `scripts/validate_release.py` is the authoritative release gate.

Runtime databases, generated outputs, caches, and release ZIPs remain excluded from source control.
