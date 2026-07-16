# Repository Architecture

Catalyst Canvas v1.1.1 is organized as a reproducible multi-surface repository.

- `VERSION` is the canonical release version.
- `python/catalyst_canvas_core.py` is the maintained deterministic brief generator.
- `python/catalyst_canvas_brief.py` is a deprecated v1.x compatibility adapter.
- `app/` and `templates/` provide the local Flask workflow.
- `demo/seed_demo.py` generates disposable local SQLite databases.
- `schemas/` defines the validated core brief export.
- `wordpress/catalyst-canvas-demo/` provides the public shortcode demo.
- `scripts/validate_release.py` is the authoritative verification command.
- `scripts/build_plugin.py` builds the versioned WordPress package.
- `tests/` runs under both pytest and unittest from the repository root.

Runtime databases, generated output, and release ZIP files are intentionally excluded from source control.
