# Python Core

This folder contains a dependency-light Catalyst Canvas brief generator.

## Generate JSON

```bash
python3 python/catalyst_canvas_core.py \
  --input data/catalyst_canvas_sample_input.json \
  --output outputs/sample_canvas_brief.json
```

## Generate Markdown

```bash
python3 python/catalyst_canvas_core.py \
  --input data/catalyst_canvas_sample_input.json \
  --markdown outputs/sample_canvas_brief.md
```

The generator is intentionally conservative: it creates structured draft artifacts for review, not final strategy or professional advice.
