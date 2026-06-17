# Task Plan

## Task Metadata
- Task Name: Hogangnono zero-listing diagnostics
- Task ID: hogangnono-zero-listing-diagnostics
- Task Branch: task/hogangnono-zero-listing-diagnostics
- Task Worktree: D:\git\i_want_house
- Plan Version: v1
- Last Updated: 2026-06-17

## Planning Assumptions
- The next backlog item is `BL-20260617-002`, the earliest open source-code backlog item.
- A Hogangnono response with an empty `aptItems` list and no exception means the source was reachable and returned zero sale items for the configured apt hash/trade type.
- Repository-verifiable implementation should separate successful empty responses from mapping/API failures; current live portal state remains external-state evidence.

## Requirement Brief
- In scope:
  - Persist per-complex listing collection diagnostics for successful runs.
  - Mark zero-listing Hogangnono targets as empty-but-collected rather than indistinguishable from missing data.
  - Surface the diagnostic status in dashboard/operator-facing artifacts.
  - Record current Hogangnono API cross-check evidence without committing secrets.
- Out of scope:
  - Bypassing Hogangnono access controls, CAPTCHA, login walls, or rate limits.
  - Changing Telegram send behavior.
  - Solving broader dashboard monitoring redesign items tracked by later backlog IDs.
- Acceptance summary:
  - A successful zero-item Hogangnono response is visible in `health.json` with source kind, target complex, source apt hash, trade type, listing count, and diagnosis status.
  - Mapping/API failures still record collector failure diagnostics and preserve previous state.
  - Dashboard or operator docs make the distinction understandable.

## Related Wiki Discovery
| Document | Relevance | Gap |
|----------|-----------|-----|
| `docs/wiki/domains/jeonseloop/overview.md` | Describes Hogangnono source mode, health/dashboard state, and external-state boundary. | Needs a short note after implementation explaining per-complex collection diagnostics. |
| `docs/wiki/rules/workflow/loop-engineering-routing.md` | Requires separating repo-verifiable code behavior from external service state. | No structural change needed. |
| `docs/wiki/rules/workflow/development-automation-loop.md` | Development verification pattern for tests and reports. | No structural change needed. |

## Related Backlog Items
| Backlog ID | Route | Status | Relationship |
|------------|-------|--------|--------------|
| BL-20260617-002 | source-code | Doing | Parent task item for this orchestration |

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | Source diagnostic contract | Persist source/target diagnostics that distinguish empty Hogangnono responses from collection failures | None | Medium | Backend Agent |
| F-002 | Dashboard and operator visibility | Show zero-listing diagnostics in dashboard/docs and record live cross-check evidence | F-001 | Medium | Backend Agent |

## Feature Detail
### F-001 Source diagnostic contract
- Scope:
  - Add per-complex collection diagnostics to successful run records.
  - Include Hogangnono source kind, apt hash, trade type, listing count, and diagnosis status.
  - Add regression tests for zero-listing Hogangnono success and existing mapping failure behavior.
- Acceptance Criteria:
  - [x] A successful Hogangnono run with one empty target writes `latest.listing_diagnostics.targets[]` to health.
  - [x] Empty Hogangnono targets are marked with a stable status such as `empty_response`.
  - [x] Existing collector failure diagnostics still redact secrets and preserve previous listing JSON.
  - [x] Full unittest suite passes.
- Out of Scope:
  - Dashboard rendering changes.

### F-002 Dashboard and operator visibility
- Scope:
  - Render per-complex zero-listing diagnostics on the dashboard or in the existing complex summary.
  - Update operator/wiki documentation with the interpretation rule.
  - Record live API cross-check evidence for the current watchlist mappings.
- Acceptance Criteria:
  - [ ] A user can tell whether a 0-count complex was collected successfully or blocked by source/mapping failure.
  - [ ] Current Hogangnono API evidence for `E152` and `B11b` is recorded without secrets.
  - [ ] Dashboard static tests cover the new diagnostic rendering.
  - [ ] Wiki/backlog closeout names exact files and sections changed.
- Out of Scope:
  - Broader first-screen dashboard redesign tracked by `BL-20260617-003`.

## Execution Order
1. F-001
2. F-002

## Revision Log
| Version | Date | Changed Feature IDs | Changed Backlog IDs | Why Revised | Author |
|---------|------|---------------------|---------------------|-------------|--------|
| v1 | 2026-06-17 | F-001,F-002 | BL-20260617-002 | Initial planning baseline from backlog item | Codex |
