# Catalyst Canvas

**Current release: v1.2.0 — Canonical Canvas Contract and Shared Engine**

Catalyst Canvas is the strategic-design and problem-framing workspace for Sustainable Catalyst. It turns ambiguous challenges into structured, reviewable work products covering audiences, personas, stakeholders, point-of-view statements, “How might we?” questions, ideation frameworks, evidence, assumptions, prototypes, tests, and review notes.

Version 1.2.0 replaces the repository's divergent data shapes and generation paths with **Canvas Contract 1.0** and a shared engine architecture.

## Canvas Contract 1.0

Every canonical saved or exported Canvas declares:

```json
{
  "schema_version": "catalyst-canvas/1.0",
  "canvas_id": "canvas-...",
  "revision_id": "revision-..."
}
```

The complete contract includes:

- title, lifecycle status, owner context, and timestamps;
- challenge, structured audience context, goal, and constraints;
- persona and stakeholder records;
- POV and HMW records;
- framework selection and generated prompts;
- evidence and assumptions;
- prototypes and tests;
- review notes and provenance.

The authoritative schema is `schemas/catalyst_canvas_contract_1_0.schema.json`.

## Shared engine architecture

The repository contains four contract-conformant surfaces:

1. **Canonical Python package** — `catalyst_canvas/` owns normalization, generation, validation, migration, and exporters.
2. **CLI and compatibility adapters** — generate, validate, migrate, and export without maintaining a second domain engine.
3. **Flask adapter** — maps existing workflow forms to Contract 1.0 and validates every SQLite save and read/import migration.
4. **WordPress browser adapter** — uses a shared JavaScript engine and generated framework registry to create equivalent canonical downloads without transmitting visitor inputs.

`fixtures/canvas_contract_1_0.input.json` and its expected output are consumed by Python, Flask, and Node conformance tests.

## Repository structure

```text
VERSION                            Canonical release version
catalyst_canvas/                   Canonical contract, engine, migration, adapters, exporters, CLI
contracts/frameworks.json          Authoritative framework registry
schemas/                           Canvas Contract 1.0 and legacy schema archive
fixtures/                          Shared deterministic conformance fixtures
app/                               Flask surface and validated SQLite persistence
python/                            Deprecated v1.x Python adapters
wordpress/catalyst-canvas-demo/    WordPress shortcode and shared browser engine
scripts/                           Asset sync, validation, and plugin packaging
Tests/                             Python and browser conformance suites
```

## Requirements

- Python 3.11, 3.12, or 3.13
- PHP for local plugin syntax validation
- Node.js for browser-engine syntax and conformance validation

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
cp .env.example .env
```

## Generate a canonical Canvas

```bash
python -m catalyst_canvas.cli generate \
  --input data/catalyst_canvas_sample_input.json \
  --json outputs/sample_canvas.json \
  --markdown outputs/sample_canvas.md \
  --html outputs/sample_canvas.html
```

Validate an existing contract:

```bash
python -m catalyst_canvas.cli validate --input outputs/sample_canvas.json
```

Migrate a recognized v1.0/v1.1 export:

```bash
python -m catalyst_canvas.cli migrate \
  --input legacy-canvas.json \
  --output canonical-canvas.json
```

Recognized legacy shapes include the original Python core export, the legacy wrapper export, and Flask's flat SQLite payload. Unknown or future contract versions are rejected with a migration message.

## Flask application

```bash
python demo/seed_demo.py
python app.py
```

Open <http://127.0.0.1:5000>.

Flask writes only validated Contract 1.0 payloads. Existing flat v1.x SQLite records are migrated on read and become canonical when next saved. The import endpoint is:

```text
POST /api/canvas/import
```

Stable exports are available as JSON, Markdown, and standalone print HTML.

## WordPress plugin

Build the plugin:

```bash
python scripts/sync_contract_assets.py
python scripts/build_plugin.py
```

The package is written to:

```text
dist/catalyst-canvas-demo-v1.2.0.zip
```

Activate it and use:

```text
[catalyst_canvas_demo]
```

The browser experience creates and downloads Canvas Contract 1.0 JSON locally. Inputs are not submitted to Sustainable Catalyst.

## Tests

```bash
python -m pytest tests
python -m unittest discover -s tests -v
node tests/js/test_contract_fixture.js
```

The authoritative release gate runs all tests, validates schemas and fixtures, checks generated assets, exercises CLI generation and migration, checks PHP and JavaScript syntax, and inspects the plugin ZIP:

```bash
python scripts/validate_release.py
```

## Compatibility

`python/catalyst_canvas_core.py` and `python/catalyst_canvas_brief.py` remain available as deprecated v1.x adapters. They delegate to `catalyst_canvas/` and no longer contain independent generation logic.

## Boundaries

Catalyst Canvas supports design thinking, research framing, and review. It does not certify strategy, adoption, impact, compliance, funding, product-market fit, or implementation success.

## License

MIT. See [LICENSE](LICENSE).
