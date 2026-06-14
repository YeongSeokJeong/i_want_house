from __future__ import annotations

import json
from pathlib import Path
import time
from typing import Any, Callable

from .sources import TransientSourceFetchError
from .watchlist import WatchTarget


class TransientListingFetchError(RuntimeError):
    """Raised by live listing adapters when a retry may succeed."""


class ListingSourceNotConfiguredError(RuntimeError):
    """Raised when live collection is requested without a listing source."""


ListingFetcher = Callable[[WatchTarget], list[dict[str, Any]]]
Sleeper = Callable[[float], None]


class ListingCollector:
    def __init__(
        self,
        *,
        fetcher: ListingFetcher | None = None,
        request_interval_seconds: int = 2,
        retry_attempts: int = 3,
        sleeper: Sleeper = time.sleep,
    ) -> None:
        if request_interval_seconds < 2:
            raise ValueError("request_interval_seconds must be at least 2")
        if retry_attempts < 1:
            raise ValueError("retry_attempts must be at least 1")

        self._fetcher = fetcher
        self._request_interval_seconds = request_interval_seconds
        self._retry_attempts = retry_attempts
        self._sleeper = sleeper

    def collect(
        self,
        targets: tuple[WatchTarget, ...],
        fixture_path: Path | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        """Return listing snapshots limited to watchlist complexes."""

        result = {target.complex_id: [] for target in targets}
        if fixture_path is None:
            if self._fetcher is None:
                raise ListingSourceNotConfiguredError(
                    "live listing source is not configured; provide a fixture or JEONSELOOP_LISTING_SOURCE_URL"
                )
            for index, target in enumerate(targets):
                if index:
                    self._sleeper(self._request_interval_seconds)
                result[target.complex_id] = self._fetch_with_retries(target)
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

    def _fetch_with_retries(self, target: WatchTarget) -> list[dict[str, Any]]:
        if self._fetcher is None:
            return []
        return _fetch_with_retries(
            target,
            fetcher=self._fetcher,
            retry_attempts=self._retry_attempts,
            request_interval_seconds=self._request_interval_seconds,
            sleeper=self._sleeper,
        )


def collect_listings(
    targets: tuple[WatchTarget, ...],
    fixture_path: Path | None = None,
    *,
    fetcher: ListingFetcher | None = None,
    request_interval_seconds: int = 2,
    retry_attempts: int = 3,
    sleeper: Sleeper = time.sleep,
) -> dict[str, list[dict[str, Any]]]:
    return ListingCollector(
        fetcher=fetcher,
        request_interval_seconds=request_interval_seconds,
        retry_attempts=retry_attempts,
        sleeper=sleeper,
    ).collect(targets, fixture_path)


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
        except (TransientListingFetchError, TransientSourceFetchError):
            if attempt == retry_attempts:
                raise
            sleeper(request_interval_seconds)
    return []
