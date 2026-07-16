#!/usr/bin/env python3
"""Local launcher for the Catalyst Canvas Flask demo."""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=app.config["CATALYST_CANVAS_ENV"] in {"development", "local"},
    )
