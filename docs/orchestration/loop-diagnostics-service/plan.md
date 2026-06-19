# Task Plan

## Task Metadata
- Task Name: Loop diagnostics service
- Task ID: loop-diagnostics-service
- Task Branch: task/loop-diagnostics-service-stacked
- Task Worktree: D:\git\i_want_house_loop_diagnostics_service
- Plan Version: v1
- Last Updated: 2026-06-19

## Planning Assumptions
- BL-20260618-003 is the selected source-code backlog item for this run.
- The task should preserve the current `health.json` and `collector-diagnostics.json` contracts.
- The implementation should only move diagnostic projection responsibility out of `LoopCoordinator`; persistence behavior and environment variable contracts stay unchanged.
- This branch is stacked on `task/listing-source-adapters-closeout` because `origin/main` still has BL-20260618-002 as `Doing`, while closeout PR #15 records that prerequisite as complete.

## Related Wiki Evidence
- `docs/wiki/domains/jeonseloop/overview.md` documents `LoopCoordinator`, health state, collector diagnostics, and Hogangnono listing diagnostics.
- `docs/orchestration/hogangnono-zero-listing-diagnostics/` defines the successful `listing_diagnostics` contract that must remain compatible.
- `docs/orchestration/hogangnono-missing-map-diagnostics/` defines collector failure diagnostics for missing Hogangnono mappings.
- Wiki gap: after implementation, update the JeonseLoop architecture note only if the service boundary is durable enough to document.

## Related Backlog Items
| Backlog ID | Route | Status | Relationship |
|------------|-------|--------|--------------|
| BL-20260618-003 | source-code | Doing | Parent task item for this orchestration |

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | Diagnostic projection service | Move runtime and listing diagnostic projection from `LoopCoordinator` into a dedicated service module | None | Medium | Backend Agent |

## Feature Detail
### F-001 Diagnostic projection service
- Scope:
  - Add a dedicated diagnostics module/service for collector failure diagnostics, listing diagnostics, source kind inference, and Hogangnono mapping diagnostic projection.
  - Make `LoopCoordinator` call the diagnostics service instead of owning diagnostic helper functions.
  - Keep existing health and collector diagnostics JSON shapes compatible.
  - Add focused tests for the diagnostics service boundary and run reliability regression tests.
- Acceptance Criteria:
  - [ ] `src/jeonseloop/diagnostics.py` owns diagnostic projection logic.
  - [ ] `LoopCoordinator` no longer contains source-kind, Hogangnono mapping, collector diagnostics, or listing diagnostics helper functions.
  - [ ] Existing runtime failure and successful listing diagnostics tests keep passing.
  - [ ] No Telegram alerts are sent and no `--send` path is used.
- Out of Scope:
  - Changing public JSON contracts.
  - Changing environment variable names or source adapter behavior.
  - Refactoring persistence repositories.

## Execution Order
1. F-001

## Revision Log
| Version | Date | Changed Feature IDs | Changed Backlog IDs | Why Revised | Author |
|---------|------|---------------------|---------------------|-------------|--------|
| v1 | 2026-06-19 | F-001 | BL-20260618-003 | Initial planning baseline from selected backlog item | Codex |
