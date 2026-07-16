# Catalyst Canvas v1.3.0

## Persistent Projects and Workspace Management

Version 1.3.0 turns the single-brief Flask demonstration and browser-only generator into durable project workspaces.

### Project workspace

- Every Canvas belongs to a workspace-scoped project.
- Projects carry stable project IDs, titles, descriptions, tags, status, and timestamps.
- Active and archived projects can be searched and filtered independently.
- Projects can be duplicated without sharing Canvas or revision identities.
- Archive is reversible and keeps all project history intact.

### Immutable revision history

- Every manual save and autosave creates an immutable Canvas Contract 1.0 revision.
- Projects retain a current-revision pointer rather than overwriting earlier payloads.
- Historical revisions can be exported or restored as a new revision.
- Autosaves are retained separately and pruned to a bounded history.
- Revision records identify save type, timestamp, change note, and restoration provenance.

### Storage migration

- Existing v1.2 `canvas_briefs` rows migrate into the default local workspace.
- Old numeric JSON and Markdown export URLs continue to resolve.
- The legacy table is retained as a compatibility source but receives no new writes.
- Local SQLite databases remain ignored and are preserved by the installer.

### Flask workspace

- Added workspace and project dashboards.
- Added project creation, switching, metadata editing, search, duplicate, archive, restore, and history routes.
- Added workspace-scoped project, revision, autosave, and schema APIs.
- Added debounced form autosave after a project has been created.
- Added workspace boundary checks to project and export routes.

### WordPress browser workspace

- Added localStorage-backed projects and revisions.
- Added save, autosave, switch, duplicate, archive, and new-project controls.
- Browser workspace data remains on the visitor's device and is not transmitted to Sustainable Catalyst.
- Added a dependency-free browser workspace module with Node tests.

### Contracts and validation

- Canvas documents remain on `catalyst-canvas/1.0`.
- Added `catalyst-canvas-workspace/1.0` for project registry records.
- Expanded Python, Flask, migration, browser, syntax, schema, and package validation.
