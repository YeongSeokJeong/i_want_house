from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
import re
import sys
from typing import Any

from .backlog_store import BacklogItem, BacklogStore
from .persistence import JsonStateStore
from .telegram_updates import (
    extract_updates as _extract_updates,
    fetch_telegram_updates,
    load_env_with_file as _env_with_file,
    merge_by_update_id as _merge_by_update_id,
    message_from_update as _shared_message_from_update,
    sanitize_text as _sanitize_text,
    update_id as _update_id,
)


DEFAULT_UPDATES_PATH = Path("data/state/telegram-updates.json")
DEFAULT_STATE_PATH = Path("data/state/telegram-intake.json")
DEFAULT_BACKLOG_PATH = Path("docs/backlog.md")


@dataclass(frozen=True)
class IntakeOptions:
    updates_path: Path = DEFAULT_UPDATES_PATH
    state_path: Path = DEFAULT_STATE_PATH
    backlog_path: Path = DEFAULT_BACKLOG_PATH
    today: str | None = None
    chat_id: str | None = None
    fetch_updates: bool = False
    limit: int = 20
    poll_timeout: int = 0
    timeout_seconds: int = 15
    env_file: Path | None = Path(".env")
    dry_run: bool = False
    write_fetched_updates: bool = False


def run_intake(options: IntakeOptions) -> dict[str, Any]:
    store = JsonStateStore()
    state = _load_state(store, options.state_path)
    updates_payload: dict[str, Any] | None = None
    if options.fetch_updates:
        updates_payload = _fetch_updates(options, state)
        if updates_payload.get("status") == "skipped":
            return updates_payload
        if not options.dry_run or options.write_fetched_updates:
            store.atomic_write_json(options.updates_path, updates_payload)
    updates = _extract_updates(updates_payload if updates_payload is not None else store.load_json(options.updates_path, {"updates": []}))
    processed_ids = {int(value) for value in state.get("processed_update_ids", [])}
    today = options.today or datetime.now(tz=UTC).date().isoformat()

    accepted: list[dict[str, Any]] = []
    clarification_needed: list[dict[str, Any]] = []
    skipped = 0
    backlog_store = BacklogStore(options.backlog_path)
    next_id = backlog_store.next_sequence(today)
    backlog_items: list[BacklogItem] = []

    for update in updates:
        update_id = _update_id(update)
        if update_id is None or update_id in processed_ids:
            skipped += 1
            continue
        message = _message_from_update(update, options.chat_id)
        if message is None:
            processed_ids.add(update_id)
            skipped += 1
            continue
        if _is_ops_message(message["text"]):
            processed_ids.add(update_id)
            skipped += 1
            continue
        triage = triage_message(message["text"])
        if triage["status"] == "accepted":
            backlog_id = f"BL-{today.replace('-', '')}-{next_id:03d}"
            next_id += 1
            context = f"Telegram update_id={update_id} \uc790\ub3d9 \uc218\uc9d1. \uc6d0\ubb38 \uc694\uc57d: {triage['excerpt']}"
            backlog_items.append(
                BacklogItem(
                    backlog_id=backlog_id,
                    status="Todo",
                    route=triage["route"],
                    task=triage["task"],
                    context=context,
                    created=today,
                    artifact=triage["artifact"],
                )
            )
            accepted.append(
                {
                    "update_id": update_id,
                    "message_id": message.get("message_id"),
                    "backlog_id": backlog_id,
                    "route": triage["route"],
                    "task": triage["task"],
                    "excerpt": triage["excerpt"],
                }
            )
        else:
            clarification_needed.append(
                {
                    "update_id": update_id,
                    "message_id": message.get("message_id"),
                    "status": "clarification_needed",
                    "reason": triage["reason"],
                    "excerpt": triage["excerpt"],
                    "draft_question": triage["draft_question"],
                }
            )
        processed_ids.add(update_id)

    result_state = {
        "generated_at": _now(),
        "processed_update_ids": sorted(processed_ids),
        "last_update_id": max(processed_ids) if processed_ids else None,
        "accepted": _merge_by_update_id(state.get("accepted", []), accepted),
        "clarification_needed": _merge_by_update_id(state.get("clarification_needed", []), clarification_needed),
    }
    result = {
        "status": "success",
        "updates_seen": len(updates),
        "accepted_count": len(accepted),
        "clarification_needed_count": len(clarification_needed),
        "skipped_count": skipped,
        "accepted": accepted,
        "clarification_needed": clarification_needed,
    }

    if not options.dry_run:
        if backlog_items:
            backlog_store.append_items(backlog_items)
        store.atomic_write_json(options.state_path, result_state)
    else:
        result["dry_run"] = True
    return result


