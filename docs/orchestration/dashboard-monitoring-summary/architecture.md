# Architecture Review

## Task Context
- Task Name: Dashboard monitoring summary
- Task ID: dashboard-monitoring-summary
- Last Updated: 2026-06-17

## System Context
- Current Stack: static HTML/CSS/JavaScript dashboard, Python product loop, JSON state under `data/`.
- Existing Patterns: dashboard fetches `health.json`, `history/*.json`, and `urgent-feed.json` directly; tests inspect static assets and committed JSON state.
- Integration Points: `data/state/health.json`, `data/history/{complex_id}.json`, `data/state/urgent-feed.json`, watchlist metadata.

## Feature Decomposition Map
| Feature ID | Feature | Description | Depends On | Complexity | Risk |
|------------|---------|-------------|------------|------------|------|
| F-001 | Monitoring summary data and layout | Add first-screen per-complex monitoring status summary | None | Medium | Medium |

## Dependency Map
- `assets/dashboard.js` -> `data/history/*.json` for latest listing price and trade baseline.
- `assets/dashboard.js` -> `data/state/health.json` for source diagnostic status.
- `assets/dashboard.js` -> embedded watchlist metadata for target price and discount ratio.
- `index.html`/`assets/dashboard.css` provide the primary layout and responsive presentation.

## Technical Decisions
- Decision: Keep summary calculations client-side for this task.
  - Rationale: Existing dashboard already computes chart summaries client-side and has no build step.
  - Trade-offs: Faster implementation, but duplicated criterion math must be tested and may later move to persisted projection.
- Decision: Preserve recent urgent feed as a secondary panel.
  - Rationale: The task asks to demote, not remove, urgent candidates.
  - Trade-offs: Page gets denser, so CSS must keep rows scannable.

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| Dashboard math drifts from analyzer | Medium | Keep formula simple and test helper strings/static contract; defer detailed criterion explanation to BL-20260617-004 | Frontend/Backend Agent |
| Mobile layout becomes cramped | Medium | Use compact table/card styling with responsive behavior | Frontend/Backend Agent |
| Missing history data hides status | Medium | Render fallback status from `listing_diagnostics` and explicit dash values | Frontend/Backend Agent |
