from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ValidationIssue:
    complex_id: str | None
    reason: str
    record: dict[str, Any]


def validate_listing_records(
    records_by_complex: dict[str, list[dict[str, Any]]],
) -> tuple[dict[str, list[dict[str, Any]]], list[ValidationIssue]]:
    valid: dict[str, list[dict[str, Any]]] = {complex_id: [] for complex_id in records_by_complex}
    issues: list[ValidationIssue] = []

    for complex_id, records in records_by_complex.items():
        for record in records:
            reason = _validate_record(complex_id, record)
            if reason:
                issues.append(ValidationIssue(complex_id=complex_id, reason=reason, record=record))
            else:
                valid[complex_id].append(record)

    return valid, issues


def listing_key(record: dict[str, Any]) -> str:
    listing_id = str(record.get("listing_id", "")).strip()
    if listing_id:
        return listing_id
    parts = [
        record.get("complex_id", ""),
        record.get("building", ""),
        record.get("floor", ""),
        record.get("area_m2", ""),
        record.get("price_krw", ""),
        record.get("link", ""),
    ]
    return "|".join(str(part) for part in parts)


def _validate_record(expected_complex_id: str, record: dict[str, Any]) -> str | None:
    if record.get("complex_id") != expected_complex_id:
        return "complex_id_not_in_watchlist"

    for field in ("price_krw", "area_m2", "floor", "link"):
        if field not in record:
            return f"missing_{field}"

    if _to_number(record["price_krw"]) <= 0:
        return "invalid_price_krw"
    if _to_number(record["area_m2"]) <= 0:
        return "invalid_area_m2"
    if not str(record["link"]).strip():
        return "missing_link"

    return None


def _to_number(value: Any) -> float:
    if isinstance(value, bool):
        return 0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0
