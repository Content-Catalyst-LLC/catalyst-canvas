# Canvas Contract 1.4

`catalyst-canvas/1.4` is the canonical interoperable document contract for Catalyst Canvas v1.7.0.

Contract 1.4 preserves all Contract 1.3 research, evidence, framework, and ideation records while adding transparent prioritization and decision-readiness structures.

## Added records

- `decision_criteria`
- `decision_options`
- `sensitivity_views`
- `decision_notes`
- `decision_handoffs`
- `prioritization_summary`

Decision options carry ICE and RICE models, weighted criterion values, four matrix positions, ethical gates, dependencies, blockers, resource needs, deadlines, recommendation states, evidence, assumptions, research questions, and design lineage.

## Score transparency

Every score input identifies its value, unit, basis, confidence, rationale, evidence links, and assumption links. Weighted rankings are recalculated from normalized raw criterion values. A sensitivity view may override criterion weights, but it cannot overwrite the underlying raw values.

## Gates and readiness

Gate criteria are evaluated independently of weighted rankings. A failed gate produces `blocked_by_gate`. Unknown gate results or incomplete score records produce `needs_review`. A high score alone never marks an option ready.

## Migration

Contracts 1.0 through 1.3 are recognized migration sources. The migration engine records `provenance.migrated_from`, adds a review warning, normalizes missing decision fields, and validates the result against Contract 1.4.
