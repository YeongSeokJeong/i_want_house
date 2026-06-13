from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from .analyzer import apply_quality_blocks, approved_candidates, classify_candidates, detect_average_price_jumps
from .collector import collect_listings
from .notifier import send_candidates
from .persistence import load_json, load_previous_average_prices, persist_cycle, write_failure_health
from .trades import load_trade_baselines
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

    raw_records = collect_listings(
        watchlist.complexes,
        options.fixture_path,
        request_interval_seconds=watchlist.request_interval_seconds,
    )
    valid_records, invalid_records = validate_listing_records(raw_records)
    trade_baselines = load_trade_baselines(options.data_dir, watchlist.complexes)
    previous_averages = load_previous_average_prices(
        options.data_dir,
        tuple(target.complex_id for target in watchlist.complexes),
    )
    quality_blocks = detect_average_price_jumps(valid_records, previous_averages)
    candidates = classify_candidates(watchlist.complexes, valid_records, notified_state, trade_baselines)
    candidates = apply_quality_blocks(candidates, quality_blocks)
    approved_total = len([candidate for candidate in candidates if candidate.decision == "approve"])
    approved = approved_candidates(candidates)
    alert_cap_overflow = max(approved_total - len(approved), 0)
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
    if quality_blocks:
        status = "failed"
        reason = "data_quality_blocked"

    run_record = _run_record(
        run_id,
        started_at,
        status=status,
        reason=reason,
        counts={
            "watched_complexes": len(watchlist.complexes),
            "valid_listings": sum(len(records) for records in valid_records.values()),
            "invalid_listings": len(invalid_records),
            "approved_candidates": approved_total,
            "notifications_sent": len(sent_by_key),
            "notifications_planned": len(approved),
            "data_quality_blocks": len(quality_blocks),
            "alert_cap_overflow": alert_cap_overflow,
        },
    )

    if not options.dry_run:
        if quality_blocks:
            write_failure_health(options.data_dir, run_record)
        else:
            persist_cycle(
                data_dir=options.data_dir,
                logs_dir=options.logs_dir,
                run_record=run_record,
                records_by_complex=valid_records,
                candidates=candidates,
                invalid_records=invalid_records,
                notified_updates=notified_updates,
                trade_baselines=trade_baselines,
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
