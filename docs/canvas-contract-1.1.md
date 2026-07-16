# Canvas Contract 1.1

`catalyst-canvas/1.1` is the canonical interoperable document contract for Catalyst Canvas v1.4.0.

## Compatibility

Contract 1.1 is a backward-compatible research-model upgrade over Contract 1.0. Imports and persisted 1.0 records are normalized into 1.1 with migration provenance and a warning that the newly structured research fields require review. Unknown future `catalyst-canvas/*` versions are rejected.

## Identity and lifecycle

- `canvas_id` identifies the durable Canvas.
- `revision_id` identifies one immutable revision.
- `status`, owner context, and timestamps preserve lifecycle context.

## Research records

### Audiences

The audience object distinguishes primary, secondary, affected, and excluded groups so the boundaries of the current design scope remain visible.

### Personas and empathy maps

Personas include role, context, jobs, goals, needs, pains, gains, behaviors, barriers, motivations, accessibility needs, channels, quotes, evidence, assumptions, tags, source notes, confidence, and validation status. Empathy maps preserve says, thinks, does, feels, sees, hears, pains, and gains.

Persona attributes explicitly record whether a statement is observed, research-derived, or assumed, together with confidence, evidence identifiers, and notes.

### Stakeholders

Stakeholders include type, relationship, one-to-five influence, interest, and impact scores, responsibilities, tensions, stance, decision role, engagement strategy, notes, evidence links, dependencies, and tags.

### Journeys

Journeys link to a persona and include scenario, desired outcome, lifecycle status, evidence and assumption links, tags, and ordered stages. Each stage can capture actions, questions, thoughts, pain points, frictions, opportunities, touchpoints, channels, metrics, emotion, evidence, proposed experiment identifiers, and ownership.

### Behavioral signals

`behavioral_signals` stores normalized analytics or observation rows as `hint` evidence only. The contract requires a limitation statement and does not permit demographic or identity fields. Analytics cannot establish intent, identity, motivation, or demographic attributes.

### Research summary

`research_summary` provides normalized counts and a readiness assessment derived from record completeness, evidence linkage, confidence, validation state, stakeholder mapping, journey coverage, and behavioral-signal presence. It is an operational review signal, not independent research certification.

## Design and decision records

The contract retains structured challenge, audience, goal, constraints, point of view, HMW prompts, framework prompts, evidence, assumptions, prototypes, tests, review notes, and provenance.

## Validation

The authoritative schema is `schemas/catalyst_canvas_contract_1_1.schema.json`. Python saves, imports, storage reads, and exports run full JSON Schema validation. The browser engine uses structural validation and must match the same deterministic fixture in Node conformance tests.
