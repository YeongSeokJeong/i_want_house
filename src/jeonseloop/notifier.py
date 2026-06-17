from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Callable, Iterable
from urllib import parse, request

from .analyzer import Candidate


@dataclass(frozen=True)
class NotificationResult:
    listing_key: str
    sent: bool
    reason: str


class TelegramNotifier:
    def __init__(self, token: str, chat_id: str) -> None:
        if not token or not chat_id:
            raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are required for --send")
        self._token = token
        self._chat_id = chat_id

    @classmethod
    def from_env(cls) -> "TelegramNotifier":
        return cls(
            token=os.environ.get("TELEGRAM_BOT_TOKEN", ""),
            chat_id=os.environ.get("TELEGRAM_CHAT_ID", ""),
        )

    def send(self, candidate: Candidate) -> NotificationResult:
        message = format_candidate_message(candidate)
        body = parse.urlencode({"chat_id": self._chat_id, "text": message}).encode("utf-8")
        url = f"https://api.telegram.org/bot{self._token}/sendMessage"
        req = request.Request(url, data=body, method="POST")
        try:
            with request.urlopen(req, timeout=15) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # pragma: no cover - live network path
            return NotificationResult(candidate.listing_key, False, f"telegram_error:{exc}")
        if payload.get("ok") is True:
            return NotificationResult(candidate.listing_key, True, "sent")
        return NotificationResult(candidate.listing_key, False, "telegram_rejected")


class NotificationService:
    def __init__(self, notifier_factory: Callable[[], TelegramNotifier] | None = None) -> None:
        self._notifier_factory = notifier_factory if notifier_factory is not None else TelegramNotifier.from_env

    def send_candidates(
        self,
        candidates: Iterable[Candidate],
        *,
        allow_send: bool,
    ) -> list[NotificationResult]:
        candidate_list = list(candidates)
        if not allow_send:
            return [NotificationResult(candidate.listing_key, False, "no_send") for candidate in candidate_list]

        notifier = self._notifier_factory()
        return [notifier.send(candidate) for candidate in candidate_list]


def format_candidate_message(candidate: Candidate) -> str:
    listing = candidate.listing
    title = listing.get("title") or listing.get("description") or candidate.listing_key
    lines = [
        "[JeonseLoop 급매 후보]",
        f"단지: {listing.get('watch_name') or title} ({candidate.complex_id})",
        f"매물: {title}",
        f"호가: {_format_krw(candidate.price_krw)}",
        f"목표가: {_format_krw(listing.get('target_price_krw'))} ({_format_gap(listing.get('target_gap_krw'), '목표가')})",
        f"판정: {candidate.reason}",
    ]
    if listing.get("recent_trade_price_krw"):
        lines.append(f"최근 실거래 기준: {_format_krw(listing.get('recent_trade_price_krw'))}")
    if listing.get("baseline_limit_krw"):
        discount = _format_discount(listing.get("urgent_discount_ratio"))
        lines.append(f"할인 급매선: {_format_krw(listing.get('baseline_limit_krw'))} ({discount})")
        lines.append(f"급매선 차이: {_format_gap(listing.get('baseline_gap_krw'), '급매선')}")
    if listing.get("area_m2") or listing.get("floor"):
        lines.append(f"면적/층: {listing.get('area_m2', '-')} m2 / {listing.get('floor', '-')}층")
    lines.append(f"link: {listing.get('link', '')}")
    lines.append(f"complex_id: {candidate.complex_id}")
    return "\n".join(lines)


def _format_krw(value: object) -> str:
    try:
        number = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return "-"
    return f"{number:,}원"


def _format_gap(value: object, label: str) -> str:
    try:
        amount = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return f"{label} 차이 -"
    if amount == 0:
        return f"{label}과 동일"
    direction = "낮음" if amount < 0 else "높음"
    return f"{label}보다 {_format_krw(abs(amount))} {direction}"


def _format_discount(value: object) -> str:
    try:
        ratio = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return "할인율 -"
    return f"실거래 대비 {ratio * 100:.1f}% 할인"


def send_candidates(
    candidates: Iterable[Candidate],
    *,
    allow_send: bool,
) -> list[NotificationResult]:
    return NotificationService().send_candidates(candidates, allow_send=allow_send)
