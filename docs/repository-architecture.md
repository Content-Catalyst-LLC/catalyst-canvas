# Repository Architecture

Catalyst Canvas v1.6.0 is organized around one canonical domain package, explicit surface adapters, and workspace-scoped persistence.

- `VERSION` is the canonical release version.
- `catalyst_canvas/contract.py` owns Contract 1.3 normalization and validation.
- `catalyst_canvas/research.py` owns persona, stakeholder, journey, stage, behavioral-signal, and readiness normalization.
- `catalyst_canvas/ledger.py` owns sources, evidence, claims, assumptions, research planning, ledger indicators, and handoff packages.
- `catalyst_canvas/migrations.py` upgrades Contracts 1.0 and 1.1 plus recognized legacy formats.
- `catalyst_canvas/exporters.py` produces stable JSON, Markdown, and print HTML.
- `contracts/frameworks.json` is the authoritative framework registry.
- `schemas/catalyst_canvas_contract_1_3.schema.json` is the current Canvas schema.
- `schemas/catalyst_canvas_workspace_1_0.schema.json` is the project-registry schema.
- `app/services/storage.py` owns projects, immutable revisions, reusable assets, and project links.
- `fixtures/` supplies deterministic cross-surface conformance records.
- `wordpress/catalyst-canvas-demo/` provides the browser-local workspace, research surface, and ledger.
- `scripts/sync_contract_assets.py` derives browser contract data from repository sources.
- `scripts/validate_release.py` is the authoritative release gate.

Runtime databases, generated outputs, caches, and release ZIPs remain excluded from source control.
