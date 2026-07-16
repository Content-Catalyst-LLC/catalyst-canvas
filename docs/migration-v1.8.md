# Migration to Catalyst Canvas v1.8.0

Version 1.8.0 upgrades saved projects to Canvas Contract 1.5 when they are read by the shared engine.

## Supported sources

- Canvas Contract 1.0
- Canvas Contract 1.1
- Canvas Contract 1.2
- Canvas Contract 1.3
- Canvas Contract 1.4
- recognized legacy Python, wrapper, and Flask records

## Behavior

Existing prototype and test-plan fields are retained. Prototype records are normalized into the richer Contract 1.5 structure. Legacy tests remain in `tests` and also seed governed experiment plans when no `experiment_plans` are present.

New hypotheses, plans, runs, decisions, iterations, handoffs, and summary fields receive deterministic defaults where needed. The original source contract is recorded in `provenance.migrated_from`, and a review warning identifies the newly normalized research, ideation, prioritization, prototype, and experiment fields.

## Review after migration

Review prototype ownership and version, hypothesis wording and falsification conditions, participant assumptions, metrics and thresholds, safeguards, evidence links, and any automatically derived experiment plan.
