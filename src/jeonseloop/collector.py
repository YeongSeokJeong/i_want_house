from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .watchlist import WatchTarget


def collect_listings(
    targets: tuple[WatchTarget, ...],
    fixture_path: Path | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Return listing snapshots limited to watchlist complexes.

    The first implementation intentionally avoids live portal calls. A fixture
    file can supply records for tests and dry-runs; otherwise each watched
    complex returns an empty result set.
    """

    result = {target.complex_id: [] for target in targets}
    if fixture_path is None:
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
