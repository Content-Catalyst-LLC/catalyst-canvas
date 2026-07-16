# Catalyst Canvas WordPress Plugin

## Location

```text
wordpress/catalyst-canvas-demo/
```

## Versioning

The repository `VERSION` file is canonical. The release validator confirms that the plugin header and internal asset version match it.

## Build

```bash
python scripts/build_plugin.py
```

Expected package:

```text
dist/catalyst-canvas-demo-v1.1.1.zip
```

## Install

1. Open **Plugins → Add New → Upload Plugin**.
2. Upload the versioned ZIP.
3. Activate **Catalyst Canvas Demo**.
4. Add `[catalyst_canvas_demo]` to the desired page.

## Validation

```bash
python scripts/validate_release.py
```

When PHP and Node.js are available, the validator checks both the plugin PHP file and its JavaScript asset.
