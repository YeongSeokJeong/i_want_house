# Task Plan

## Task Metadata
- Task Name: Persistence state repositories
- Task ID: persistence-state-repositories
- Task Branch: task/persistence-state-repositories
- Task Worktree: D:\git\i_want_house\.worktrees\persistence-state-repositories
- Plan Version: v1
- Last Updated: 2026-06-20

## Planning Assumptions
- The refactor must preserve existing JSON file names, payload shapes, and validate-before-replace writes.
- Public compatibility wrappers in `jeonseloop.persistence` remain available for existing callers and tests.
- No Telegram sends or `--send` execution are needed for this task.

## Related Backlog Items
| Backlog ID | Route | Status | Relationship |
|------------|-------|--------|--------------|
| BL-20260618-007 | source-code | Doing | Parent task item for this orchestration |

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | Split state repository boundaries | Move health, history, feed, criteria, listings, and notified-state persistence behind focused repository classes while keeping `LoopStateRepository` as the orchestration facade. | None | Medium | Backend Agent |

## Feature Detail
### F-001 Split state repository boundaries
- Scope:
  - Add `src/jeonseloop/state_repositories.py` with focused repository classes and shared atomic JSON store usage.
  - Refactor `src/jeonseloop/persistence.py` so `LoopStateRepository` delegates storage responsibilities without changing caller contracts.
  - Update focused tests to cover the delegated repositories and existing loop behavior.
- Acceptance Criteria:
  - [ ] Successful cycle still writes listing snapshots, per-complex history, notified state, health, urgent feed, criteria log, and criteria suggestions with existing JSON/Markdown shapes.
  - [ ] Failure health still preserves failure streak behavior and sanitized collector diagnostics.
  - [ ] `load_previous_average_prices`, module-level wrappers, and `LoopCoordinator` integration remain compatible.
  - [ ] Focused and broad unit tests pass without using `--send`.
- Out of Scope:
  - Changing public state file paths or environment variable contracts.
  - Adding new runtime persistence backends.
  - Rewriting dashboard or notification behavior.

## Execution Order
1. F-001

## Revision Log
| Version | Date | Changed Feature IDs | Changed Backlog IDs | Why Revised | Author |
|---------|------|---------------------|---------------------|-------------|--------|
| v1 | 2026-06-20 | F-001 | BL-20260618-007 | Initial planning baseline | Codex |

