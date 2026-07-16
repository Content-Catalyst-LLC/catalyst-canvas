# Catalyst Canvas v1.2.0

## Canonical Canvas Contract and Shared Engine

Version 1.2.0 establishes one authoritative domain contract for the Python, CLI, Flask, and WordPress surfaces.

### Delivered

- Canvas Contract 1.0 and strict JSON Schema.
- Canonical Python normalization, generation, validation, migration, and export package.
- Flask form/view adapter and validated SQLite boundaries.
- WordPress browser adapter with generated framework data.
- Stable JSON, Markdown, and print-report exports.
- v1.0/v1.1 migration rules and provenance warnings.
- Shared deterministic fixtures across Python, Flask, and Node.
- Expanded release and package validation.

### Acceptance results

- The shared fixture produces the same contract in Python, Flask, and WordPress.
- Every newly saved or exported Canvas declares `catalyst-canvas/1.0`.
- Recognized legacy exports migrate with provenance; unknown or future versions fail with actionable messages.
- 31 tests pass under pytest and unittest, with an additional Node conformance test.
