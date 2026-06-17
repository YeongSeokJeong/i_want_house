# Task Plan

## Task Metadata
- Task Name: Dashboard rejection summary
- Task ID: dashboard-rejection-summary
- Task Branch: task/dashboard-rejection-summary
- Task Worktree: D:\git\i_want_house
- Plan Version: v1
- Last Updated: 2026-06-17

## Planning Assumptions
- The task is driven by `BL-20260617-005`.
- `data/state/urgent-feed.json` already persists every classified candidate with `decision`, `reason`, `complex_id`, and listing metadata.
- The dashboard can derive reason summaries from the existing feed without changing alert behavior.

## Requirement Brief
- In scope:
  - Add dashboard-level rejection/hold/approval reason counts.
  - Add per-complex summaries that explain why no alert was planned for a watched complex.
  - Keep the static dashboard no-build architecture.
  - Add static tests covering the new UI labels and helper functions.
- Out of scope:
  - Changing candidate classification rules.
  - Changing Telegram alert planning.
  - Persisting a new state file unless the existing feed is insufficient.

## Related Wiki Discovery
| Document | Relevance | Gap |
|----------|-----------|-----|
| `docs/wiki/domains/jeonseloop/overview.md` | Documents dashboard interpretation and urgent feed behavior. | Needs a closeout note that the dashboard summarizes rejected/held reasons from the urgent feed. |
| `docs/wiki/rules/workflow/loop-engineering-routing.md` | Confirms repo-verifiable dashboard behavior. | No structural change needed. |

## Related Backlog Items
| Backlog ID | Route | Status | Relationship |
|------------|-------|--------|--------------|
| BL-20260617-005 | source-code | Doing | Parent task item for this orchestration |

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | Decision reason summary | Show aggregate and per-complex rejected/held reason summaries on the dashboard | None | Medium | Frontend/Backend Agent |

## Feature Detail
### F-001 Decision reason summary
- Scope:
  - Add a dashboard section near the urgent feed showing decision counts and top reasons.
  - Summarize each complex by approved, held, rejected, alert-planned counts and the dominant reasons.
  - Convert technical reason codes into concise Korean labels where practical.
  - Add static tests for labels/helper names and urgent-feed compatibility.
- Acceptance Criteria:
  - [x] Dashboard text includes rejection/hold reason summary concepts.
  - [x] Per-complex rows show why alerts were absent or limited.
  - [x] Existing urgent feed item rendering remains intact.
  - [x] `node --check assets/dashboard.js` and full unittest suite pass.
- Out of Scope:
  - Pre-urgent grading, tracked by `BL-20260617-006`.

## Execution Order
1. F-001

## Revision Log
| Version | Date | Changed Feature IDs | Changed Backlog IDs | Why Revised | Author |
|---------|------|---------------------|---------------------|-------------|--------|
| v1 | 2026-06-17 | F-001 | BL-20260617-005 | Initial planning baseline from backlog item | Codex |
