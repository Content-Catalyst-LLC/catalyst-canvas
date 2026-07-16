# Repository Architecture

Catalyst Canvas v1.2.0 is organized around one canonical domain package and explicit surface adapters.

- `VERSION` is the canonical release version.
- `catalyst_canvas/` owns Contract 1.0 generation, validation, migrations, exports, and adapters.
- `contracts/frameworks.json` is the authoritative framework registry.
- `schemas/catalyst_canvas_contract_1_0.schema.json` is the authoritative data contract.
- `fixtures/` supplies deterministic cross-surface conformance records.
- `app/` and `templates/` provide the Flask surface.
- `python/` retains deprecated v1.x adapters.
- `wordpress/catalyst-canvas-demo/` provides the browser surface.
- `scripts/sync_contract_assets.py` derives browser framework data from the repository registry.
- `scripts/validate_release.py` is the authoritative release gate.

Runtime databases, generated outputs, and release ZIPs remain excluded from source control.
