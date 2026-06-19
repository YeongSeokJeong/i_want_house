# Task Plan

## Task Metadata
- Task Name: Telegram updates shared module
- Task ID: telegram-updates-shared
- Task Branch: task/telegram-updates-shared
- Task Worktree: D:\git\i_want_house_telegram_updates_shared
- Plan Version: v1
- Last Updated: 2026-06-19

## Planning Assumptions
- The backlog and ops intakes must keep their existing CLI behavior and JSON state contracts.
- This task should only extract shared Telegram update handling; it should not change send behavior, approval gates, or workflow scheduling.
- The current task branch is stacked on `origin/task/loop-diagnostics-service-stacked` to preserve the already completed prerequisite backlog work.

## Related Backlog Items
| Backlog ID | Route | Status | Relationship |
|------------|-------|--------|--------------|
| BL-20260618-004 | source-code | Doing | Parent task item for this orchestration |

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | Shared Telegram update utilities | Extract update parsing, chat filtering, state merging, env loading, sanitizing, and getUpdates fetch into a reusable module | None | Medium | Codex |

## Feature Detail
### F-001 Shared Telegram update utilities
- Scope:
  - Add `src/jeonseloop/telegram_updates.py` for shared update payload parsing and utility behavior.
  - Refactor `telegram_backlog_intake.py` and `telegram_ops.py` to use the shared module.
  - Add focused regression tests for the shared module and run existing intake/ops tests.
- Acceptance Criteria:
  - [ ] Both intake modules use shared helpers for update extraction, update ID parsing, chat filtering, update-id merges, env-file loading, and text sanitizing.
  - [ ] Existing backlog intake and ops intake tests pass without changing no-send behavior.
  - [ ] New tests cover shared helper behavior that both intakes rely on.
  - [ ] No Telegram alerts are sent and `--send` is not introduced.
- Out of Scope:
  - Changing the Telegram workflow schedule or permissions.
  - Applying ops proposals automatically.
  - Fixing separate empty-environment-variable policy work tracked by BL-20260618-009.

## Execution Order
1. F-001

## Revision Log
| Version | Date | Changed Feature IDs | Changed Backlog IDs | Why Revised | Author |
|---------|------|---------------------|---------------------|-------------|--------|
| v1 | 2026-06-19 | F-001 | BL-20260618-004 | Initial planning baseline | Codex |
