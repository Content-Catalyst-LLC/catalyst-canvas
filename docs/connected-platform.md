# Connected Strategic Design Platform

Catalyst Canvas v2.0.0 connects strategic-design work to the rest of the Sustainable Catalyst platform through explicit, reviewable contracts.

## Product connection records

A connection records the target product, direction, lifecycle status, endpoint, authentication mode, declared capabilities, data classes, accepted contracts, retention statement, owner, and verification note.

Supported product keys are:

```text
knowledge_library
research_librarian
site_intelligence
workbench
decision_studio
research_lab
feature_support
contact_engagement
wordpress
public_api
```

## Interoperability profiles

Profiles define the exchange rules shared by one or more products:

- supported contracts and export formats;
- stable-ID and correlation-ID modes;
- event types;
- required fields;
- redaction rules;
- retention boundaries;
- profile lifecycle status and version.

## Workflow links

Workflow links retain cross-product lineage such as:

```text
Knowledge Library source
→ Research Librarian question
→ Canvas claim or assumption
→ Decision Studio alternative
→ Research Lab experiment
→ Canvas learning decision
→ WordPress or Knowledge Library publication
```

Links describe relationships; they do not copy or silently synchronize remote records.

## Exchange integrity

Every generated package uses canonical JSON serialization and a SHA-256 payload checksum. HMAC-SHA256 is optional for institutional transports that share a protected signing key. Verification detects payload changes after signing.

HMAC proves possession of the shared key; it does not replace transport security, user authorization, replay protection, key rotation, audit logging, or receiving-system policy.

## Capability discovery

`GET /api/capabilities` returns the machine-readable `catalyst-canvas-capabilities/1.0` manifest. It lists the Canvas contract, exchange and event contracts, supported products, payload types, integrity modes, and current API routes.

## Platform readiness

Platform readiness composes:

- research and evidence readiness;
- ideation lineage;
- decision gates;
- experiment learning state;
- collaboration and publication gates;
- verified, degraded, and configured connections;
- broken workflow links;
- rejected or unsigned ready exchanges.

The result is a workflow indicator, never an uptime, security, legal-compliance, or institutional-acceptance certification.
