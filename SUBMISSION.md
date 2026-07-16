# Catalyst Canvas Submission

**Catalyst Canvas v1.7.0 — Prioritization and Decision Readiness**

This release adds Canvas Contract 1.4, transparent ICE and RICE scoring, editable weighted criteria, four decision matrices, ethical gates, sensitivity analysis, dependencies, blockers, resources, deadlines, recommendation states, decision notes, and provenance-preserving Decision Studio and Workbench handoffs.

Run the release gate before submission:

```bash
python scripts/validate_release.py
```

Build the WordPress package with:

```bash
python scripts/build_plugin.py
```

Canonical release metadata is stored in `VERSION` and `canvas_manifest.json`.
