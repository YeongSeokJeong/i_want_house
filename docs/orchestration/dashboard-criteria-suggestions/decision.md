# Session Decisions

## Task Context
- Task Name: Dashboard criteria suggestions
- Task ID: dashboard-criteria-suggestions

## Decision Log
| Session | Feature ID | Feature | Decision | Rationale | Impact | Date |
|---------|------------|---------|----------|-----------|--------|------|
| 1 | PLAN | Planning | Render suggestions as optional dashboard state | The product only writes `criteria-suggestions.json` after enough decision history | Prevents missing optional JSON from appearing as a hard dashboard failure | 2026-06-17 |

## Session 1
- Feature ID: F-001
- Feature: Criteria suggestions panel
- Decisions:
  - Show review-only status and never imply automatic criteria changes.
  - Treat HTTP 404 for `criteria-suggestions.json` as an empty state.
- Alternatives Considered:
  - Lower suggestion generation threshold to force a committed file: rejected because it changes backend behavior and policy.
- Risks Introduced:
  - Dashboard copy must stay clear that suggestions require human approval.
- Follow-up Notes:
  - Verification passed with `node --check assets/dashboard.js`, `python -m unittest discover -s tests -v`, and local static HTTP smoke (`/`, `/assets/dashboard.js` returned 200; `/data/state/criteria-suggestions.json` returned expected 404 empty-state input).
