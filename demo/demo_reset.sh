#!/bin/bash
# Reset Catalyst Canvas demo environment with pre-seeded DB
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cp "$SCRIPT_DIR/catalyst_seed.sqlite3" "$SCRIPT_DIR/../catalyst.sqlite3"
echo "Demo DB copied into place. Run: make run"
