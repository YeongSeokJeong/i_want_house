from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Any, Mapping
from urllib import error, request

from ..watchlist import WatchTarget
from .common import (
    Opener,
    SourceFetchError,
    TransientSourceFetchError,
    blank_to_none,
    positive_int,
    records_from_payload,
    target_url,
)


@dataclass(frozen=True)
class HttpJsonSourceConfig:
    listing_url: str | None = None
    trade_url: str | None = None
    bearer_token: str | None = None
    timeout_seconds: int = 15

    @classmethod
    def from_env(cls, values: Mapping[str, str] | None = None) -> HttpJsonSourceConfig:
        env = os.environ if values is None else values
        timeout = positive_int(env.get("JEONSELOOP_SOURCE_TIMEOUT_SECONDS"), default=15)
        return cls(
            listing_url=blank_to_none(env.get("JEONSELOOP_LISTING_SOURCE_URL")),
            trade_url=blank_to_none(env.get("JEONSELOOP_TRADE_SOURCE_URL")),
            bearer_token=blank_to_none(env.get("JEONSELOOP_SOURCE_BEARER_TOKEN")),
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

        payload = self._get_json(target_url(self._config.listing_url, target))
        records = records_from_payload(payload, "listings")
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

        payload = self._get_json(target_url(self._config.trade_url, target))
        return [dict(record) for record in records_from_payload(payload, "trades")]

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
