# Task Plan

## Task Metadata
- Task Name: Backlog markdown store extraction
- Task ID: backlog-store
- Task Branch: task/backlog-store
- Task Worktree: D:\git\i_want_house_backlog_store
- Plan Version: v1
- Last Updated: 2026-06-19

## Planning Assumptions
- The backlog file remains a Markdown table at `docs/backlog.md` with the existing column contract.
- The first implementation scope is extraction only; no new backlog lifecycle behavior is introduced.
- Telegram intake behavior, generated rows, duplicate ID validation, and validate-before-replace writes must remain compatible.
- The `.agent.md` workflow references are absent in this repo; matching `.codex/agents/*.toml` instructions were used instead. `feature-implementation` skill is also absent, so implementation follows the repository backend/QA instructions directly.

## Related Backlog Items
| Backlog ID | Route | Status | Relationship |
|------------|-------|--------|--------------|
| BL-20260618-005 | source-code | Done | Parent task item for this orchestration |

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | Backlog markdown store | Extract backlog Markdown table creation, insertion, ID allocation, and validation from Telegram intake into a reusable module | None | Medium | Codex |

## Feature Detail
### F-001 Backlog markdown store
- Scope:
  - Add `src/jeonseloop/backlog_store.py` for backlog row modeling, next ID allocation, row insertion, and table validation.
  - Update `src/jeonseloop/telegram_backlog_intake.py` to delegate backlog table operations to the new module.
  - Add focused tests for the store behavior and keep Telegram intake regression tests passing.
- Acceptance Criteria:
  - [ ] Telegram backlog intake still creates the same accepted backlog rows and state records.
  - [ ] Duplicate backlog IDs are rejected before replacing `docs/backlog.md`.
  - [ ] Missing backlog tables fail clearly.
  - [ ] The new store can be reused independently from Telegram intake.
- Out of Scope:
  - Full manual backlog editing CLI.
  - Changing route classification or triage policy.
  - Changing backlog table columns.

## Execution Order
1. F-001

## Revision Log
| Version | Date | Changed Feature IDs | Changed Backlog IDs | Why Revised | Author |
|---------|------|---------------------|---------------------|-------------|--------|
| v1 | 2026-06-19 | F-001 | BL-20260618-005 | Initial planning baseline | Codex |
