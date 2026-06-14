from __future__ import annotations

from collections import Counter
import json
import os
from pathlib import Path
from typing import Any

CRITERIA_SUGGESTION_THRESHOLD = 30
FALSE_POSITIVE_REASON_PREFIXES = (
    "llm_",
    "average_price_jump",
    "duplicate_listing",
)


class CriteriaSuggestionService:
    def __init__(
        self,
        *,
        logs_dir: Path,
        data_dir: Path,
        min_decisions: int = CRITERIA_SUGGESTION_THRESHOLD,
    ) -> None:
        self._logs_dir = logs_dir
        self._data_dir = data_dir
        self._min_decisions = min_decisions

    def write(self, *, generated_at: str) -> dict[str, Any] | None:
        rows = _criteria_rows(self._logs_dir / "criteria-log.md")
        if len(rows) < self._min_decisions:
            return None

        reason_counts = Counter(row["reason"] for row in rows if row.get("reason"))
        false_positive_rows = [row for row in rows if _is_false_positive_signal(row)]
        false_positive_reason_counts = Counter(row["reason"] for row in false_positive_rows if row.get("reason"))
        suggestions = _suggestions(reason_counts, false_positive_reason_counts)
        payload = {
            "generated_at": generated_at,
            "decision_count": len(rows),
            "metrics": _metrics(rows, reason_counts, false_positive_rows, false_positive_reason_counts),
            "status": "review_required",
            "suggestions": suggestions,
            "auto_applied": False,
        }
        _atomic_write_json(self._data_dir / "state" / "criteria-suggestions.json", payload)
        return payload


def write_criteria_suggestions(
    *,
    logs_dir: Path,
    data_dir: Path,
    generated_at: str,
    min_decisions: int = CRITERIA_SUGGESTION_THRESHOLD,
) -> dict[str, Any] | None:
    return CriteriaSuggestionService(
        logs_dir=logs_dir,
        data_dir=data_dir,
        min_decisions=min_decisions,
    ).write(generated_at=generated_at)


def _metrics(
    rows: list[dict[str, str]],
    reason_counts: Counter[str],
    false_positive_rows: list[dict[str, str]],
    false_positive_reason_counts: Counter[str],
) -> dict[str, Any]:
    approved_count = sum(1 for row in rows if row.get("decision") == "approve")
    false_positive_count = len(false_positive_rows)
    reviewed_count = approved_count + false_positive_count
    false_positive_ratio = false_positive_count / reviewed_count if reviewed_count else 0.0
    return {
        "total_decisions": len(rows),
        "approved_decisions": approved_count,
        "false_positive_signals": false_positive_count,
        "reviewed_decisions": reviewed_count,
        "false_positive_ratio": round(false_positive_ratio, 4),
        "reason_counts": dict(reason_counts.most_common()),
        "false_positive_reason_counts": dict(false_positive_reason_counts.most_common()),
    }


def _suggestions(
    reason_counts: Counter[str],
    false_positive_reason_counts: Counter[str],
) -> list[dict[str, Any]]:
    proposals: list[dict[str, Any]] = []
    for reason, count in false_positive_reason_counts.most_common(5):
        proposals.append(
            {
                "reason": reason,
                "decision_count": count,
                "signal": "false_positive",
                "proposal": f"Review candidate review or data-quality rules related to `{reason}`.",
                "requires_human_approval": True,
            }
        )

    for reason, count in reason_counts.most_common(5):
        if reason in false_positive_reason_counts:
            continue
        proposals.append(
            {
                "reason": reason,
                "decision_count": count,
                "signal": "criteria_frequency",
                "proposal": f"Review watchlist thresholds or exclusion rules related to `{reason}`.",
                "requires_human_approval": True,
            }
        )
        if len(proposals) >= 5:
            break
    return proposals


def _is_false_positive_signal(row: dict[str, str]) -> bool:
    if row.get("decision") == "approve":
        return False
    reason = row.get("reason", "")
    return reason.startswith(FALSE_POSITIVE_REASON_PREFIXES)


def _criteria_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    rows: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "---" in line or " time " in line:
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) < 6:
            continue
        rows.append(
            {
                "time": parts[0],
                "complex_id": parts[1],
                "listing_key": parts[2],
                "decision": parts[3],
                "reason": parts[4],
                "price_krw": parts[5],
            }
        )
    return rows


def _atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    json.loads(text)
    temp = path.with_name(f".{path.name}.tmp")
    temp.write_text(text, encoding="utf-8")
    os.replace(temp, path)
