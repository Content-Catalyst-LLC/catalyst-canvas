# WordPress Plugin

The v2.0.0 shortcode plugin uses four dependency-free scripts:

1. generated release and registry data;
2. the shared browser Canvas Contract 2.0 engine;
3. the browser-local workspace and revision manager;
4. the interactive form and report interface.

Build it with:

```bash
python scripts/sync_contract_assets.py
python scripts/build_plugin.py
```

The versioned archive is:

```text
dist/catalyst-canvas-demo-v2.0.0.zip
```

Generated JSON declares `catalyst-canvas/2.0`. The plugin supports structured research, evidence, ideation, prioritization, prototypes, hypotheses, experiment plans and runs, learning decisions, iteration history, handoff plans, descriptive readiness indicators, local project persistence, Contract 1.0–1.6 migration, Markdown export, JSON download, and browser printing.

Version 2.0.0 also exposes browser-local platform connections, interoperability profiles, workflow links, exchange records, events, platform readiness, and deterministic exchange downloads. HMAC signing keys are intentionally excluded from the public browser surface.
