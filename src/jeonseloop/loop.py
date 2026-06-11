from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from .analyzer import approved_candidates, classify_candidates
from .collector import collect_listings
from .notifier import send_candidates
from .persistence import load_json, persist_cycle, write_failure_health
from .validator import validate_listing_records
from .watchlist import WatchlistError, load_watchlist


@dataclass(frozen=True)
class LoopOptions:
    watchlist_path: Path
    data_dir: Path
    logs_dir: Path
    fixture_path: Path | None = None
    dry_run: bool = False
    allow_send: bool = False


def run_cycle(options: LoopOptions) -> dict[str, Any]:
    started_at = _now()
    run_id = str(uuid4())

    watchlist = load_watchlist(options.watchlist_path)
    notified_state = load_json(options.data_dir / "state" / "notified.json", {"notified": {}})

    if not watchlist.complexes:
        run_record = _run_record(
            run_id,
            started_at,
            status="skipped",
            reason="empty_watchlist",
            counts={"watched_complexes": 0, "valid_listings": 0, "invalid_listings": 0, "approved_candidates": 0},
        )
        if not options.dry_run:
            persist_cycle(
                data_dir=options.data_dir,
                logs_dir=options.logs_dir,
                run_record=run_record,
                records_by_complex={},
                candidates=[],
                invalid_records=[],
                notified_updates={},
            )
        return run_record

    raw_records = collect_listings(watchlist.complexes, options.fixture_path)
    valid_records, invalid_records = validate_listing_records(raw_records)
    candidates = classify_candidates(watchlist.complexes, valid_records, notified_state)
    approved = approved_candidates(candidates)
    notifications = send_candidates(approved, allow_send=options.allow_send and not options.dry_run)

    sent_by_key = {result.listing_key: result for result in notifications if result.sent}
    notified_updates = {
        candidate.listing_key: {
            "price_krw": candidate.price_krw,
            "complex_id": candidate.complex_id,
            "notified_at": _now(),
        }
        for candidate in approved
        if candidate.listing_key in sent_by_key
    }

    status = "success"
    reason = "completed"
    if invalid_records and not any(valid_records.values()):
        status = "failed"
        reason = "all_records_invalid"

    run_record = _run_record(
        run_id,
        started_at,
        status=status,
        reason=reason,
        counts={
            "watched_complexes": len(watchlist.complexes),
            "valid_listings": sum(len(records) for records in valid_records.values()),
            "invalid_listings": len(invalid_records),
            "approved_candidates": len(approved),
            "notifications_sent": len(sent_by_key),
            "notifications_planned": len(approved),
        },
    )

    if not options.dry_run:
        persist_cycle(
            data_dir=options.data_dir,
            logs_dir=options.logs_dir,
            run_record=run_record,
            records_by_complex=valid_records,
            candidates=candidates,
            invalid_records=invalid_records,
            notified_updates=notified_updates,
        )

    return run_record


def run_failure_health(options: LoopOptions, error: WatchlistError) -> dict[str, Any]:
    now = _now()
    record = {
        "run_id": str(uuid4()),
        "started_at": now,
        "finished_at": now,
        "status": "failed",
        "reason": "watchlist_invalid",
        "error": str(error),
        "counts": {
            "watched_complexes": 0,
            "valid_listings": 0,
            "invalid_listings": 0,
            "approved_candidates": 0,
        },
    }
    if not options.dry_run:
        write_failure_health(options.data_dir, record)
    return record


def _run_record(
    run_id: str,
    started_at: str,
    *,
    status: str,
    reason: str,
    counts: dict[str, int],
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "started_at": started_at,
        "finished_at": _now(),
        "status": status,
        "reason": reason,
        "counts": counts,
    }


def _now() -> str:
    return datetime.now(tz=UTC).replace(microsecond=0).isoformat()
