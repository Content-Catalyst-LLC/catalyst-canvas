# Catalyst Canvas Flask App

The local Flask app is a repository companion to the public WordPress demo. It supports local workflow testing, reviewable briefs, and disposable SQLite persistence.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python demo/seed_demo.py
python app.py
```

Open <http://127.0.0.1:5000>.

## Workflow

```text
Define → Empathize → Ideate → Prototype → Test → Export
```

## Data

The app stores local briefs in `catalyst.sqlite3`. The seed script also writes `demo/catalyst_seed.sqlite3`. These runtime databases are ignored and can be regenerated at any time.

## Environment safety

The default `development` mode uses a local-only fallback secret. Set `CATALYST_CANVAS_ENV=production` and provide `CATALYST_CANVAS_SECRET` for any production-like run. Debug mode is enabled only for `development` and `local`.

## Boundary

The app is an educational and research-oriented workspace. It does not replace user research, domain expertise, legal review, sustainability assurance, implementation planning, or professional judgment.
