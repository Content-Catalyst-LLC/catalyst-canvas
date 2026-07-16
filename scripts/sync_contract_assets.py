#!/usr/bin/env python3
"""Generate the WordPress contract-data module from canonical repository sources."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "wordpress" / "catalyst-canvas-demo" / "assets" / "catalyst-canvas-contract-data.js"


def render() -> str:
    frameworks = json.loads((ROOT / "contracts" / "frameworks.json").read_text(encoding="utf-8"))
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    payload = {
        "releaseVersion": version,
        "contractVersion": "catalyst-canvas/1.0",
        "frameworks": frameworks,
    }
    serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return """(function (root, factory) {
  'use strict';
  const data = factory();
  if (typeof module === 'object' && module.exports) module.exports = data;
  if (root) root.CatalystCanvasContractData = data;
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  return %s;
}));
""" % serialized


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(), encoding="utf-8")
    print(f"Synchronized contract asset: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