def triage_message(text: str) -> dict[str, Any]:
    excerpt = _sanitize_text(text)
    normalized = excerpt.lower()
    action_tokens = (
        "해줘",
        "추가",
        "수정",
        "개선",
        "구현",
        "만들",
        "작성",
        "정리",
        "확인",
        "분석",
        "보여",
        "전환",
        "변경",
        "자동",
        "연동",
        "검증",
        "필요",
        "싶",
        "add",
        "implement",
        "fix",
        "create",
        "update",
        "show",
        "check",
        "analyze",
    )
    object_tokens = (
        "백로그",
        "대시보드",
        "텔레그램",
        "telegram",
        "호갱노노",
        "네이버",
        "매물",
        "단지",
        "알림",
        "workflow",
        "actions",
        "config",
        "watchlist",
        "수집",
        "기준",
        "문서",
        "테스트",
        "mcp",
        "agent",
        "github",
    )
    has_action = any(token in normalized for token in action_tokens)
    has_object = any(token in normalized for token in object_tokens)
    has_enough_detail = len(re.sub(r"\s+", "", excerpt)) >= 12
    if has_action and has_object and has_enough_detail:
        route = _classify_route(normalized)
        return {
            "status": "accepted",
            "route": route,
            "task": _task_from_excerpt(excerpt),
            "context": f"Telegram request intake: {_truncate(excerpt, 180)}",
            "artifact": _artifact_for_route(route),
            "excerpt": excerpt,
        }
    return {
        "status": "clarification_needed",
        "reason": "insufficient_action_or_target",
        "excerpt": excerpt,
        "draft_question": "요청하려는 대상, 원하는 변경, 완료 기준을 한 문장으로 더 구체화해 주세요.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Triage saved Telegram updates into JeonseLoop backlog items.")
    parser.add_argument("--updates-path", default=str(DEFAULT_UPDATES_PATH))
    parser.add_argument("--state-path", default=str(DEFAULT_STATE_PATH))
    parser.add_argument("--backlog-path", default=str(DEFAULT_BACKLOG_PATH))
    parser.add_argument("--today", help="override BL-* date for deterministic tests")
    parser.add_argument("--chat-id", help="only process messages from this Telegram chat id")
    parser.add_argument("--fetch-updates", action="store_true", help="read getUpdates before triage; never sends messages")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--poll-timeout", type=int, default=0)
    parser.add_argument("--timeout-seconds", type=int, default=15)
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--dry-run", action="store_true", help="print result without writing backlog or intake state")
    parser.add_argument("--write-fetched-updates", action="store_true", help="write fetched updates even in dry-run, for ephemeral workflow sharing")
    args = parser.parse_args(argv)
    env = _env_with_file(Path(args.env_file) if args.env_file else None)
    options = IntakeOptions(
        updates_path=Path(args.updates_path),
        state_path=Path(args.state_path),
        backlog_path=Path(args.backlog_path),
        today=args.today,
        chat_id=args.chat_id or env.get("TELEGRAM_CHAT_ID"),
        fetch_updates=args.fetch_updates,
        limit=args.limit,
        poll_timeout=args.poll_timeout,
        timeout_seconds=args.timeout_seconds,
        env_file=Path(args.env_file) if args.env_file else None,
        dry_run=args.dry_run,
        write_fetched_updates=args.write_fetched_updates,
    )
    result = run_intake(options)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {"success", "skipped"} else 1


def _fetch_updates(options: IntakeOptions, state: dict[str, Any]) -> dict[str, Any]:
    env = _env_with_file(options.env_file)
    token = env.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        return {"status": "skipped", "reason": "TELEGRAM_BOT_TOKEN is not configured"}
    last_update_id = state.get("last_update_id")
    offset = int(last_update_id) + 1 if last_update_id is not None else None
    return fetch_telegram_updates(
        token=token,
        offset=offset,
        limit=options.limit,
        poll_timeout=options.poll_timeout,
        timeout_seconds=options.timeout_seconds,
    )


def _load_state(store: JsonStateStore, path: Path) -> dict[str, Any]:
    state = store.load_json(path, {"processed_update_ids": [], "accepted": [], "clarification_needed": []})
    if not isinstance(state, dict):
        return {"processed_update_ids": [], "accepted": [], "clarification_needed": []}
    state.setdefault("processed_update_ids", [])
    state.setdefault("accepted", [])
    state.setdefault("clarification_needed", [])
    return state


def _message_from_update(update: dict[str, Any], chat_id: str | None) -> dict[str, Any] | None:
    return _shared_message_from_update(update, chat_id, message_keys=("message", "edited_message", "channel_post"))


def _classify_route(normalized: str) -> str:
    if any(token in normalized for token in ("wiki", "위키")):
        return "wiki-domain"
    if any(token in normalized for token in ("readme", "문서", "가이드", "체크리스트")):
        return "operator-doc"
    if any(token in normalized for token in ("mcp", "agent", "skill", "에이전트", "스킬")):
        return "skill-agent"
    if "backlog" in normalized or "백로그" in normalized:
        return "backlog"
    return "source-code"


def _is_ops_message(text: str) -> bool:
    stripped = text.strip().lower()
    return stripped.startswith("/ops ") or stripped.startswith("ops:")


def _artifact_for_route(route: str) -> str:
    return {
        "source-code": "`src/`, `tests/`, `docs/orchestration/`",
        "wiki-domain": "`docs/wiki/`",
        "wiki-decision": "`docs/wiki/decisions/`",
        "wiki-rule": "`docs/wiki/rules/common/`",
        "wiki-workflow": "`docs/wiki/rules/workflow/`",
        "operator-doc": "`docs/`",
        "skill-agent": "`.codex/`",
        "spec": "`docs/`",
        "backlog": "`docs/backlog.md`",
    }.get(route, "`docs/`")


def _task_from_excerpt(excerpt: str) -> str:
    compact = _truncate(excerpt, 90)
    return f"Telegram 요청 처리: {compact}"


def _truncate(text: str, max_length: int) -> str:
    return text if len(text) <= max_length else text[: max_length - 1].rstrip() + "..."


def _now() -> str:
    return datetime.now(tz=UTC).replace(microsecond=0).isoformat()


if __name__ == "__main__":
    raise SystemExit(main())
