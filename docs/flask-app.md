# Catalyst Canvas Flask App

The local Flask app is a repository companion to the public WordPress demo. It is useful for testing Canvas workflows, generating reviewable local briefs, and preserving examples in SQLite.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 demo/seed_demo.py
python3 app.py
```

Open <http://127.0.0.1:5000>.

## Workflow

```text
Define → Empathize → Ideate → Prototype → Test → Export
```

## Data

The app stores local briefs in `catalyst.sqlite3`. The demo seed database is also written to `demo/catalyst_seed.sqlite3`.

## Boundary

The app is an educational demo. It does not replace user research, domain expertise, legal review, sustainability assurance, implementation planning, or professional judgment.
