# Architecture Review

## Task Context
- Task Name: Persistence state repositories
- Task ID: persistence-state-repositories
- Last Updated: 2026-06-20

## System Context
- Current Stack: Python standard library, `unittest`, JSON/Markdown file persistence.
- Existing Patterns: Small service classes with module-level compatibility wrappers; validate-before-replace writes through temporary files and `os.replace`.
- Integration Points: `LoopCoordinator`, `CriteriaSuggestionService`, dashboard JSON files under `data/state`, listing/history files under `data/`, and criteria log under `logs/`.

## Feature Decomposition Map
| Feature ID | Feature | Description | Depends On | Complexity | Risk |
|------------|---------|-------------|------------|------------|------|
| F-001 | Split state repository boundaries | Extract focused repositories for listing snapshots, history, notified state, health, urgent feed, and criteria persistence. | None | Medium | Medium |

## Dependency Map
- `LoopCoordinator` -> `LoopStateRepository` (cycle persistence and failure health)
- `LoopStateRepository` -> focused repositories in `state_repositories.py` (delegated persistence responsibilities)
- Focused repositories -> `JsonStateStore` (shared JSON load/write and atomic replacement)
- Criteria persistence -> `CriteriaSuggestionService` (existing suggestion generation behavior)

## Technical Decisions
- Decision: Keep `persistence.py` as the public facade and create `state_repositories.py` for focused storage classes.
  - Rationale: Existing imports remain stable while the implementation boundary becomes testable and narrower.
  - Trade-offs: One facade still coordinates multiple writes, but file-target-specific behavior moves out of the coordinator-facing class.
- Decision: Keep helper functions for feed item projection and diagnostics sanitization importable from the facade where existing callers expect them.
  - Rationale: Avoids broad import churn and keeps compatibility wrappers intact.
  - Trade-offs: Some implementation helpers remain visible, but ownership is clearer.

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| JSON shape regression in health/history/feed files | High | Preserve existing tests and add focused repository coverage. | Backend Agent |
| Accidental non-atomic JSON writes | High | Route JSON writes through `JsonStateStore.atomic_write_json`. | Backend Agent |
| Criteria log behavior changes | Medium | Keep append temp-file replacement behavior and assert generated artifacts in tests. | Backend Agent |

