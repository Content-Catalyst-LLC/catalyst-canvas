# Catalyst Canvas Demo Workflow

The online demo mirrors the core Catalyst Canvas method:

```text
challenge → audience → goal → constraint → persona → POV → HMW → ideas → prototype → test plan → export
```

The WordPress plugin provides a public-facing guided demo. The Python companion provides a CLI/export layer for reproducible JSON briefs.

## CLI example

```bash
python3 python/catalyst_canvas_brief.py \
  --challenge "A nonprofit needs clearer impact reporting" \
  --audience "Program director" \
  --goal "build a defensible impact story" \
  --constraint "limited data and stakeholder pressure" \
  --framework JTBD \
  --output outputs/sample-canvas-brief.json
```

