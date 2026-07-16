# Catalyst Canvas

**Current release: v1.9.0 — Collaboration, Review, and Publication**

Catalyst Canvas is the strategic-design workspace for Sustainable Catalyst. It turns ambiguous challenges into persistent, reviewable projects spanning research, evidence, personas, journeys, ideation, prioritization, prototypes, experiments, collaboration, approvals, and governed publication.

Version 1.9.0 adds the operational layer required to move a Canvas from an internal working record to a reviewed public artifact without losing revision provenance or exposing private collaboration data.

## Canonical contracts

Every current Canvas declares:

```json
{
  "schema_version": "catalyst-canvas/1.6",
  "canvas_id": "canvas-...",
  "revision_id": "revision-..."
}
```

Related contracts:

- Workspace projects: `catalyst-canvas-workspace/1.0`
- Framework packages: `catalyst-canvas-framework-package/1.0`
- Research handoffs: `catalyst-canvas-research-handoff/1.0`
- Decision handoffs: `catalyst-canvas-decision-handoff/1.0`
- Experiment handoffs: `catalyst-canvas-experiment-handoff/1.0`
- Publication records: `catalyst-canvas-publication/1.0`
- Public-safe packages: `catalyst-canvas-public-safe/1.0`

Authoritative schemas and registries:

- `schemas/catalyst_canvas_contract_1_6.schema.json`
- `schemas/catalyst_canvas_workspace_1_0.schema.json`
- `contracts/frameworks.json`
- `contracts/persona_templates.json`
- `contracts/decision_criteria.json`

Canvas Contracts 1.0 through 1.5 remain supported migration sources. Unknown future versions are rejected rather than silently reshaped.

## Collaboration and review

Contract 1.6 adds:

- capability-based workspace roles: owner, editor, contributor, reviewer, and viewer;
- review assignments with scope, assignees, due dates, status, and required/optional designation;
- threaded comments linked to sections, claims, assumptions, ideas, decisions, prototypes, experiments, or publications;
- approval decisions: pending, approved, changes requested, rejected, or abstained;
- immutable revisions for every comment, review, approval, and publication change;
- workspace-scoped collaboration indexes for search and operational views.

Role capabilities are explicit records. They are workflow controls, not identity verification or institutional authorization.

## Governed publication

Publication records preserve:

- publication type, channel, audience, version, slug, and owner;
- source revision identity;
- selected public sections;
- required reviews and approvals;
- redaction notes and release notes;
- scheduled, published, withdrawn, and archived states;
- release checksums, publisher identity, URL, and publication history.

A public publication is blocked when required reviews are incomplete, linked approvals are missing or not approved, a blocking decision exists, or public redaction review is not recorded.

Public-safe packages omit workspace members, internal comments, review assignments, approvals, participant details, private notes, and other working records. They preserve a SHA-256 content checksum and source Canvas/revision identity.

## Existing capabilities

Catalyst Canvas also includes:

- evidence-aware personas, empathy maps, stakeholder maps, and journeys;
- source, evidence, claim, assumption, research-question, interview, and observation ledgers;
- ten built-in framework packs plus portable custom frameworks and prompt packs;
- divergent and convergent ideation, clustering, votes, merges, and lineage;
- ICE, RICE, weighted criteria, decision matrices, gates, sensitivity scenarios, and recommendations;
- versioned prototypes, hypotheses, participant plans, safeguards, experiment runs, learning decisions, and iterations;
- Knowledge Library, Research Librarian, Decision Studio, Workbench, and Research Lab handoffs.

Readiness indicators describe recorded workflow coverage. They do not establish factual accuracy, legal clearance, accessibility, security, ethical acceptability, causal validity, or institutional approval.

## Shared surfaces

1. **Canonical Python package** — Contract 1.6 normalization, validation, migrations, collaboration rules, public-safe packaging, and exporters.
2. **CLI and compatibility adapters** — generation, validation, migration, framework exchange, JSON, Markdown, and print HTML.
3. **Flask workspace** — persistent projects, immutable revisions, autosave, research, ideation, decisions, experiments, collaboration, review, and publication APIs.
4. **WordPress browser workspace** — localStorage-backed projects with Contract 1.6 editing, review records, publication records, full JSON, and public-safe JSON exports.

## Repository structure

```text
VERSION                            Canonical release version
catalyst_canvas/                   Contracts, engines, collaboration, publication
contracts/                         Framework, persona, and decision registries
schemas/                           Current and historical schemas
app/                               Flask routes and SQLite persistence
fixtures/                          Cross-surface Contract 1.6 fixtures
wordpress/catalyst-canvas-demo/    Browser engine and local workspace
scripts/                           Asset sync, validation, and packaging
tests/                             Python, Flask, storage, route, and Node tests
```

## Requirements and local setup

- Python 3.11, 3.12, or 3.13
- PHP for plugin syntax validation
- Node.js for browser conformance validation

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
cp .env.example .env
python demo/seed_demo.py
python app.py
```

Open `http://127.0.0.1:5000`. Main studios include `/research`, `/ledger`, `/ideate`, `/prioritize`, `/experiment`, and `/collaborate`.

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

## Collaboration and publication APIs

```text
GET  /collaborate
GET  /api/collaboration
GET  /api/workspaces/members
POST /api/workspaces/members
POST /api/comments
POST /api/comments/<comment_id>/resolve
POST /api/reviews
POST /api/approvals
POST /api/publications/<publication_id>/publish
GET  /projects/<project_id>/publication/<target>.json
GET  /projects/<project_id>/public.json
```

All project and publication routes enforce the active workspace boundary.

## WordPress plugin

```bash
python scripts/sync_contract_assets.py
python scripts/build_plugin.py
```

Install `dist/catalyst-canvas-demo-v1.9.0.zip`, activate it, and place `[catalyst_canvas_demo]` on a page. Browser projects and revisions remain in localStorage. Clearing site data removes them.

## Validation

```bash
python scripts/validate_release.py
```

The release gate runs pytest and unittest, schema checks, Contract 1.0–1.5 migrations, SQLite persistence, exact Python/Flask/browser fixture conformance, collaboration permissions, review and approval workflows, publication blocking, public-safe redaction, release checksums, PHP and JavaScript syntax, sample exports, and plugin inspection.

## License

MIT. See `LICENSE`.
