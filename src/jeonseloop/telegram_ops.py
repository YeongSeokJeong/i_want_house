from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
import re
from typing import Any

from .persistence import JsonStateStore
from .telegram_updates import (
    extract_updates as _extract_updates,
    load_env_with_file as _env_with_file,
    merge_by_update_id as _merge_by_update_id,
    message_from_update as _message_from_update,
    sanitize_text as _sanitize_text,
    update_id as _update_id,
)


DEFAULT_UPDATES_PATH = Path("data/state/telegram-updates.json")
DEFAULT_STATE_PATH = Path("data/state/telegram-ops.json")


@dataclass(frozen=True)
class OpsOptions:
    updates_path: Path = DEFAULT_UPDATES_PATH
    state_path: Path = DEFAULT_STATE_PATH
    today: str | None = None
    chat_id: str | None = None
    dry_run: bool = False
    env_file: Path | None = Path(".env")


def run_ops_intake(options: OpsOptions) -> dict[str, Any]:
    store = JsonStateStore()
    state = _load_state(store, options.state_path)
    updates = _extract_updates(store.load_json(options.updates_path, {"updates": []}))
    processed_ids = {int(value) for value in state.get("processed_update_ids", [])}
    today = options.today or datetime.now(tz=UTC).date().isoformat()
    next_id = _next_proposal_number(state, today)

    proposals: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    skipped = 0
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
        parsed = parse_ops_request(message["text"])
        if parsed["status"] == "proposed":
            parsed["proposal_id"] = f"OPS-{today.replace('-', '')}-{next_id:03d}"
            parsed["update_id"] = update_id
            parsed["message_id"] = message.get("message_id")
            parsed["created_at"] = _now()
            next_id += 1
            proposals.append(parsed)
        else:
            rejected.append(
                {
                    "update_id": update_id,
                    "message_id": message.get("message_id"),
                    "status": parsed["status"],
                    "reason": parsed["reason"],
                    "excerpt": parsed["excerpt"],
                    "operator_note": parsed["operator_note"],
                }
            )
        processed_ids.add(update_id)

    result_state = {
        "generated_at": _now(),
        "processed_update_ids": sorted(processed_ids),
        "last_update_id": max(processed_ids) if processed_ids else None,
        "proposals": _merge_by_update_id(state.get("proposals", []), proposals),
        "rejected": _merge_by_update_id(state.get("rejected", []), rejected),
    }
    result = {
        "status": "success",
        "updates_seen": len(updates),
        "proposal_count": len(proposals),
        "rejected_count": len(rejected),
        "skipped_count": skipped,
        "proposals": proposals,
        "rejected": rejected,
    }
    if not options.dry_run:
        store.atomic_write_json(options.state_path, result_state)
    else:
        result["dry_run"] = True
    return result


