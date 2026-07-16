# Storage Migration for v1.8.0

The SQLite schema remains compatible with the v1.7 workspace model. Canvas payloads are migrated at the contract layer when read and saved.

The installer preserves ignored SQLite databases. After the updated application opens a project, its current Canvas is normalized to Contract 1.5. The next manual save or autosave creates a new immutable revision containing the Contract 1.5 payload.

The reusable workspace asset index now includes:

- prototype;
- hypothesis;
- experiment plan;
- experiment run;
- learning decision;
- iteration.

Existing projects and revisions are not deleted or rewritten in place.
