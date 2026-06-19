# Session Decisions

## Task Context
- Task Name: Listing/Candidate/Run domain models
- Task ID: listing-domain-models

## Decision Log
| Session | Feature ID | Feature | Decision | Rationale | Impact | Date |
|---------|------------|---------|----------|-----------|--------|------|
| 1 | PLAN | Planning | Split domain model work into conversion, analyzer/validator adoption, and persistence/feed adoption | Keeps cross-module refactor reviewable and preserves JSON compatibility after each feature | Enables incremental verification and feature-scoped commits | 2026-06-20 |
| 1 | PLAN | Planning | Use independent worktree `D:/git/i_want_house_listing-domain-models` and branch `task/listing-domain-models` | Source-code lifecycle requires implementation outside the primary checkout | Keeps unattended backlog work isolated from the main worktree | 2026-06-20 |
| 1 | F-002 | Analyzer and validator adoption | Normalize listing records through `NormalizedListing` at analyzer and validator boundaries | Moves field coercion and required-field checks into the shared model layer without changing public dict output | Reduces duplicated validation logic before persistence adoption | 2026-06-20 |
| 1 | F-003 | Persistence and feed adoption | Normalize run records and feed items through model helpers before JSON persistence | Keeps state-file writers tied to explicit contracts while preserving validate-before-replace writes | Makes health/feed schema drift easier to catch in tests | 2026-06-20 |

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

## Session 1 F-002
- Feature ID: F-002
- Feature: Analyzer and validator adoption
- Decisions:
  - `ListingValidator` maps `ModelValidationError` back to existing validation reason strings so current health and criteria logs remain stable.
  - `CandidateAnalyzer` normalizes each listing once at the classification boundary and still returns the existing `Candidate` dataclass with dict-compatible listing payloads.
- Alternatives Considered:
  - Replace `Candidate` with `CandidateRecord` immediately: rejected because notifier/review/persistence callers can be migrated more safely with feed persistence in F-003.
- Risks Introduced:
  - Analyzer now raises model validation errors if called with unvalidated records; current production flow validates first, and tests cover the service boundary.
- Follow-up Notes:
  - F-003 should use `RunRecord` and `FeedItem` in persistence while preserving the exact JSON fields consumed by the dashboard.

## Session 1 F-003
- Feature ID: F-003
- Feature: Persistence and feed adoption
- Decisions:
  - `LoopStateRepository` converts incoming run records through `RunRecord` before writing health/history/feed state.
  - Urgent feed item projection now builds through `FeedItem` before atomic JSON write.
- Alternatives Considered:
  - Convert all listing snapshots in persistence immediately: rejected because analyzer/validator already own listing normalization for this task and snapshot shape should stay provider-compatible.
- Risks Introduced:
  - Count values are coerced to integers in persisted `health.latest.counts`; this matches existing runtime intent and is covered by tests.
- Follow-up Notes:
  - Closeout should update durable architecture notes and close `BL-20260618-006`.
