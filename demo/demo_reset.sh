#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 demo/seed_demo.py
printf '\nDemo databases refreshed. Run locally with:\n  python3 app.py\n\n'
