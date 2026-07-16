# Shared Engine

Catalyst Canvas uses one canonical data model across Python, Flask, CLI, and WordPress.

- `contract.py` normalizes and validates Canvas Contract 1.5.
- `ledger.py` governs sources, evidence, claims, assumptions, and research handoffs.
- `ideation.py` governs framework sessions, ideas, clusters, votes, merges, and lineage.
- `prioritization.py` governs score inputs, criteria, gates, sensitivity, and decision handoffs.
- `experiments.py` governs prototypes, hypotheses, plans, runs, results, learning decisions, iterations, and experiment handoffs.
- `migrations.py` upgrades recognized Contracts 1.0 through 1.4 and legacy payloads.

The WordPress engine is implemented in JavaScript because it runs locally in the visitor's browser. Its generated registry and exact Contract 1.5 fixture are compared with Python and Flask in Node conformance tests.
