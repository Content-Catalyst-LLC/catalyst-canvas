# Canvas Contract 1.6

Canvas Contract 1.6 is the canonical document contract for Catalyst Canvas v1.9.0.

```text
catalyst-canvas/1.6
```

The authoritative schema is `schemas/catalyst_canvas_contract_1_6.schema.json`.

Contract 1.6 retains all research, ideation, prioritization, prototype, and experiment records from Contract 1.5 and adds:

- `workspace_members`
- `review_assignments`
- `comments`
- `approvals`
- `publication_records`
- `release_history`
- `publication_handoffs`
- `collaboration_summary`

Every collaboration record has a stable identifier. Every persisted change creates a new Canvas revision. Contracts 1.0 through 1.5 migrate to Contract 1.6 with provenance and review warnings.
