from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib import parse, request

from .persistence import sanitize_diagnostics


DEFAULT_MESSAGE_KEYS = ("message",)


def extract_updates(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict) and isinstance(payload.get("updates"), list):
        return [item for item in payload["updates"] if isinstance(item, dict)]
    if isinstance(payload, dict) and isinstance(payload.get("result"), list):
        return [item for item in payload["result"] if isinstance(item, dict)]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []


def update_id(update: dict[str, Any]) -> int | None:
    try:
        return int(update.get("update_id"))
    except (TypeError, ValueError):
        return None


def message_from_update(
    update: dict[str, Any],
    chat_id: str | None,
    *,
    message_keys: tuple[str, ...] = DEFAULT_MESSAGE_KEYS,
) -> dict[str, Any] | None:
    for key in message_keys:
        raw = update.get(key)
        if not isinstance(raw, dict):
            continue
        text = raw.get("text")
        if not isinstance(text, str) or not text.strip():
            return None
        chat = raw.get("chat") if isinstance(raw.get("chat"), dict) else {}
        if chat_id and str(chat.get("id")) != str(chat_id):
            return None
        return {"text": text, "message_id": raw.get("message_id")}
    return None


def merge_by_update_id(existing: Any, new_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[int, dict[str, Any]] = {}
    if isinstance(existing, list):
        for item in existing:
            if not isinstance(item, dict) or "update_id" not in item:
                continue
            try:
                merged[int(item["update_id"])] = item
            except (TypeError, ValueError):
                continue
    for item in new_items:
        merged[int(item["update_id"])] = item
    return [merged[key] for key in sorted(merged)]


def sanitize_text(text: str, max_length: int = 300) -> str:
    sanitized = sanitize_diagnostics({"message": text}).get("message", "")
    compact = " ".join(str(sanitized).split())
    return truncate(compact, max_length)


def load_env_with_file(env_file: Path | None) -> dict[str, str]:
    env = dict(os.environ)
    if env_file and env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            normalized_key = key.strip()
            normalized_value = value.strip().strip('"').strip("'")
            if not env.get(normalized_key):
                env[normalized_key] = normalized_value
    return env


def fetch_telegram_updates(
    *,
    token: str,
    offset: int | None,
    limit: int,
    poll_timeout: int,
    timeout_seconds: int,
) -> dict[str, Any]:
    params: dict[str, Any] = {"limit": limit, "timeout": poll_timeout}
    if offset is not None:
        params["offset"] = offset
    body = parse.urlencode(params).encode("utf-8")
    req = request.Request(f"https://api.telegram.org/bot{token}/getUpdates", data=body, method="POST")
    with request.urlopen(req, timeout=timeout_seconds) as response:  # pragma: no cover - live network path
        payload = json.loads(response.read().decode("utf-8"))
    return {
        "generated_at": generated_at(),
        "source": "telegram_getUpdates",
        "updates": payload.get("result", []) if isinstance(payload, dict) else [],
    }


def truncate(text: str, max_length: int) -> str:
    return text if len(text) <= max_length else text[: max_length - 1].rstrip() + "..."


def generated_at() -> str:
    from datetime import UTC, datetime

    return datetime.now(tz=UTC).replace(microsecond=0).isoformat()
