# v1.2 to v1.3 Storage Migration

`init_db()` performs an idempotent in-place upgrade.

1. The existing `canvas_briefs` table is retained.
2. The default local workspace is created when absent.
3. Each unmigrated legacy row receives a project record.
4. Its payload is migrated and validated as Canvas Contract 1.0.
5. One immutable revision is written and selected as the project's current revision.
6. `legacy_storage_id` prevents duplicate imports on later starts.

New saves write only to `projects` and `canvas_revisions`. Legacy numeric export URLs are resolved through the migration link.

Before installing, the macOS installer creates a repository backup and preserves ignored `.sqlite3`, `.db`, and `.env` runtime files.
