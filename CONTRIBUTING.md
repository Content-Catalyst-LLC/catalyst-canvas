# Contributing

Contributions should strengthen Catalyst Canvas reviewability, clarity, reproducibility, accessibility, and release integrity.

Before opening a pull request:

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_release.py
```

The validation command must pass from the repository root.

## Version discipline

`VERSION` is the canonical repository version source. A release change must synchronize all checked markers. Do not independently change the WordPress plugin version, JSON Schema version constant, Python export version, or manifest version without updating `VERSION` and running the release validator.

## Generated files

Do not commit:

- SQLite runtime databases;
- files under `dist/`;
- generated files under `outputs/` other than `.gitkeep`;
- local virtual environments or `.env` files.

Use `demo/seed_demo.py` and `scripts/build_plugin.py` to reproduce these artifacts.

## Compatibility boundary

`python/catalyst_canvas_brief.py` is a deprecated v1.x compatibility adapter. Bug fixes may preserve its existing interface, but new generation behavior belongs in `python/catalyst_canvas_core.py` until the canonical package planned for v1.2.0 is introduced.

Avoid contributions that overpromise outcomes, imply professional advice, or make the tool appear to certify strategy, impact, compliance, or product-market fit.
