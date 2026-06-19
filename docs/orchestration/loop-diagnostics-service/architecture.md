# Architecture Review

## Task Context
- Task Name: Loop diagnostics service
- Task ID: loop-diagnostics-service
- Last Updated: 2026-06-19

## System Context
- Current Stack: Python package with unittest coverage, JSON state persistence, static dashboard consumers.
- Existing Patterns: `LoopCoordinator` orchestrates a cycle and delegates collection, validation, analysis, persistence, review, notification, and trade baseline concerns to services.
- Integration Points: `data/state/health.json`, `data/state/collector-diagnostics.json`, `ListingCollector`, `LoopStateRepository`, source adapter environment variables.

## Feature Decomposition Map
| Feature ID | Feature | Description | Depends On | Complexity | Risk |
|------------|---------|-------------|------------|------------|------|
| F-001 | Diagnostic projection service | Extract diagnostic JSON projection and source-kind inference from `LoopCoordinator` into a dedicated service | None | Medium | Medium |

## Dependency Map
- `LoopCoordinator` -> `LoopDiagnostics` for collector failure diagnostics and successful listing diagnostics.
- `LoopDiagnostics` -> `Watchlist`/`WatchTarget` data only for target metadata.
- `LoopStateRepository` remains responsible for validate-before-replace JSON writes.

## Technical Decisions
- Decision: Add a dedicated diagnostics module, not a persistence repository.
  - Rationale: The backlog item targets diagnostic/health generation responsibility, while persistence splitting is tracked separately.
  - Trade-offs: One more service object is introduced, but `LoopCoordinator` loses source-specific projection details.
- Decision: Preserve JSON contracts exactly.
  - Rationale: Dashboard, tests, and operator docs already consume these fields.
  - Trade-offs: The new service inherits current naming until a separate contract migration is planned.

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| Diagnostic JSON shape changes accidentally | High | Run focused reliability tests and full unittest suite | Codex |
| Stacked branch includes prerequisite closeout commits | Medium | Base PR on `task/listing-source-adapters-closeout` and record dependency | Codex |
