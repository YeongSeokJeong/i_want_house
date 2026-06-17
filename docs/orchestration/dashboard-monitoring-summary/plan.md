# Task Plan

## Task Metadata
- Task Name: Dashboard monitoring summary
- Task ID: dashboard-monitoring-summary
- Task Branch: task/dashboard-monitoring-summary
- Task Worktree: D:\git\i_want_house
- Plan Version: v1
- Last Updated: 2026-06-17

## Planning Assumptions
- The task is driven by `BL-20260617-003`, the next open source-code backlog item after zero-listing diagnostics.
- The dashboard remains a static HTML/CSS/JavaScript app with no build step.
- The first-screen summary can be derived from existing committed JSON state plus watchlist metadata embedded in `assets/dashboard.js`; deeper criterion math refinements remain available for `BL-20260617-004`.

## Requirement Brief
- In scope:
  - Rework the dashboard first screen so the primary signal is per-complex monitoring status rather than recent urgent feed items.
  - Show each monitored complex with area, target price, latest minimum listing price, recent trade baseline, urgent line, gap ratio, and status.
  - Keep recent urgent candidates visible as a secondary section.
  - Cover the behavior with static dashboard tests and update orchestration/handoff docs.
- Out of scope:
  - New backend API or dynamic server.
  - Telegram message changes.
  - Full criterion explanation and remaining-to-urgent-line detail tracked by `BL-20260617-004`.

## Related Wiki Discovery
| Document | Relevance | Gap |
|----------|-----------|-----|
| `docs/wiki/domains/jeonseloop/overview.md` | Defines dashboard JSON sources and health/history interpretation. | Should record the monitoring-summary interpretation after closeout. |
| `docs/wiki/rules/workflow/loop-engineering-routing.md` | Separates product-loop implementation from external state. | No structural change needed. |
| `docs/wiki/rules/workflow/development-automation-loop.md` | Defines repo-verifiable QA expectations. | No structural change needed. |

## Related Backlog Items
| Backlog ID | Route | Status | Relationship |
|------------|-------|--------|--------------|
| BL-20260617-003 | source-code | Doing | Parent task item for this orchestration |

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | Monitoring summary data and layout | Add the first-screen per-complex monitoring summary table/cards from existing dashboard state | None | Medium | Frontend/Backend Agent |

## Feature Detail
### F-001 Monitoring summary data and layout
- Scope:
  - Add a primary dashboard section for per-complex monitoring status.
  - Compute latest minimum listing price, recent trade baseline, urgent line, gap ratio, and status from `data/history/*.json`, `health.latest.listing_diagnostics`, and watchlist metadata.
  - Keep urgent feed as a lower secondary section.
  - Add/adjust static tests for the new first-screen contract.
- Acceptance Criteria:
  - [x] Dashboard HTML places `단지별 감시 상태` before recent urgent candidate feed.
  - [x] Each complex row/card can show complex name, area, target price, latest minimum listing price, recent trade baseline, urgent line, gap ratio, and status.
  - [x] Zero-listing complexes render as collected/no-listing rather than simply empty feed.
  - [x] Existing run history, chart, diagnostics, and feed behavior still work.
  - [x] `node --check assets/dashboard.js` and full unittest suite pass.
- Out of Scope:
  - Persisting a new backend projection file.

## Execution Order
1. F-001

## Revision Log
| Version | Date | Changed Feature IDs | Changed Backlog IDs | Why Revised | Author |
|---------|------|---------------------|---------------------|-------------|--------|
| v1 | 2026-06-17 | F-001 | BL-20260617-003 | Initial planning baseline from backlog item | Codex |
