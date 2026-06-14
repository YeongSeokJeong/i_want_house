from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


class WatchlistError(ValueError):
    """Raised when the watchlist cannot safely drive a loop cycle."""


@dataclass(frozen=True)
class WatchTarget:
    complex_id: str
    name: str
    area_m2: float
    target_price_krw: int
    urgent_discount_ratio: float = 0.1
    exclude: tuple[str, ...] = ()


@dataclass(frozen=True)
class Watchlist:
    version: int
    request_interval_seconds: int
    complexes: tuple[WatchTarget, ...]


def load_watchlist(path: Path | str) -> Watchlist:
    source = Path(path)
    if not source.exists():
        raise WatchlistError(f"watchlist not found: {source}")

    text = source.read_text(encoding="utf-8")
    if not text.strip():
        return Watchlist(version=1, request_interval_seconds=2, complexes=())

    data = _load_yaml_subset(text)
    return validate_watchlist(data)


def validate_watchlist(data: dict[str, Any]) -> Watchlist:
    if not isinstance(data, dict):
        raise WatchlistError("watchlist root must be a mapping")

    version = _positive_int(data.get("version", 1), "version")
    interval = _positive_int(data.get("request_interval_seconds", 2), "request_interval_seconds")
    if interval < 2:
        raise WatchlistError("request_interval_seconds must be at least 2")

    raw_complexes = data.get("complexes", [])
    if raw_complexes is None:
        raw_complexes = []
    if not isinstance(raw_complexes, list):
        raise WatchlistError("complexes must be a list")

    targets: list[WatchTarget] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(raw_complexes):
        if not isinstance(item, dict):
            raise WatchlistError(f"complexes[{index}] must be a mapping")

        complex_id = _required_str(item, "complex_id", index)
        if complex_id in seen_ids:
            raise WatchlistError(f"duplicate complex_id: {complex_id}")
        seen_ids.add(complex_id)

        exclude = item.get("exclude", [])
        if exclude is None:
            exclude = []
        if not isinstance(exclude, list) or not all(isinstance(value, str) for value in exclude):
            raise WatchlistError(f"complexes[{index}].exclude must be a list of strings")

        targets.append(
            WatchTarget(
                complex_id=complex_id,
                name=_required_str(item, "name", index),
                area_m2=_positive_float(item.get("area_m2"), f"complexes[{index}].area_m2"),
                target_price_krw=_positive_int(
                    item.get("target_price_krw"), f"complexes[{index}].target_price_krw"
                ),
                urgent_discount_ratio=_ratio(
                    item.get("urgent_discount_ratio", 0.1),
                    f"complexes[{index}].urgent_discount_ratio",
                ),
                exclude=tuple(exclude),
            )
        )

    return Watchlist(version=version, request_interval_seconds=interval, complexes=tuple(targets))


def _load_yaml_subset(text: str) -> dict[str, Any]:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = _parse_simple_yaml(text)
    if not isinstance(parsed, dict):
        raise WatchlistError("watchlist root must be a mapping")
    return parsed


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_list_key: str | None = None
    current_item: dict[str, Any] | None = None
    current_nested_list_key: str | None = None

    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        if indent == 0:
            key, value = _split_yaml_key_value(stripped, line_no)
            current_item = None
            current_nested_list_key = None
            if value == "":
                data[key] = []
                current_list_key = key
            else:
                data[key] = _parse_scalar(value)
                current_list_key = None
            continue

        if indent == 2 and current_list_key:
            if stripped.startswith("- "):
                current_item = {}
                data[current_list_key].append(current_item)
                current_nested_list_key = None
                rest = stripped[2:].strip()
                if rest:
                    key, value = _split_yaml_key_value(rest, line_no)
                    current_item[key] = _parse_scalar(value)
                continue

            raise WatchlistError(f"line {line_no}: expected list item")

        if indent == 4 and current_item is not None:
            if current_nested_list_key and stripped.startswith("- "):
                current_item[current_nested_list_key].append(_parse_scalar(stripped[2:].strip()))
                continue

            key, value = _split_yaml_key_value(stripped, line_no)
            if value == "":
                current_item[key] = []
                current_nested_list_key = key
            else:
                current_item[key] = _parse_scalar(value)
                current_nested_list_key = None
            continue

        if indent == 6 and current_item is not None and current_nested_list_key:
            if not stripped.startswith("- "):
                raise WatchlistError(f"line {line_no}: expected nested list item")
            current_item[current_nested_list_key].append(_parse_scalar(stripped[2:].strip()))
            continue

        raise WatchlistError(f"line {line_no}: unsupported YAML structure")

    return data


def _split_yaml_key_value(text: str, line_no: int) -> tuple[str, str]:
    if ":" not in text:
        raise WatchlistError(f"line {line_no}: expected key: value")
    key, value = text.split(":", 1)
    key = key.strip()
    if not key:
        raise WatchlistError(f"line {line_no}: empty key")
    return key, value.strip()


def _parse_scalar(value: str) -> Any:
    if value in {"[]", ""}:
        return [] if value == "[]" else ""
    if value in {"true", "false"}:
        return value == "true"
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value


def _required_str(item: dict[str, Any], key: str, index: int) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        raise WatchlistError(f"complexes[{index}].{key} is required")
    return value.strip()


def _positive_int(value: Any, label: str) -> int:
    if isinstance(value, bool):
        raise WatchlistError(f"{label} must be a positive integer")
    try:
        integer = int(value)
    except (TypeError, ValueError) as exc:
        raise WatchlistError(f"{label} must be a positive integer") from exc
    if integer <= 0:
        raise WatchlistError(f"{label} must be a positive integer")
    return integer


def _positive_float(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise WatchlistError(f"{label} must be a positive number")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise WatchlistError(f"{label} must be a positive number") from exc
    if number <= 0:
        raise WatchlistError(f"{label} must be a positive number")
    return number


def _ratio(value: Any, label: str) -> float:
    number = _positive_float(value, label)
    if number >= 1:
        raise WatchlistError(f"{label} must be less than 1")
    return number
