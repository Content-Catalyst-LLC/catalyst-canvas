# Catalyst Canvas

**Current release: v1.3.0 — Persistent Projects and Workspace Management**

Catalyst Canvas is the strategic-design and problem-framing workspace for Sustainable Catalyst. It turns ambiguous challenges into structured, reviewable projects covering audiences, personas, stakeholders, point-of-view statements, “How might we?” questions, ideation frameworks, evidence, assumptions, prototypes, tests, and review notes.

Version 1.3.0 adds durable workspaces, projects, immutable revision history, autosave, search, duplication, archive/restore, and browser-local WordPress persistence while retaining Canvas Contract 1.0.

## Contracts

Every saved Canvas declares:

```json
{
  "schema_version": "catalyst-canvas/1.0",
  "canvas_id": "canvas-...",
  "revision_id": "revision-..."
}
```

Every project registry record declares:

```json
{
  "schema_version": "catalyst-canvas-workspace/1.0",
  "workspace_id": "workspace-...",
  "project_id": "project-..."
}
```

Authoritative schemas:

- `schemas/catalyst_canvas_contract_1_0.schema.json`
- `schemas/catalyst_canvas_workspace_1_0.schema.json`

## Workspace model

```text
Workspace
└── Project
    ├── metadata and lifecycle status
    ├── current revision pointer
    └── immutable Canvas Contract 1.0 revisions
```

Manual saves, autosaves, imports, and revision restoration create new revision records. Historical payloads are never overwritten. Projects can be searched, duplicated, archived, restored, exported, and isolated by workspace.

Existing v1.2 `canvas_briefs` rows migrate automatically into the default local workspace. The migration is idempotent and preserves old numeric export URLs.

## Shared surfaces

1. **Canonical Python package** — normalization, generation, validation, migration, workspace contracts, and exporters.
2. **CLI and compatibility adapters** — canonical generation, validation, migration, JSON, Markdown, and print HTML.
3. **Flask workspace** — SQLite projects, revisions, search, archive/restore, duplicate, autosave, and workspace-scoped APIs.
4. **WordPress browser workspace** — localStorage-backed project and revision management without transmitting visitor inputs.

## Repository structure

```text
VERSION                            Canonical release version
catalyst_canvas/                   Canvas and workspace contracts, engine, migration, exporters
schemas/                           Canvas Contract 1.0, Workspace Contract 1.0, legacy archive
app/                               Flask workspace routes and SQLite persistence
fixtures/                          Cross-surface deterministic Canvas fixtures
wordpress/catalyst-canvas-demo/    Browser engine and local project workspace
scripts/                           Asset sync, validation, and plugin packaging
tests/                             Python, Flask, storage, route, and Node tests
```

## Requirements

- Python 3.11, 3.12, or 3.13
- PHP for local plugin syntax validation
- Node.js for browser syntax and conformance validation

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
cp .env.example .env
```

Run the Flask workspace:

```bash
python demo/seed_demo.py
python app.py
```

Open `http://127.0.0.1:5000`.

## CLI

Generate a canonical Canvas:

```bash
python -m catalyst_canvas.cli generate \
  --input data/catalyst_canvas_sample_input.json \
  --json outputs/sample_canvas.json \
  --markdown outputs/sample_canvas.md \
  --html outputs/sample_canvas.html
```

Validate or migrate:

```bash
python -m catalyst_canvas.cli validate --input outputs/sample_canvas.json
python -m catalyst_canvas.cli migrate --input legacy-canvas.json --output canonical-canvas.json
```

## Flask APIs

```text
GET  /api/workspaces
GET  /api/projects?q=&status=
GET  /api/projects/<project_id>
PATCH /api/projects/<project_id>
GET  /api/projects/<project_id>/revisions
POST /api/projects/<project_id>/autosave
POST /api/canvas/import
GET  /api/contract/schema.json
GET  /api/workspace-contract/schema.json
```

All project endpoints enforce the active workspace boundary.

## WordPress plugin

Build the client-side workspace plugin:

```bash
python scripts/sync_contract_assets.py
python scripts/build_plugin.py
```

Install `dist/catalyst-canvas-demo-v1.3.0.zip`, activate it, and add:

```text
[catalyst_canvas_demo]
```

Projects and revisions are saved only in the current browser's localStorage. Clearing site data removes them.

## Validation

```bash
python scripts/validate_release.py
```

The release gate runs Python tests under pytest and unittest, schemas, v1.2 storage migration, Flask workspace workflows, cross-surface fixtures, Node browser tests, optional PHP/JavaScript syntax checks, sample exports, and WordPress package inspection.

## Boundaries

Catalyst Canvas supports problem framing, structured review, and experimentation. It does not certify evidence, guarantee product-market fit, provide legal or compliance advice, or guarantee implementation outcomes.

## License

MIT. See `LICENSE`.
