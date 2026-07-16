# Catalyst Canvas Demo Workflow

The v1.5.0 workflow follows:

```text
challenge → research questions → sources → evidence → claims and assumptions → personas/stakeholders/journeys → POV/HMW → prototype → experiment → review → handoff/export
```

The WordPress plugin provides the public browser-local demonstration. The Flask workspace provides persistent projects, immutable revisions, reusable research assets, and the Evidence Ledger. The canonical Python package provides reproducible contracts, migrations, exports, and handoff packages.

## Recommended CLI

```bash
python -m catalyst_canvas.cli generate \
  --input data/catalyst_canvas_sample_input.json \
  --json outputs/sample-canvas.json \
  --markdown outputs/sample-canvas.md \
  --html outputs/sample-canvas.html
```

Existing v1.x automation may continue to call `python/catalyst_canvas_core.py` or `python/catalyst_canvas_brief.py`; both are compatibility adapters over the canonical package.
