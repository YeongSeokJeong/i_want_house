from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .analyzer import Candidate
from .validator import ValidationIssue

HEALTH_ALERT_FAILURE_STREAK = 3


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    json.loads(text)
    temp = path.with_name(f".{path.name}.tmp")
    temp.write_text(text, encoding="utf-8")
    os.replace(temp, path)


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
    for complex_id, records in records_by_complex.items():
        atomic_write_json(data_dir / "listings" / f"{complex_id}.json", {"listings": records})
        _append_history(data_dir / "history" / f"{complex_id}.json", run_record, records, trade_baselines or {})

    notified_path = data_dir / "state" / "notified.json"
    notified_state = load_json(notified_path, {"notified": {}})
    notified_state.setdefault("notified", {})
    if notified_updates:
        notified_state.setdefault("notified", {}).update(notified_updates)
    atomic_write_json(notified_path, notified_state)

    health_path = data_dir / "state" / "health.json"
    health_state = load_json(health_path, {"runs": []})
    runs = list(health_state.get("runs", []))
    runs.append(run_record)
    health_state["failure_streak"] = 0
    health_state["health_alert_eligible"] = False
    health_state["latest"] = run_record
    health_state["last_success_at"] = run_record["finished_at"]
    health_state["last_success_run_id"] = run_record["run_id"]
    health_state["runs"] = runs[-10:]
    atomic_write_json(health_path, health_state)

    _append_criteria_log(logs_dir / "criteria-log.md", candidates, invalid_records, run_record["finished_at"])


def write_failure_health(data_dir: Path, run_record: dict[str, Any]) -> None:
    health_path = data_dir / "state" / "health.json"
    health_state = load_json(health_path, {"runs": []})
    runs = list(health_state.get("runs", []))
    runs.append(run_record)
    failure_streak = int(health_state.get("failure_streak", 0)) + 1
    health_state["failure_streak"] = failure_streak
    health_state["health_alert_eligible"] = failure_streak >= HEALTH_ALERT_FAILURE_STREAK
    health_state["latest"] = run_record
    health_state["runs"] = runs[-10:]
    atomic_write_json(health_path, health_state)


def load_previous_average_prices(data_dir: Path, complex_ids: list[str] | tuple[str, ...]) -> dict[str, int]:
    averages: dict[str, int] = {}
    for complex_id in complex_ids:
        history = load_json(data_dir / "history" / f"{complex_id}.json", {"history": []})
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
