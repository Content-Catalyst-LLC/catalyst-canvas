# WordPress Plugin

The v1.3.0 shortcode plugin uses four scripts:

1. generated contract/framework data;
2. the shared browser Canvas engine;
3. the presentation and interaction layer.

Build:

```bash
python scripts/sync_contract_assets.py
python scripts/build_plugin.py
```

Artifact:

```text
dist/catalyst-canvas-demo-v1.3.0.zip
```

Shortcode:

```text
[catalyst_canvas_demo]
```

Generated JSON declares `catalyst-canvas/1.0`. Visitor inputs remain in the browser.
