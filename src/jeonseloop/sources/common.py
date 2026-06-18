from __future__ import annotations

import json
from typing import Any, Callable
from urllib import parse, request

from ..watchlist import WatchTarget


class SourceFetchError(RuntimeError):
    """Raised when a configured external source cannot return usable JSON."""


class TransientSourceFetchError(SourceFetchError):
    """Raised when an external source failure may succeed on retry."""


Opener = Callable[[request.Request, int], Any]


def records_from_payload(payload: Any, key: str) -> list[dict[str, Any]]:
    raw_records = payload.get(key, payload) if isinstance(payload, dict) else payload
    if not isinstance(raw_records, list):
        raise SourceFetchError(f"source payload must be a list or contain a {key} list")
    if not all(isinstance(record, dict) for record in raw_records):
        raise SourceFetchError(f"source {key} payload must contain objects only")
    return raw_records


def target_url(template: str, target: WatchTarget) -> str:
    replacements = {
        "{complex_id}": parse.quote(target.complex_id, safe=""),
        "{name}": parse.quote(target.name, safe=""),
        "{area_m2}": parse.quote(str(target.area_m2), safe=""),
    }
    url = template
    for token, value in replacements.items():
        url = url.replace(token, value)
    return url


def parse_json_object_map(value: str | None, *, env_name: str) -> dict[str, str]:
    stripped = blank_to_none(value)
    if stripped is None:
        return {}
    try:
        raw = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise SourceFetchError(f"{env_name} must be a JSON object") from exc
    if not isinstance(raw, dict):
        raise SourceFetchError(f"{env_name} must be a JSON object")
    parsed: dict[str, str] = {}
    for key, raw_value in raw.items():
        parsed_key = str(key).strip()
        parsed_value = str(raw_value).strip()
        if not parsed_key or not parsed_value:
            raise SourceFetchError(f"{env_name} entries must be non-empty")
        parsed[parsed_key] = parsed_value
    return parsed


def blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def positive_int(value: str | None, *, default: int) -> int:
    if value is None or not value.strip():
        return default
    try:
        parsed = int(value)
    except ValueError:
        return default
    return parsed if parsed > 0 else default
