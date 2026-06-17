# Architecture Review

## Task Context
- Task Name: Dashboard pre urgent grades
- Task ID: dashboard-pre-urgent-grades
- Last Updated: 2026-06-17

## System Context
- Current Stack: static dashboard, JSON state files, Python unittest suite.
- Existing Patterns: dashboard derives monitoring and decision summaries from committed JSON state and embedded watchlist metadata.
- Integration Points: `assets/dashboard.js`, `assets/dashboard.css`, `tests/test_dashboard_static.py`.

## Feature Decomposition Map
| Feature ID | Feature | Description | Depends On | Complexity | Risk |
|------------|---------|-------------|------------|------------|------|
| F-001 | Pre urgent grades | Classify and render feed items by distance to urgent line | None | Medium | Medium |

## Dependency Map
- `data/state/urgent-feed.json` provides candidate prices and alert-planned flags.
- `data/history/{complex_id}.json` provides latest trade baseline for urgent-line calculation.
- `assets/dashboard.js` contains shared urgent-line helpers.

## Technical Decisions
- Decision: Reuse `criteriaThresholds` for feed grading.
  - Rationale: Keeps grade distance consistent with the monitoring summary display.
  - Trade-offs: Requires `renderFeed` to fetch latest history for the selected complex.

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| Grade threshold disagreement with future policy | Medium | Document thresholds in wiki and keep helper names explicit | Frontend/Backend Agent |
| Extra feed/history fetch latency | Low | Reuse small static JSON files and keep rendering async | Frontend/Backend Agent |
