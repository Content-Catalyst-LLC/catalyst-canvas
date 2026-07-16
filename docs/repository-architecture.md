# Repository Architecture

Catalyst Canvas v2.0.0 is organized around one canonical domain package, explicit surface adapters, and workspace-scoped persistence.

- `catalyst_canvas/contract.py` owns Contract 2.0 normalization and validation.
- `catalyst_canvas/experiments.py` owns prototype and experiment records and handoffs.
- `catalyst_canvas/migrations.py` owns recognized historical migrations.
- `app/` adapts the contract to Flask routes and SQLite workspaces.
- `wordpress/catalyst-canvas-demo/` adapts the same contract to a browser-local shortcode workspace.
- `scripts/` generates browser registries, validates releases, and builds the plugin.
- `fixtures/` supplies exact cross-surface conformance inputs and outputs.

Runtime databases, local environment files, and generated archives are not source artifacts and remain ignored.
