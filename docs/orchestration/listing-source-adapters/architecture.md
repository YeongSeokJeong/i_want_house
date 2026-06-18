# Architecture Review

## Task Context
- Task Name: Listing source provider adapter split
- Task ID: listing-source-adapters
- Last Updated: 2026-06-19

## System Context
- Current Stack: Python standard library, `unittest`, JSON/Markdown repository state, GitHub Actions, static dashboard assets.
- Existing Patterns: Product modules under `src/jeonseloop/` expose cohesive services while preserving module-level wrappers for CLI and tests.
- Integration Points: `src/jeonseloop/collector.py`, `src/jeonseloop/loop.py`, `tests/test_reliability.py`, environment variables for HTTP JSON, Naver, and Hogangnono providers.

## Feature Decomposition Map
| Feature ID | Feature | Description | Depends On | Complexity | Risk |
|------------|---------|-------------|------------|------------|------|
| F-001 | Source package extraction | Split source clients/config/normalizers into provider modules behind the existing public facade | None | High | Medium |
| F-002 | Reliability regression coverage | Verify provider parsing, factory selection, diagnostics, and import compatibility | F-001 | Medium | Medium |
| F-003 | Closeout and handoff | Final verification and backlog/orchestration closeout | F-001,F-002 | Medium | Low |

## Dependency Map
- `collector.py` -> `listing_fetcher_from_env` result (provider-agnostic fetcher contract).
- `loop.py` -> source errors for collector failure diagnostics.
- `tests/test_reliability.py` -> public imports from `jeonseloop.sources`.
- `sources/__init__.py` -> re-exported public classes/functions for compatibility.
- `sources/http_json.py` -> HTTP JSON listing/trade provider.
- `sources/naver.py` -> Naver listing provider and normalizer.
- `sources/hogangnono.py` -> Hogangnono listing provider and normalizer.
- `sources/factory.py` -> environment-driven source selection.
- `sources/common.py` -> shared errors, types, parsing helpers, and JSON payload utilities.

## Technical Decisions
- Decision: Use a package facade instead of renaming all imports.
  - Rationale: Existing tests and callers import `jeonseloop.sources` directly.
  - Trade-offs: The facade must re-export every supported public symbol.
- Decision: Keep helpers private inside provider modules unless shared by multiple providers.
  - Rationale: Provider modules should own provider-specific parsing details.
  - Trade-offs: Some similar HTTP request code remains duplicated until a later transport abstraction is justified.
- Decision: Do not change environment variable contracts.
  - Rationale: This backlog item is an architecture split, not an operator contract change.
  - Trade-offs: Any provider fallback or multi-source behavior remains deferred to separate backlog items.

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| Import compatibility regression | High | Preserve `sources/__init__.py` exports and run existing reliability tests | Backend Agent |
| Diagnostic message drift | Medium | Keep exception text stable where tests assert it | Backend Agent |
| Provider behavior changes during move | Medium | Move code mechanically first; defer behavioral changes | Backend Agent |
| Stacked local branch complicates PR closeout | Medium | Record base status and stop before PR if prior branch is not landed | SCM Agent |
