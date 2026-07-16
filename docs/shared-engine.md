# Shared Engine Architecture

The authoritative domain implementation lives in `catalyst_canvas/`.

- `contract.py` normalizes and validates Canvas Contract 1.1.
- `research.py` normalizes personas, stakeholders, journeys, stages, and research readiness.
- `engine.py` exposes canonical generation.
- `migrations.py` handles Contract 1.0 and recognized legacy payloads.
- `exporters.py` produces JSON, Markdown, and print HTML.
- `adapters/flask.py` maps Flask forms to and from the contract.
- `workspaces.py` validates project registry records.
- `cli.py` exposes generation, validation, and migration commands.

The WordPress engine is implemented in JavaScript because it must run locally in the visitor's browser. Its release and framework registry are generated from repository sources, and its output is compared exactly with the Python Contract 1.1 fixture by Node tests.
