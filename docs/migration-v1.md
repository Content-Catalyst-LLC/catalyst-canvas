# Canvas v1.x Migration

Catalyst Canvas v1.2.0 recognizes three earlier payload families:

1. original Python core exports containing `version`, `generated_at`, `persona`, and `test_plan`;
2. legacy wrapper exports containing `inputs` and `canvas`;
3. Flask flat payloads containing challenge, audience, goal, and constraint fields.

Migration creates Canvas and revision IDs, normalizes nested records, and adds provenance warnings. Because earlier formats did not distinguish all evidence, persona-confidence, stakeholder, and review fields, migrated records should be reviewed before publication or decision use.

Unknown payloads and future `catalyst-canvas/*` versions are rejected rather than silently coerced.

Use:

```bash
python -m catalyst_canvas.cli migrate --input legacy.json --output canonical.json
```
