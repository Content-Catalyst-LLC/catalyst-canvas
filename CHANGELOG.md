# Changelog

All notable changes to Catalyst Canvas are documented here.

## 1.4.0 — 2026-07-16

### Canvas Contract 1.1

- Upgraded the canonical document contract to `catalyst-canvas/1.1` while retaining explicit migration support for Contract 1.0 and legacy v1.x payloads.
- Expanded persona records with context, jobs, goals, needs, pains, gains, behaviors, barriers, motivations, accessibility needs, channels, quotes, evidence and assumption links, tags, source notes, confidence notes, and validation status.
- Added empathy maps and attribute-level observed, research, or assumed basis records with evidence and confidence.
- Expanded stakeholder records with type, relationship, quantified influence, interest, and impact, responsibilities, tensions, stance, decision role, engagement strategy, evidence links, dependencies, and tags.
- Added reusable journey maps with persona linkage, scenario, desired outcome, status, ordered stages, evidence, assumptions, and tags.
- Added stage-level actions, questions, thoughts, pain points, frictions, opportunities, touchpoints, channels, metrics, emotional state, owner, evidence links, and proposed experiment identifiers.
- Added behavioral-signal records whose schema enforces hint status and excludes identity or demographic fields.
- Added a normalized research-readiness summary to every Canvas.

### Persona, stakeholder, and journey studio

- Added a Flask research studio for editing persona and empathy records, influence/interest/impact stakeholder maps, and ordered journey stages.
- Added six reusable persona templates and workspace persona/journey comparison.
- Added UTF-8 analytics and GA4 CSV upload with file-type, size, and unsupported-column safeguards.
- Added matrix and journey previews that remain tied to the saved canonical revision.
- Added workspace-scoped `research_assets` and `project_research_links` storage with automatic indexing on save.
- Added search, counts, retrieval, reuse, and archive operations for research assets without crossing workspace boundaries.
- Added `GET /api/research/assets`, `GET /api/research/persona-templates`, comparison views, and project-level research-asset reuse routes.

### Shared browser engine and exports

- Updated the WordPress browser engine to generate and migrate Canvas Contract 1.1 documents.
- Added browser-local persona, empathy, stakeholder, journey, CSV-hint, template, and comparison workflows while retaining the no-transmission privacy boundary.
- Expanded Markdown and print exports with research readiness, persona detail, stakeholder maps, and journey stages.
- Added deterministic Python, Flask, and Node conformance fixtures for the enriched research contract.

### Validation and migration

- Added Contract 1.0-to-1.1 migration coverage and migration provenance warnings.
- Added research normalization, journey sequencing, stakeholder scoring, reusable asset, route, and browser conformance tests.
- Expanded the release gate to validate research asset indexing and plugin packaging against Contract 1.1.

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
