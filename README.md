# Catalyst Canvas

**Current release: v1.1.1 — Repository Integrity and CI Repair**

Catalyst Canvas is an open-source design-thinking and problem-framing workspace for Sustainable Catalyst. It turns ambiguous challenges into structured, reviewable work products: personas, point-of-view statements, “How might we?” prompts, ideation frameworks, prototype concepts, test plans, assumptions, and review notes.

The repository contains three connected surfaces:

1. **Python core generator** for reproducible JSON and Markdown briefs.
2. **Local Flask application** with SQLite-backed workflow screens.
3. **WordPress shortcode plugin** providing the browser-based `[catalyst_canvas_demo]` experience.

Catalyst Canvas is designed around accountable human review. It does not certify strategy, product-market fit, impact, compliance, or implementation success.

## v1.1.1 release guarantees

- `VERSION` is the canonical repository version source.
- Python exports, the project manifest, JSON Schema, WordPress plugin header, and WordPress asset version are synchronized to v1.1.1.
- Both `pytest` and `unittest` work from the repository root.
- One GitHub Actions workflow runs the authoritative validation command.
- Runtime SQLite databases and generated ZIP files are not source-controlled.
- The legacy `python/catalyst_canvas_brief.py` interface is retained as a documented compatibility adapter over the maintained core generator.
- Production-like Flask environments require an explicit secret key.
- Plugin packaging produces a versioned artifact: `catalyst-canvas-demo-v1.1.1.zip`.

## Repository structure

```text
VERSION                         Canonical release version
app/                            Flask application package
python/                         Core generator and v1.x compatibility adapter
templates/                      Flask workflow templates
demo/                           Deterministic seed script and sample analytics CSV
data/                           Sample Canvas input
schemas/                        JSON Schema for generated core briefs
wordpress/catalyst-canvas-demo/ WordPress shortcode plugin
scripts/                        Release validation and plugin packaging tools
tests/                          Root-runnable pytest and unittest suite
docs/                           Methodology, architecture, and release documentation
outputs/                        Local generated outputs; ignored except .gitkeep
dist/                           Generated release packages; ignored
```

## Requirements

- Python 3.11 or 3.12
- PHP for the optional local WordPress syntax check
- Node.js for the optional local JavaScript syntax check

GitHub Actions provides PHP and Node.js on the Ubuntu runner and performs both syntax checks.

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
cp .env.example .env
```

The application reads environment variables from the process environment. The `.env.example` file documents the supported settings but is not automatically loaded.

## Seed and run the Flask application

```bash
python demo/seed_demo.py
python app.py
```

Open <http://127.0.0.1:5000>.

The seed command creates local `catalyst.sqlite3` and `demo/catalyst_seed.sqlite3` files. Both are ignored by Git.

### Production secret requirement

Local development uses a bounded fallback secret. Any environment other than `development`, `local`, or `test` must provide a real secret:

```bash
export CATALYST_CANVAS_ENV=production
export CATALYST_CANVAS_SECRET="$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')"
python app.py
```

The application exits with a clear error when a production-like environment has no secret.

## Generate a Canvas brief

JSON:

```bash
python python/catalyst_canvas_core.py \
  --input data/catalyst_canvas_sample_input.json \
  --output outputs/sample_canvas_brief.json
```

Markdown:

```bash
python python/catalyst_canvas_core.py \
  --input data/catalyst_canvas_sample_input.json \
  --markdown outputs/sample_canvas_brief.md
```

Both formats include the canonical release version.

## Tests

Pytest:

```bash
python -m pytest tests
```

Unittest:

```bash
python -m unittest discover -s tests -v
```

Both commands are supported from the repository root.

## Authoritative release validation

```bash
python scripts/validate_release.py
```

This command performs:

- version synchronization checks;
- source-tree hygiene checks;
- Python bytecode compilation;
- pytest and unittest execution;
- sample JSON and Markdown generation;
- JSON Schema validation;
- PHP syntax validation when PHP is available;
- JavaScript syntax validation when Node.js is available;
- WordPress plugin ZIP construction and content verification.

## Build the WordPress plugin

```bash
python scripts/build_plugin.py
```

The versioned package is written to:

```text
dist/catalyst-canvas-demo-v1.1.1.zip
```

Upload the ZIP in WordPress under **Plugins → Add New → Upload Plugin**, activate it, and place this shortcode on the Catalyst Canvas page:

```text
[catalyst_canvas_demo]
```

The current public demo runs in the browser and does not submit visitor inputs to Sustainable Catalyst.

## Compatibility module

`python/catalyst_canvas_brief.py` is a deprecated v1.x compatibility adapter. Existing imports remain supported, but new development should use `python/catalyst_canvas_core.py`. The adapter delegates generation to the core engine so the repository no longer maintains two independent Python generation systems.

## License

The repository code is available under the MIT License. See [LICENSE](LICENSE).
