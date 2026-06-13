from __future__ import annotations

from collections import Counter
import json
import os
from pathlib import Path
from typing import Any

CRITERIA_SUGGESTION_THRESHOLD = 30


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
        suggestions = [
            {
                "reason": reason,
                "decision_count": count,
                "proposal": f"Review watchlist thresholds or exclusion rules related to `{reason}`.",
                "requires_human_approval": True,
            }
            for reason, count in reason_counts.most_common(5)
        ]
        payload = {
            "generated_at": generated_at,
            "decision_count": len(rows),
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
