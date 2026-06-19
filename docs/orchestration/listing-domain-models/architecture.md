# Architecture Review

## Task Context
- Task Name: Listing/Candidate/Run domain models
- Task ID: listing-domain-models
- Last Updated: 2026-06-20

## System Context
- Current Stack: Python standard library modules, `unittest`, static HTML/CSS/JavaScript dashboard.
- Existing Patterns: product loop composes collector, validator, analyzer, diagnostics, persistence, notifier, and review services through `LoopCoordinator`; public JSON contracts are dict-based.
- Integration Points: listing source adapters, watchlist criteria, trade baselines, JSON state files under `data/`, Telegram notification text, dashboard feed JSON.

## Feature Decomposition Map
| Feature ID | Feature | Description | Depends On | Complexity | Risk |
|------------|---------|-------------|------------|------------|------|
| F-001 | Domain conversion layer | Introduce typed dataclass conversion helpers with dict round-trip compatibility | None | Medium | Medium |
| F-002 | Analyzer and validator adoption | Apply typed boundaries where listings and candidates are validated and scored | F-001 | Medium | Medium |
| F-003 | Persistence and feed adoption | Apply typed run/feed projections for persisted JSON state | F-001,F-002 | High | High |

## Dependency Map
- `src/jeonseloop/sources/` -> listing dicts (provider-normalized fields).
- `src/jeonseloop/validator.py` -> listing dict validation and normalization checks.
- `src/jeonseloop/analyzer.py` -> candidate dict enrichment and decision metadata.
- `src/jeonseloop/persistence.py` -> listing/history/health/feed JSON output.
- `assets/dashboard.js` -> persisted JSON contracts; must not require a coordinated frontend change for F-001.

## Technical Decisions
- Decision: introduce `models.py` as a conversion layer before broad caller migration.
  - Rationale: it creates a testable contract without changing runtime behavior in the same step.
  - Trade-offs: temporary duplication remains until F-002/F-003 adopt the helpers.
- Decision: preserve unknown dict keys in model extras.
  - Rationale: provider-specific metadata, diagnostics, and dashboard fields may be added by independent modules.
  - Trade-offs: dataclasses cannot fully prevent arbitrary extra data, but they clarify core fields.

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| JSON compatibility regression in dashboard or Telegram output | High | Round-trip tests and full unittest discovery before closeout | Codex |
| Over-broad refactor exceeds unattended loop timebox | Medium | Feature-scope commits and stop at verified boundaries | Codex |
| Model helpers become unused abstraction | Medium | F-002 and F-003 explicitly adopt module boundaries after F-001 | Codex |
