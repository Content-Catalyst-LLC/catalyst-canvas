# Catalyst Canvas Export Specification

Catalyst Canvas v1.6.0 exports the same validated `catalyst-canvas/1.3` document through JSON, Markdown, and standalone print HTML. It also exports a research handoff package for supported institutional targets.

## JSON

JSON is the canonical machine-readable representation and must validate against `schemas/catalyst_canvas_contract_1_3.schema.json`. It includes research records, ledger records, descriptive ledger indicators, and provenance.

## Markdown

Markdown preserves contract version, Canvas and revision IDs, status, timestamps, ledger warnings, challenge context, sources, evidence, claims, assumptions, research planning, persona and stakeholder detail, journeys, prototypes, tests, review notes, handoffs, and provenance in a stable order. Unsupported, disputed, or outdated claims appear in a publication-and-review warning before narrative sections.

## Print HTML

The HTML exporter is dependency-free, self-contained, and print-safe. It is intended for browser printing or Save as PDF without changing the underlying contract.

## Research handoff JSON

`catalyst-canvas-research-handoff/1.0` packages the current Canvas context, complete research ledger, ledger summary, and provenance for `knowledge_library` or `research_librarian`.

All exporters validate or normalize before writing. Invalid contracts fail rather than producing partial artifacts.
