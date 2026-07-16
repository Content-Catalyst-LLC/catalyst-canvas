# WordPress Demo

The public Catalyst Canvas demo lives in:

```text
wordpress/catalyst-canvas-demo/
```

Build the versioned plugin package from the repository root:

```bash
python scripts/build_plugin.py
```

The generated artifact is:

```text
dist/catalyst-canvas-demo-v1.1.1.zip
```

Install it through **Plugins → Add New → Upload Plugin**, activate it, and add:

```text
[catalyst_canvas_demo]
```

The plugin runs client-side. Visitor form inputs are not submitted to Sustainable Catalyst. The generated JSON includes the plugin version supplied by the PHP render layer.
