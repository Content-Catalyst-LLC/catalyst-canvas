# Flask Application

The Flask application is a local workflow adapter over Canvas Contract 1.0.

- Forms are mapped into the canonical contract by `catalyst_canvas.adapters.flask`.
- SQLite writes validate the complete contract before persistence.
- Existing flat v1.x payloads migrate on read.
- JSON, Markdown, and print HTML exports validate before delivery.
- `POST /api/canvas/import` accepts canonical or recognized legacy JSON.
- `GET /api/contract/schema.json` exposes the canonical JSON Schema.

Run:

```bash
python demo/seed_demo.py
python app.py
```
