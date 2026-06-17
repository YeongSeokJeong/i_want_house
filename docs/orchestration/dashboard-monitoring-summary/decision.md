# Session Decisions

## Task Context
- Task Name: Dashboard monitoring summary
- Task ID: dashboard-monitoring-summary

## Decision Log
| Session | Feature ID | Feature | Decision | Rationale | Impact | Date |
|---------|------------|---------|----------|-----------|--------|------|
| 1 | PLAN | Planning | Implement as one feature | The requested first-screen dashboard rework is a cohesive static UI/data-projection change | Keeps the task small enough for one feature commit | 2026-06-17 |
| 1 | PLAN | Planning | Use current checkout as task worktree | The backlog sequence builds on the just-completed dashboard diagnostics branch | Avoids losing dependent state/dashboard changes | 2026-06-17 |

## Session 1
- Feature ID: F-001
- Feature: Monitoring summary data and layout
- Decisions:
  - Use existing static JSON sources instead of adding a new projection file.
  - Treat urgent line as the stricter of watchlist target price and recent trade baseline after discount when a baseline exists.
- Alternatives Considered:
  - Add a new persisted dashboard projection JSON: deferred because current dashboard can compute the summary from existing state.
  - Merge this with `BL-20260617-004`: rejected because `BL-20260617-004` asks for deeper criterion explanation and remaining amount details.
- Risks Introduced:
  - Client-side calculations must stay aligned with analyzer behavior.
- Follow-up Notes:
  - Add tests that assert the first-screen summary strings and calculation helpers exist.
  - Implemented `단지별 감시 상태` as the first main panel and kept recent urgent candidates as a secondary panel.
  - `node --check assets/dashboard.js` passed.
  - `python -m unittest discover -s tests -v` passed 68 tests.
  - Local static HTTP smoke returned HTTP 200 for `/` and `/data/state/health.json`.
