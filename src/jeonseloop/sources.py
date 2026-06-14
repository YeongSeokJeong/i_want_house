from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Any, Callable, Mapping
from urllib import error, parse, request

from .watchlist import WatchTarget


class SourceFetchError(RuntimeError):
    """Raised when a configured external source cannot return usable JSON."""


class TransientSourceFetchError(SourceFetchError):
    """Raised when an external source failure may succeed on retry."""


Opener = Callable[[request.Request, int], Any]


@dataclass(frozen=True)
class HttpJsonSourceConfig:
    listing_url: str | None = None
    trade_url: str | None = None
    bearer_token: str | None = None
    timeout_seconds: int = 15

    @classmethod
    def from_env(cls, values: Mapping[str, str] | None = None) -> HttpJsonSourceConfig:
        env = os.environ if values is None else values
        timeout = _positive_int(env.get("JEONSELOOP_SOURCE_TIMEOUT_SECONDS"), default=15)
        return cls(
            listing_url=_blank_to_none(env.get("JEONSELOOP_LISTING_SOURCE_URL")),
            trade_url=_blank_to_none(env.get("JEONSELOOP_TRADE_SOURCE_URL")),
            bearer_token=_blank_to_none(env.get("JEONSELOOP_SOURCE_BEARER_TOKEN")),
            timeout_seconds=timeout,
        )


class HttpJsonSourceClient:
    def __init__(
        self,
        config: HttpJsonSourceConfig,
        *,
        opener: Opener | None = None,
    ) -> None:
        self._config = config
        self._opener = opener if opener is not None else request.urlopen

    def fetch_listings(self, target: WatchTarget) -> list[dict[str, Any]]:
        if not self._config.listing_url:
            raise SourceFetchError("listing source URL is not configured")

        payload = self._get_json(_target_url(self._config.listing_url, target))
        records = _records_from_payload(payload, "listings")
        normalized: list[dict[str, Any]] = []
        for record in records:
            item = dict(record)
            complex_id = str(item.get("complex_id", "")).strip()
            if complex_id and complex_id != target.complex_id:
                continue
            item["complex_id"] = target.complex_id
            normalized.append(item)
        return normalized

    def fetch_trades(self, target: WatchTarget) -> list[dict[str, Any]]:
        if not self._config.trade_url:
            raise SourceFetchError("trade source URL is not configured")

        payload = self._get_json(_target_url(self._config.trade_url, target))
        return [dict(record) for record in _records_from_payload(payload, "trades")]

    def _get_json(self, url: str) -> Any:
        headers = {"Accept": "application/json", "User-Agent": "JeonseLoop/1.0"}
        if self._config.bearer_token:
            headers["Authorization"] = f"Bearer {self._config.bearer_token}"
        req = request.Request(url, headers=headers, method="GET")
        try:
            with self._opener(req, timeout=self._config.timeout_seconds) as response:
                status = int(getattr(response, "status", 200))
                if status == 429 or status >= 500:
                    raise TransientSourceFetchError(f"source returned HTTP {status}")
                if status >= 400:
                    raise SourceFetchError(f"source returned HTTP {status}")
                body = response.read()
        except error.HTTPError as exc:
            if exc.code == 429 or exc.code >= 500:
                raise TransientSourceFetchError(f"source returned HTTP {exc.code}") from exc
            raise SourceFetchError(f"source returned HTTP {exc.code}") from exc
        except (TimeoutError, error.URLError) as exc:
            raise TransientSourceFetchError(f"source request failed: {exc}") from exc

        try:
            return json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SourceFetchError("source response is not valid UTF-8 JSON") from exc


def listing_fetcher_from_env(
    values: Mapping[str, str] | None = None,
) -> Callable[[WatchTarget], list[dict[str, Any]]] | None:
    config = HttpJsonSourceConfig.from_env(values)
    if not config.listing_url:
        return None
    return HttpJsonSourceClient(config).fetch_listings


def trade_fetcher_from_env(
    values: Mapping[str, str] | None = None,
) -> Callable[[WatchTarget], list[dict[str, Any]]] | None:
    config = HttpJsonSourceConfig.from_env(values)
    if not config.trade_url:
        return None
    return HttpJsonSourceClient(config).fetch_trades


def _records_from_payload(payload: Any, key: str) -> list[dict[str, Any]]:
    raw_records = payload.get(key, payload) if isinstance(payload, dict) else payload
    if not isinstance(raw_records, list):
        raise SourceFetchError(f"source payload must be a list or contain a {key} list")
    if not all(isinstance(record, dict) for record in raw_records):
        raise SourceFetchError(f"source {key} payload must contain objects only")
    return raw_records


def _target_url(template: str, target: WatchTarget) -> str:
    replacements = {
        "{complex_id}": parse.quote(target.complex_id, safe=""),
        "{name}": parse.quote(target.name, safe=""),
        "{area_m2}": parse.quote(str(target.area_m2), safe=""),
    }
    url = template
    for token, value in replacements.items():
        url = url.replace(token, value)
    return url


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _positive_int(value: str | None, *, default: int) -> int:
    if value is None or not value.strip():
        return default
    try:
        parsed = int(value)
    except ValueError:
        return default
    return parsed if parsed > 0 else default
