# Task Plan

## Task Metadata
- Task Name: Dashboard data readiness
- Task ID: dashboard-data-readiness
- Task Branch: task/dashboard-data-readiness
- Task Worktree: D:\git\i_want_house
- Plan Version: v1
- Last Updated: 2026-06-17

## Planning Assumptions
- The task is driven by `BL-20260617-008`.
- Recent history, listing diagnostics, and urgent feed data are enough to distinguish collection issues, baseline readiness, and quality blocks in the static dashboard.
- This task should not change collector or analyzer behavior.

## Requirement Brief
- In scope:
  - Add per-complex data quality/readiness dashboard display.
  - Show latest collection time, listing count, consecutive zero-listing streak, trade baseline readiness, and quality block status.
  - Add static tests for labels/helper functions.
- Out of scope:
  - Changing source adapters.
  - Changing quality block policy.
  - Persisting new state files.

## Related Wiki Discovery
| Document | Relevance | Gap |
|----------|-----------|-----|
| `docs/wiki/domains/jeonseloop/overview.md` | Documents dashboard and source diagnostics. | Needs a closeout note that the dashboard shows per-complex data readiness. |

## Related Backlog Items
| Backlog ID | Route | Status | Relationship |
|------------|-------|--------|--------------|
| BL-20260617-008 | source-code | Doing | Parent task item for this orchestration |

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | Data readiness panel | Show per-complex collection and baseline readiness on the dashboard | None | Medium | Frontend/Backend Agent |

## Feature Detail
### F-001 Data readiness panel
- Scope:
  - Add a dashboard panel/table for per-complex readiness.
  - Compute latest collection time, listing count, zero streak, trade baseline state, and quality block state from existing JSON.
  - Add static tests for labels/helper functions.
- Acceptance Criteria:
  - [x] Dashboard distinguishes collection zero-count state from market price state.
  - [x] Dashboard shows trade baseline readiness and quality block state per complex.
  - [x] Existing dashboard behavior remains intact.
  - [x] `node --check assets/dashboard.js` and full unittest suite pass.
- Out of Scope:
  - New persisted state contracts.

## Execution Order
1. F-001

## Revision Log
| Version | Date | Changed Feature IDs | Changed Backlog IDs | Why Revised | Author |
|---------|------|---------------------|---------------------|-------------|--------|
| v1 | 2026-06-17 | F-001 | BL-20260617-008 | Initial planning baseline from backlog item | Codex |
