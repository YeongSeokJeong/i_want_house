from __future__ import annotations

from pathlib import Path
from typing import Any

from .analyzer import Candidate
from .models import RunRecord
from .state_repositories import (
    CollectorDiagnosticsRepository,
    CriteriaRepository,
    HealthStateRepository,
    HistoryRepository,
    JsonStateStore,
    ListingSnapshotRepository,
    NotifiedStateRepository,
    UrgentFeedRepository,
    sanitize_diagnostics,
)
from .validator import ValidationIssue


class LoopStateRepository:
    def __init__(
        self,
        *,
        data_dir: Path,
        logs_dir: Path | None = None,
        store: JsonStateStore | None = None,
    ) -> None:
        self._data_dir = data_dir
        self._logs_dir = logs_dir
        self._store = store if store is not None else JsonStateStore()
        self._listings = ListingSnapshotRepository(data_dir, store=self._store)
        self._history = HistoryRepository(data_dir, store=self._store)
        self._notified = NotifiedStateRepository(data_dir, store=self._store)
        self._health = HealthStateRepository(data_dir, store=self._store)
        self._diagnostics = CollectorDiagnosticsRepository(data_dir, store=self._store)
        self._feed = UrgentFeedRepository(data_dir, store=self._store)

    def persist_cycle(
        self,
        *,
        run_record: dict[str, Any],
        records_by_complex: dict[str, list[dict[str, Any]]],
        candidates: list[Candidate],
        invalid_records: list[ValidationIssue],
        notified_updates: dict[str, dict[str, Any]],
        trade_baselines: dict[str, int] | None = None,
    ) -> None:
        run_payload = RunRecord.from_dict(run_record).to_dict()
        logs_dir = self._require_logs_dir()
        criteria = CriteriaRepository(data_dir=self._data_dir, logs_dir=logs_dir)

        self._listings.write_all(records_by_complex)
        self._history.append_for_records(run_payload, records_by_complex, trade_baselines or {})
        self._notified.merge_updates(notified_updates)
        self._health.record_success(run_payload)
        self._feed.write(run_payload, candidates)
        criteria.append_log(candidates, invalid_records, run_payload["finished_at"])
        criteria.write_suggestions(generated_at=run_payload["finished_at"])

    def write_failure_health(
        self,
        run_record: dict[str, Any],
        diagnostics: dict[str, Any] | None = None,
    ) -> None:
        run_payload = RunRecord.from_dict(run_record).to_dict()
        self._health.record_failure(run_payload)
        if diagnostics is not None:
            self._diagnostics.write(diagnostics)

    def load_previous_average_prices(self, complex_ids: list[str] | tuple[str, ...]) -> dict[str, int]:
        return self._history.load_previous_average_prices(complex_ids)

    def _require_logs_dir(self) -> Path:
        if self._logs_dir is None:
            raise ValueError("logs_dir is required to persist a successful cycle")
        return self._logs_dir


def load_json(path: Path, default: Any) -> Any:
    return JsonStateStore().load_json(path, default)


def atomic_write_json(path: Path, payload: Any) -> None:
    JsonStateStore().atomic_write_json(path, payload)


def persist_cycle(
    *,
    data_dir: Path,
    logs_dir: Path,
    run_record: dict[str, Any],
    records_by_complex: dict[str, list[dict[str, Any]]],
    candidates: list[Candidate],
    invalid_records: list[ValidationIssue],
    notified_updates: dict[str, dict[str, Any]],
    trade_baselines: dict[str, int] | None = None,
) -> None:
    LoopStateRepository(data_dir=data_dir, logs_dir=logs_dir).persist_cycle(
        run_record=run_record,
        records_by_complex=records_by_complex,
        candidates=candidates,
        invalid_records=invalid_records,
        notified_updates=notified_updates,
        trade_baselines=trade_baselines,
    )


def write_failure_health(
    data_dir: Path,
    run_record: dict[str, Any],
    diagnostics: dict[str, Any] | None = None,
) -> None:
    LoopStateRepository(data_dir=data_dir).write_failure_health(run_record, diagnostics=diagnostics)


def load_previous_average_prices(data_dir: Path, complex_ids: list[str] | tuple[str, ...]) -> dict[str, int]:
    return LoopStateRepository(data_dir=data_dir).load_previous_average_prices(complex_ids)


def _append_history(
    path: Path,
    run_record: dict[str, Any],
    records: list[dict[str, Any]],
    trade_baselines: dict[str, int],
) -> None:
    HistoryRepository(path.parents[1]).append(path, run_record, records, trade_baselines)


def _write_urgent_feed(path: Path, run_record: dict[str, Any], candidates: list[Candidate]) -> None:
    UrgentFeedRepository(path.parents[1]).write(run_record, candidates)


def _append_criteria_log(
    path: Path,
    candidates: list[Candidate],
    invalid_records: list[ValidationIssue],
    finished_at: str,
) -> None:
    CriteriaRepository(data_dir=path.parents[1] / "data", logs_dir=path.parent).append_log(
        candidates,
        invalid_records,
        finished_at,
    )
