from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import os
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from .analyzer import CandidateAnalyzer
from .collector import ListingCollector, ListingSourceNotConfiguredError, TransientListingFetchError
from .notifier import NotificationService
from .persistence import JsonStateStore, LoopStateRepository
from .review import CandidateReviewService
from .sources import SourceFetchError, listing_fetcher_from_env, trade_fetcher_from_env
from .trades import TradeBaselineRepository
from .validator import ListingValidator
from .watchlist import Watchlist, WatchlistError, load_watchlist


@dataclass(frozen=True)
class LoopOptions:
    watchlist_path: Path
    data_dir: Path
    logs_dir: Path
    fixture_path: Path | None = None
    dry_run: bool = False
    allow_send: bool = False


WatchlistLoader = Callable[[Path], Watchlist]
Clock = Callable[[], str]
RunIdFactory = Callable[[], str]


class LoopCoordinator:
    def __init__(
        self,
        options: LoopOptions,
        *,
        watchlist_loader: WatchlistLoader = load_watchlist,
        collector: ListingCollector | None = None,
        validator: ListingValidator | None = None,
        analyzer: CandidateAnalyzer | None = None,
        state_store: JsonStateStore | None = None,
        state_repository: LoopStateRepository | None = None,
        trade_repository: TradeBaselineRepository | None = None,
        review_service: CandidateReviewService | None = None,
        notification_service: NotificationService | None = None,
        clock: Clock | None = None,
        run_id_factory: RunIdFactory | None = None,
    ) -> None:
        self._options = options
        self._watchlist_loader = watchlist_loader
        self._collector = collector
        self._validator = validator if validator is not None else ListingValidator()
        self._analyzer = analyzer if analyzer is not None else CandidateAnalyzer()
        self._state_store = state_store if state_store is not None else JsonStateStore()
        self._state_repository = state_repository
        self._trade_repository = trade_repository
        self._review_service = review_service if review_service is not None else CandidateReviewService()
        self._notification_service = notification_service if notification_service is not None else NotificationService()
        self._clock = clock if clock is not None else _now
        self._run_id_factory = run_id_factory if run_id_factory is not None else lambda: str(uuid4())

    def run(self) -> dict[str, Any]:
        started_at = self._clock()
        run_id = self._run_id_factory()

        watchlist = self._watchlist_loader(self._options.watchlist_path)
        notified_state = self._state_store.load_json(self._options.data_dir / "state" / "notified.json", {"notified": {}})
        state_repository = self._state_repository_for_run()

        if not watchlist.complexes:
            run_record = self._run_record(
                run_id,
                started_at,
                status="skipped",
                reason="empty_watchlist",
                counts={"watched_complexes": 0, "valid_listings": 0, "invalid_listings": 0, "approved_candidates": 0},
            )
            if not self._options.dry_run:
                state_repository.persist_cycle(
                    run_record=run_record,
                    records_by_complex={},
                    candidates=[],
                    invalid_records=[],
                    notified_updates={},
                )
            return run_record

        try:
            collector = self._collector_for_watchlist(watchlist)
            raw_records = collector.collect(watchlist.complexes, self._options.fixture_path)
        except ListingSourceNotConfiguredError as exc:
            return self._record_runtime_failure(
                run_id,
                started_at,
                state_repository,
                reason="listing_source_unconfigured",
                error=exc,
                watched_complexes=len(watchlist.complexes),
                target_complex_ids=tuple(target.complex_id for target in watchlist.complexes),
            )
        except (TransientListingFetchError, SourceFetchError) as exc:
            return self._record_runtime_failure(
                run_id,
                started_at,
                state_repository,
                reason="collector_failed",
                error=exc,
                watched_complexes=len(watchlist.complexes),
                target_complex_ids=tuple(target.complex_id for target in watchlist.complexes),
            )
        valid_records, invalid_records = self._validator.validate(raw_records)
        try:
            trade_baselines = self._trade_repository_for_run().load(watchlist.complexes)
        except SourceFetchError as exc:
            return self._record_runtime_failure(
                run_id,
                started_at,
                state_repository,
                reason="trade_source_failed",
                error=exc,
                watched_complexes=len(watchlist.complexes),
                target_complex_ids=tuple(target.complex_id for target in watchlist.complexes),
            )
        previous_averages = state_repository.load_previous_average_prices(
            tuple(target.complex_id for target in watchlist.complexes),
        )
        quality_blocks = self._analyzer.detect_average_price_jumps(valid_records, previous_averages)
        candidates = self._analyzer.classify(watchlist.complexes, valid_records, notified_state, trade_baselines)
        candidates = self._analyzer.apply_quality_blocks(candidates, quality_blocks)
        candidates = self._review_service.apply(candidates)
        approved_total = len([candidate for candidate in candidates if candidate.decision == "approve"])
        approved = self._analyzer.approved(candidates)
        alert_cap_overflow = max(approved_total - len(approved), 0)
        notifications = self._notification_service.send_candidates(
            approved,
            allow_send=self._options.allow_send and not self._options.dry_run,
        )

        sent_by_key = {result.listing_key: result for result in notifications if result.sent}
        notified_updates = {
            candidate.listing_key: {
                "price_krw": candidate.price_krw,
                "complex_id": candidate.complex_id,
                "notified_at": self._clock(),
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

        run_record = self._run_record(
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

        if not self._options.dry_run:
            if quality_blocks:
                state_repository.write_failure_health(run_record)
            else:
                state_repository.persist_cycle(
                    run_record=run_record,
                    records_by_complex=valid_records,
                    candidates=candidates,
                    invalid_records=invalid_records,
                    notified_updates=notified_updates,
                    trade_baselines=trade_baselines,
                )

        return run_record

    def record_watchlist_failure(self, error: WatchlistError) -> dict[str, Any]:
        now = self._clock()
        record = {
            "run_id": self._run_id_factory(),
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
        if not self._options.dry_run:
            self._state_repository_for_run().write_failure_health(record)
        return record

    def _collector_for_watchlist(self, watchlist: Watchlist) -> ListingCollector:
        if self._collector is not None:
            return self._collector
        return ListingCollector(
            fetcher=listing_fetcher_from_env(),
            request_interval_seconds=watchlist.request_interval_seconds,
        )

    def _state_repository_for_run(self) -> LoopStateRepository:
        if self._state_repository is not None:
            return self._state_repository
        return LoopStateRepository(
            data_dir=self._options.data_dir,
            logs_dir=self._options.logs_dir,
            store=self._state_store,
        )

    def _trade_repository_for_run(self) -> TradeBaselineRepository:
        if self._trade_repository is not None:
            return self._trade_repository
        return TradeBaselineRepository(self._options.data_dir, fetcher=trade_fetcher_from_env())

    def _run_record(
        self,
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
            "finished_at": self._clock(),
            "status": status,
            "reason": reason,
            "counts": counts,
        }

    def _record_runtime_failure(
        self,
        run_id: str,
        started_at: str,
        state_repository: LoopStateRepository,
        *,
        reason: str,
        error: Exception,
        watched_complexes: int,
        target_complex_ids: tuple[str, ...] = (),
    ) -> dict[str, Any]:
        run_record = self._run_record(
            run_id,
            started_at,
            status="failed",
            reason=reason,
            counts={
                "watched_complexes": watched_complexes,
                "valid_listings": 0,
                "invalid_listings": 0,
                "approved_candidates": 0,
            },
        )
        run_record["error"] = str(error)
        if not self._options.dry_run:
            state_repository.write_failure_health(
                run_record,
                diagnostics=_collector_diagnostics(run_record, reason, error, target_complex_ids),
            )
        return run_record


def run_cycle(options: LoopOptions) -> dict[str, Any]:
    return LoopCoordinator(options).run()


def run_failure_health(options: LoopOptions, error: WatchlistError) -> dict[str, Any]:
    return LoopCoordinator(options).record_watchlist_failure(error)


def _now() -> str:
    return datetime.now(tz=UTC).replace(microsecond=0).isoformat()


def _collector_diagnostics(
    run_record: dict[str, Any],
    reason: str,
    error: Exception,
    target_complex_ids: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "run_id": run_record["run_id"],
        "generated_at": run_record["finished_at"],
        "run_reason": reason,
        "failure_stage": _failure_stage(reason),
        "source_kind": _listing_source_kind_for_diagnostics(),
        "error_type": type(error).__name__,
        "error": str(error),
        "targets": [{"complex_id": complex_id} for complex_id in target_complex_ids],
    }


def _failure_stage(reason: str) -> str:
    if reason in {"listing_source_unconfigured", "collector_failed"}:
        return "listing_collection"
    if reason == "trade_source_failed":
        return "trade_collection"
    return "runtime"


def _listing_source_kind_for_diagnostics() -> str:
    kind = os.environ.get("JEONSELOOP_LISTING_SOURCE_KIND", "").strip()
    if kind:
        return kind
    if os.environ.get("JEONSELOOP_LISTING_SOURCE_URL", "").strip():
        return "http-json"
    return "unconfigured"
