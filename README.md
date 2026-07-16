# Catalyst Canvas

**Current release: v1.6.0 — Framework and Ideation Studio**

Catalyst Canvas is the strategic-design and problem-framing workspace for Sustainable Catalyst. It turns ambiguous challenges into structured, reviewable projects covering audiences, personas, stakeholders, journeys, sources, evidence, claims, assumptions, research questions, ideation, prototypes, experiments, review notes, and institutional handoffs.

Version 1.6.0 adds a data-driven framework registry and a traceable ideation workspace. Built-in and custom frameworks now use the same portable definition, while idea cards preserve the challenge, HMW prompt, author, rationale, votes, clusters, merges, evidence, assumptions, and prototype links that shaped them.

## Contracts

Every saved Canvas declares:

```json
{
  "schema_version": "catalyst-canvas/1.3",
  "canvas_id": "canvas-...",
  "revision_id": "revision-..."
}
```

Every project registry record declares `catalyst-canvas-workspace/1.0`. Portable custom frameworks use `catalyst-canvas-framework-package/1.0`.

Authoritative schemas and registries:

- `schemas/catalyst_canvas_contract_1_3.schema.json`
- `schemas/catalyst_canvas_workspace_1_0.schema.json`
- `contracts/frameworks.json`
- `contracts/persona_templates.json`

Canvas Contracts 1.0, 1.1, and 1.2 remain migration sources. Recognized older payloads are upgraded to Contract 1.3 with migration provenance and review warnings. Unknown future versions are rejected rather than silently reshaped.

## Framework and ideation model

```text
Challenge
└── How-might-we question
    └── Framework or prompt pack
        └── Ideation session
            ├── idea cards
            ├── clusters, tags, votes, and rationale
            ├── merges with preserved parent lineage
            └── selected ideas linked to prototypes and experiments
```

The built-in framework registry includes:

- AIDA
- Jobs to Be Done
- Value Proposition Canvas
- Message House
- SWOT
- PESTLE
- 5W1H
- Hero/Guide
- Assumption Matrix
- Impact–Effort

Each framework defines its description, intended uses, limitations, required inputs, output types, supported modes, and structured prompts. Custom organization frameworks and reusable prompt packs follow the same model and can be exported and imported without source-code changes.

Idea votes and selections represent participant judgment. They do not establish objective quality, feasibility, impact, or decision readiness.

## Shared surfaces

1. **Canonical Python package** — Contract 1.3 normalization, research ledger, framework registry, ideation lineage, migration, validation, handoffs, and exporters.
2. **CLI and compatibility adapters** — generation, validation, migration, framework-package import/export, JSON, Markdown, and print HTML.
3. **Flask workspace** — persistent projects, immutable revisions, autosave, research and evidence studios, ideation sessions, clusters, votes, merges, archive/restore, and APIs.
4. **WordPress browser workspace** — localStorage-backed projects, frameworks, prompt packs, ideas, clusters, ledger indicators, and exports without transmitting visitor inputs.

## Repository structure

```text
VERSION                            Canonical release version
catalyst_canvas/                   Contracts, engines, research, ledger, ideation, migration
contracts/                         Framework and persona registries
schemas/                           Canvas 1.3, Workspace 1.0, and historical schemas
app/                               Flask routes and SQLite persistence
fixtures/                          Cross-surface Contract 1.3 fixtures
wordpress/catalyst-canvas-demo/    Browser engine and local workspace
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
python demo/seed_demo.py
python app.py
```

Open `http://127.0.0.1:5000`. Use `/research` for design research, `/ledger` for evidence governance, and `/ideate` for frameworks and ideation after a project is active.

## CLI

```bash
python -m catalyst_canvas.cli generate \
  --input data/catalyst_canvas_sample_input.json \
  --json outputs/sample_canvas.json \
  --markdown outputs/sample_canvas.md \
  --html outputs/sample_canvas.html

python -m catalyst_canvas.cli validate --input outputs/sample_canvas.json
python -m catalyst_canvas.cli migrate --input legacy-canvas.json --output canonical-canvas.json

python -m catalyst_canvas.cli framework-export \
  --input outputs/sample_canvas.json \
  --output outputs/framework-package.json

python -m catalyst_canvas.cli framework-import \
  --input outputs/sample_canvas.json \
  --package outputs/framework-package.json \
  --output outputs/sample-with-frameworks.json
```

## Flask APIs

```text
GET  /api/workspaces
GET  /api/projects?q=&status=
GET  /api/projects/<project_id>
PATCH /api/projects/<project_id>
GET  /api/projects/<project_id>/revisions
POST /api/projects/<project_id>/autosave
GET  /api/research/assets?q=&type=
GET  /api/ledger
GET  /api/frameworks
GET  /projects/<project_id>/frameworks.json
POST /api/frameworks/import
GET  /api/ideation
POST /api/ideas/<idea_id>/vote
POST /api/ideas/merge
GET  /projects/<project_id>/research-handoff/<target>.json
POST /api/canvas/import
GET  /api/contract/schema.json
GET  /api/workspace-contract/schema.json
```

Project operations enforce the active workspace boundary.

## WordPress plugin

```bash
python scripts/sync_contract_assets.py
python scripts/build_plugin.py
```

Install `dist/catalyst-canvas-demo-v1.6.0.zip`, activate it, and add:

```text
[catalyst_canvas_demo]
```

Projects, revisions, research records, custom frameworks, prompt packs, and ideas remain in the current browser's localStorage. Clearing site data removes them.

## Validation

```bash
python scripts/validate_release.py
```

The release gate runs pytest and unittest, both current schemas, Contract 1.0–1.2 migrations, SQLite workspace operations, ledger and ideation lineage checks, framework-package round trips, Flask routes, exact Python/Flask/browser fixtures, Node tests, PHP and JavaScript syntax checks, sample exports, and WordPress package inspection.

## Boundaries

Catalyst Canvas supports problem framing, design research, evidence organization, ideation, structured review, and experimentation. It does not certify evidence, establish causality, guarantee product-market fit, provide legal or compliance advice, or guarantee implementation outcomes. Claims, assumptions, votes, and selected ideas remain provisional until reviewed against appropriate evidence and stakeholder context.

## License

MIT. See `LICENSE`.
