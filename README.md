# Catalyst Canvas

**Current release: v1.7.0 — Prioritization and Decision Readiness**

Catalyst Canvas is the strategic-design, research-synthesis, ideation, and decision-framing workspace for Sustainable Catalyst. It turns ambiguous challenges into structured, reviewable projects covering audiences, personas, stakeholders, journeys, sources, evidence, claims, assumptions, research questions, ideas, alternatives, prototypes, experiments, review notes, and institutional handoffs.

Version 1.7.0 adds transparent prioritization and decision-readiness workflows. Alternatives can be compared with editable ICE, RICE, weighted criteria, four matrix views, ethical gates, sensitivity scenarios, dependencies, blockers, resources, deadlines, and recommendation states without hiding the recorded inputs or replacing human judgment.

## Contracts

Every saved Canvas declares:

```json
{
  "schema_version": "catalyst-canvas/1.4",
  "canvas_id": "canvas-...",
  "revision_id": "revision-..."
}
```

Related contracts:

- Workspace projects: `catalyst-canvas-workspace/1.0`
- Custom framework packages: `catalyst-canvas-framework-package/1.0`
- Research handoffs: `catalyst-canvas-research-handoff/1.0`
- Decision handoffs: `catalyst-canvas-decision-handoff/1.0`

Authoritative schemas and registries:

- `schemas/catalyst_canvas_contract_1_4.schema.json`
- `schemas/catalyst_canvas_workspace_1_0.schema.json`
- `contracts/frameworks.json`
- `contracts/persona_templates.json`
- `contracts/decision_criteria.json`

Canvas Contracts 1.0, 1.1, 1.2, and 1.3 remain migration sources. Recognized older payloads are upgraded to Contract 1.4 with migration provenance and review warnings. Unknown future versions are rejected rather than silently reshaped.

## Decision model

```text
Challenge and research context
└── ideas and prototypes
    └── decision alternatives
        ├── ICE and RICE inputs
        ├── weighted criteria with rationale and evidence
        ├── impact–effort, confidence–risk,
        │   urgency–importance, and reversibility matrices
        ├── ethical and governance gates
        ├── dependencies, blockers, resources, and deadlines
        └── sensitivity scenarios
            ├── explore / test / defer / reject / escalate
            └── ready for decision review
```

All score inputs retain:

- value and unit;
- measured, estimated, opinion, or unknown basis;
- confidence;
- rationale;
- evidence and assumption links.

Changing criterion weights recalculates rankings without overwriting raw values. Scores and rankings summarize recorded judgment; they do not establish certainty, approval, ethical acceptability, technical validity, or objective quality.

## Built-in decision criteria

The editable default library includes:

- Impact
- Evidence confidence
- Feasibility
- Urgency
- Strategic alignment
- Equity and harm review
- Resource efficiency
- Reversibility

The equity and harm criterion is a decision gate. A failed gate blocks decision readiness even when the weighted score is high.

## Framework and ideation model

The data-driven framework registry includes AIDA, Jobs to Be Done, Value Proposition Canvas, Message House, SWOT, PESTLE, 5W1H, Hero/Guide, Assumption Matrix, and Impact–Effort. Custom frameworks and prompt packs follow the same portable definition.

Idea cards preserve challenge, HMW question, framework prompt, author, rationale, tags, votes, clusters, merges, evidence, assumptions, and prototype links. Votes and selections represent participant judgment, not objective quality.

## Shared surfaces

1. **Canonical Python package** — Contract 1.4 normalization, research ledger, framework registry, ideation lineage, prioritization, migration, validation, handoffs, and exporters.
2. **CLI and compatibility adapters** — generation, validation, migration, framework-package import/export, JSON, Markdown, and print HTML.
3. **Flask workspace** — persistent projects, immutable revisions, autosave, research, evidence, ideation, prioritization, archive/restore, and APIs.
4. **WordPress browser workspace** — localStorage-backed projects, research records, ideas, decision alternatives, sensitivity views, and exports without transmitting visitor inputs.

## Repository structure

```text
VERSION                            Canonical release version
catalyst_canvas/                   Contracts, engines, ledger, ideation, prioritization
contracts/                         Framework, persona, and decision-criteria registries
schemas/                           Canvas 1.4, Workspace 1.0, and historical schemas
app/                               Flask routes and SQLite persistence
fixtures/                          Cross-surface Contract 1.4 fixtures
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

Open `http://127.0.0.1:5000`. Use `/research`, `/ledger`, `/ideate`, and `/prioritize` after a project is active.

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
GET  /api/prioritization
POST /api/prioritization/sensitivity
GET  /projects/<project_id>/decision-handoff/<target>.json
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

Install `dist/catalyst-canvas-demo-v1.7.0.zip`, activate it, and add:

```text
[catalyst_canvas_demo]
```

Projects, revisions, research records, frameworks, ideas, decision alternatives, and sensitivity scenarios remain in the current browser's localStorage. Clearing site data removes them.

## Validation

```bash
python scripts/validate_release.py
```

The release gate runs pytest and unittest, current schemas, Contract 1.0–1.3 migrations, SQLite workspace operations, ledger, ideation, prioritization and handoff checks, exact Python/Flask/browser fixtures, Node tests, PHP and JavaScript syntax checks, sample exports, and WordPress package inspection.

## Boundaries

Catalyst Canvas supports problem framing, design research, evidence organization, ideation, prioritization, structured review, and experimentation. It does not certify evidence, establish causality, guarantee product-market fit, make binding decisions, provide legal or compliance advice, or guarantee implementation outcomes. Claims, assumptions, scores, rankings, votes, gates, and recommendations remain provisional until reviewed by the appropriate people and systems.

## License

MIT. See `LICENSE`.
