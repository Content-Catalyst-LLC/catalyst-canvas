# Catalyst Canvas

**Current release: v1.4.0 — Persona, Stakeholder, and Journey Studio**

Catalyst Canvas is the strategic-design and problem-framing workspace for Sustainable Catalyst. It turns ambiguous challenges into structured, reviewable projects covering audiences, personas, stakeholders, journey stages, point-of-view statements, “How might we?” questions, ideation frameworks, evidence, assumptions, prototypes, tests, and review notes.

Version 1.4.0 adds an evidence-aware design-research layer while preserving the persistent project and immutable revision system introduced in v1.3.0. It adds empathy maps, observed-versus-assumed persona attributes, influence/interest/impact stakeholder mapping, experiment-linked journeys, guarded analytics CSV hints, reusable persona templates, and research comparison.

## Contracts

Every saved Canvas declares:

```json
{
  "schema_version": "catalyst-canvas/1.1",
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

- `schemas/catalyst_canvas_contract_1_1.schema.json`
- `schemas/catalyst_canvas_workspace_1_0.schema.json`

Canvas Contract 1.0 remains available as a migration source and historical schema. Reads and imports upgrade 1.0 payloads to 1.1 with migration provenance and review warnings.

## Research model

```text
Workspace
├── Projects
│   └── immutable Canvas Contract 1.1 revisions
└── Reusable research assets
    ├── personas
    ├── stakeholders
    └── journeys with ordered, evidence- and experiment-linked stages
```

Saving a project indexes its current personas, stakeholders, and journeys into the workspace research library. Assets can be searched and reused in another project without weakening project or workspace boundaries.

Research readiness is summarized from record completeness, evidence links, confidence, validation status, journey coverage, and behavioral hints. Analytics remain hints only and never establish identity, intent, motivation, or demographic attributes.

## Shared surfaces

1. **Canonical Python package** — Contract 1.1 normalization, research modeling, migration, validation, workspace contracts, and exporters.
2. **CLI and compatibility adapters** — canonical generation, validation, migration, JSON, Markdown, and print HTML.
3. **Flask workspace** — persistent projects, revisions, autosave, research studio, CSV import, templates, comparison, reusable asset library, archive/restore, and workspace APIs.
4. **WordPress browser workspace** — localStorage-backed projects, personas, empathy maps, stakeholder mapping, journeys, CSV hints, templates, comparison, and exports without transmitting visitor inputs.

## Repository structure

```text
VERSION                            Canonical release version
catalyst_canvas/                   Contracts, shared engine, research model, migration, exporters
schemas/                           Canvas 1.1, Workspace 1.0, and historical schemas
app/                               Flask routes and SQLite persistence
fixtures/                          Cross-surface Canvas Contract 1.1 fixtures
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

Open `http://127.0.0.1:5000`. The research studio is available at `/research` after a project is active.

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
POST /api/canvas/import
GET  /api/contract/schema.json
GET  /api/workspace-contract/schema.json
```

Project and research-asset operations enforce the active workspace boundary.

## WordPress plugin

```bash
python scripts/sync_contract_assets.py
python scripts/build_plugin.py
```

Install `dist/catalyst-canvas-demo-v1.4.0.zip`, activate it, and add:

```text
[catalyst_canvas_demo]
```

Projects, revisions, and research records are saved only in the current browser's localStorage. Clearing site data removes them.

## Validation

```bash
python scripts/validate_release.py
```

The release gate runs pytest and unittest, both schemas, Contract 1.0 migration, v1.2 SQLite migration, persona templates, empathy and attribute normalization, guarded CSV import, research-asset indexing and reuse, Flask routes, cross-surface fixtures, Node browser tests, PHP and JavaScript syntax checks, sample exports, and WordPress package inspection.

## Boundaries

Catalyst Canvas supports problem framing, design research, structured review, and experimentation. It does not certify evidence, guarantee product-market fit, provide legal or compliance advice, or guarantee implementation outcomes. Personas and journeys should be identified as provisional until supported by appropriate research and human review.

## License

MIT. See `LICENSE`.
