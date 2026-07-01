"""Catalyst Canvas Flask application package.

The Flask demo is a local, educational companion to the WordPress demo and the
repository's reproducible Python brief generator. It is deliberately bounded:
inputs stay in a local SQLite database, outputs are review aids, and the app does
not certify impact, compliance, product fit, or implementation success.
"""

from __future__ import annotations

import os
from pathlib import Path
from flask import Flask

from .routes import bp
from .services.storage import init_db


def create_app(test_config: dict | None = None) -> Flask:
    repo_root = Path(__file__).resolve().parents[1]
    app = Flask(__name__, template_folder=str(repo_root / "templates"))

    app.config.update(
        SECRET_KEY=os.environ.get("CATALYST_CANVAS_SECRET", "dev-only-change-me"),
        CANVAS_DB=os.environ.get("CATALYST_CANVAS_DB", str(repo_root / "catalyst.sqlite3")),
        JSON_SORT_KEYS=False,
    )

    if test_config:
        app.config.update(test_config)

    Path(app.config["CANVAS_DB"]).parent.mkdir(parents=True, exist_ok=True)
    init_db(app.config["CANVAS_DB"])

    app.register_blueprint(bp)
    return app
