# Catalyst Canvas Submission Notes

Catalyst Canvas has been refreshed from the older local Flask/demo structure into a more coherent Sustainable Catalyst module.

## Current status

The repository now contains:

- refreshed `app/` Flask package with an application factory, route blueprint, service layer, and SQLite persistence;
- refreshed `templates/` UI for Define, Empathize, Personas, Ideate, Prototype, Test, and Export workflows;
- refreshed `demo/` folder with seed script, reset script, GA4-style sample CSV, and regenerated SQLite demo databases;
- root `app.py` launcher for local development;
- root `catalyst.sqlite3` seeded demo database;
- repository-level Python brief generator in `python/`;
- JSON schema, sample data, examples, docs, tests, and GitHub Actions workflow;
- WordPress shortcode plugin for the public Catalyst Canvas page.

## Local run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 demo/seed_demo.py
python3 app.py
```

Open <http://127.0.0.1:5000>.

## WordPress demo

The WordPress plugin lives in:

```text
wordpress/catalyst-canvas-demo/
```

Use this shortcode on the Catalyst Canvas page:

```text
[catalyst_canvas_demo]
```

## Boundary

Catalyst Canvas is a design-thinking, problem-framing, and experimentation workflow. It does not guarantee product-market fit, implementation success, funding, adoption, impact, compliance, or decision accuracy.
