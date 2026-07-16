# Storage Migration for v1.6.0

The v1.6.0 installer replaces tracked application source while preserving ignored runtime databases and local environment files.

When the updated application reads a stored Canvas revision:

1. Canvas Contracts 1.0, 1.1, or 1.2 migrate to Contract 1.3.
2. Existing workspace, project, Canvas, and revision identifiers remain stable.
3. Existing personas, journeys, ledger records, prototypes, tests, and handoffs remain intact.
4. Framework, prompt-pack, session, idea, and cluster fields are normalized without inventing research or decision history.
5. Saving the migrated record creates a new immutable revision rather than overwriting prior history.

The installer itself does not rewrite the SQLite file. Migration occurs through the application engine after initialization.
