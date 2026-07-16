# Canvas Migration to Contract 1.1

Catalyst Canvas v1.4.0 recognizes four earlier payload families:

1. Canvas Contract 1.0 documents;
2. original Python core exports containing `version`, `generated_at`, `persona`, and `test_plan`;
3. legacy wrapper exports containing `inputs` and `canvas`;
4. Flask flat payloads containing challenge, audience, goal, and constraint fields.

Migration preserves stable identities when available, creates missing Canvas and revision IDs, normalizes nested records, upgrades personas and stakeholders, initializes journeys and research summaries, and records provenance warnings.

Earlier formats did not distinguish all evidence, confidence, validation, stakeholder, journey, and review fields. Migrated records should therefore be reviewed before publication or decision use.

Unknown payloads and unsupported future `catalyst-canvas/*` versions are rejected rather than silently coerced.

```bash
python -m catalyst_canvas.cli migrate --input legacy.json --output canonical.json
```
