# Architecture Review

## Task Context
- Task Name: Watchlist YAML Support
- Task ID: watchlist-yaml-support
- Last Updated: 2026-06-14

## System Context
- Current Stack: Python standard library, `unittest`, PowerShell/Bash loop scripts, GitHub Actions.
- Existing Patterns: `LoopCoordinator` loads `config/watchlist.yaml` through `src/jeonseloop/watchlist.py`; validation converts parsed mappings into immutable dataclasses before collection begins.
- Integration Points: `config/watchlist.yaml`, `src/jeonseloop/watchlist.py`, `src/jeonseloop/loop.py`, `tests/test_watchlist.py`, invalid-watchlist health persistence.

## Feature Decomposition Map
| Feature ID | Feature | Description | Depends On | Complexity | Risk |
|------------|---------|-------------|------------|------------|------|
| F-001 | Watchlist YAML parser hardening | Extend and test the dependency-free watchlist YAML subset. | None | Medium | Medium |

## Dependency Map
- `loop.py` -> `watchlist.py` (loop startup must receive a validated `Watchlist` or a `WatchlistError`).
- `watchlist.py` -> Python standard library only (avoid adding package-management surface for one config parser).
- `tests/test_watchlist.py` -> `watchlist.py` (focused behavior coverage).

## Technical Decisions
- Decision: Keep parsing and validation separated.
  - Rationale: Parser support can widen without weakening existing required-field and type checks.
  - Trade-offs: The parser needs clear unsupported-structure errors because it is not a full YAML implementation.
- Decision: Do not mutate `config/watchlist.yaml`.
  - Rationale: Existing product decisions reserve watchlist changes for the operator.
  - Trade-offs: Parser improvements only affect loading, not config generation or migration.

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| Custom YAML subset is mistaken for full YAML support | Medium | Document the supported subset in task decisions/tests and fail unsupported structures explicitly | Backend Agent |
| Parser regression blocks unattended loop startup | High | Run focused watchlist tests and the full unit test suite | QA Agent |
| Existing unrelated backlog edit is accidentally committed | Medium | Stage explicit paths/hunks only and inspect status before commit | SCM Agent |

