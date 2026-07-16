# Canvas Contract 1.0

`catalyst-canvas/1.0` is the interoperable document contract for Catalyst Canvas.

## Identity and lifecycle

- `canvas_id` identifies the durable Canvas.
- `revision_id` identifies a particular revision.
- `status` supports draft, active, review, validated, and archived states.
- `owner_context`, `created_at`, and `updated_at` preserve operational context.

## Problem and human context

The contract separates the challenge, primary/secondary/affected/excluded audiences, goal, constraints, personas, and stakeholders. Persona source type and confidence prevent assumed attributes from appearing as researched facts.

## Design records

POV, HMW, framework prompts, evidence, assumptions, prototypes, tests, and review notes are structured records with stable local IDs and statuses.

## Provenance

Every contract records the generator version, source surface, source version, migration origin, and warnings.

## Validation

The canonical schema is `schemas/catalyst_canvas_contract_1_0.schema.json`. Python saves, imports, and exports run full JSON Schema validation. Browser generation uses the contract engine's structural validator and is checked against the same deterministic fixture in CI.
