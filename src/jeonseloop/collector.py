from __future__ import annotations

import json
from pathlib import Path
import time
from typing import Any, Callable

from .watchlist import WatchTarget


class TransientListingFetchError(RuntimeError):
    """Raised by live listing adapters when a retry may succeed."""


ListingFetcher = Callable[[WatchTarget], list[dict[str, Any]]]
Sleeper = Callable[[float], None]


def collect_listings(
    targets: tuple[WatchTarget, ...],
    fixture_path: Path | None = None,
    *,
    fetcher: ListingFetcher | None = None,
    request_interval_seconds: int = 2,
    retry_attempts: int = 3,
    sleeper: Sleeper = time.sleep,
) -> dict[str, list[dict[str, Any]]]:
    """Return listing snapshots limited to watchlist complexes."""

    if request_interval_seconds < 2:
        raise ValueError("request_interval_seconds must be at least 2")
    if retry_attempts < 1:
        raise ValueError("retry_attempts must be at least 1")

    result = {target.complex_id: [] for target in targets}
    if fixture_path is None:
        if fetcher is not None:
            for index, target in enumerate(targets):
                if index:
                    sleeper(request_interval_seconds)
                result[target.complex_id] = _fetch_with_retries(
                    target,
                    fetcher=fetcher,
                    retry_attempts=retry_attempts,
                    request_interval_seconds=request_interval_seconds,
                    sleeper=sleeper,
                )
        return result

    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    raw_records = payload.get("listings", payload) if isinstance(payload, dict) else payload
    if not isinstance(raw_records, list):
        raise ValueError("listing fixture must be a list or contain a listings list")

    allowed = set(result)
    for record in raw_records:
        if not isinstance(record, dict):
            continue
        complex_id = record.get("complex_id")
        if complex_id in allowed:
            result[complex_id].append(dict(record))
    return result


def _fetch_with_retries(
    target: WatchTarget,
    *,
    fetcher: ListingFetcher,
    retry_attempts: int,
    request_interval_seconds: int,
    sleeper: Sleeper,
) -> list[dict[str, Any]]:
    for attempt in range(1, retry_attempts + 1):
        try:
            return fetcher(target)
        except TransientListingFetchError:
            if attempt == retry_attempts:
                raise
            sleeper(request_interval_seconds)
    return []
