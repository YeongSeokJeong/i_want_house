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


def classify_candidates(
    targets: tuple[WatchTarget, ...],
    records_by_complex: dict[str, list[dict[str, Any]]],
    notified_state: dict[str, Any],
) -> list[Candidate]:
    targets_by_id = {target.complex_id: target for target in targets}
    notified = notified_state.get("notified", {}) if isinstance(notified_state, dict) else {}
    candidates: list[Candidate] = []

    for complex_id, records in records_by_complex.items():
        target = targets_by_id[complex_id]
        for record in _dedupe(records):
            key = listing_key(record)
            price = int(record["price_krw"])
            previous = notified.get(key, {}) if isinstance(notified, dict) else {}
            previous_price = previous.get("price_krw") if isinstance(previous, dict) else None

            if previous_price is not None and price >= int(previous_price):
                candidates.append(
                    Candidate(complex_id, key, price, "hold", "already_notified_without_price_drop", record)
                )
                continue

            if price <= target.target_price_krw:
                candidates.append(Candidate(complex_id, key, price, "approve", "target_price", record))
            else:
                candidates.append(Candidate(complex_id, key, price, "reject", "above_target_price", record))

    return candidates


def approved_candidates(candidates: list[Candidate], limit: int = 5) -> list[Candidate]:
    approved = [candidate for candidate in candidates if candidate.decision == "approve"]
    return sorted(approved, key=lambda candidate: candidate.price_krw)[:limit]


def _dedupe(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    best_by_key: dict[str, dict[str, Any]] = {}
    for record in records:
        key = listing_key(record)
        current = best_by_key.get(key)
        if current is None or int(record["price_krw"]) < int(current["price_krw"]):
            best_by_key[key] = record
    return list(best_by_key.values())
