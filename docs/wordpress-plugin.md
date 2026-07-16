# WordPress Plugin

The v1.4.0 shortcode plugin uses four dependency-free scripts:

1. generated release and framework data;
2. the shared browser Canvas Contract 1.1 engine;
3. the browser-local project and revision workspace;
4. the presentation, research-studio, and export layer.

Build:

```bash
python scripts/sync_contract_assets.py
python scripts/build_plugin.py
```

Artifact:

```text
dist/catalyst-canvas-demo-v1.4.0.zip
```

Shortcode:

```text
[catalyst_canvas_demo]
```

Generated JSON declares `catalyst-canvas/1.1`. The plugin supports structured personas, influence/interest stakeholder records, journey stages, local project persistence, Contract 1.0 migration, Markdown export, JSON download, and browser printing. Visitor inputs remain in the browser.
