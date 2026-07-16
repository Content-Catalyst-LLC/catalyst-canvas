# Storage Migration for v1.7.0

The v1.7.0 installer replaces tracked application source while preserving ignored SQLite runtime databases and local `.env` configuration.

No destructive database rewrite occurs during installation. When the updated application reads an existing project revision, Contracts 1.0 through 1.3 normalize to Contract 1.4. The migrated Canvas is written only through the existing immutable-revision workflow.

The installer validation must prove that:

1. the existing SQLite file remains byte-for-byte unchanged during installation;
2. the updated application can initialize and read the preserved workspace;
3. the active Canvas normalizes to `catalyst-canvas/1.4`;
4. prior projects and revision history remain available.
