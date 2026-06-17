# Architecture Review

## Task Context
- Task Name: Hogangnono missing map diagnostics
- Task ID: hogangnono-missing-map-diagnostics
- Last Updated: 2026-06-17

## System Context
- Current Stack: Python source adapters, loop failure diagnostics, unittest suite.
- Existing Patterns: collector failures preserve previous JSON state and write sanitized diagnostics.
- Integration Points: `src/jeonseloop/sources.py`, `src/jeonseloop/loop.py`, `tests/test_reliability.py`.

## Feature Decomposition Map
| Feature ID | Feature | Description | Depends On | Complexity | Risk |
|------------|---------|-------------|------------|------------|------|
| F-001 | Missing map diagnostics | Improve Hogangnono apt hash mapping diagnostics | None | Medium | Low |

## Dependency Map
- `HogangnonoListingSourceClient._apt_hash_for` raises the direct source error.
- `LoopCoordinator` writes collector diagnostics on source failure.
- `sanitize_diagnostics` redacts sensitive fields before writing diagnostics.

## Technical Decisions
- Decision: Compute missing mapping targets in loop diagnostics from watchlist IDs and current env mapping.
  - Rationale: The source client only sees one target at a time, while loop has the complete watchlist.
  - Trade-offs: Diagnostics helper duplicates simple mapping parsing logic.

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| Diagnostics accidentally include secrets | High | Only emit env variable name, complex IDs, and placeholder hashes | Backend Agent |
