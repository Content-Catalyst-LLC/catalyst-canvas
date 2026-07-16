# v1.3 to v1.4 Storage Migration

`init_db()` performs an idempotent in-place upgrade for the Persona, Stakeholder, and Journey Studio.

1. Existing workspaces, projects, and immutable revisions remain unchanged.
2. The `research_assets` table is created for normalized persona, stakeholder, and journey records.
3. The `project_research_links` table records which projects and revisions contributed each asset.
4. Existing Canvas Contract 1.0 payloads are migrated to Contract 1.1 when read or saved.
5. Saving a revision indexes its research records into the workspace library.
6. Re-running initialization does not duplicate projects, revisions, or research links.

Research reuse creates a new project revision and leaves the source project and historical records unchanged. Workspace checks are applied before listing or reusing assets.

The macOS installer preserves ignored SQLite, database, and `.env` files while replacing tracked source files.
