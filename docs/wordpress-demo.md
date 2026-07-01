# WordPress Demo Installation

The WordPress plugin lives in:

```text
wordpress/catalyst-canvas-demo/
```

## Build zip

```bash
cd wordpress
zip -r ../catalyst-canvas-demo.zip catalyst-canvas-demo -x "*/.DS_Store"
```

## Install

1. Open WordPress admin.
2. Go to **Plugins → Add New → Upload Plugin**.
3. Upload `catalyst-canvas-demo.zip`.
4. Activate the plugin.
5. Add `[catalyst_canvas_demo]` to the Catalyst Canvas page.

## Boundary

The demo runs in the browser and does not submit visitor inputs to Sustainable Catalyst. It is an educational and research-oriented design-thinking aid, not a consulting or advisory service.
