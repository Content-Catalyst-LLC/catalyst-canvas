# Catalyst Canvas

Catalyst Canvas is an open-source design-thinking and problem-framing workspace for Sustainable Catalyst. It helps turn messy problems into structured, reviewable work products: personas, point-of-view statements, “How might we?” prompts, ideation frameworks, prototype concepts, test plans, and decision notes.

The repository now includes three connected layers:

1. **Core Canvas logic** — a lightweight Python brief generator for reproducible design-thinking outputs.
2. **Application layer** — the existing Flask application and templates for structured Canvas workflows.
3. **WordPress demo plugin** — a browser-based online demo for the Catalyst Canvas page using the shortcode `[catalyst_canvas_demo]`.

## Why this exists

Catalyst Canvas supports the Sustainable Catalyst methodology:

- claims should be supportable;
- assumptions should be visible;
- methods should be explainable;
- outputs should be reviewable;
- AI can assist the work, but it does not replace accountable human judgment.

The module is intentionally practical. It is designed for builders, sustainability teams, researchers, students, civic projects, content strategists, and public-interest organizations that need a repeatable way to move from ambiguity to structured experimentation.

## Repository structure

```text
app/                         Existing Flask application layer
templates/                   Existing Flask templates
demo/                        Existing demo database and sample assets
python/                      Reproducible Canvas brief generator and CLI
data/                        Sample input data
schemas/                     JSON schema for Canvas brief outputs
examples/                    Example generated brief
wordpress/catalyst-canvas-demo/  WordPress shortcode demo plugin
docs/                        Methodology, plugin, architecture, and export docs
tests/                       Lightweight test suite
.github/workflows/           CI workflow
outputs/                     Generated local outputs, ignored except .gitkeep
notebooks/                   Notebook workspace and notes
```

## WordPress demo

The WordPress demo plugin adds a guided client-side Canvas tool to any WordPress page.

### Install

1. Run the repository upgrade script or build the zip from this repository.
2. In WordPress, go to **Plugins → Add New → Upload Plugin**.
3. Upload `catalyst-canvas-demo.zip`.
4. Activate the plugin.
5. Add this shortcode to the Catalyst Canvas page:

```text
[catalyst_canvas_demo]
```

The demo runs in the browser. It does not submit visitor inputs to Sustainable Catalyst.

## Python brief generator

Generate a sample Canvas brief:

```bash
python3 python/catalyst_canvas_core.py \
  --input data/catalyst_canvas_sample_input.json \
  --output outputs/sample_canvas_brief.json
```

Generate Markdown:

```bash
python3 python/catalyst_canvas_core.py \
  --input data/catalyst_canvas_sample_input.json \
  --markdown outputs/sample_canvas_brief.md
```

## Tests

```bash
python3 -m pytest tests
```

The test suite intentionally stays lightweight and dependency-minimal.

## Build the plugin zip

From the repository root:

```bash
cd wordpress
zip -r ../catalyst-canvas-demo.zip catalyst-canvas-demo -x "*/.DS_Store"
```

## Boundaries

Catalyst Canvas is a design-thinking and problem-framing tool. It does not guarantee product-market fit, implementation success, stakeholder adoption, funding, impact, compliance, or decision accuracy. Outputs depend on user inputs, assumptions, context, and human review.

## License

Code is governed by the repository license. Site text, Sustainable Catalyst branding, and related written materials may be subject to separate rights unless explicitly licensed.
