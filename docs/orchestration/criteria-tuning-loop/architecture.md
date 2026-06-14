# Architecture Review

## Task Context
- Task Name: Criteria tuning loop
- Task ID: criteria-tuning-loop
- Last Updated: 2026-06-14

## System Context
- Current Stack: Python standard library, unittest, JSON/Markdown state files, static dashboard assets.
- Existing Patterns: `LoopCoordinator` orchestrates collector, validator, analyzer, review, notification, persistence, and suggestion services; JSON state writes use validate-before-replace paths.
- Integration Points: `logs/criteria-log.md`, `data/state/criteria-suggestions.json`, `config/watchlist.yaml`, optional OpenAI review.

## Feature Decomposition Map
| Feature ID | Feature | Description | Depends On | Complexity | Risk |
|------------|---------|-------------|------------|------------|------|
| F-001 | Criteria metrics and suggestions | Parse criteria logs into false-positive metrics and review-required suggestions | None | Medium | Medium |

## Dependency Map
- `LoopStateRepository.persist_cycle` -> `write_criteria_suggestions` after appending criteria decisions.
- `CriteriaSuggestionService` -> `logs/criteria-log.md` for decision rows.
- `CriteriaSuggestionService` -> `data/state/criteria-suggestions.json` for operator review artifact.

## Technical Decisions
- Decision: Extend `CriteriaSuggestionService` instead of adding a new service.
  - Rationale: Existing service already owns criteria-log parsing and suggestion output.
  - Trade-offs: Keeps scope small, but reason-prefix heuristics should be revisited after real data labels exist.
- Decision: Keep JSON output backward-compatible with `suggestions`, `status`, and `auto_applied`.
  - Rationale: Existing tests and operator expectations depend on review-only suggestions.
  - Trade-offs: Adds nested metrics rather than replacing the payload.

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| False-positive ratio is inferred from reasons instead of explicit operator labels | Medium | Keep reason counts visible and record future explicit-label follow-up if needed | Backend Agent |
| Suggestion generation could accidentally mutate configuration | High | Test `config/watchlist.yaml` remains unchanged and keep service write target limited to `data/state/criteria-suggestions.json` | Backend Agent |
