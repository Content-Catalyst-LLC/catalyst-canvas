# Shared Engine Architecture

The authoritative domain implementation lives in `catalyst_canvas/`.

- `contract.py` normalizes and validates Canvas Contract 1.2.
- `research.py` normalizes personas, stakeholders, journeys, stages, behavioral signals, and research readiness.
- `ledger.py` normalizes source, evidence, claim, assumption, research-question, interview-guide, observation-note, summary, and handoff records.
- `engine.py` exposes canonical generation.
- `migrations.py` handles Contracts 1.0 and 1.1 plus recognized legacy payloads.
- `exporters.py` produces JSON, Markdown, and print HTML.
- `adapters/flask.py` maps Flask forms to and from the contract.
- `workspaces.py` validates project registry records.
- `cli.py` exposes generation, validation, and migration commands.

The WordPress engine is implemented in JavaScript because it must run locally in the visitor's browser. Its release and framework registry are generated from repository sources, and its output is compared exactly with the Python Contract 1.2 fixture by Node tests.
