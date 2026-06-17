# Task Plan

## Task Metadata
- Task Name: Dashboard pre urgent grades
- Task ID: dashboard-pre-urgent-grades
- Task Branch: task/dashboard-pre-urgent-grades
- Task Worktree: D:\git\i_want_house
- Plan Version: v1
- Last Updated: 2026-06-17

## Planning Assumptions
- The task is driven by `BL-20260617-006`.
- The previous tasks added dashboard urgent-line calculation and decision reason summaries.
- A dashboard projection is sufficient because urgent-feed items already include candidate price and complex ID, and the dashboard can combine them with watchlist metadata and latest history.

## Requirement Brief
- In scope:
  - Classify urgent-feed items into `급매`, `근접`, `관심`, `멀리 있음`, or `기준 부족` by distance from the dashboard urgent line.
  - Separate selected-complex feed rendering into alert-planned items and observation items.
  - Add static tests for grade labels/helper functions and section labels.
- Out of scope:
  - Changing analyzer approval rules.
  - Changing Telegram alert behavior.
  - Persisting new feed fields.

## Related Wiki Discovery
| Document | Relevance | Gap |
|----------|-----------|-----|
| `docs/wiki/domains/jeonseloop/overview.md` | Documents dashboard urgent-line and urgent-feed interpretation. | Needs a closeout note that feed items are displayed with pre-urgent grades. |

## Related Backlog Items
| Backlog ID | Route | Status | Relationship |
|------------|-------|--------|--------------|
| BL-20260617-006 | source-code | Doing | Parent task item for this orchestration |

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | Pre urgent grades | Display feed candidates by urgency grade and separate alerts from observations | None | Medium | Frontend/Backend Agent |

## Feature Detail
### F-001 Pre urgent grades
- Scope:
  - Add dashboard helpers to compute grade and urgent-line distance for feed items.
  - Render grade badges and distance text on feed items.
  - Split selected-complex feed into `알림 대상` and `관찰 대상`.
  - Add static tests for grade labels/helper functions.
- Acceptance Criteria:
  - [x] Feed UI includes `급매`, `근접`, `관심`, and `멀리 있음` grade concepts.
  - [x] Alert-planned items are visually separated from non-alert observation items.
  - [x] Existing feed and dashboard behavior remain intact.
  - [x] `node --check assets/dashboard.js` and full unittest suite pass.
- Out of Scope:
  - Persisted grade contract.

## Execution Order
1. F-001

## Revision Log
| Version | Date | Changed Feature IDs | Changed Backlog IDs | Why Revised | Author |
|---------|------|---------------------|---------------------|-------------|--------|
| v1 | 2026-06-17 | F-001 | BL-20260617-006 | Initial planning baseline from backlog item | Codex |
