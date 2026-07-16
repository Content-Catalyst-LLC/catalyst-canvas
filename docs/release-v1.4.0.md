# Catalyst Canvas v1.4.0

## Persona, Stakeholder, and Journey Studio

Version 1.4.0 adds the first complete evidence-aware design-research layer to the persistent Catalyst Canvas workspace.

### Delivered

- Canvas Contract 1.1 with backward-compatible Contract 1.0 migration.
- Detailed persona records for jobs, needs, pains, gains, behaviors, barriers, motivations, evidence, source, confidence, and validation.
- Empathy maps and observed-versus-assumed persona attributes.
- Primary, secondary, affected, and excluded audience designations.
- Stakeholder maps with influence, interest, impact, responsibilities, tensions, stance, role, and strategy.
- Persona-linked journeys with actions, questions, frictions, opportunities, touchpoints, owners, evidence, metrics, and proposed experiment links.
- UTF-8 analytics and GA4 CSV import with type/size validation and a mandatory behavioral-hint safeguard.
- Six reusable persona templates for civic, sustainability, research, technical-content, institutional, and public-interest work.
- Workspace-scoped reusable research storage plus persona and journey comparison.
- Matching Flask, Python, CLI, and WordPress browser engines and enriched JSON, Markdown, and print exports.

### Acceptance criteria

- Python, Flask, and browser engines produce the same deterministic Contract 1.1 fixture.
- Contract 1.0 records migrate with provenance and review warnings.
- Assumed and observed persona attributes remain visibly distinct.
- Journey stages link evidence, opportunity, owner, and proposed experiments.
- Analytics fields outside the approved behavioral schema are discarded and never become demographic or intent claims.
- Saving a revision indexes personas, stakeholders, and journeys into the active workspace library.
- Research assets cannot be listed or reused across workspace boundaries.
- Revision restoration and asset reuse create new immutable revisions.
- The complete release validation and plugin package inspection succeed.
