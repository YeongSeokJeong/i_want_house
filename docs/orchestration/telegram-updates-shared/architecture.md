# Architecture Review

## Task Context
- Task Name: Telegram updates shared module
- Task ID: telegram-updates-shared
- Last Updated: 2026-06-19

## System Context
- Current Stack: Python standard library CLI modules with `unittest` tests.
- Existing Patterns: Small service modules, dataclass options objects, JSON state through `JsonStateStore`.
- Integration Points: Telegram Bot API `getUpdates`, local `.env`, `data/state/telegram-updates.json`, intake state JSON files, `docs/backlog.md`.

## Feature Decomposition Map
| Feature ID | Feature | Description | Depends On | Complexity | Risk |
|------------|---------|-------------|------------|------------|------|
| F-001 | Shared Telegram update utilities | Extract reusable update parsing and utility helpers used by backlog and ops intakes | None | Medium | Medium |

## Dependency Map
- `telegram_backlog_intake.py` -> `telegram_updates.py` for fetch, env, update parsing, sanitizing, and merge helpers.
- `telegram_ops.py` -> `telegram_updates.py` for env, update parsing, sanitizing, and merge helpers.
- `telegram_updates.py` -> `persistence.sanitize_diagnostics` for redaction consistency.

## Technical Decisions
- Decision: Keep domain-specific triage and proposal parsing in their existing modules.
  - Rationale: Backlog intake and ops intake have different outputs and approval boundaries.
  - Trade-offs: Some loop shape remains similar, but shared low-level Telegram handling moves to one place.
- Decision: Parameterize message keys in `message_from_update`.
  - Rationale: Backlog intake accepts `message`, `edited_message`, and `channel_post`, while ops intake only accepted `message`.
  - Trade-offs: Slightly broader helper API, but no behavior regression.

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| Accidental behavior change in processed update tracking | Medium | Keep merge helper deterministic and run existing duplicate tests | Codex |
| Live Telegram fetch behavior changes | Medium | Preserve public `fetch_telegram_updates` import in backlog intake and test via patching | Codex |
