# Architecture Review

## Task Context
- Task Name: Switch listing source to Hogangnono
- Task ID: hogangnono-listing-source
- Last Updated: 2026-06-15

## System Context
- Current Stack: Python standard library CLI, unittest, GitHub Actions, static JSON/Markdown state.
- Existing Patterns: `sources.py` provides source-specific clients selected by `listing_fetcher_from_env`; `collector.py` retries transient failures and `loop.py` records collector diagnostics.
- Integration Points: Hogangnono public HTTP JSON endpoints, GitHub Actions environment variables, watchlist complex IDs, dashboard state JSON.

## Feature Decomposition Map
| Feature ID | Feature | Description | Depends On | Complexity | Risk |
|------------|---------|-------------|------------|------------|------|
| F-001 | Hogangnono listing source | Source client, normalization, config, workflow, docs, tests | None | High | Medium |

## Dependency Map
- `listing_fetcher_from_env` -> `HogangnonoListingSourceClient` (source selection)
- `HogangnonoListingSourceClient` -> `WatchTarget` (target-specific apt hash mapping)
- `collector.py` -> source fetcher exceptions (retry and diagnostics behavior)
- GitHub Actions -> environment variables (live scheduled collection)

## Technical Decisions
- Decision: Implement a source-specific client rather than changing the collector contract.
  - Rationale: Existing HTTP JSON and Naver clients already satisfy the collector interface.
  - Trade-offs: More source-specific normalization code, but lower blast radius.
- Decision: Use configurable apt hash mapping.
  - Rationale: Operator values differ from internal complex IDs and may change.
  - Trade-offs: Requires operator setup, but avoids committing machine-specific values.

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| Hogangnono endpoint schema changes | Medium | Raise `SourceFetchError`, preserve prior state, record diagnostics | Backend Agent |
| Rate limiting or access blocking | Medium | Reuse timeout/retry handling, avoid bypass logic | Backend Agent |
| Misconfigured apt hash map | Medium | Fail with explicit configuration error before replacing state | Backend Agent |
