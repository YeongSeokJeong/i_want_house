#!/usr/bin/env sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
PYTHONPATH="$ROOT_DIR/src" \
  python -m jeonseloop.run \
    --watchlist "$ROOT_DIR/config/watchlist.yaml" \
    --data-dir "$ROOT_DIR/data" \
    --logs-dir "$ROOT_DIR/logs" \
    "$@"
