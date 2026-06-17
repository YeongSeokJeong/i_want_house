# Architecture Review

## Task Context
- Task Name: Dashboard criteria thresholds
- Task ID: dashboard-criteria-thresholds
- Last Updated: 2026-06-17

## System Context
- Current Stack: static dashboard, JSON state files, Python unittest suite.
- Existing Patterns: dashboard derives visual summaries from `health.json`, `history/*.json`, and embedded watchlist metadata.
- Integration Points: `assets/dashboard.js`, `index.html`, `assets/dashboard.css`, `tests/test_dashboard_static.py`.

## Feature Decomposition Map
| Feature ID | Feature | Description | Depends On | Complexity | Risk |
|------------|---------|-------------|------------|------------|------|
| F-001 | Criteria threshold details | Add applied criterion and remaining-to-urgent-line details to the monitoring summary | None | Medium | Medium |

## Dependency Map
- `assets/dashboard.js` computes criterion values from watchlist target/discount and latest history.
- `index.html` defines the table columns.
- `assets/dashboard.css` keeps the wider table scannable.

## Technical Decisions
- Decision: Keep calculations in dashboard helpers.
  - Rationale: The static dashboard already computes first-screen status from existing JSON.
  - Trade-offs: Duplicates a small amount of analyzer logic but avoids changing runtime persistence.

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| Label/calculation drift from analyzer | Medium | Use simple helper names and static tests; document in wiki | Frontend/Backend Agent |
| Table width grows too large | Medium | Keep compact columns and horizontal overflow behavior | Frontend/Backend Agent |
