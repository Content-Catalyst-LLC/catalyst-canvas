# Flask Application

The Flask application is a local workspace adapter over Canvas Contract 1.1 and Workspace Project Contract 1.0.

- Forms are mapped into the canonical contract by `catalyst_canvas.adapters.flask`.
- SQLite writes validate the complete contract before persistence.
- Existing Contract 1.0 and legacy v1.x payloads migrate on read or import.
- Every save creates an immutable revision and indexes current research records.
- `/research` provides persona, stakeholder, and journey editing plus reusable workspace assets.
- `GET /api/research/assets` exposes workspace-scoped research records and counts.
- JSON, Markdown, and print HTML exports validate before delivery.
- `POST /api/canvas/import` accepts canonical or recognized legacy JSON.
- Schema endpoints expose both canonical schemas.

Run:

```bash
python demo/seed_demo.py
python app.py
```
