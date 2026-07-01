# Local Demo Notes

The local demo is intentionally lightweight:

- Flask app with local SQLite persistence
- no external database service required
- no direct analytics connection
- no AI API dependency
- no data submission to Sustainable Catalyst

## Reset demo data

```bash
bash demo/demo_reset.sh
```

## Export paths

After saving a Canvas brief, use:

```text
/api/canvas/<id>.json
/export/<id>.md
```

## WordPress versus Flask

The WordPress plugin is the public page demo. The Flask app is the local repository demonstration and development companion.
