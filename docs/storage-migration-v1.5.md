# Storage Migration for v1.5.0

`init_db()` performs an idempotent in-place upgrade for the Research, Evidence, and Assumption Ledger.

## Behavior

1. Existing workspaces, projects, immutable revisions, autosaves, archive state, and project metadata remain intact.
2. Existing Contract 1.0 or 1.1 Canvas payloads migrate to Contract 1.2 when read, imported, saved, restored, duplicated, or reused.
3. Current source, evidence, claim, assumption, research-question, interview-guide, and observation-note records are indexed in the workspace research-asset registry on save.
4. Re-indexing is idempotent for the current project and revision.
5. Assets remain constrained to their workspace and retain contributing project and revision links.
6. Historical revisions remain immutable; migration creates normalized current output without rewriting the audit history silently.

## Installer preservation

The macOS installer preserves ignored SQLite databases and `.env` configuration before replacing tracked repository files. Runtime databases remain excluded from Git and release ZIPs.
