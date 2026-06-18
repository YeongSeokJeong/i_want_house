from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Any, Mapping
from urllib import error, parse, request

from ..watchlist import WatchTarget
from .common import (
    Opener,
    SourceFetchError,
    TransientSourceFetchError,
    blank_to_none,
    parse_json_object_map,
    positive_int,
)


@dataclass(frozen=True)
class HogangnonoSourceConfig:
    apt_hash_by_id: dict[str, str]
    trade_types: str = "0"
    page_size: int = 50
    max_pages: int = 3
    timeout_seconds: int = 15

    @classmethod
    def from_env(cls, values: Mapping[str, str] | None = None) -> HogangnonoSourceConfig:
        env = os.environ if values is None else values
        timeout = positive_int(env.get("JEONSELOOP_SOURCE_TIMEOUT_SECONDS"), default=15)
        return cls(
            apt_hash_by_id=parse_json_object_map(
                env.get("JEONSELOOP_HOGANGNONO_APT_HASH_MAP"),
                env_name="JEONSELOOP_HOGANGNONO_APT_HASH_MAP",
            ),
            trade_types=blank_to_none(env.get("JEONSELOOP_HOGANGNONO_TRADE_TYPES")) or "0",
            page_size=positive_int(env.get("JEONSELOOP_HOGANGNONO_PAGE_SIZE"), default=50),
            max_pages=positive_int(env.get("JEONSELOOP_HOGANGNONO_MAX_PAGES"), default=3),
            timeout_seconds=timeout,
        )


class HogangnonoListingSourceClient:
    BASE_URL = "https://hogangnono.com/api/v2/apts"

    def __init__(
        self,
        config: HogangnonoSourceConfig,
        *,
        opener: Opener | None = None,
    ) -> None:
        self._config = config
        self._opener = opener if opener is not None else request.urlopen

    def fetch_listings(self, target: WatchTarget) -> list[dict[str, Any]]:
        apt_hash = self._apt_hash_for(target)
        listings: list[dict[str, Any]] = []
        for page_index in range(self._config.max_pages):
            offset = page_index * self._config.page_size
            payload = self._get_json(self._items_url(apt_hash, offset), apt_hash)
            items, total_count = _hogangnono_items_from_payload(payload)
            listings.extend(_normalize_hogangnono_item(item, target, apt_hash) for item in items)
            if not items or len(items) < self._config.page_size:
                break
            if total_count is not None and offset + len(items) >= total_count:
                break
        return listings

    def _apt_hash_for(self, target: WatchTarget) -> str:
        mapped = self._config.apt_hash_by_id.get(target.complex_id)
        if mapped:
            return mapped
        if _looks_like_hogangnono_apt_hash(target.complex_id):
            return target.complex_id
        raise SourceFetchError(
            "hogangnono source requires JEONSELOOP_HOGANGNONO_APT_HASH_MAP entry "
            f"for missing complex_id '{target.complex_id}' or a direct Hogangnono apt hash; "
            f"add JSON entry {{\"{target.complex_id}\":\"<hogangnono_apt_hash>\"}}"
        )

    def _items_url(self, apt_hash: str, offset: int) -> str:
        query = {
            "tradeTypes": self._config.trade_types,
            "offset": str(offset),
            "limit": str(self._config.page_size),
        }
        return f"{self.BASE_URL}/{parse.quote(apt_hash, safe='')}/items?{parse.urlencode(query)}"

    def _get_json(self, url: str, apt_hash: str) -> dict[str, Any]:
        headers = {
            "Accept": "application/json",
            "Referer": f"https://hogangnono.com/apt/{apt_hash}/item-catalog",
            "User-Agent": "JeonseLoop/1.0",
        }
        req = request.Request(url, headers=headers, method="GET")
        try:
            with self._opener(req, timeout=self._config.timeout_seconds) as response:
                status = int(getattr(response, "status", 200))
                if status == 429 or status >= 500:
                    raise TransientSourceFetchError(f"hogangnono source returned HTTP {status}")
                if status >= 400:
                    raise SourceFetchError(f"hogangnono source returned HTTP {status}")
                body = response.read()
        except error.HTTPError as exc:
            if exc.code == 429 or exc.code >= 500:
                raise TransientSourceFetchError(f"hogangnono source returned HTTP {exc.code}") from exc
            raise SourceFetchError(f"hogangnono source returned HTTP {exc.code}") from exc
        except (TimeoutError, error.URLError) as exc:
            raise TransientSourceFetchError(f"hogangnono source request failed: {exc}") from exc

        try:
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SourceFetchError("hogangnono source response is not valid UTF-8 JSON") from exc
        if not isinstance(payload, dict):
            raise SourceFetchError("hogangnono source payload must be a JSON object")
        return payload


