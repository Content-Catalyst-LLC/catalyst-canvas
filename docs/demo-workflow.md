# Catalyst Canvas Demo Workflow

The v1.4.0 workflow follows:

```text
challenge → audience → persona research → stakeholder map → journey stages → POV → HMW → framework → evidence and assumptions → prototype → test → review → export
```

The WordPress plugin provides the public browser-local demonstration. The Flask workspace provides persistent projects, revisions, and reusable research assets. The canonical Python package provides reproducible contracts and exports.

## Recommended CLI

```bash
python -m catalyst_canvas.cli generate \
  --input data/catalyst_canvas_sample_input.json \
  --json outputs/sample-canvas.json \
  --markdown outputs/sample-canvas.md \
  --html outputs/sample-canvas.html
```

Existing v1.x automation may continue to call `python/catalyst_canvas_core.py` or `python/catalyst_canvas_brief.py`; both are compatibility adapters over the canonical package.
