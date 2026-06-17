# Architecture Review

## Task Context
- Task Name: Dashboard criteria suggestions
- Task ID: dashboard-criteria-suggestions
- Last Updated: 2026-06-17

## System Context
- Current Stack: static dashboard, JSON state files, Python unittest suite.
- Existing Patterns: dashboard fetches optional and required JSON state and renders local section states.
- Integration Points: `data/state/criteria-suggestions.json`, `assets/dashboard.js`, `index.html`, `assets/dashboard.css`, `tests/test_dashboard_static.py`.

## Feature Decomposition Map
| Feature ID | Feature | Description | Depends On | Complexity | Risk |
|------------|---------|-------------|------------|------------|------|
| F-001 | Criteria suggestions panel | Render optional review-required criteria suggestions | None | Medium | Low |

## Dependency Map
- `CriteriaSuggestionService` writes `data/state/criteria-suggestions.json` when there is enough criteria-log volume.
- `assets/dashboard.js` should fetch the optional JSON and render either suggestions or empty state.

## Technical Decisions
- Decision: Do not change suggestion generation.
  - Rationale: The backlog asks for dashboard display, and existing safety rules require human approval.
  - Trade-offs: The committed dashboard often shows an empty state until enough real history accumulates.

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| Operators think suggestions auto-apply | Medium | Render review-only/approval-required copy and document in wiki | Frontend/Backend Agent |
| Missing optional JSON looks like an error | Low | Treat 404 as empty state | Frontend/Backend Agent |
