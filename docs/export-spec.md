# Catalyst Canvas Export Specification

Catalyst Canvas v1.2.0 exports the same validated `catalyst-canvas/1.0` document through JSON, Markdown, and standalone print HTML.

## JSON

JSON is the canonical machine-readable representation and must validate against `schemas/catalyst_canvas_contract_1_0.schema.json`.

## Markdown

Markdown preserves contract version, Canvas and revision IDs, status, updated timestamp, all core design sections, and provenance in a stable human-readable order.

## Print HTML

The HTML exporter is dependency-free, self-contained, and print-safe. It is intended for browser printing or Save as PDF without changing the underlying contract.

All exporters validate before writing. Invalid contracts fail rather than producing partial artifacts.
