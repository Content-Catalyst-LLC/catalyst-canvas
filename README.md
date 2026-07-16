# Catalyst Canvas

**Current release: v1.5.0 — Research, Evidence, and Assumption Ledger**

Catalyst Canvas is the strategic-design and problem-framing workspace for Sustainable Catalyst. It turns ambiguous challenges into structured, reviewable projects covering audiences, personas, stakeholders, journeys, sources, evidence, claims, assumptions, research questions, prototypes, experiments, review notes, and institutional handoffs.

Version 1.5.0 adds a governed research ledger to the persistent project and immutable revision system. It keeps sources, excerpts, claims, assumptions, contradictions, limitations, ownership, review state, and test plans visible across Python, Flask, CLI, and WordPress surfaces.

## Contracts

Every saved Canvas declares:

```json
{
  "schema_version": "catalyst-canvas/1.2",
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

- `schemas/catalyst_canvas_contract_1_2.schema.json`
- `schemas/catalyst_canvas_workspace_1_0.schema.json`

Canvas Contracts 1.0 and 1.1 remain available as migration sources. Recognized older payloads are upgraded to Contract 1.2 with migration provenance and review warnings. Unknown future contract versions are rejected rather than silently reshaped.

## Research ledger

```text
Workspace
├── Projects
│   └── immutable Canvas Contract 1.2 revisions
└── Reusable research assets
    ├── personas, stakeholders, and journeys
    ├── sources and evidence excerpts
    ├── claims and assumptions
    └── research questions, interview guides, and observation notes
```

The ledger supports:

- structured source records with creator, date, URL, rights, limitations, tags, and Knowledge Library identifiers;
- evidence excerpts with locators, citations, confidence, limitations, and contradiction links;
- claims marked `supported`, `partially_supported`, `unsupported`, `disputed`, or `outdated`;
- assumptions with owner, confidence, criticality, consequence, test method, status, evidence links, and experiment links;
- open research questions, interview guides, observation notes, and synthesis tags;
- exportable handoff packages for Knowledge Library and Research Librarian;
- publication warnings for unsupported, disputed, or outdated claims.

Ledger indicators describe recorded coverage and workflow gaps. They do not certify truth, score research quality, or replace expert and stakeholder review.

## Shared surfaces

1. **Canonical Python package** — Contract 1.2 normalization, research and ledger modeling, migration, validation, workspace contracts, handoffs, and exporters.
2. **CLI and compatibility adapters** — canonical generation, validation, migration, JSON, Markdown, and print HTML.
3. **Flask workspace** — persistent projects, immutable revisions, autosave, design-research studio, evidence ledger, reusable assets, comparison, archive/restore, and workspace APIs.
4. **WordPress browser workspace** — localStorage-backed projects, research records, ledger indicators, and exports without transmitting visitor inputs.

## Repository structure

```text
VERSION                            Canonical release version
catalyst_canvas/                   Contracts, engine, research, ledger, migration, exporters
schemas/                           Canvas 1.2, Workspace 1.0, and historical schemas
app/                               Flask routes and SQLite persistence
fixtures/                          Cross-surface Canvas Contract 1.2 fixtures
wordpress/catalyst-canvas-demo/    Browser engine and local research workspace
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

Open `http://127.0.0.1:5000`. The design-research studio is available at `/research`; the evidence ledger is available at `/ledger` after a project is active.

## CLI

```bash
python -m catalyst_canvas.cli generate \
  --input data/catalyst_canvas_sample_input.json \
  --json outputs/sample_canvas.json \
  --markdown outputs/sample_canvas.md \
  --html outputs/sample_canvas.html

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
GET  /api/research/assets?q=&type=
GET  /api/research/persona-templates
GET  /research/compare?type=persona|journey
GET  /api/ledger
GET  /projects/<project_id>/research-handoff/<target>.json
POST /api/canvas/import
GET  /api/contract/schema.json
GET  /api/workspace-contract/schema.json
```

Supported handoff targets are `knowledge_library` and `research_librarian`. Project and research-asset operations enforce the active workspace boundary.

## WordPress plugin

```bash
python scripts/sync_contract_assets.py
python scripts/build_plugin.py
```

Install `dist/catalyst-canvas-demo-v1.5.0.zip`, activate it, and add:

```text
[catalyst_canvas_demo]
```

Projects, revisions, and research records are saved only in the current browser's localStorage. Clearing site data removes them.

## Validation

```bash
python scripts/validate_release.py
```

The release gate runs pytest and unittest, both schemas, Contract 1.0 and 1.1 migration, SQLite workspace operations, ledger coverage and handoff tests, research-asset indexing, Flask routes, cross-surface fixtures, Node browser tests, PHP and JavaScript syntax checks, sample exports, and WordPress package inspection.

## Boundaries

Catalyst Canvas supports problem framing, design research, evidence organization, structured review, and experimentation. It does not certify evidence, establish causality, guarantee product-market fit, provide legal or compliance advice, or guarantee implementation outcomes. Claims and assumptions remain provisional until reviewed against appropriate evidence and stakeholder context.

## License

MIT. See `LICENSE`.
