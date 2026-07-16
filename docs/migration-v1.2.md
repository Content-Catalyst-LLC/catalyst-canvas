# Canvas Migration to Contract 1.2

Catalyst Canvas v1.5.0 recognizes these earlier payload families:

- `catalyst-canvas/1.0`
- `catalyst-canvas/1.1`
- legacy Python core v1.0-v1.1 exports
- legacy wrapper exports
- legacy Flask flat records

All recognized records pass through the canonical migration and normalization engine. The migrated document declares `catalyst-canvas/1.2`, records `provenance.migrated_from`, and preserves warnings that structured ledger fields may require review.

Contract 1.0 and 1.1 source schemas remain in the repository for explicit historical validation. Unknown future `catalyst-canvas/*` versions fail with a compatibility error rather than being silently downgraded.

Migration does not certify converted evidence or assumptions. Owners should review source links, claim states, confidence, limitations, criticality, and experiment links after conversion.
