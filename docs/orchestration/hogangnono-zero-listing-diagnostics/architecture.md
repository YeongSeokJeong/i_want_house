# Architecture Review

## Task Context
- Task Name: Hogangnono zero-listing diagnostics
- Task ID: hogangnono-zero-listing-diagnostics
- Last Updated: 2026-06-17

## System Context
- Current Stack: Python standard library product loop, unittest regression suite, static HTML/CSS/JavaScript dashboard.
- Existing Patterns: `LoopCoordinator` orchestrates a cycle; `ListingCollector` fetches records; `LoopStateRepository` persists validated JSON through validate-before-replace atomic writes.
- Integration Points: Hogangnono public JSON endpoint, `data/state/health.json`, `data/history/*.json`, static dashboard fetches.

## Feature Decomposition Map
| Feature ID | Feature | Description | Depends On | Complexity | Risk |
|------------|---------|-------------|------------|------------|------|
| F-001 | Source diagnostic contract | Add successful collection diagnostics to run records and health state | None | Medium | Medium |
| F-002 | Dashboard and operator visibility | Render/explain diagnostics and record live cross-check evidence | F-001 | Medium | Medium |

## Dependency Map
- `LoopCoordinator` -> `ListingCollector` because diagnostics are derived after collection succeeds.
- `LoopCoordinator` -> `LoopStateRepository` because health stores the run record unchanged.
- `assets/dashboard.js` -> `data/state/health.json` because dashboard visibility should consume the persisted contract.
- F-002 depends on F-001 because UI should not infer diagnostics from historical count alone.

## Technical Decisions
- Decision: Add a small `listing_diagnostics` object to successful run records.
  - Rationale: Health already records run-level status and counts, and dashboard already reads it.
  - Trade-offs: Keeps the contract simple, but health grows beyond numeric counts.
- Decision: Preserve collector failure behavior for mapping/API problems.
  - Rationale: Failures should still avoid replacing previous JSON state.
  - Trade-offs: Operators must inspect both success diagnostics and failure diagnostics depending on run status.

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| Hogangnono response shape changes | Medium | Keep parser tests and treat malformed payloads as source failures | Backend Agent |
| Empty response is misread as source failure | High | Use explicit `empty_response` status and dashboard copy | Backend Agent |
| Runtime secrets leak into diagnostics | High | Reuse sanitization and avoid recording raw environment values except public apt hashes | Backend Agent |
