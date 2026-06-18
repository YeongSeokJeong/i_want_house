from __future__ import annotations

import os
from typing import Any, Callable, Mapping

from ..watchlist import WatchTarget
from .common import SourceFetchError, blank_to_none
from .hogangnono import HogangnonoListingSourceClient, HogangnonoSourceConfig
from .http_json import HttpJsonSourceClient, HttpJsonSourceConfig
from .naver import NaverListingSourceClient, NaverSourceConfig


def listing_fetcher_from_env(
    values: Mapping[str, str] | None = None,
) -> Callable[[WatchTarget], list[dict[str, Any]]] | None:
    env = os.environ if values is None else values
    kind = _listing_source_kind(env)
    if kind is None:
        return None
    if kind == "naver":
        return NaverListingSourceClient(NaverSourceConfig.from_env(values)).fetch_listings
    if kind == "hogangnono":
        return HogangnonoListingSourceClient(HogangnonoSourceConfig.from_env(values)).fetch_listings
    if kind != "http-json":
        return _invalid_listing_source_kind(kind)

    config = HttpJsonSourceConfig.from_env(values)
    return HttpJsonSourceClient(config).fetch_listings


def trade_fetcher_from_env(
    values: Mapping[str, str] | None = None,
) -> Callable[[WatchTarget], list[dict[str, Any]]] | None:
    config = HttpJsonSourceConfig.from_env(values)
    if not config.trade_url:
        return None
    return HttpJsonSourceClient(config).fetch_trades


def _listing_source_kind(env: Mapping[str, str]) -> str | None:
    raw_kind = blank_to_none(env.get("JEONSELOOP_LISTING_SOURCE_KIND"))
    if raw_kind is None:
        return "http-json" if blank_to_none(env.get("JEONSELOOP_LISTING_SOURCE_URL")) else None
    normalized = raw_kind.strip().lower().replace("_", "-")
    if normalized in {"http", "json", "http-json"}:
        return "http-json"
    return normalized


def _invalid_listing_source_kind(kind: str) -> Callable[[WatchTarget], list[dict[str, Any]]]:
    def fetcher(target: WatchTarget) -> list[dict[str, Any]]:
        raise SourceFetchError(f"unsupported JEONSELOOP_LISTING_SOURCE_KIND '{kind}'")

    return fetcher
