# Catalyst Canvas Export Specification

Catalyst Canvas v1.4.0 exports the same validated `catalyst-canvas/1.1` document through JSON, Markdown, and standalone print HTML.

## JSON

JSON is the canonical machine-readable representation and must validate against `schemas/catalyst_canvas_contract_1_1.schema.json`. It includes project research records and the normalized research summary.

## Markdown

Markdown preserves contract version, Canvas and revision IDs, status, updated timestamp, research readiness, persona detail, stakeholder mapping, journey stages, design records, testing records, review notes, and provenance in a stable order.

## Print HTML

The HTML exporter is dependency-free, self-contained, and print-safe. It is intended for browser printing or Save as PDF without changing the underlying contract.

All exporters validate before writing. Invalid contracts fail rather than producing partial artifacts.
