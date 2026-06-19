from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import ModelValidationError, NormalizedListing


@dataclass(frozen=True)
class ValidationIssue:
    complex_id: str | None
    reason: str
    record: dict[str, Any]


class ListingValidator:
    def validate(
        self,
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

    def listing_key(self, record: dict[str, Any]) -> str:
        return listing_key(record)


def validate_listing_records(
    records_by_complex: dict[str, list[dict[str, Any]]],
) -> tuple[dict[str, list[dict[str, Any]]], list[ValidationIssue]]:
    return ListingValidator().validate(records_by_complex)


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

    try:
        listing = NormalizedListing.from_dict(record)
    except ModelValidationError as exc:
        return _validation_reason(exc)

    if listing.price_krw <= 0:
        return "invalid_price_krw"
    if listing.area_m2 <= 0:
        return "invalid_area_m2"

    return None


def _validation_reason(exc: ModelValidationError) -> str:
    if exc.field_name in {"price_krw", "area_m2", "floor", "link"} and exc.reason == "is required":
        return f"missing_{exc.field_name}"
    if exc.field_name == "price_krw":
        return "invalid_price_krw"
    if exc.field_name == "area_m2":
        return "invalid_area_m2"
    if exc.field_name == "link":
        return "missing_link"
    if exc.field_name == "complex_id":
        return "complex_id_not_in_watchlist"
    return f"invalid_{exc.field_name}"