def parse_ops_request(text: str) -> dict[str, Any]:
    excerpt = _sanitize_text(text)
    tokens = excerpt.split()
    if len(tokens) < 2 or tokens[0].lower() not in {"/ops", "ops:"}:
        return _not_allowed(excerpt, "missing_ops_prefix")
    command = tokens[1].lower()
    args = tokens[2:]
    if command == "source":
        return _source_kind(args, excerpt)
    if command == "naver-map":
        return _naver_map(args, excerpt)
    if command == "trade-type":
        return _trade_type(args, excerpt)
    if command == "target-price":
        return _target_price(args, excerpt)
    if command == "price-cap":
        return _price_cap(args, excerpt)
    if command == "find-complex":
        return _find_complex(args, excerpt)
    return _not_allowed(excerpt, "unknown_ops_command")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create audited JeonseLoop ops proposals from Telegram updates.")
    parser.add_argument("--updates-path", default=str(DEFAULT_UPDATES_PATH))
    parser.add_argument("--state-path", default=str(DEFAULT_STATE_PATH))
    parser.add_argument("--today")
    parser.add_argument("--chat-id")
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    env = _env_with_file(Path(args.env_file) if args.env_file else None)
    result = run_ops_intake(
        OpsOptions(
            updates_path=Path(args.updates_path),
            state_path=Path(args.state_path),
            today=args.today,
            chat_id=args.chat_id or env.get("TELEGRAM_CHAT_ID"),
            env_file=Path(args.env_file) if args.env_file else None,
            dry_run=args.dry_run,
        )
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "success" else 1


def _source_kind(args: list[str], excerpt: str) -> dict[str, Any]:
    if len(args) != 1:
        return _needs_clarification(excerpt, "source_requires_one_value")
    value = args[0].lower().replace("_", "-")
    if value not in {"naver", "hogangnono", "http-json"}:
        return _not_allowed(excerpt, "unsupported_source_kind")
    return _proposal(
        excerpt,
        "set_source_kind",
        env_changes=[{"name": "JEONSELOOP_LISTING_SOURCE_KIND", "value": value, "sensitive": False}],
        rollback=["Restore the previous JEONSELOOP_LISTING_SOURCE_KIND value from GitHub Variables or local .env."],
    )


def _naver_map(args: list[str], excerpt: str) -> dict[str, Any]:
    if len(args) != 2:
        return _needs_clarification(excerpt, "naver_map_requires_complex_id_and_complex_no")
    complex_id, complex_no = args
    if not _valid_key(complex_id) or not complex_no.isdigit():
        return _not_allowed(excerpt, "invalid_naver_map_arguments")
    return _proposal(
        excerpt,
        "set_naver_complex_map",
        env_changes=[
            {
                "name": "JEONSELOOP_NAVER_COMPLEX_NO_MAP",
                "merge_json": {complex_id: complex_no},
                "sensitive": False,
            }
        ],
        rollback=[f"Remove `{complex_id}` from JEONSELOOP_NAVER_COMPLEX_NO_MAP or restore the previous JSON value."],
        review_notes=[f"Verify Naver complex number `{complex_no}` belongs to `{complex_id}` before applying."],
    )


def _trade_type(args: list[str], excerpt: str) -> dict[str, Any]:
    if len(args) != 1:
        return _needs_clarification(excerpt, "trade_type_requires_sale_or_jeonse")
    value = args[0].lower()
    mapping = {
        "sale": ("A1", "0"),
        "매매": ("A1", "0"),
        "jeonse": ("B1", None),
        "전세": ("B1", None),
    }
    if value not in mapping:
        return _not_allowed(excerpt, "unsupported_trade_type")
    naver_value, hogangnono_value = mapping[value]
    env_changes = [{"name": "JEONSELOOP_NAVER_TRADE_TYPE", "value": naver_value, "sensitive": False}]
    review_notes = ["Verify source-specific trade type semantics before applying."]
    if hogangnono_value is not None:
        env_changes.append({"name": "JEONSELOOP_HOGANGNONO_TRADE_TYPES", "value": hogangnono_value, "sensitive": False})
    else:
        review_notes.append("Hogangnono jeonse tradeTypes value is not encoded by this proposal and needs manual confirmation.")
    return _proposal(
        excerpt,
        "set_trade_type",
        env_changes=env_changes,
        rollback=["Restore previous trade type variables from GitHub Variables or local .env."],
        review_notes=review_notes,
    )


def _target_price(args: list[str], excerpt: str) -> dict[str, Any]:
    if len(args) != 2:
        return _needs_clarification(excerpt, "target_price_requires_complex_id_and_price")
    complex_id, raw_price = args
    price = _positive_int(raw_price)
    if not _valid_key(complex_id) or price is None:
        return _not_allowed(excerpt, "invalid_target_price_arguments")
    return _proposal(
        excerpt,
        "set_watchlist_target_price",
        file_changes=[
            {
                "path": "config/watchlist.yaml",
                "selector": {"complex_id": complex_id},
                "field": "target_price_krw",
                "value": price,
            }
        ],
        rollback=[f"Restore `{complex_id}` target_price_krw in config/watchlist.yaml to its previous value."],
    )


def _price_cap(args: list[str], excerpt: str) -> dict[str, Any]:
    if len(args) != 1:
        return _needs_clarification(excerpt, "price_cap_requires_price")
    price = _positive_int(args[0])
    if price is None:
        return _not_allowed(excerpt, "invalid_price_cap")
    return _proposal(
        excerpt,
        "set_collection_price_cap",
        follow_up_required=[
            {
                "reason": "No current env contract exists for collection price cap.",
                "suggested_env": "JEONSELOOP_NAVER_PRICE_MAX_KRW",
                "value": price,
            }
        ],
        rollback=["Do not apply until a source config contract and tests exist."],
        review_notes=["This is a proposal for a follow-up implementation, not an immediately applicable env change."],
    )


def _find_complex(args: list[str], excerpt: str) -> dict[str, Any]:
    if len(args) < 2:
        return _needs_clarification(excerpt, "find_complex_requires_complex_id_and_name")
    complex_id = args[0]
    name = " ".join(args[1:])
    if not _valid_key(complex_id):
        return _not_allowed(excerpt, "invalid_complex_id")
    query = f"{name} 네이버부동산 단지번호"
    return _proposal(
        excerpt,
        "research_complex_identifier",
        research_tasks=[
            {
                "complex_id": complex_id,
                "name": name,
                "queries": [
                    query,
                    f"{name} KB부동산 단지",
                    f"{name} 호갱노노",
                ],
                "expected_outputs": [
                    "JEONSELOOP_NAVER_COMPLEX_NO_MAP candidate",
                    "Hogangnono apt hash candidate",
                ],
            }
        ],
        rollback=["No config value is changed by research proposals."],
        review_notes=["Verify identifiers against live portal pages before applying mappings."],
    )


def _proposal(
    excerpt: str,
    intent: str,
    *,
    env_changes: list[dict[str, Any]] | None = None,
    file_changes: list[dict[str, Any]] | None = None,
    follow_up_required: list[dict[str, Any]] | None = None,
    research_tasks: list[dict[str, Any]] | None = None,
    rollback: list[str] | None = None,
    review_notes: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "status": "proposed",
        "intent": intent,
        "approval_required": True,
        "auto_applied": False,
        "excerpt": excerpt,
        "env_changes": env_changes or [],
        "file_changes": file_changes or [],
        "follow_up_required": follow_up_required or [],
        "research_tasks": research_tasks or [],
        "rollback": rollback or [],
        "review_notes": review_notes or [],
    }


def _needs_clarification(excerpt: str, reason: str) -> dict[str, Any]:
    return {
        "status": "needs_clarification",
        "reason": reason,
        "excerpt": excerpt,
        "operator_note": "Use an allowlisted format such as `/ops source naver` or `/ops naver-map <complex_id> <complex_no>`.",
    }


def _not_allowed(excerpt: str, reason: str) -> dict[str, Any]:
    return {
        "status": "rejected",
        "reason": reason,
        "excerpt": excerpt,
        "operator_note": "The request was not converted into an operational proposal.",
    }


def _load_state(store: JsonStateStore, path: Path) -> dict[str, Any]:
    state = store.load_json(path, {"processed_update_ids": [], "proposals": [], "rejected": []})
    if not isinstance(state, dict):
        return {"processed_update_ids": [], "proposals": [], "rejected": []}
    state.setdefault("processed_update_ids", [])
    state.setdefault("proposals", [])
    state.setdefault("rejected", [])
    return state


def _next_proposal_number(state: dict[str, Any], today: str) -> int:
    prefix = f"OPS-{today.replace('-', '')}-"
    max_seen = 0
    for proposal in state.get("proposals", []):
        if not isinstance(proposal, dict):
            continue
        proposal_id = str(proposal.get("proposal_id", ""))
        if proposal_id.startswith(prefix):
            try:
                max_seen = max(max_seen, int(proposal_id.rsplit("-", 1)[1]))
            except (IndexError, ValueError):
                continue
    return max_seen + 1


def _valid_key(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{1,80}", value))


def _positive_int(value: str) -> int | None:
    try:
        parsed = int(value.replace(",", ""))
    except ValueError:
        return None
    return parsed if parsed > 0 else None


def _truncate(text: str, max_length: int) -> str:
    return text if len(text) <= max_length else text[: max_length - 1].rstrip() + "..."


def _now() -> str:
    return datetime.now(tz=UTC).replace(microsecond=0).isoformat()


if __name__ == "__main__":
    raise SystemExit(main())
