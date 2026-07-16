# Python Utilities

## Maintained core

`catalyst_canvas_core.py` is the maintained v1.1.1 brief generator.

Generate JSON:

```bash
python python/catalyst_canvas_core.py \
  --input data/catalyst_canvas_sample_input.json \
  --output outputs/sample_canvas_brief.json
```

Generate Markdown:

```bash
python python/catalyst_canvas_core.py \
  --input data/catalyst_canvas_sample_input.json \
  --markdown outputs/sample_canvas_brief.md
```

## Compatibility adapter

`catalyst_canvas_brief.py` preserves the earlier v1.x import and CLI shape. It delegates to the maintained core and is formally deprecated for new development.

The generators create structured drafts for review, not final strategy, assurance, certification, or professional advice.
