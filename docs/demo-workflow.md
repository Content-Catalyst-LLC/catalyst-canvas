# Catalyst Canvas Demo Workflow

The current Canvas workflow follows:

```text
challenge → audience → goal → constraint → persona → POV → HMW → ideas → prototype → test plan → export
```

The WordPress plugin provides the public guided demo. The maintained Python core provides reproducible JSON and Markdown exports.

## Recommended CLI

```bash
python python/catalyst_canvas_core.py \
  --input data/catalyst_canvas_sample_input.json \
  --output outputs/sample-canvas-brief.json \
  --markdown outputs/sample-canvas-brief.md
```

## Legacy-compatible CLI

Existing v1.x automation may continue to call `python/catalyst_canvas_brief.py`. That module is now a compatibility adapter over the core engine and should not be used for new development.
