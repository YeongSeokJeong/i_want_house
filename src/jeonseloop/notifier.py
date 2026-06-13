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
    return (
        "[JeonseLoop]\n"
        f"complex_id: {candidate.complex_id}\n"
        f"price_krw: {candidate.price_krw}\n"
        f"reason: {candidate.reason}\n"
        f"title: {title}\n"
        f"link: {listing.get('link', '')}"
    )


def send_candidates(
    candidates: Iterable[Candidate],
    *,
    allow_send: bool,
) -> list[NotificationResult]:
    return NotificationService().send_candidates(candidates, allow_send=allow_send)
