# Flask Application

The Flask application is a local workspace adapter over Canvas Contract 1.4 and Workspace Project Contract 1.0.

- Forms are mapped into the canonical contract by `catalyst_canvas.adapters.flask`.
- SQLite writes validate the complete contract before persistence.
- Existing Contract 1.0, Contract 1.1, and recognized legacy payloads migrate on read or import.
- Every save creates an immutable revision and indexes current research and ledger records.
- `/research` provides persona, stakeholder, and journey editing plus reusable workspace assets.
- `/ledger` provides source, evidence, claim, assumption, research-question, synthesis-tag, and handoff editing.
- `GET /api/research/assets` exposes workspace-scoped research records and counts.
- `GET /api/ledger` returns the active project's current ledger and descriptive summary.
- `/projects/<project_id>/research-handoff/<target>.json` exports a provenance-preserving institutional handoff.
- JSON, Markdown, print HTML, and handoff exports preserve current Canvas and revision identity.
- `POST /api/canvas/import` accepts canonical or recognized legacy JSON.
- Schema endpoints expose both canonical schemas.

Run:

```bash
python demo/seed_demo.py
python app.py
```
