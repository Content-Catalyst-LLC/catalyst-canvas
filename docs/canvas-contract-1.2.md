# Canvas Contract 1.2

`catalyst-canvas/1.2` is the canonical interoperable document contract for Catalyst Canvas v1.5.0.

## Purpose

Contract 1.2 extends the design-research model with a governed ledger for sources, evidence excerpts, claims, assumptions, research questions, interview guides, observation notes, synthesis tags, and institutional handoffs. It preserves stable Canvas and revision identities and remains deterministic across Python, Flask, CLI, and browser generation.

## Migration

- Contract 1.0 and Contract 1.1 payloads are normalized into Contract 1.2.
- Recognized legacy Python and Flask payloads are migrated through the same canonical engine.
- Migration provenance is recorded in `provenance.migrated_from`.
- Review warnings remain visible after migration because newly structured fields may require human confirmation.
- Unknown future `catalyst-canvas/*` versions are rejected.

## Ledger records

### Sources

Sources identify the origin of research material. Records may include type, creator, publisher, date, URL, owner, rights, limitations, tags, provenance notes, and a Knowledge Library record identifier.

### Evidence

Evidence records preserve a summary or excerpt together with source linkage, locator, citation, URL, capture metadata, confidence, limitations, contradiction links, and tags.

### Claims

Claims preserve a statement, evidence/source/assumption links, state, confidence, uncertainty, limitations, contradictions, missing data, review status, and reviewer metadata. Supported states are:

- `supported`
- `partially_supported`
- `unsupported`
- `disputed`
- `outdated`

### Assumptions

Assumptions preserve ownership, confidence, criticality, consequence, test method, status, evidence links, experiment links, due date, limitations, and tags. Supported statuses include `untested`, `planned`, `testing`, `supported`, `refuted`, `challenged`, and `retired`.

### Research planning

Research questions, interview guides, and observation notes preserve unresolved questions and fieldwork context without forcing premature claims.

### Handoffs

Handoff records describe intended transfer to Knowledge Library or Research Librarian. A separate `catalyst-canvas-research-handoff/1.0` export packages Canvas context, research records, ledger indicators, and provenance.

## Ledger indicators

`ledger_summary` reports descriptive counts and linkage states, including claim-state counts, unsupported/disputed exposure, high-criticality open assumptions, material-claim evidence coverage, and ownership/test gaps. These indicators do not establish truth or score research quality.

## Authoritative files

- Schema: `schemas/catalyst_canvas_contract_1_2.schema.json`
- Shared input fixture: `fixtures/canvas_contract_1_2.input.json`
- Shared expected fixture: `fixtures/canvas_contract_1_2.expected.json`
