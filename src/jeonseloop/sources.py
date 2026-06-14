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


@dataclass(frozen=True)
class NaverSourceConfig:
    complex_no_by_id: dict[str, str]
    trade_type: str = "B1"
    real_estate_type: str = "APT"
    max_pages: int = 3
    timeout_seconds: int = 15

    @classmethod
    def from_env(cls, values: Mapping[str, str] | None = None) -> NaverSourceConfig:
        env = os.environ if values is None else values
        timeout = _positive_int(env.get("JEONSELOOP_SOURCE_TIMEOUT_SECONDS"), default=15)
        return cls(
            complex_no_by_id=_parse_complex_no_map(env.get("JEONSELOOP_NAVER_COMPLEX_NO_MAP")),
            trade_type=_blank_to_none(env.get("JEONSELOOP_NAVER_TRADE_TYPE")) or "B1",
            real_estate_type=_blank_to_none(env.get("JEONSELOOP_NAVER_REAL_ESTATE_TYPE")) or "APT",
            max_pages=_positive_int(env.get("JEONSELOOP_NAVER_MAX_PAGES"), default=3),
            timeout_seconds=timeout,
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
        timeout = _positive_int(env.get("JEONSELOOP_SOURCE_TIMEOUT_SECONDS"), default=15)
        return cls(
            apt_hash_by_id=_parse_hogangnono_apt_hash_map(env.get("JEONSELOOP_HOGANGNONO_APT_HASH_MAP")),
            trade_types=_blank_to_none(env.get("JEONSELOOP_HOGANGNONO_TRADE_TYPES")) or "0",
            page_size=_positive_int(env.get("JEONSELOOP_HOGANGNONO_PAGE_SIZE"), default=50),
            max_pages=_positive_int(env.get("JEONSELOOP_HOGANGNONO_MAX_PAGES"), default=3),
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


class NaverListingSourceClient:
    BASE_URL = "https://new.land.naver.com/api/articles/complex"

    def __init__(
        self,
        config: NaverSourceConfig,
        *,
        opener: Opener | None = None,
    ) -> None:
        self._config = config
        self._opener = opener if opener is not None else request.urlopen

    def fetch_listings(self, target: WatchTarget) -> list[dict[str, Any]]:
        complex_no = self._complex_no_for(target)
        listings: list[dict[str, Any]] = []
        for page in range(1, self._config.max_pages + 1):
            payload = self._get_json(self._articles_url(complex_no, page), complex_no)
            articles = payload.get("articleList") if isinstance(payload, dict) else None
            if not isinstance(articles, list):
                raise SourceFetchError("naver source payload must contain an articleList list")
            listings.extend(_normalize_naver_article(article, target, complex_no) for article in articles)
            if not articles or payload.get("isMoreData") is False:
                break
        return listings

    def _complex_no_for(self, target: WatchTarget) -> str:
        mapped = self._config.complex_no_by_id.get(target.complex_id)
        if mapped:
            return mapped
        if str(target.complex_id).isdigit():
            return str(target.complex_id)
        raise SourceFetchError(
            "naver source requires JEONSELOOP_NAVER_COMPLEX_NO_MAP entry "
            f"for complex_id '{target.complex_id}' or a numeric watchlist complex_id"
        )

    def _articles_url(self, complex_no: str, page: int) -> str:
        query = {
            "realEstateType": self._config.real_estate_type,
            "tradeType": self._config.trade_type,
            "tag": "::::::::",
            "rentPriceMin": "0",
            "rentPriceMax": "900000000",
            "priceMin": "0",
            "priceMax": "900000000",
            "areaMin": "0",
            "areaMax": "900000000",
            "showArticle": "false",
            "sameAddressGroup": "true",
            "priceType": "RETAIL",
            "page": str(page),
            "complexNo": complex_no,
            "type": "list",
            "order": "prc",
        }
        return f"{self.BASE_URL}/{parse.quote(complex_no, safe='')}?{parse.urlencode(query)}"

    def _get_json(self, url: str, complex_no: str) -> dict[str, Any]:
        headers = {
            "Accept": "application/json",
            "Referer": f"https://new.land.naver.com/complexes/{complex_no}",
            "User-Agent": "JeonseLoop/1.0",
        }
        req = request.Request(url, headers=headers, method="GET")
        try:
            with self._opener(req, timeout=self._config.timeout_seconds) as response:
                status = int(getattr(response, "status", 200))
                if status == 429 or status >= 500:
                    raise TransientSourceFetchError(f"naver source returned HTTP {status}")
                if status >= 400:
                    raise SourceFetchError(f"naver source returned HTTP {status}")
                body = response.read()
        except error.HTTPError as exc:
            if exc.code == 429 or exc.code >= 500:
                raise TransientSourceFetchError(f"naver source returned HTTP {exc.code}") from exc
            raise SourceFetchError(f"naver source returned HTTP {exc.code}") from exc
        except (TimeoutError, error.URLError) as exc:
            raise TransientSourceFetchError(f"naver source request failed: {exc}") from exc

        try:
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SourceFetchError("naver source response is not valid UTF-8 JSON") from exc
        if not isinstance(payload, dict):
            raise SourceFetchError("naver source payload must be a JSON object")
        return payload


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
            f"for complex_id '{target.complex_id}' or a direct Hogangnono apt hash"
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


def _listing_source_kind(env: Mapping[str, str]) -> str | None:
    raw_kind = _blank_to_none(env.get("JEONSELOOP_LISTING_SOURCE_KIND"))
    if raw_kind is None:
        return "http-json" if _blank_to_none(env.get("JEONSELOOP_LISTING_SOURCE_URL")) else None
    normalized = raw_kind.strip().lower().replace("_", "-")
    if normalized in {"http", "json", "http-json"}:
        return "http-json"
    return normalized


def _invalid_listing_source_kind(kind: str) -> Callable[[WatchTarget], list[dict[str, Any]]]:
    def fetcher(target: WatchTarget) -> list[dict[str, Any]]:
        raise SourceFetchError(f"unsupported JEONSELOOP_LISTING_SOURCE_KIND '{kind}'")

    return fetcher


def _parse_complex_no_map(value: str | None) -> dict[str, str]:
    stripped = _blank_to_none(value)
    if stripped is None:
        return {}
    try:
        raw = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise SourceFetchError("JEONSELOOP_NAVER_COMPLEX_NO_MAP must be a JSON object") from exc
    if not isinstance(raw, dict):
        raise SourceFetchError("JEONSELOOP_NAVER_COMPLEX_NO_MAP must be a JSON object")
    parsed: dict[str, str] = {}
    for key, raw_value in raw.items():
        complex_id = str(key).strip()
        complex_no = str(raw_value).strip()
        if not complex_id or not complex_no:
            raise SourceFetchError("JEONSELOOP_NAVER_COMPLEX_NO_MAP entries must be non-empty")
        parsed[complex_id] = complex_no
    return parsed


def _parse_hogangnono_apt_hash_map(value: str | None) -> dict[str, str]:
    stripped = _blank_to_none(value)
    if stripped is None:
        return {}
    try:
        raw = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise SourceFetchError("JEONSELOOP_HOGANGNONO_APT_HASH_MAP must be a JSON object") from exc
    if not isinstance(raw, dict):
        raise SourceFetchError("JEONSELOOP_HOGANGNONO_APT_HASH_MAP must be a JSON object")
    parsed: dict[str, str] = {}
    for key, raw_value in raw.items():
        complex_id = str(key).strip()
        apt_hash = str(raw_value).strip()
        if not complex_id or not apt_hash:
            raise SourceFetchError("JEONSELOOP_HOGANGNONO_APT_HASH_MAP entries must be non-empty")
        parsed[complex_id] = apt_hash
    return parsed


def _normalize_naver_article(article: Any, target: WatchTarget, complex_no: str) -> dict[str, Any]:
    if not isinstance(article, dict):
        raise SourceFetchError("naver articleList must contain objects only")
    article_no = _required_text(article, "articleNo")
    price_krw = _parse_korean_price_krw(_required_text(article, "dealOrWarrantPrc"))
    area_m2 = _naver_area_m2(article)
    return {
        "listing_id": f"naver:{article_no}",
        "complex_id": target.complex_id,
        "title": str(article.get("articleName") or target.name),
        "price_krw": price_krw,
        "area_m2": area_m2,
        "building": str(article.get("buildingName") or ""),
        "floor": str(article.get("floorInfo") or ""),
        "posted_at": _naver_date(article.get("articleConfirmYmd")),
        "description": str(article.get("articleFeatureDesc") or ""),
        "link": f"https://new.land.naver.com/complexes/{complex_no}?articleNo={parse.quote(article_no, safe='')}",
        "source": "naver",
        "trade_type": str(article.get("tradeTypeName") or ""),
        "real_estate_type": str(article.get("realEstateTypeName") or ""),
    }


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


def _required_text(record: dict[str, Any], key: str) -> str:
    value = str(record.get(key, "")).strip()
    if not value:
        raise SourceFetchError(f"naver article missing {key}")
    return value


def _required_hogangnono_text(record: dict[str, Any], key: str) -> str:
    value = str(record.get(key, "")).strip()
    if not value:
        raise SourceFetchError(f"hogangnono item missing {key}")
    return value


def _naver_area_m2(article: dict[str, Any]) -> float:
    for key in ("area2", "exclusiveArea", "area1", "supplyArea"):
        value = article.get(key)
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            continue
        if parsed > 0:
            return parsed
    area_name = str(article.get("areaName", "")).strip()
    if area_name:
        numeric = "".join(ch for ch in area_name if ch.isdigit() or ch == ".")
        try:
            parsed = float(numeric)
        except ValueError:
            parsed = 0
        if parsed > 0:
            return parsed
    raise SourceFetchError("naver article missing area_m2")


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


def _parse_korean_price_krw(value: str) -> int:
    text = value.replace(",", "").replace(" ", "").strip()
    if not text:
        raise SourceFetchError("naver article missing price")

    total = 0
    if "억" in text:
        eok_text, rest = text.split("억", 1)
        try:
            total += int(float(eok_text) * 100_000_000)
        except ValueError as exc:
            raise SourceFetchError(f"naver article has invalid price '{value}'") from exc
        text = rest
    if text:
        man_text = text.replace("만원", "").replace("만", "")
        try:
            total += int(float(man_text) * 10_000)
        except ValueError as exc:
            raise SourceFetchError(f"naver article has invalid price '{value}'") from exc
    if total <= 0:
        raise SourceFetchError(f"naver article has invalid price '{value}'")
    return total


def _hogangnono_price_krw(item: dict[str, Any]) -> int:
    value = item.get("deposit")
    try:
        parsed = int(float(value))
    except (TypeError, ValueError) as exc:
        raise SourceFetchError("hogangnono item missing price") from exc
    if parsed <= 0:
        raise SourceFetchError("hogangnono item has invalid price")
    return parsed * 10_000


def _naver_date(value: Any) -> str:
    text = str(value or "").strip()
    if len(text) == 8 and text.isdigit():
        return f"{text[0:4]}-{text[4:6]}-{text[6:8]}"
    return text


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
