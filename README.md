# Catalyst Canvas

**Current release: v1.8.0 — Prototype and Experiment Management**

Catalyst Canvas is the strategic-design, research-synthesis, ideation, prioritization, and experimentation workspace for Sustainable Catalyst. It turns ambiguous challenges into reviewable projects covering audiences, personas, stakeholders, journeys, sources, evidence, claims, assumptions, ideas, alternatives, prototypes, hypotheses, experiments, learning decisions, iteration history, and institutional handoffs.

Version 1.8.0 adds a governed prototype and experiment layer. Teams can preserve the full path from an evidence-linked challenge and selected concept through prototype versions, falsifiable hypotheses, participant plans, metrics, safeguards, experiment runs, observed results, learning decisions, and subsequent iterations.

## Contracts

Every saved Canvas declares:

```json
{
  "schema_version": "catalyst-canvas/1.5",
  "canvas_id": "canvas-...",
  "revision_id": "revision-..."
}
```

Related contracts:

- Workspace projects: `catalyst-canvas-workspace/1.0`
- Custom framework packages: `catalyst-canvas-framework-package/1.0`
- Research handoffs: `catalyst-canvas-research-handoff/1.0`
- Decision handoffs: `catalyst-canvas-decision-handoff/1.0`
- Experiment handoffs: `catalyst-canvas-experiment-handoff/1.0`

Authoritative schemas and registries:

- `schemas/catalyst_canvas_contract_1_5.schema.json`
- `schemas/catalyst_canvas_workspace_1_0.schema.json`
- `contracts/frameworks.json`
- `contracts/persona_templates.json`
- `contracts/decision_criteria.json`

Canvas Contracts 1.0 through 1.4 remain migration sources. Recognized older payloads are upgraded to Contract 1.5 with provenance and review warnings. Unknown future versions are rejected rather than silently reshaped.

## Prototype and experiment model

```text
Challenge and research evidence
└── selected idea or decision alternative
    └── versioned prototype
        ├── falsifiable hypothesis
        ├── experiment plan
        │   ├── participant and recruitment plan
        │   ├── metrics and thresholds
        │   ├── risks, mitigations, and stop conditions
        │   └── data-handling and ethics-review status
        ├── experiment run
        │   ├── participant count
        │   ├── metric results
        │   ├── observations and incidents
        │   └── limitations and evidence
        ├── continue / iterate / pivot / stop / escalate / retest
        └── versioned iteration history
```

Prototype and experiment records retain owners, source links, assumptions, evidence, artifacts, dates, status, limitations, and stable identifiers. Contract 1.5 keeps the older `tests` collection as a compatibility view while treating `experiment_plans`, `experiment_runs`, and `learning_decisions` as the governed records.

Experiment readiness is a workflow coverage indicator. It does not establish causal validity, statistical power, safety, desirability, feasibility, viability, or impact.

## Research Lab and Workbench handoffs

Research Lab handoffs preserve participant plans, safeguards, dataset references, compute requirements, prototypes, hypotheses, experiment plans, runs, learning decisions, assumptions, evidence, and provenance.

Workbench handoffs preserve metric definitions, calculation requirements, modeling questions, prototype artifacts, experiment context, assumptions, evidence, and provenance.

## Existing design and decision capabilities

Catalyst Canvas also includes:

- evidence-aware personas, empathy maps, stakeholder maps, and journey stages;
- sources, evidence excerpts, claims, assumptions, research questions, interview guides, and observations;
- ten built-in framework packs plus portable custom frameworks and prompt packs;
- divergent and convergent ideation sessions, idea cards, clusters, votes, merges, and lineage;
- ICE, RICE, weighted criteria, four decision matrices, gates, sensitivity scenarios, and recommendation states;
- Knowledge Library, Research Librarian, Decision Studio, Workbench, and Research Lab handoffs.

Scores, rankings, votes, claims, and experiment results preserve their recorded basis and limitations. They do not replace human judgment, governance, ethical review, or technical validation.

## Shared surfaces

1. **Canonical Python package** — Contract 1.5 normalization, research ledger, framework registry, ideation, prioritization, experiments, migrations, handoffs, and exporters.
2. **CLI and compatibility adapters** — generation, validation, migration, framework-package exchange, JSON, Markdown, and print HTML.
3. **Flask workspace** — persistent projects, immutable revisions, autosave, research, evidence, ideation, prioritization, experiments, archive/restore, and APIs.
4. **WordPress browser workspace** — localStorage-backed projects, research records, ideas, alternatives, prototypes, experiments, learning history, and exports without transmitting visitor inputs.

## Repository structure

```text
VERSION                            Canonical release version
catalyst_canvas/                   Contracts, engines, ledger, ideation, prioritization, experiments
contracts/                         Framework, persona, and decision-criteria registries
schemas/                           Canvas 1.5, Workspace 1.0, and historical schemas
app/                               Flask routes and SQLite persistence
fixtures/                          Cross-surface Contract 1.5 fixtures
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

Open `http://127.0.0.1:5000`. Use `/research`, `/ledger`, `/ideate`, `/prioritize`, and `/experiment` after a project is active.

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
GET  /api/ideation
GET  /api/prioritization
POST /api/prioritization/sensitivity
GET  /api/experiments
POST /api/experiments/runs
GET  /projects/<project_id>/research-handoff/<target>.json
GET  /projects/<project_id>/decision-handoff/<target>.json
GET  /projects/<project_id>/experiment-handoff/<target>.json
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

Install `dist/catalyst-canvas-demo-v1.8.0.zip`, activate it, and add:

```text
[catalyst_canvas_demo]
```

Projects, revisions, research records, frameworks, decisions, prototypes, experiment runs, and learning history remain in the current browser's localStorage. Clearing site data removes them.

## Validation

```bash
python scripts/validate_release.py
```

The release gate runs pytest and unittest, current schemas, Contract 1.0–1.4 migrations, SQLite workspace and asset indexing, research, ideation, prioritization, prototype and experiment invariants, all handoffs, exact Python/Flask/browser fixtures, Node tests, PHP and JavaScript syntax checks, sample exports, and WordPress package inspection.

## Boundaries

Catalyst Canvas supports problem framing, design research, evidence organization, ideation, prioritization, prototyping, structured experimentation, and learning review. It does not certify evidence, establish causality, guarantee product-market fit, make binding decisions, provide legal or compliance advice, approve human-subject research, or guarantee implementation outcomes.

## License

MIT. See `LICENSE`.
