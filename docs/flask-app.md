# Flask Application

The Flask application is a persistent workspace adapter over Canvas Contract 2.0 and Workspace Project Contract 1.0.

It provides project creation, switching, search, immutable revisions, autosave, archive and restore, historical export, research and evidence studios, framework-driven ideation, prioritization, and prototype and experiment management.

Primary workspaces:

```text
/research
/ledger
/ideate
/prioritize
/experiment
```

Experiment APIs:

```text
GET  /api/experiments
POST /api/experiments/runs
GET  /projects/<project_id>/experiment-handoff/research_lab.json
GET  /projects/<project_id>/experiment-handoff/workbench.json
```

Every save passes through the canonical engine and creates an immutable revision. Project and handoff routes enforce the active workspace boundary.

## Connected-platform routes

```text
GET  /platform
GET  /api/platform
GET  /api/capabilities
GET  /projects/<project_id>/exchange/<target>.json
POST /api/exchange/verify
```

`CANVAS_EXCHANGE_SIGNING_KEY` enables server-side HMAC-SHA256 signing. Connection metadata and successful local verification do not assert remote delivery or authorization.
