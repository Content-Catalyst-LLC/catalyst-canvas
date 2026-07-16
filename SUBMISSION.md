# Catalyst Canvas v1.1.1 Submission Notes

## Release

**Catalyst Canvas v1.1.1 — Repository Integrity and CI Repair**

This release repairs the v1.1.0 repository baseline before product expansion. It does not introduce a new Canvas workflow. It makes the existing Flask, Python, schema, WordPress, test, and packaging surfaces reproducible and version-consistent.

## Included repairs

- canonical root `VERSION` file;
- synchronized v1.1.1 manifest, Python exports, schema, plugin header, and asset versions;
- root-runnable pytest and unittest suites;
- one GitHub Actions workflow;
- deterministic release validator and plugin builder;
- MIT license;
- production secret enforcement;
- removal of committed runtime SQLite and generated ZIP artifacts;
- formal deprecation of the duplicate Python brief engine as a compatibility adapter.

## Validate

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/validate_release.py
```

## Run locally

```bash
python demo/seed_demo.py
python app.py
```

Open <http://127.0.0.1:5000>.

## Build the WordPress package

```bash
python scripts/build_plugin.py
```

Expected artifact:

```text
dist/catalyst-canvas-demo-v1.1.1.zip
```

Shortcode:

```text
[catalyst_canvas_demo]
```
