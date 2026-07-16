# Canvas Contract 1.3

`catalyst-canvas/1.3` is the canonical interoperable document contract for Catalyst Canvas v1.6.0.

Contract 1.3 preserves the research and evidence ledger from Contract 1.2 and adds portable framework definitions, prompt packs, ideation sessions, idea cards, clusters, votes, merges, and explicit lineage from challenge and HMW question to prototype.

## Compatibility

- Contract 1.0, 1.1, and 1.2 payloads migrate through the canonical normalization engine.
- Migration records `provenance.migrated_from` and a human-review warning.
- Unknown future contract versions fail with an explicit compatibility error.
- Historical schemas remain in the repository as migration sources.

## New top-level records

- `challenge_id`
- `custom_frameworks`
- `prompt_packs`
- `ideation_sessions`
- `ideas`
- `idea_clusters`
- `ideation_summary`

## Framework records

Frameworks define a stable key, name, category, description, intended uses, limitations, required inputs, output types, supported ideation modes, structured prompts, origin, organization, creator, version, and tags.

Built-in and custom framework definitions use the same normalized shape. Custom records can therefore move between projects and installations without source-code changes.

## Idea lineage

Each idea may retain:

- its ideation session;
- originating challenge and HMW question;
- originating prompt;
- author and rationale;
- tags, votes, and voters;
- cluster membership;
- parent and merge relationships;
- linked evidence and assumptions;
- linked prototype records.

Merged ideas remain present with `status: merged` and a `merged_into_id`, preserving the decision trail.

## Ideation indicators

`ideation_summary` reports recorded session, idea, cluster, vote, selection, merge, prototype-link, and orphaned-lineage counts. These indicators describe recorded activity. They are not scores of concept quality, feasibility, impact, or decision readiness.

## Authoritative files

- Schema: `schemas/catalyst_canvas_contract_1_3.schema.json`
- Shared input fixture: `fixtures/canvas_contract_1_3.input.json`
- Shared expected fixture: `fixtures/canvas_contract_1_3.expected.json`
- Built-in registry: `contracts/frameworks.json`
