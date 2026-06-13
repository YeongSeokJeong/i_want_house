from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .analyzer import Candidate, approved_candidates
from .suggestions import write_criteria_suggestions
from .validator import ValidationIssue

HEALTH_ALERT_FAILURE_STREAK = 3


class JsonStateStore:
    def load_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def atomic_write_json(self, path: Path, payload: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        json.loads(text)
        temp = path.with_name(f".{path.name}.tmp")
        temp.write_text(text, encoding="utf-8")
        os.replace(temp, path)


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
        logs_dir = self._require_logs_dir()
        for complex_id, records in records_by_complex.items():
            self._store.atomic_write_json(self._data_dir / "listings" / f"{complex_id}.json", {"listings": records})
            _append_history(self._data_dir / "history" / f"{complex_id}.json", run_record, records, trade_baselines or {})

        notified_path = self._data_dir / "state" / "notified.json"
        notified_state = self._store.load_json(notified_path, {"notified": {}})
        notified_state.setdefault("notified", {})
        if notified_updates:
            notified_state.setdefault("notified", {}).update(notified_updates)
        self._store.atomic_write_json(notified_path, notified_state)

        health_path = self._data_dir / "state" / "health.json"
        health_state = self._store.load_json(health_path, {"runs": []})
        runs = list(health_state.get("runs", []))
        runs.append(run_record)
        health_state["failure_streak"] = 0
        health_state["health_alert_eligible"] = False
        health_state["latest"] = run_record
        health_state["last_success_at"] = run_record["finished_at"]
        health_state["last_success_run_id"] = run_record["run_id"]
        health_state["runs"] = runs[-10:]
        self._store.atomic_write_json(health_path, health_state)

        _write_urgent_feed(self._data_dir / "state" / "urgent-feed.json", run_record, candidates)
        _append_criteria_log(logs_dir / "criteria-log.md", candidates, invalid_records, run_record["finished_at"])
        write_criteria_suggestions(logs_dir=logs_dir, data_dir=self._data_dir, generated_at=run_record["finished_at"])

    def write_failure_health(self, run_record: dict[str, Any]) -> None:
        health_path = self._data_dir / "state" / "health.json"
        health_state = self._store.load_json(health_path, {"runs": []})
        runs = list(health_state.get("runs", []))
        runs.append(run_record)
        failure_streak = int(health_state.get("failure_streak", 0)) + 1
        health_state["failure_streak"] = failure_streak
        health_state["health_alert_eligible"] = failure_streak >= HEALTH_ALERT_FAILURE_STREAK
        health_state["latest"] = run_record
        health_state["runs"] = runs[-10:]
        self._store.atomic_write_json(health_path, health_state)

    def load_previous_average_prices(self, complex_ids: list[str] | tuple[str, ...]) -> dict[str, int]:
        averages: dict[str, int] = {}
        for complex_id in complex_ids:
            history = self._store.load_json(self._data_dir / "history" / f"{complex_id}.json", {"history": []})
            entries = history.get("history", []) if isinstance(history, dict) else []
            if not isinstance(entries, list):
                continue
            for entry in reversed(entries):
                if not isinstance(entry, dict):
                    continue
                value = entry.get("average_price_krw")
                if value is None:
                    continue
                try:
                    average = int(value)
                except (TypeError, ValueError):
                    continue
                if average > 0:
                    averages[complex_id] = average
                    break
        return averages

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


def write_failure_health(data_dir: Path, run_record: dict[str, Any]) -> None:
    LoopStateRepository(data_dir=data_dir).write_failure_health(run_record)


def load_previous_average_prices(data_dir: Path, complex_ids: list[str] | tuple[str, ...]) -> dict[str, int]:
    return LoopStateRepository(data_dir=data_dir).load_previous_average_prices(complex_ids)


def _append_history(
    path: Path,
    run_record: dict[str, Any],
    records: list[dict[str, Any]],
    trade_baselines: dict[str, int],
) -> None:
    history = load_json(path, {"history": []})
    prices = [int(record["price_krw"]) for record in records]
    entry = {
        "run_id": run_record["run_id"],
        "finished_at": run_record["finished_at"],
        "listing_count": len(records),
        "min_price_krw": min(prices) if prices else None,
        "average_price_krw": int(sum(prices) / len(prices)) if prices else None,
        "recent_trade_price_krw": trade_baselines.get(path.stem),
    }
    history.setdefault("history", []).append(entry)
    atomic_write_json(path, history)


def _write_urgent_feed(path: Path, run_record: dict[str, Any], candidates: list[Candidate]) -> None:
    planned_keys = {candidate.listing_key for candidate in approved_candidates(candidates)}
    payload = {
        "run_id": run_record["run_id"],
        "generated_at": run_record["finished_at"],
        "alert_limit": 5,
        "alert_cap_overflow": run_record.get("counts", {}).get("alert_cap_overflow", 0),
        "items": [_feed_item(candidate, candidate.listing_key in planned_keys) for candidate in candidates],
    }
    atomic_write_json(path, payload)


def _feed_item(candidate: Candidate, alert_planned: bool) -> dict[str, Any]:
    listing = candidate.listing
    return {
        "complex_id": candidate.complex_id,
        "listing_key": candidate.listing_key,
        "decision": candidate.decision,
        "reason": candidate.reason,
        "price_krw": candidate.price_krw,
        "alert_planned": alert_planned,
        "title": listing.get("title"),
        "description": listing.get("description"),
        "building": listing.get("building"),
        "floor": listing.get("floor"),
        "area_m2": listing.get("area_m2"),
        "link": listing.get("link"),
    }


def _append_criteria_log(
    path: Path,
    candidates: list[Candidate],
    invalid_records: list[ValidationIssue],
    finished_at: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        lines = path.read_text(encoding="utf-8").splitlines()
    else:
        lines = [
            "# Criteria Log",
            "",
            "| time | complex_id | listing_key | decision | reason | price_krw |",
            "|---|---|---|---|---|---|",
        ]

    for candidate in candidates:
        lines.append(
            f"| {finished_at} | {candidate.complex_id} | {candidate.listing_key} | "
            f"{candidate.decision} | {candidate.reason} | {candidate.price_krw} |"
        )
    for issue in invalid_records:
        lines.append(
            f"| {finished_at} | {issue.complex_id or ''} | invalid_record | quarantine | {issue.reason} |  |"
        )

    temp = path.with_name(f".{path.name}.tmp")
    temp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.replace(temp, path)
