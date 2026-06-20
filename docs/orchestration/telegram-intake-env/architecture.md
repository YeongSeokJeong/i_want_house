# Architecture Review

## Task Context
- Task Name: Telegram intake empty env handling
- Task ID: telegram-intake-env
- Last Updated: 2026-06-20

## System Context
- Current Stack: Python standard library CLI modules with `unittest`; GitHub Actions for manual dry-run checks.
- Existing Patterns: Telegram update parsing and `.env` loading are centralized in `src/jeonseloop/telegram_updates.py`; backlog intake and ops intake reuse the shared module.
- Integration Points: Local `.env`, process environment, Telegram Bot API `getUpdates`, `docs/backlog.md`, JSON state files under `data/state/`.

## Feature Decomposition Map
| Feature ID | Feature | Description | Depends On | Complexity | Risk |
|------------|---------|-------------|------------|------------|------|
| F-001 | Empty env fallback | Normalize `.env` fallback behavior and cover intake fetch regression | None | Low | Low |

## Dependency Map
- `telegram_backlog_intake.run_intake()` -> `telegram_updates.load_env_with_file()` for token/chat configuration.
- `telegram_ops` -> `telegram_updates.load_env_with_file()` for shared Telegram environment handling.
- Tests -> temporary `.env` files to avoid real secrets and live network sends.

## Technical Decisions
- Decision: Update the shared environment loader rather than intake-specific code.
  - Rationale: The bug is a policy mismatch in shared env merging, and fixing it centrally keeps backlog intake and ops behavior consistent.
  - Trade-offs: Empty environment values lose their ability to intentionally mask `.env` values, but this repo treats empty required secrets as not configured elsewhere.

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| Shared helper behavior affects ops intake unexpectedly | Low | Preserve non-empty process env precedence and add helper-level regression tests | Backend |
| Accidental live Telegram access during tests | Low | Keep tests patched/mocked and do not use `--send` | QA |
