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
class NaverSourceConfig:
    complex_no_by_id: dict[str, str]
    trade_type: str = "B1"
    real_estate_type: str = "APT"
    max_pages: int = 3
    timeout_seconds: int = 15

    @classmethod
    def from_env(cls, values: Mapping[str, str] | None = None) -> NaverSourceConfig:
        env = os.environ if values is None else values
        timeout = positive_int(env.get("JEONSELOOP_SOURCE_TIMEOUT_SECONDS"), default=15)
        return cls(
            complex_no_by_id=parse_json_object_map(
                env.get("JEONSELOOP_NAVER_COMPLEX_NO_MAP"),
                env_name="JEONSELOOP_NAVER_COMPLEX_NO_MAP",
            ),
            trade_type=blank_to_none(env.get("JEONSELOOP_NAVER_TRADE_TYPE")) or "B1",
            real_estate_type=blank_to_none(env.get("JEONSELOOP_NAVER_REAL_ESTATE_TYPE")) or "APT",
            max_pages=positive_int(env.get("JEONSELOOP_NAVER_MAX_PAGES"), default=3),
            timeout_seconds=timeout,
        )


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


def _required_text(record: dict[str, Any], key: str) -> str:
    value = str(record.get(key, "")).strip()
    if not value:
        raise SourceFetchError(f"naver article missing {key}")
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


def _naver_date(value: Any) -> str:
    text = str(value or "").strip()
    if len(text) == 8 and text.isdigit():
        return f"{text[0:4]}-{text[4:6]}-{text[6:8]}"
    return text
