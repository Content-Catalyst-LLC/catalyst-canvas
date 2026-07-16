# Python Adapters

New development should import the canonical package:

```python
from catalyst_canvas import generate_canvas, validate_contract
from catalyst_canvas.exporters import export_json, export_markdown, export_print_html
```

The supported CLI is:

```bash
python -m catalyst_canvas.cli generate --input input.json --json canvas.json
python -m catalyst_canvas.cli validate --input canvas.json
python -m catalyst_canvas.cli migrate --input legacy.json --output canvas.json
```

`python/catalyst_canvas_core.py` and `python/catalyst_canvas_brief.py` preserve older imports and command flags. Both delegate to the canonical package and are deprecated for new development.
