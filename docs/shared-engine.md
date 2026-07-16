# Shared Engine Architecture

The authoritative domain implementation lives in `catalyst_canvas/`.

- `contract.py` normalizes and validates Contract 1.0.
- `engine.py` exposes canonical generation.
- `migrations.py` handles recognized legacy payloads.
- `exporters.py` produces JSON, Markdown, and print HTML.
- `adapters/flask.py` maps the Flask workflow to and from the contract.
- `cli.py` exposes generation, validation, and migration commands.

The WordPress engine is implemented in JavaScript because it must run locally in the visitor's browser. Its framework registry is generated from `contracts/frameworks.json`, and its output is compared exactly with the Python fixture by `tests/js/test_contract_fixture.js`.