def _hogangnono_items_from_payload(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], int | None]:
    data = payload.get("data")
    if not isinstance(data, dict):
        raise SourceFetchError("hogangnono source payload must contain a data object")
    items = data.get("aptItems")
    if not isinstance(items, list):
        raise SourceFetchError("hogangnono source payload must contain an aptItems list")
    if not all(isinstance(item, dict) for item in items):
        raise SourceFetchError("hogangnono aptItems payload must contain objects only")
    total_count = data.get("aptItemTotalCount")
    return items, total_count if isinstance(total_count, int) else None


def _normalize_hogangnono_item(item: Any, target: WatchTarget, apt_hash: str) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise SourceFetchError("hogangnono aptItems payload must contain objects only")
    item_id = _required_hogangnono_text(item, "itemId")
    trade_type = str(item.get("tradeType", "")).strip()
    area_ho_id = str(item.get("areaHoId", "")).strip()
    return {
        "listing_id": f"hogangnono:{item_id}",
        "complex_id": target.complex_id,
        "title": str(item.get("itemTitle") or item.get("aptName") or target.name),
        "price_krw": _hogangnono_price_krw(item),
        "area_m2": _hogangnono_area_m2(item),
        "building": str(item.get("areaBuildingName") or item.get("aptDongName") or ""),
        "floor": str(item.get("floor") or ""),
        "posted_at": _hogangnono_date(item.get("effectivenessUpdatedAt") or item.get("updatedAt") or item.get("createdAt")),
        "description": str(item.get("itemDescription") or item.get("description") or item.get("itemTitle") or ""),
        "link": _hogangnono_listing_link(apt_hash, area_ho_id, trade_type),
        "source": "hogangnono",
        "trade_type": trade_type,
        "item_source": str(item.get("itemSource") or ""),
        "real_estate_type": "apt",
    }


def _required_hogangnono_text(record: dict[str, Any], key: str) -> str:
    value = str(record.get(key, "")).strip()
    if not value:
        raise SourceFetchError(f"hogangnono item missing {key}")
    return value


def _hogangnono_area_m2(item: dict[str, Any]) -> float:
    required_info = item.get("itemRequiredInfo")
    if isinstance(required_info, dict):
        for key in ("privateArea", "publicArea"):
            value = required_info.get(key)
            try:
                parsed = float(value)
            except (TypeError, ValueError):
                continue
            if parsed > 0:
                return parsed
    for key in ("privateArea", "sizeM2", "publicArea", "sizeContractM2"):
        value = item.get(key)
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            continue
        if parsed > 0:
            return parsed
    raise SourceFetchError("hogangnono item missing area_m2")


def _hogangnono_price_krw(item: dict[str, Any]) -> int:
    value = item.get("deposit")
    try:
        parsed = int(float(value))
    except (TypeError, ValueError) as exc:
        raise SourceFetchError("hogangnono item missing price") from exc
    if parsed <= 0:
        raise SourceFetchError("hogangnono item has invalid price")
    return parsed * 10_000


def _hogangnono_date(value: Any) -> str:
    text = str(value or "").strip()
    if "T" in text:
        return text.split("T", 1)[0]
    return text


def _hogangnono_listing_link(apt_hash: str, area_ho_id: str, trade_type: str) -> str:
    base = f"https://hogangnono.com/apt/{parse.quote(apt_hash, safe='')}/item-catalog"
    if area_ho_id and trade_type:
        return f"{base}/{parse.quote(area_ho_id, safe='')}/{parse.quote(trade_type, safe='')}"
    return base


def _looks_like_hogangnono_apt_hash(value: str) -> bool:
    text = str(value).strip()
    return bool(text) and text.isalnum() and any(ch.isdigit() for ch in text)
