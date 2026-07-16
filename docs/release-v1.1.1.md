# Catalyst Canvas v1.1.1 — Repository Integrity and CI Repair

## Objective

Make the current Catalyst Canvas repository reproducible before the v1.2.0 canonical contract and shared-engine work begins.

## Resolved defects

1. `pytest` failed during collection because a legacy test imported an unresolved top-level module.
2. `pytest` and `unittest` exercised different portions of the suite.
3. Two GitHub Actions workflows used different commands and produced contradictory outcomes.
4. Python and WordPress surfaces reported different versions.
5. Runtime SQLite files and a generated plugin ZIP were included in the source snapshot.
6. The repository referenced licensing without including a root license file.
7. The Flask application silently used a development secret in every environment.
8. The repository carried two independent Python brief generators.

## Release design

- `VERSION` is authoritative.
- The maintained Python engine is `python/catalyst_canvas_core.py`.
- `python/catalyst_canvas_brief.py` remains only as a v1.x compatibility adapter.
- `scripts/validate_release.py` is the authoritative local and CI command.
- `scripts/build_plugin.py` creates the versioned WordPress package.
- Runtime state is reproduced from scripts rather than committed binaries.

## Acceptance gate

```bash
python scripts/validate_release.py
```

The command must finish with:

```text
PASS: Catalyst Canvas v1.1.1 release validation completed.
```
