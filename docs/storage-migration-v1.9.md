# Storage Migration for v1.9.0

The installer preserves ignored SQLite databases and `.env` configuration. The updated storage service adds workspace-member and collaboration-record indexes without rewriting prior revision payloads.

When an older project is opened, its Canvas is normalized to Contract 1.6 in memory. The next manual save, autosave, comment, review, approval, or publication action creates a new immutable Contract 1.6 revision.
