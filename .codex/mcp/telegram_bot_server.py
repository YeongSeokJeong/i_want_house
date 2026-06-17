from __future__ import annotations

from datetime import UTC, datetime
import json
import os
from pathlib import Path
import sys
from typing import Any
from urllib import parse, request


SERVER_NAME = "jeonseloop-telegram-bot"
API_BASE = "https://api.telegram.org"


def main() -> None:
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            message = json.loads(line)
            response = handle_message(message)
        except Exception as exc:  # pragma: no cover - defensive stdio boundary
            response = _error_response(None, -32603, f"internal error: {type(exc).__name__}: {exc}")
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()


def handle_message(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    request_id = message.get("id")
    if request_id is None:
        return None
    if method == "initialize":
        return _result_response(
            request_id,
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": SERVER_NAME, "version": "0.1.0"},
            },
        )
    if method == "tools/list":
        return _result_response(request_id, {"tools": _tools()})
    if method == "tools/call":
        params = message.get("params") if isinstance(message.get("params"), dict) else {}
        name = params.get("name")
        arguments = params.get("arguments") if isinstance(params.get("arguments"), dict) else {}
        try:
            result = call_tool(str(name), arguments)
        except ToolError as exc:
            return _error_response(request_id, -32000, str(exc))
        return _result_response(
            request_id,
            {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]},
        )
    return _error_response(request_id, -32601, f"unsupported method: {method}")


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "telegram_get_me":
        return _telegram_api("getMe", {}, arguments)
    if name == "telegram_get_updates":
        return _telegram_api("getUpdates", _update_params(arguments), arguments)
    if name == "telegram_get_chat":
        chat_id = _chat_id(arguments)
        return _telegram_api("getChat", {"chat_id": chat_id}, arguments)
    if name == "telegram_save_recent_updates":
        updates = _telegram_api("getUpdates", _update_params(arguments), arguments)
        output_path = Path(str(arguments.get("output_path") or "data/state/telegram-updates.json"))
        payload = {
            "generated_at": _now(),
            "source": "telegram_getUpdates",
            "updates": updates.get("result", []),
        }
        _atomic_write_json(output_path, payload)
        return {"saved_to": str(output_path), "update_count": len(payload["updates"])}
    if name == "telegram_read_saved_updates":
        path = Path(str(arguments.get("path") or "data/state/telegram-updates.json"))
        if not path.exists():
            return {"path": str(path), "updates": [], "message": "saved update file does not exist"}
        return json.loads(path.read_text(encoding="utf-8"))
    if name == "telegram_inspect_send_result":
        return _inspect_send_result(arguments)
    raise ToolError(f"unknown tool: {name}")


def _telegram_api(method: str, params: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    token = _telegram_token(arguments)
    body = parse.urlencode({key: value for key, value in params.items() if value is not None}).encode("utf-8")
    req = request.Request(f"{API_BASE}/bot{token}/{method}", data=body, method="POST")
    try:
        with request.urlopen(req, timeout=int(arguments.get("timeout_seconds") or 15)) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as exc:  # pragma: no cover - live network path
        raise ToolError(f"Telegram Bot API request failed for {method}: {type(exc).__name__}: {exc}") from exc
    return _redact_token(payload, token)


def _update_params(arguments: dict[str, Any]) -> dict[str, Any]:
    params: dict[str, Any] = {
        "offset": arguments.get("offset"),
        "limit": arguments.get("limit", 20),
        "timeout": arguments.get("poll_timeout", 0),
    }
    allowed_updates = arguments.get("allowed_updates")
    if isinstance(allowed_updates, list):
        params["allowed_updates"] = json.dumps(allowed_updates)
    return params


def _inspect_send_result(arguments: dict[str, Any]) -> dict[str, Any]:
    raw = arguments.get("send_result")
    if isinstance(raw, str):
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ToolError("send_result must be valid JSON") from exc
    elif isinstance(raw, dict):
        payload = raw
    else:
        raise ToolError("send_result must be a Telegram sendMessage response object or JSON string")
    result = payload.get("result") if isinstance(payload.get("result"), dict) else {}
    chat = result.get("chat") if isinstance(result.get("chat"), dict) else {}
    return {
        "ok": payload.get("ok") is True,
        "message_id": result.get("message_id"),
        "date": result.get("date"),
        "chat": {
            "id": chat.get("id"),
            "type": chat.get("type"),
            "title": chat.get("title"),
            "username": chat.get("username"),
        },
        "note": "Bot API does not provide arbitrary historical chat scraping; use sendMessage response, getChat, and getUpdates evidence.",
    }


def _telegram_token(arguments: dict[str, Any]) -> str:
    env = _env_with_file(arguments.get("env_file"))
    token = env.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise ToolError("TELEGRAM_BOT_TOKEN is required in environment or env_file")
    return token


def _chat_id(arguments: dict[str, Any]) -> str:
    explicit = str(arguments.get("chat_id") or "").strip()
    if explicit:
        return explicit
    env = _env_with_file(arguments.get("env_file"))
    chat_id = env.get("TELEGRAM_CHAT_ID", "").strip()
    if not chat_id:
        raise ToolError("chat_id argument or TELEGRAM_CHAT_ID is required")
    return chat_id


def _env_with_file(env_file: object) -> dict[str, str]:
    env = dict(os.environ)
    path_text = str(env_file or ".env")
    path = Path(path_text)
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            env.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    return env


def _atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    json.loads(text)
    temp = path.with_name(f".{path.name}.tmp")
    temp.write_text(text, encoding="utf-8")
    os.replace(temp, path)


def _redact_token(payload: Any, token: str) -> Any:
    text = json.dumps(payload, ensure_ascii=False)
    if token:
        text = text.replace(token, "[redacted]")
    return json.loads(text)


def _tools() -> list[dict[str, Any]]:
    return [
        _tool("telegram_get_me", "Return Bot API getMe metadata."),
        _tool("telegram_get_updates", "Return recent Bot API updates. This cannot scrape arbitrary old chat history."),
        _tool("telegram_get_chat", "Return chat metadata for chat_id or TELEGRAM_CHAT_ID."),
        _tool("telegram_save_recent_updates", "Save recent getUpdates output to a local JSON file."),
        _tool("telegram_read_saved_updates", "Read a saved Telegram updates JSON file."),
        _tool("telegram_inspect_send_result", "Summarize a sendMessage response JSON object."),
    ]


def _tool(name: str, description: str) -> dict[str, Any]:
    return {
        "name": name,
        "description": description,
        "inputSchema": {
            "type": "object",
            "properties": {
                "env_file": {"type": "string"},
                "chat_id": {"type": "string"},
                "offset": {"type": "integer"},
                "limit": {"type": "integer"},
                "poll_timeout": {"type": "integer"},
                "timeout_seconds": {"type": "integer"},
                "allowed_updates": {"type": "array", "items": {"type": "string"}},
                "output_path": {"type": "string"},
                "path": {"type": "string"},
                "send_result": {},
            },
        },
    }


def _result_response(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error_response(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def _now() -> str:
    return datetime.now(tz=UTC).replace(microsecond=0).isoformat()


class ToolError(RuntimeError):
    pass


if __name__ == "__main__":
    main()
