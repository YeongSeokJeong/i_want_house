# Task Plan

## Task Metadata
- Task Name: Listing/Candidate/Run domain models
- Task ID: listing-domain-models
- Task Branch: task/listing-domain-models
- Task Worktree: D:/git/i_want_house_listing-domain-models
- Plan Version: v1
- Last Updated: 2026-06-20

## Planning Assumptions
- Existing JSON input and output shapes must remain backward compatible.
- The first useful boundary is a typed conversion layer, not a broad rewrite of the loop.

## Related Backlog Items
| Backlog ID | Route | Status | Relationship |
|------------|-------|--------|--------------|
| BL-20260618-006 | source-code | Doing | Parent task item for this orchestration |

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | Domain conversion layer | Add typed Listing/Candidate/Run model conversion helpers while preserving dict compatibility | None | Medium | Codex |
| F-002 | Analyzer and validator adoption | Use model conversion at analyzer/validator module boundaries | F-001 | Medium | Codex |
| F-003 | Persistence and feed adoption | Use typed run/feed conversion for persisted health and urgent-feed projections | F-001,F-002 | High | Codex |

## Feature Detail
### F-001 Domain conversion layer
- Scope:
  - Add `src/jeonseloop/models.py` with dataclasses and `from_dict`/`to_dict` helpers for normalized listing, candidate, and run records.
  - Add focused tests for missing optional fields, unknown field preservation, and JSON-compatible output.
- Acceptance Criteria:
  - [ ] Model helpers round-trip existing fixture-shaped dicts without dropping unknown keys.
  - [ ] Required field validation errors are explicit at conversion boundaries.
  - [ ] Existing tests continue to pass.
- Out of Scope:
  - Rewriting every caller in the same feature.

### F-002 Analyzer and validator adoption
- Scope:
  - Convert analyzer/validator boundary logic to use typed listing/candidate helpers internally.
  - Keep public return values as dict-compatible JSON structures.
- Acceptance Criteria:
  - [ ] Analyzer candidate output remains compatible with existing notifier/dashboard tests.
  - [ ] Validator rejects malformed listing input through the typed boundary with unchanged user-facing behavior.
- Out of Scope:
  - Persistence repository decomposition.

### F-003 Persistence and feed adoption
- Scope:
  - Convert health run and urgent feed projection paths to explicit model helpers.
  - Keep validate-before-replace writes and current JSON filenames unchanged.
- Acceptance Criteria:
  - [ ] `health.json` and `urgent-feed.json` output remain schema-compatible.
  - [ ] Persistence tests cover model-backed projection paths.
  - [ ] Full test suite passes.
- Out of Scope:
  - New environment variables or behavior changes.

## Execution Order
1. F-001
2. F-002
3. F-003

## Revision Log
| Version | Date | Changed Feature IDs | Changed Backlog IDs | Why Revised | Author |
|---------|------|---------------------|---------------------|-------------|--------|
| v1 | 2026-06-20 | F-001,F-002,F-003 | BL-20260618-006 | Initial planning baseline | Codex |
