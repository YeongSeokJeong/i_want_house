# Architecture Review

## Task Context
- Task Name: Dashboard rejection summary
- Task ID: dashboard-rejection-summary
- Last Updated: 2026-06-17

## System Context
- Current Stack: static dashboard, JSON state files, Python unittest suite.
- Existing Patterns: dashboard derives monitoring, chart, diagnostics, and feed views from committed JSON state.
- Integration Points: `assets/dashboard.js`, `index.html`, `assets/dashboard.css`, `tests/test_dashboard_static.py`.

## Feature Decomposition Map
| Feature ID | Feature | Description | Depends On | Complexity | Risk |
|------------|---------|-------------|------------|------------|------|
| F-001 | Decision reason summary | Add aggregate and per-complex reason summaries from `urgent-feed.json` | None | Medium | Medium |

## Dependency Map
- `data/state/urgent-feed.json` provides classified candidates.
- `assets/dashboard.js` fetches and renders the urgent feed.
- `index.html` defines the new dashboard section.
- `assets/dashboard.css` styles compact reason summaries.

## Technical Decisions
- Decision: Keep summary calculation in dashboard helpers.
  - Rationale: No new runtime state is needed, and the dashboard already fetches the feed.
  - Trade-offs: The dashboard owns presentation labels for analyzer reason codes.

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| Reason label drift | Medium | Add helper functions with static tests and update wiki closeout | Frontend/Backend Agent |
| Empty feed creates confusing UI | Medium | Render explicit empty summary states | Frontend/Backend Agent |
