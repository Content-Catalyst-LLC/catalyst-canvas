# WordPress Plugin

The v1.7.0 shortcode plugin uses four dependency-free scripts:

1. generated release and framework data;
2. the shared browser Canvas Contract 1.4 engine;
3. the browser-local project and revision workspace;
4. the presentation, research-studio, evidence-ledger, and export layer.

Build:

```bash
python scripts/sync_contract_assets.py
python scripts/build_plugin.py
```

Artifact:

```text
dist/catalyst-canvas-demo-v1.7.0.zip
```

Shortcode:

```text
[catalyst_canvas_demo]
```

Generated JSON declares `catalyst-canvas/1.4`. The plugin supports structured personas, stakeholder maps, journeys, sources, evidence, claims, assumptions, research questions, handoff plans, descriptive ledger indicators, local project persistence, Contract 1.0–1.3 migration, Markdown export, JSON download, and browser printing. Visitor inputs remain in the browser.
