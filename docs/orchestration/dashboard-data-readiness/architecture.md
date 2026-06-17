# Architecture Review

## Task Context
- Task Name: Dashboard data readiness
- Task ID: dashboard-data-readiness
- Last Updated: 2026-06-17

## System Context
- Current Stack: static dashboard, JSON state files, Python unittest suite.
- Existing Patterns: dashboard derives operator-facing panels from committed JSON.
- Integration Points: `data/state/health.json`, `data/history/*.json`, `data/state/urgent-feed.json`, `assets/dashboard.js`, `index.html`, `assets/dashboard.css`.

## Feature Decomposition Map
| Feature ID | Feature | Description | Depends On | Complexity | Risk |
|------------|---------|-------------|------------|------------|------|
| F-001 | Data readiness panel | Show collection, zero streak, baseline, and quality block state per complex | None | Medium | Medium |

## Dependency Map
- `health.latest.listing_diagnostics.targets[]` gives source response status.
- `history/*.json` gives latest collection and baseline values.
- `urgent-feed.json` gives quality-block candidate reasons when present.

## Technical Decisions
- Decision: Reuse existing dashboard fetch patterns.
  - Rationale: The UI is static and already fetches the same JSON sources.
  - Trade-offs: Some data is fetched by more than one panel.

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| Inferred quality status misses future reason formats | Medium | Keep helper names explicit and document current inference | Frontend/Backend Agent |
| Wider table impacts mobile layout | Low | Use existing horizontal overflow table style | Frontend/Backend Agent |
