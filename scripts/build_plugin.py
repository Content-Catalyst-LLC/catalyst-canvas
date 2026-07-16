#!/usr/bin/env python3
"""Build the versioned Catalyst Canvas WordPress plugin ZIP."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from sync_contract_assets import render as render_contract_asset

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_DIR = ROOT / "wordpress" / "catalyst-canvas-demo"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
CONTRACT_VERSION = "catalyst-canvas/1.0"


def validate_plugin_version() -> None:
    php = (PLUGIN_DIR / "catalyst-canvas-demo.php").read_text(encoding="utf-8")
    if not re.search(rf"Version:\s*{re.escape(VERSION)}(?:\s|$)", php):
        raise RuntimeError("WordPress plugin header does not match VERSION")
    if f"private const VERSION = '{VERSION}';" not in php:
        raise RuntimeError("WordPress plugin asset version does not match VERSION")
    if f"private const CONTRACT_VERSION = '{CONTRACT_VERSION}';" not in php:
        raise RuntimeError("WordPress plugin contract version does not match Canvas Contract 1.0")


def validate_contract_asset() -> None:
    asset = PLUGIN_DIR / "assets" / "catalyst-canvas-contract-data.js"
    if not asset.exists():
        raise RuntimeError("Generated WordPress contract-data asset is missing")
    if asset.read_text(encoding="utf-8") != render_contract_asset():
        raise RuntimeError("WordPress contract-data asset is stale; run scripts/sync_contract_assets.py")


def build(output: Path) -> Path:
    validate_plugin_version()
    validate_contract_asset()
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for path in sorted(PLUGIN_DIR.rglob("*")):
            if not path.is_file() or path.name == ".DS_Store" or "__pycache__" in path.parts:
                continue
            arcname = Path(PLUGIN_DIR.name) / path.relative_to(PLUGIN_DIR)
            archive.write(path, arcname.as_posix())
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "dist" / f"catalyst-canvas-demo-v{VERSION}.zip",
    )
    args = parser.parse_args()
    result = build(args.output.resolve())
    print(f"Built WordPress plugin: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
