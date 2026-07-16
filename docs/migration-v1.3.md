# Canvas Migration to Contract 1.3

Catalyst Canvas v1.6.0 recognizes:

- Canvas Contract 1.0
- Canvas Contract 1.1
- Canvas Contract 1.2
- legacy Python core and wrapper exports
- legacy Flask flat records

Recognized records pass through the canonical migration and normalization engine. The migrated document declares `catalyst-canvas/1.3`, records `provenance.migrated_from`, and preserves a warning that research and ideation fields may require review.

Older projects receive safe defaults for the v1.6 records:

- a stable primary challenge identifier;
- no custom frameworks or prompt packs;
- a default ideation session aligned to the selected framework;
- no invented ideas or clusters;
- a descriptive ideation summary.

The migration never fabricates authors, votes, rationale, evidence links, or prototype lineage. Unsupported future contract versions are rejected.
