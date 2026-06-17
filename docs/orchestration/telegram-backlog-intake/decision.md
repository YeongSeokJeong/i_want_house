# Session Decisions

## Task Context
- Task Name: Telegram backlog intake
- Task ID: telegram-backlog-intake

## Decision Log
| Session | Feature ID | Feature | Decision | Rationale | Impact | Date |
|---------|------------|---------|----------|-----------|--------|------|
| 1 | PLAN | Planning | Use saved updates plus deterministic triage | Bot API history is limited and sendMessage is out of scope | Keeps v1 auditable and safe without Telegram sends | 2026-06-17 |
| 1 | PLAN | Planning | Record current checkout as the task worktree | Current checkout already has related backlog edits | Avoids losing context in a separate worktree | 2026-06-17 |
| 1 | F-001 | Intake triage core | Do not commit raw Telegram update payloads from workflow | Raw Bot API updates can contain personal message metadata | Workflow uses `$RUNNER_TEMP` for raw updates and commits only backlog plus intake state | 2026-06-17 |

## Session 1
- Feature ID: F-001
- Feature: Intake triage core
- Decisions:
  - Treat Telegram messages as backlog suggestions, not commands.
  - Add only sufficiently actionable messages to backlog; record unclear messages as clarification drafts.
  - Keep Telegram reply/sending and operational config changes out of v1.
- Alternatives Considered:
  - Send clarification questions automatically: rejected for v1 because the existing MCP tool intentionally does not expose sendMessage and the repo safety rules gate Telegram sends.
  - Use an LLM for triage: deferred because deterministic rules are easier to test and audit.
- Risks Introduced:
  - Deterministic sufficiency checks may miss some nuanced requests.
- Follow-up Notes:
  - `BL-20260617-011` tracks the separate operational automation scope.
  - Verification passed with `python -m py_compile src/jeonseloop/telegram_backlog_intake.py .codex/mcp/telegram_bot_server.py` and `python -m unittest discover -s tests -v`.
