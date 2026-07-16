# Workspace Project Contract 1.0

Catalyst Canvas v1.3.0 introduced `catalyst-canvas-workspace/1.0` as the stable project-registry record surrounding immutable Canvas revisions.

A project record contains:

- `workspace_id` and stable `project_id`;
- title, description, status, and tags;
- created, updated, and archived timestamps;
- the current Canvas and revision identities;
- total immutable revision count.

The authoritative schema is `schemas/catalyst_canvas_workspace_1_0.schema.json`.

The workspace contract does not duplicate the full Canvas. In v1.6.0, Canvas payloads validate against `catalyst-canvas/1.3`; Contracts 1.0 and 1.1 migrate on read, import, save, or reuse. Research and ledger assets are stored separately and linked back to contributing projects and revisions.
