# Changelog

All notable changes to Catalyst Canvas are documented here.

## 1.6.0 — 2026-07-16

### Canvas Contract 1.3 and framework registry

- Upgraded the canonical document contract to `catalyst-canvas/1.3` with explicit migration from Contracts 1.0, 1.1, and 1.2.
- Added a data-driven registry for AIDA, JTBD, Value Proposition Canvas, Message House, SWOT, PESTLE, 5W1H, Hero/Guide, Assumption Matrix, and Impact–Effort.
- Added framework descriptions, intended uses, limitations, required inputs, output types, supported modes, and structured prompts.
- Added portable custom-framework packages and reusable prompt packs without application-code changes.

### Framework and Ideation Studio

- Added divergent and convergent ideation sessions linked to challenges, HMW questions, frameworks, prompt packs, facilitators, and participants.
- Added idea cards with author, rationale, tags, votes, cluster membership, evidence, assumptions, and prototype links.
- Added clustering, accessible reordering, merging, selection, and preserved parent/merge lineage.
- Added Flask framework and ideation APIs plus browser-local WordPress editing and persistence.
- Added framework-package CLI import/export and framework-package API import.

### Conformance and release hardening

- Added deterministic Python, Flask, and Node conformance for the Contract 1.3 ideation fixture.
- Added custom-framework round-trip, registry, lineage, clustering, voting, merging, migration, route, and browser tests.
- Expanded the maintained Python suite to 60 pytest tests and 60 unittest tests before final packaging.

## 1.5.0 — 2026-07-16

### Canvas Contract 1.2 and governed ledger

- Upgraded the canonical document contract to `catalyst-canvas/1.2` with explicit migration from Contracts 1.0 and 1.1.
- Added structured source records, evidence excerpts, claims, assumptions, research questions, interview guides, observation notes, synthesis tags, and institutional handoffs.
- Added claim states for supported, partially supported, unsupported, disputed, and outdated assertions.
- Added assumption ownership, confidence, criticality, consequence, test method, lifecycle status, due date, evidence links, and experiment links.
- Added contradiction, limitation, missing-data, and review-state fields so uncertainty remains visible.
- Added descriptive ledger indicators for source and evidence counts, claim-state exposure, material-claim linkage, and high-criticality open assumptions.

### Evidence Ledger workspace

- Added the Flask `/ledger` studio for editing sources, excerpts, claims, assumptions, research questions, synthesis tags, and handoff plans.
- Added workspace-scoped indexing and reuse for source, evidence, claim, assumption, research-question, interview-guide, and observation-note assets.
- Added `GET /api/ledger` and project-scoped research-handoff endpoints.
- Added Knowledge Library and Research Librarian handoff packages using `catalyst-canvas-research-handoff/1.0`.
- Added publication and review warnings before exported narrative content when claims remain unsupported, disputed, or outdated.

### Shared browser engine and validation

- Added browser-local ledger editing and descriptive indicator cards to the WordPress shortcode workspace.
- Added deterministic Python, Flask, and Node conformance for the Contract 1.2 ledger fixture.
- Added migration, claim-state, assumption-to-experiment, handoff-provenance, route, storage-indexing, and export-warning tests.
- Expanded release validation to 53 pytest tests and 53 unittest tests before packaging.

## 1.4.0 — 2026-07-16

### Canvas Contract 1.1 research model

- Expanded persona records with context, jobs, goals, needs, pains, gains, behaviors, barriers, motivations, accessibility needs, channels, quotes, evidence and assumption links, tags, source notes, confidence notes, and validation status.
- Added empathy maps and attribute-level observed, research, or assumed basis records with evidence and confidence.
- Expanded stakeholder records with quantified influence, interest, and impact, responsibilities, tensions, stance, decision role, engagement strategy, evidence links, dependencies, and tags.
- Added reusable journey maps with persona linkage, scenario, desired outcome, ordered stages, evidence, assumptions, and tags.
- Added behavioral-signal records whose schema enforces hint status and excludes identity or demographic fields.

### Persona, stakeholder, and journey studio

- Added Flask and browser-local editing for personas, empathy maps, stakeholder maps, and ordered journey stages.
- Added six reusable persona templates and workspace persona/journey comparison.
- Added guarded UTF-8 analytics and GA4 CSV import.
- Added workspace-scoped research assets and project research links with automatic indexing on save.
- Added deterministic Python, Flask, and browser conformance fixtures for the enriched research contract.

## 1.3.0 — 2026-07-16

### Persistent workspaces and projects

- Added Workspace Project Contract 1.0 with stable workspace and project identities, lifecycle status, tags, current revision pointers, and revision counts.
- Added workspace-scoped project creation, switching, search, metadata editing, duplication, archive, and restore workflows.
- Added immutable Canvas revision storage, bounded autosave retention, historical export, and restore-as-new-revision behavior.
- Added idempotent migration of v1.2 `canvas_briefs` rows into the default workspace while preserving old numeric export URLs.
- Added Flask project, revision, autosave, workspace, schema, and export APIs with active-workspace boundary checks.
- Added a dependency-free WordPress localStorage workspace with project save, autosave, switch, duplicate, archive, and revision retention.

## 1.2.0 — 2026-07-16

### Canvas Contract 1.0 and shared engine

- Added the canonical `catalyst_canvas/` package for normalization, generation, JSON Schema validation, migrations, surface adapters, and stable exporters.
- Introduced `catalyst-canvas/1.0` with stable identities, lifecycle metadata, structured design records, evidence, assumptions, prototypes, tests, review notes, and provenance.
- Added explicit migration paths for legacy Python, wrapper, and Flask flat records.
- Routed Flask, Python compatibility modules, CLI, storage, exporters, and the WordPress browser engine through the shared contract.
- Added deterministic cross-surface fixtures and a unified release gate.

## 1.1.1 — 2026-07-16

### Repository integrity and CI repair

- Added `VERSION` as the canonical release source and synchronized release markers.
- Added MIT licensing, environment configuration, source-tree hygiene, deterministic validation, and versioned plugin packaging.
- Removed tracked runtime databases and generated release artifacts.
- Consolidated CI and made pytest and unittest execute the same maintained suite.
- Converted duplicate Python generators into compatibility adapters over the canonical core.

## 1.1.0 — 2026-07-01

- Added the WordPress shortcode demo plugin, Python core generator, CLI, schema, documentation, examples, tests, and initial CI workflows.
