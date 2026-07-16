# Canvas Contract 2.0

Canvas Contract 2.0 is the canonical document contract for Catalyst Canvas v2.0.0.

```text
catalyst-canvas/2.0
```

The authoritative schema is `schemas/catalyst_canvas_contract_2_0.schema.json`.

## Platform additions

Contract 2.0 retains every Contract 1.6 record and adds:

- `platform_connections`
- `interoperability_profiles`
- `workflow_links`
- `exchange_records`
- `platform_events`
- `platform_summary`

Each record has a stable identifier and belongs to the immutable Canvas revision in which it appears.

## Related exchange contracts

```text
catalyst-canvas-exchange/2.0
catalyst-canvas-event/1.0
catalyst-canvas-capabilities/1.0
```

Exchange packages carry source Canvas and revision identity, target product, profile, payload type, related record IDs, deterministic payload, SHA-256 checksum, creation metadata, and a boundary statement. An institutional service may add an HMAC-SHA256 signature.

## Trust boundary

A connection status records the state asserted by the workspace. It does not prove current remote availability, identity, authorization, security, delivery, retention compliance, or acceptance. Receiving systems must independently authenticate the sender, validate the contract, authorize the action, apply redaction and retention controls, and acknowledge or reject the package.

## Migration

Contracts 1.0 through 1.6 normalize into Contract 2.0. Existing identities and records are preserved. New platform collections default to empty records when no prior integration metadata exists. Provenance records the source version and a review warning. Unknown future versions are rejected.
