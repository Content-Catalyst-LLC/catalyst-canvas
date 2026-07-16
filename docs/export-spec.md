# Export Specification

Catalyst Canvas v1.9.0 exports the same validated `catalyst-canvas/1.6` document through JSON, Markdown, and standalone print HTML.

## Canonical exports

JSON preserves all contract records. Markdown and print HTML include research context, claim warnings, assumptions, ideation lineage, decision criteria and rankings, prototypes, hypotheses, participant and metric plans, safeguards, runs, observed results, learning decisions, iteration history, readiness indicators, and provenance.

## Handoff packages

- `catalyst-canvas-research-handoff/1.0` for Knowledge Library and Research Librarian
- `catalyst-canvas-decision-handoff/1.0` for Decision Studio and Workbench decision analysis
- `catalyst-canvas-experiment-handoff/1.0` for Research Lab and Workbench experiment execution or technical validation
- `catalyst-canvas-framework-package/1.0` for portable custom frameworks and prompt packs

Handoffs retain Canvas and revision identities, relevant records, evidence, assumptions, limitations, and provenance. They are transfer packages, not approval or validation certificates.
