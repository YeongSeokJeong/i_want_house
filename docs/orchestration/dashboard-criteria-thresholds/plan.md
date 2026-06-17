# Task Plan

## Task Metadata
- Task Name: Dashboard criteria thresholds
- Task ID: dashboard-criteria-thresholds
- Task Branch: task/dashboard-criteria-thresholds
- Task Worktree: D:\git\i_want_house
- Plan Version: v1
- Last Updated: 2026-06-17

## Planning Assumptions
- The task is driven by `BL-20260617-004`.
- The previous monitoring summary task already introduced watchlist target price, latest minimum listing price, trade baseline, urgent line, gap ratio, and status.
- This task should deepen that UI by naming the applied criterion and remaining amount/ratio to the urgent line, without changing analyzer behavior.

## Requirement Brief
- In scope:
  - Show target price ceiling, recent trade baseline, discount urgent line, applied criterion, current minimum listing price, remaining amount, and remaining ratio in dashboard data/UI.
  - Keep the static dashboard no-build architecture.
  - Add static tests covering the new threshold labels and helper calculations.
- Out of scope:
  - Changing candidate approval rules.
  - Telegram alert formatting.
  - Pre-urgent grading, tracked by `BL-20260617-006`.

## Related Wiki Discovery
| Document | Relevance | Gap |
|----------|-----------|-----|
| `docs/wiki/domains/jeonseloop/overview.md` | Documents dashboard interpretation and source state. | Needs a closeout note that dashboard displays applied urgent criterion and remaining amount. |
| `docs/wiki/rules/workflow/loop-engineering-routing.md` | Confirms repo-verifiable dashboard behavior vs external state. | No structural change needed. |

## Related Backlog Items
| Backlog ID | Route | Status | Relationship |
|------------|-------|--------|--------------|
| BL-20260617-004 | source-code | Doing | Parent task item for this orchestration |

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | Criteria threshold details | Make the dashboard show applied urgent criteria and amount/ratio remaining to urgent line | None | Medium | Frontend/Backend Agent |

## Feature Detail
### F-001 Criteria threshold details
- Scope:
  - Extend the monitoring summary table with applied criterion and remaining-to-urgent-line columns.
  - Compute and render target ceiling, recent trade average baseline, discount urgent line, applied criterion, current minimum listing price, remaining amount, and remaining ratio.
  - Add static tests for labels/helper functions and committed state compatibility.
- Acceptance Criteria:
  - [x] Dashboard text includes applied criterion and remaining-to-urgent-line concepts.
  - [x] The UI can distinguish target-price fallback from trade-baseline discount criterion.
  - [x] Current minimum listing price and urgent line remaining amount/ratio are visible.
  - [x] Existing monitoring summary and feed behavior remain intact.
  - [x] `node --check assets/dashboard.js` and full unittest suite pass.
- Out of Scope:
  - Persisting new backend JSON.

## Execution Order
1. F-001

## Revision Log
| Version | Date | Changed Feature IDs | Changed Backlog IDs | Why Revised | Author |
|---------|------|---------------------|---------------------|-------------|--------|
| v1 | 2026-06-17 | F-001 | BL-20260617-004 | Initial planning baseline from backlog item | Codex |
