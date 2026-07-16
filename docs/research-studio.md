# Persona, Stakeholder, and Journey Studio

The v1.8.0 research studio is the structured design-research layer inside each Catalyst Canvas workspace. It is designed to keep research findings, observations, and assumptions distinguishable throughout framing, journey design, and experimentation.

## Persona studio

Persona records support role and context, jobs, goals, needs, pains, gains, behaviors, barriers, motivations, accessibility needs, preferred channels, quotes, evidence links, assumption links, tags, source notes, confidence notes, and validation state.

Each persona can also contain:

- an empathy map covering says, thinks, does, feels, sees, hears, pains, and gains;
- structured attributes marked as `observed`, `research`, or `assumed`;
- evidence and confidence attached to each attribute;
- an explicit source type and validation status for the overall persona.

Six reusable starting templates are included: civic service, sustainability, research, technical content, institutional, and public interest. Templates remain assumptions until supported by appropriate research.

## Audience designations

Projects distinguish primary and secondary audiences from affected groups and groups deliberately excluded from the current scope. Exclusion describes the limits of the current Canvas; it must not be used to erase affected stakeholders from review.

## Stakeholder map

Stakeholders use one-to-five influence, interest, and impact scores. Records also preserve responsibilities, tensions, stance, decision role, engagement strategy, dependencies, notes, tags, and evidence. The influence/interest matrix is a planning aid, not a ranking of human worth or legitimacy.

## Journey studio

A journey links to a persona and contains an ordered set of stages. Each stage can preserve:

- actions and questions;
- thoughts and emotional direction;
- pain points and explicit frictions;
- touchpoints and channels;
- opportunities and accountable owner;
- evidence links and metrics;
- proposed experiment or test identifiers.

This makes the relationship between a research finding, an opportunity, and a proposed experiment inspectable.

## Behavioral-signal CSV import

The Flask and WordPress surfaces accept UTF-8 analytics CSV data using these columns:

```text
metric,segment,value,period,interpretation,limitation,evidence_ids,tags
```

Extra columns are ignored intentionally. GA4 and other analytics rows are stored only as `hint` evidence. They never create persona identity, intent, motivation, or demographic claims. A behavioral pattern should prompt further qualitative investigation rather than unsupported inference.

Flask uploads are limited to `.csv` files of 2 MB or less. WordPress reads the CSV in the browser and retains it only in that browser's project data.

## Comparison and reusable assets

Saving a Canvas revision indexes personas, stakeholders, and journeys in the active workspace research library. The library supports search, reuse, archive, and workspace-isolated persona or journey comparison. Reuse copies an asset into a new immutable Canvas revision; it does not create shared mutable state.

## Privacy boundary

The Flask surface stores research records in its configured local SQLite database. The WordPress shortcode stores projects and research records in the current browser's localStorage and does not transmit visitor inputs to Sustainable Catalyst.


## Evidence Ledger integration

Persona, stakeholder, and journey evidence links resolve against the Contract 1.5 ledger. Saving a revision indexes both design-research records and source/evidence/claim/assumption records in the active workspace. Reuse creates a new immutable revision and does not mutate the contributing project.
