# Repository Architecture

Catalyst Canvas is structured as a multi-layer repository.

## Existing app layer

The existing Flask application remains the full app-oriented implementation.

## Python core layer

`python/catalyst_canvas_core.py` provides a lightweight generator that can be tested and reused without the Flask app.

## WordPress layer

`wordpress/catalyst-canvas-demo/` provides an online demo for the public Catalyst Canvas page.

## Data and schema layer

`data/` stores sample inputs and `schemas/` stores output schemas for reviewable exports.

## Documentation layer

`docs/` explains methodology, installation, architecture, and exports.
