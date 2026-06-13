from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .validator import listing_key
from .watchlist import WatchTarget


@dataclass(frozen=True)
class Candidate:
    complex_id: str
    listing_key: str
    price_krw: int
    decision: str
    reason: str
    listing: dict[str, Any]


@dataclass(frozen=True)
class QualityBlock:
    complex_id: str
    current_average_price_krw: int
    previous_average_price_krw: int
    change_ratio: float
    reason: str = "average_price_jump"


def classify_candidates(
    targets: tuple[WatchTarget, ...],
    records_by_complex: dict[str, list[dict[str, Any]]],
    notified_state: dict[str, Any],
    trade_baselines: dict[str, int] | None = None,
) -> list[Candidate]:
    targets_by_id = {target.complex_id: target for target in targets}
    notified = notified_state.get("notified", {}) if isinstance(notified_state, dict) else {}
    baselines = trade_baselines or {}
    candidates: list[Candidate] = []

    for complex_id, records in records_by_complex.items():
        target = targets_by_id[complex_id]
        baseline_price = baselines.get(complex_id)
        baseline_limit = (
            int(baseline_price * (1 - target.urgent_discount_ratio)) if baseline_price is not None else None
        )
        for record, duplicate_of in _dedupe(records):
            key = listing_key(record)
            price = int(record["price_krw"])
            if duplicate_of is not None:
                candidates.append(Candidate(complex_id, key, price, "hold", f"duplicate_listing:{duplicate_of}", record))
                continue

            excluded_by = _exclusion_match(target, record)
            if excluded_by is not None:
                candidates.append(Candidate(complex_id, key, price, "reject", f"excluded:{excluded_by}", record))
                continue

            previous = notified.get(key, {}) if isinstance(notified, dict) else {}
            previous_price = previous.get("price_krw") if isinstance(previous, dict) else None

            if previous_price is not None and price >= int(previous_price):
                candidates.append(
                    Candidate(complex_id, key, price, "hold", "already_notified_without_price_drop", record)
                )
                continue

            if baseline_limit is not None and price <= baseline_limit:
                candidates.append(Candidate(complex_id, key, price, "approve", "baseline_price", record))
            elif price <= target.target_price_krw:
                candidates.append(Candidate(complex_id, key, price, "approve", "target_price", record))
            else:
                candidates.append(Candidate(complex_id, key, price, "reject", "above_target_price", record))

    return candidates


def detect_average_price_jumps(
    records_by_complex: dict[str, list[dict[str, Any]]],
    previous_averages: dict[str, int],
    *,
    threshold: float = 0.15,
) -> dict[str, QualityBlock]:
    blocks: dict[str, QualityBlock] = {}
    for complex_id, records in records_by_complex.items():
        prices = [int(record["price_krw"]) for record in records if int(record["price_krw"]) > 0]
        previous = previous_averages.get(complex_id)
        if not prices or not previous:
            continue

        current = int(sum(prices) / len(prices))
        change_ratio = (current - previous) / previous
        if abs(change_ratio) > threshold:
            blocks[complex_id] = QualityBlock(complex_id, current, previous, change_ratio)
    return blocks


def apply_quality_blocks(candidates: list[Candidate], blocks: dict[str, QualityBlock]) -> list[Candidate]:
    if not blocks:
        return candidates
    updated: list[Candidate] = []
    for candidate in candidates:
        block = blocks.get(candidate.complex_id)
        if block and candidate.decision == "approve":
            updated.append(
                Candidate(
                    candidate.complex_id,
                    candidate.listing_key,
                    candidate.price_krw,
                    "hold",
                    f"{block.reason}:{block.change_ratio:.2%}",
                    candidate.listing,
                )
            )
        else:
            updated.append(candidate)
    return updated


def approved_candidates(candidates: list[Candidate], limit: int = 5) -> list[Candidate]:
    approved = [candidate for candidate in candidates if candidate.decision == "approve"]
    return sorted(approved, key=lambda candidate: candidate.price_krw)[:limit]


def _dedupe(records: list[dict[str, Any]]) -> list[tuple[dict[str, Any], str | None]]:
    best_by_key: dict[str, dict[str, Any]] = {}
    representative_by_equivalent_key: dict[str, str] = {}
    result: list[tuple[dict[str, Any], str | None]] = []
    for record in records:
        key = listing_key(record)
        current = best_by_key.get(key)
        if current is None or int(record["price_krw"]) < int(current["price_krw"]):
            best_by_key[key] = record
    for record in best_by_key.values():
        key = listing_key(record)
        equivalent_key = _equivalent_listing_key(record)
        duplicate_of = representative_by_equivalent_key.get(equivalent_key)
        if duplicate_of is None:
            representative_by_equivalent_key[equivalent_key] = key
            result.append((record, None))
        else:
            result.append((record, duplicate_of))
    return result


def _equivalent_listing_key(record: dict[str, Any]) -> str:
    parts = [
        record.get("complex_id", ""),
        record.get("building", ""),
        record.get("floor", ""),
        record.get("area_m2", ""),
        record.get("price_krw", ""),
    ]
    return "|".join(str(part).strip().lower() for part in parts)


def _exclusion_match(target: WatchTarget, record: dict[str, Any]) -> str | None:
    if not target.exclude:
        return None
    haystack = " ".join(
        str(record.get(field, "")) for field in ("title", "description", "building", "floor", "link")
    ).lower()
    for token in target.exclude:
        normalized = token.strip().lower()
        if normalized and normalized in haystack:
            return token
    return None
