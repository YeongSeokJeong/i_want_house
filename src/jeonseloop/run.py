from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .loop import LoopOptions, run_cycle, run_failure_health
from .watchlist import WatchlistError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run one JeonseLoop monitoring cycle.")
    parser.add_argument("--watchlist", default="config/watchlist.yaml", help="watchlist config path")
    parser.add_argument("--data-dir", default="data", help="state and JSON output directory")
    parser.add_argument("--logs-dir", default="logs", help="Markdown log output directory")
    parser.add_argument("--fixture", help="optional listing fixture for dry-runs and tests")
    parser.add_argument("--dry-run", action="store_true", help="do not send alerts or write state")
    parser.add_argument("--send", action="store_true", help="send Telegram alerts; requires secrets")
    args = parser.parse_args(argv)

    options = LoopOptions(
        watchlist_path=Path(args.watchlist),
        data_dir=Path(args.data_dir),
        logs_dir=Path(args.logs_dir),
        fixture_path=Path(args.fixture) if args.fixture else None,
        dry_run=args.dry_run,
        allow_send=args.send,
    )

    try:
        result = run_cycle(options)
    except WatchlistError as exc:
        result = run_failure_health(options, exc)
        print(json.dumps(result, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {"success", "skipped"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
