# Task Plan

## Task Metadata
- Task Name: Dashboard criteria suggestions
- Task ID: dashboard-criteria-suggestions
- Task Branch: task/dashboard-criteria-suggestions
- Task Worktree: D:\git\i_want_house
- Plan Version: v1
- Last Updated: 2026-06-17

## Planning Assumptions
- The task is driven by `BL-20260617-007`.
- `CriteriaSuggestionService` already writes `data/state/criteria-suggestions.json` after enough criteria-log volume.
- The current committed state may not contain the suggestion file yet, so the dashboard must handle the optional missing file clearly.

## Requirement Brief
- In scope:
  - Add a dashboard panel for review-only criteria suggestions.
  - Render generated time, decision volume, false-positive metrics, and suggestion items when the JSON exists.
  - Render a clear empty state when the JSON does not exist yet.
  - Add static tests for labels/helper functions.
- Out of scope:
  - Automatically editing `config/watchlist.yaml`.
  - Changing suggestion generation thresholds.
  - Calling external LLM services.

## Related Wiki Discovery
| Document | Relevance | Gap |
|----------|-----------|-----|
| `docs/wiki/domains/jeonseloop/overview.md` | Documents review-only criteria suggestions. | Needs a closeout note that the dashboard displays suggestion artifacts when present. |
| `docs/wiki/decisions/jeonseloop-open-requirement-decisions.md` | Records human approval requirement for criteria changes. | No structural change needed. |

## Related Backlog Items
| Backlog ID | Route | Status | Relationship |
|------------|-------|--------|--------------|
| BL-20260617-007 | source-code | Doing | Parent task item for this orchestration |

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | Criteria suggestions panel | Show generated criteria suggestions and empty state on the dashboard | None | Medium | Frontend/Backend Agent |

## Feature Detail
### F-001 Criteria suggestions panel
- Scope:
  - Add a dashboard panel that fetches `data/state/criteria-suggestions.json`.
  - Display metrics and review-required proposal rows.
  - Make missing JSON a normal empty state.
  - Add static tests for panel labels and helper functions.
- Acceptance Criteria:
  - [x] Dashboard shows criteria suggestion concepts and review-only status.
  - [x] Missing `criteria-suggestions.json` does not make the dashboard look failed.
  - [x] Existing dashboard behavior remains intact.
  - [x] `node --check assets/dashboard.js` and full unittest suite pass.
- Out of Scope:
  - Auto-applying suggestions.

## Execution Order
1. F-001

## Revision Log
| Version | Date | Changed Feature IDs | Changed Backlog IDs | Why Revised | Author |
|---------|------|---------------------|---------------------|-------------|--------|
| v1 | 2026-06-17 | F-001 | BL-20260617-007 | Initial planning baseline from backlog item | Codex |
