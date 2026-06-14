# Architecture Review

## Task Context
- Task Name: Live data adapter validation
- Task ID: live-data-adapter-validation
- Last Updated: 2026-06-14

## System Context
- Current Stack: Python standard library CLI/background job, unittest tests, JSON/Markdown file persistence.
- Existing Patterns: `LoopCoordinator` composes service classes; `ListingCollector` accepts an injected fetcher; `TradeBaselineRepository` owns trade baseline loading.
- Integration Points: Watchlist config, listing source, trade source, JSON state, Telegram notifier, optional LLM review.

## Feature Decomposition Map
| Feature ID | Feature | Description | Depends On | Complexity | Risk |
|------------|---------|-------------|------------|------------|------|
| F-001 | Live source adapter guardrails | Configurable HTTP JSON adapters plus visible missing-source failure behavior | None | Medium | Medium |

## Dependency Map
- `LoopCoordinator` -> `ListingCollector` (collection before validation and analysis)
- `LoopCoordinator` -> `TradeBaselineRepository` (baseline lookup before candidate classification)
- `ListingCollector` -> live listing fetcher (optional dependency when fixture is absent)
- `TradeBaselineRepository` -> live trade fetcher (optional dependency before local cache fallback)

## Technical Decisions
- Decision: Add adapter factories around injected callables, not a new framework.
  - Rationale: The existing collector already supports dependency injection and tests can verify behavior without network access.
  - Trade-offs: The adapter contract requires operators to provide compatible JSON endpoints; it avoids brittle portal-specific scraping.
- Decision: Report missing live listing source as failure health.
  - Rationale: Empty success is misleading for unattended monitoring.
  - Trade-offs: Local dry-runs without fixture/source become failed runs, but fixture-backed dry-runs remain available.

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| External endpoint schema differs from adapter contract | Medium | Support list or keyed JSON payloads and keep validation failures explicit | Backend Agent |
| Credentials or API availability cannot be verified in repo tests | Medium | Document env placeholders and mark live verification as operator-owned | Operator |
| Missing source failures surprise existing local runs | Low | README and `.env.example` document fixture and live source options | Backend Agent |
