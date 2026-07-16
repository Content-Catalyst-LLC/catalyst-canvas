# Storage migration for v2.0.0

The v2.0.0 SQLite migration adds a workspace-scoped `platform_records` index for:

- platform connections;
- interoperability profiles;
- workflow links;
- exchange records;
- platform events.

Canonical Canvas JSON remains the source of truth. The index is rebuilt from the current immutable project revision whenever a project is saved.

The release installer does not replace ignored SQLite runtime databases. Existing databases remain byte-for-byte unchanged during source installation. The updated application creates required tables and normalizes projects to Contract 2.0 when the database is opened and records are read or saved.
