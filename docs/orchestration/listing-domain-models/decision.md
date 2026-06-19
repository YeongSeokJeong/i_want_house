# Session Decisions

## Task Context
- Task Name: Listing/Candidate/Run domain models
- Task ID: listing-domain-models

## Decision Log
| Session | Feature ID | Feature | Decision | Rationale | Impact | Date |
|---------|------------|---------|----------|-----------|--------|------|
| 1 | PLAN | Planning | Split domain model work into conversion, analyzer/validator adoption, and persistence/feed adoption | Keeps cross-module refactor reviewable and preserves JSON compatibility after each feature | Enables incremental verification and feature-scoped commits | 2026-06-20 |
| 1 | PLAN | Planning | Use independent worktree `D:/git/i_want_house_listing-domain-models` and branch `task/listing-domain-models` | Source-code lifecycle requires implementation outside the primary checkout | Keeps unattended backlog work isolated from the main worktree | 2026-06-20 |

## Session 1
- Feature ID: F-001
- Feature: Domain conversion layer
- Decisions:
  - Model conversion helpers will preserve unknown fields to avoid breaking provider-specific listing metadata and existing JSON projections.
  - Public module contracts stay dict-compatible until each caller is explicitly migrated.
- Alternatives Considered:
  - Rewrite analyzer, validator, and persistence in one feature: rejected because it would make verification and rollback too broad for one hourly run.
  - Use `TypedDict` only: rejected because runtime conversion/validation is needed at module boundaries.
- Risks Introduced:
  - Partial adoption can leave both dict and typed paths temporarily present.
- Follow-up Notes:
  - F-002 and F-003 should remove duplicate ad hoc field access where the typed boundary is adopted.
  - Verification passed with `python -m unittest tests.test_models -v` and `python -m unittest discover -s tests -v`.
