# Architecture Review

## Task Context
- Task Name: src OOP architecture refactor
- Task ID: src-oop-refactor
- Last Updated: 2026-06-13

## System Context
- Current Stack: Python 3.12 standard library, `unittest`, GitHub Actions, GitHub Pages static assets, JSON/Markdown repository state.
- Existing Patterns: Product code is divided into modules under `src/jeonseloop/` for watchlist loading, collection, validation, analysis, trade baselines, persistence, notification, review, suggestions, CLI, and loop orchestration.
- Integration Points: `config/watchlist.yaml`, fixture listing JSON, `data/**/*.json`, `logs/*.md`, `.github/workflows/jeonseloop.yml`, Telegram Bot API, optional Anthropic API.

## Feature Decomposition Map
| Feature ID | Feature | Description | Depends On | Complexity | Risk |
|------------|---------|-------------|------------|------------|------|
| F-001 | Domain and service object boundaries | Add cohesive class APIs around existing responsibilities while retaining wrappers | None | High | Medium |
| F-002 | Object-oriented loop orchestration | Compose service objects through an application-level coordinator for one loop run | F-001 | High | High |
| F-003 | Architecture QA and closeout | Verify compatibility, document evidence, and decide wiki closeout | F-001,F-002 | Medium | Medium |

## Dependency Map
- `scripts/run-loop.*` -> `src/jeonseloop/run.py` (operator entrypoints invoke the CLI).
- `src/jeonseloop/run.py` -> `src/jeonseloop/loop.py` (CLI delegates one-cycle orchestration).
- `loop.py` -> watchlist, collector, validator, analyzer, trades, review, suggestions, notifier, persistence (current product-loop stages).
- F-001 service classes -> existing module functions as compatibility wrappers during migration.
- `ListingCollector` -> `WatchTarget`, fixture files, optional live fetcher callback.
- `ListingValidator` -> raw listing dictionaries, `ValidationIssue`.
- `CandidateAnalyzer` -> `WatchTarget`, valid listing dictionaries, notified state, trade baselines.
- `LoopStateRepository` -> `JsonStateStore`, state JSON files, criteria log, urgent feed.
- `NotificationService` -> `TelegramNotifier` only when sending is explicitly allowed.
- `CandidateReviewService` -> `AnthropicCandidateReviewer` only when review config is enabled.
- `CriteriaSuggestionService` -> criteria log and suggestions JSON.
- `TradeBaselineRepository` -> trade cache JSON files.
- Proposed F-002 coordinator -> F-001 service classes for explicit dependency composition.

## Technical Decisions
- Decision: Prefer service classes with explicit constructor dependencies over module-level orchestration state.
  - Rationale: The user requested architecture alignment with OOP; cohesive objects make responsibilities and dependencies visible.
  - Trade-offs: Temporary wrappers create two access styles until closeout completes.
- Decision: Keep pure data shapes as dictionaries/lists where current persisted JSON and tests depend on them.
  - Rationale: Changing DTO shapes would risk dashboard and persistence regressions unrelated to OOP structure.
  - Trade-offs: Domain modeling remains pragmatic rather than a full entity rewrite.
- Decision: Avoid new runtime dependencies and DI frameworks.
  - Rationale: The product baseline is standard-library only and already testable with `unittest`.
  - Trade-offs: Dependency injection will be manual through constructors.
- Decision: Use tests and fixture-backed CLI runs as the primary compatibility gate.
  - Rationale: The refactor should preserve behavior while changing structure.
  - Trade-offs: Some architecture quality remains review-based rather than fully machine-verifiable.

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| Refactor changes persisted JSON shapes | High | Preserve dictionary contracts and run fixture-backed write tests | Backend Agent |
| Dry-run accidentally writes state or sends alerts | High | Keep send/write gates test-covered before and after coordinator refactor | Backend Agent |
| Public wrappers hide incomplete OOP migration | Medium | Track remaining procedural orchestration in F-003 QA | QA Agent |
| Missing workflow `.agent.md` files weaken lifecycle evidence | Low | Record the gap and use available same-role `.toml` specs | Codex |
