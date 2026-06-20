# Task Plan

## Task Metadata
- Task Name: Telegram intake empty env handling
- Task ID: telegram-intake-env
- Task Branch: task/telegram-intake-env
- Task Worktree: D:\git\i_want_house\.worktrees\telegram-intake-env
- Plan Version: v1
- Last Updated: 2026-06-20

## Planning Assumptions
- Empty environment variable values should be treated as absent for local `.env` fallback.
- Non-empty process environment values still take precedence over `.env`.
- The task must not send Telegram messages or use `--send`.
- The fix should preserve existing workflow behavior when no token is configured.

## Related Backlog Items
| Backlog ID | Route | Status | Relationship |
|------------|-------|--------|--------------|
| BL-20260618-009 | source-code | Doing | Parent task item for this orchestration |

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | Empty env fallback | Make Telegram intake fetch tests pass when CI exports empty Telegram env vars | None | Low | Backend |

## Feature Detail
### F-001 Empty env fallback
- Scope:
  - Update shared Telegram `.env` loading so empty process values can be filled from `.env`.
  - Add regression coverage for the shared helper and backlog intake fetch path.
  - Verify targeted Telegram tests and the full unittest suite.
- Acceptance Criteria:
  - [x] `load_env_with_file()` preserves non-empty process env precedence.
  - [x] `load_env_with_file()` replaces empty process env values with non-empty `.env` values.
  - [x] `run_intake(fetch_updates=True)` returns normal triage counts when `TELEGRAM_BOT_TOKEN` is empty in the process but present in the supplied `.env`.
  - [x] Focused and full unittest commands pass without sending Telegram messages.
- Out of Scope:
  - Changing workflow schedules, secrets names, public env var contracts, or live Telegram send behavior.

## Execution Order
1. F-001

## Revision Log
| Version | Date | Changed Feature IDs | Changed Backlog IDs | Why Revised | Author |
|---------|------|---------------------|---------------------|-------------|--------|
| v1 | 2026-06-20 | F-001 | BL-20260618-009 | Initial planning baseline | Codex |
