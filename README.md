# Catalyst Canvas

**Current release: v2.0.0 — Connected Strategic Design Platform**

Catalyst Canvas is the strategic-design workspace for Sustainable Catalyst. It turns ambiguous challenges into persistent, reviewable projects spanning research, evidence, personas, journeys, ideation, prioritization, prototypes, experiments, collaboration, approval, publication, and cross-product execution.

Version 2.0.0 establishes Catalyst Canvas as a connected platform rather than an isolated planning tool. It adds explicit product connections, institutional interoperability profiles, cross-product workflow links, deterministic exchange packages, event envelopes, capability discovery, and unified platform readiness while preserving every v1.x project and revision.

## Canonical contracts

Every current Canvas declares:

```json
{
  "schema_version": "catalyst-canvas/2.0",
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
- Platform exchange packages: `catalyst-canvas-exchange/2.0`
- Platform events: `catalyst-canvas-event/1.0`
- Capability manifests: `catalyst-canvas-capabilities/1.0`

Authoritative schemas and registries:

- `schemas/catalyst_canvas_contract_2_0.schema.json`
- `schemas/catalyst_canvas_workspace_1_0.schema.json`
- `contracts/frameworks.json`
- `contracts/persona_templates.json`
- `contracts/decision_criteria.json`

Canvas Contracts 1.0 through 1.6 remain supported migration sources. Unknown future versions are rejected rather than silently reshaped.

## Connected platform

Contract 2.0 adds:

- first-party product connection records with direction, status, endpoint, authentication mode, capabilities, accepted contracts, ownership, and verification notes;
- interoperability profiles defining supported contracts, formats, identity modes, events, required fields, redaction rules, and retention boundaries;
- cross-product workflow links with stable record IDs, relationship types, status, and correlation IDs;
- deterministic exchange packages with payload-specific boundaries and SHA-256 integrity checks;
- optional HMAC-SHA256 signatures for institutional transport;
- event envelopes with producer, subject, correlation, occurrence time, checksum, and metadata;
- a machine-readable capability manifest for API and connector discovery;
- unified platform readiness that composes research, evidence, ideation, decision, experiment, collaboration, connection, link, and exchange states.

A configured or verified connection record does not prove a remote service is currently reachable, authorized, secure, or institutionally accepted. Receiving products must independently authenticate, validate, authorize, redact, retain, and acknowledge each exchange.

## Supported product relationships

The shared platform registry supports structured relationships with:

- Knowledge Library
- Research Librarian
- Site Intelligence
- Workbench
- Decision Studio
- Research Lab
- Product Support and Feedback
- Contact and Engagement
- WordPress
- Public API consumers

## Existing strategic-design capabilities

Catalyst Canvas also includes:

- evidence-aware personas, empathy maps, stakeholder maps, and journeys;
- source, evidence, claim, assumption, research-question, interview, and observation ledgers;
- ten built-in framework packs plus portable custom frameworks and prompt packs;
- divergent and convergent ideation, clustering, votes, merges, and lineage;
- ICE, RICE, weighted criteria, decision matrices, gates, sensitivity scenarios, and recommendations;
- versioned prototypes, hypotheses, participant plans, safeguards, experiment runs, learning decisions, and iterations;
- capability-based workspace roles, comments, reviews, approvals, publication gates, release history, and public-safe packages.

Readiness indicators describe recorded workflow coverage. They do not establish factual accuracy, legal clearance, accessibility, security, ethical acceptability, causal validity, remote availability, or institutional approval.

## Shared surfaces

1. **Canonical Python package** — Contract 2.0 normalization, validation, migrations, platform exchange, collaboration, publication, and exporters.
2. **CLI and compatibility adapters** — generation, validation, migration, framework exchange, JSON, Markdown, and print HTML.
3. **Flask workspace** — persistent projects, immutable revisions, research, ideation, decisions, experiments, collaboration, publication, platform registry, exchange, and capability APIs.
4. **WordPress browser workspace** — localStorage-backed projects with Contract 2.0 editing, platform records, full JSON, public-safe JSON, and exchange-package downloads.

## Repository structure

```text
VERSION                            Canonical release version
catalyst_canvas/                   Contracts, engines, platform exchange, workflow layers
contracts/                         Framework, persona, and decision registries
schemas/                           Current and historical schemas
app/                               Flask routes and SQLite persistence
fixtures/                          Cross-surface Contract 2.0 fixtures
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

Open `http://127.0.0.1:5000`. Main studios include `/research`, `/ledger`, `/ideate`, `/prioritize`, `/experiment`, `/collaborate`, and `/platform`.

Set `CANVAS_EXCHANGE_SIGNING_KEY` in `.env` only when HMAC-signed institutional exchange packages are required. Keep the key outside source control and rotate it under the receiving institution's security policy.

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

## Platform APIs

```text
GET  /platform
GET  /api/platform
GET  /api/capabilities
GET  /projects/<project_id>/exchange/<target>.json
POST /api/exchange/verify
```

Existing research, decision, experiment, collaboration, publication, and project APIs remain available. All project and platform routes enforce the active workspace boundary.

## WordPress plugin

```bash
python scripts/sync_contract_assets.py
python scripts/build_plugin.py
```

Install `dist/catalyst-canvas-demo-v2.0.0.zip`, activate it, and place `[catalyst_canvas_demo]` on a page. Browser projects and revisions remain in localStorage. Clearing site data removes them.

## Validation

```bash
python scripts/validate_release.py
```

The release gate runs pytest and unittest, current and historical schema checks, Contract 1.0–1.6 migrations, SQLite persistence, exact Python/Flask/browser fixture conformance, exchange signing and tamper detection, capability-manifest verification, platform-record indexing, collaboration and publication controls, PHP and JavaScript syntax, sample exports, and WordPress package inspection.

## License

MIT. See `LICENSE`.
