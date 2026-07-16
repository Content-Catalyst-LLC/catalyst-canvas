# Catalyst Canvas Submission

**Catalyst Canvas v1.8.0 — Prototype and Experiment Management**

This release adds Canvas Contract 1.5, versioned prototypes, falsifiable hypotheses, participant and metric plans, safeguards, structured experiment runs, observed results, learning decisions, iteration history, and provenance-preserving Research Lab and Workbench handoffs.

Run the release gate before submission:

```bash
python scripts/validate_release.py
```

Build the WordPress package with:

```bash
python scripts/build_plugin.py
```

Canonical release metadata is stored in `VERSION` and `canvas_manifest.json`.
