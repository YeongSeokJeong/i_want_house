# Task Plan

## Task Metadata
- Task Name: Listing source provider adapter split
- Task ID: listing-source-adapters
- Task Branch: task/listing-source-adapters
- Task Worktree: D:/git/i_want_house_listing_source_adapters
- Plan Version: v1
- Last Updated: 2026-06-19

## Planning Assumptions
- `BL-20260618-002` is the parent backlog item for this orchestration.
- Public factory functions in `jeonseloop.sources` must remain import-compatible.
- Provider behavior, environment variable names, and normalized listing JSON contracts must not change.
- The task branch is based on current HEAD because the current backlog items are not present on local `main`.

## Related Backlog Items
| Backlog ID | Route | Status | Relationship |
|------------|-------|--------|--------------|
| BL-20260618-002 | source-code | Doing | Parent task item for this orchestration |

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | Source package extraction | Move shared source contracts, HTTP JSON support, Naver support, and Hogangnono support into `src/jeonseloop/sources/` while preserving the existing public import surface. | None | High | Backend Agent |
| F-002 | Reliability regression coverage | Keep provider-specific parsing, factory, and collector failure tests passing against the new package layout. | F-001 | Medium | QA Agent |
| F-003 | Closeout and handoff | Run focused and full verification, update orchestration/backlog closeout, and record any durable architecture note only if needed. | F-001,F-002 | Medium | Handoff Agent |

## Feature Detail
### F-001 Source package extraction
- Scope:
  - Convert `src/jeonseloop/sources.py` into a compatibility facade over a `sources/` package.
  - Separate common contracts/config helpers, HTTP JSON client, Naver client/normalizer, and Hogangnono client/normalizer.
  - Keep `from jeonseloop.sources import ...` working for existing callers and tests.
- Acceptance Criteria:
  - [ ] Existing imports from `jeonseloop.sources` continue to resolve.
  - [ ] `listing_fetcher_from_env()` and `trade_fetcher_from_env()` return equivalent fetchers for existing environment settings.
  - [ ] Provider-specific error types and messages used by diagnostics remain compatible.
- Out of Scope:
  - Changing provider behavior, environment variable contracts, fallback strategy, or external request semantics.

### F-002 Reliability regression coverage
- Scope:
  - Run existing reliability tests that exercise HTTP JSON, Naver, Hogangnono, and collector failure diagnostics.
  - Add focused import/facade regression coverage only if existing tests do not catch the package split.
- Acceptance Criteria:
  - [ ] `python -m unittest tests.test_reliability -v` passes.
  - [ ] Existing provider normalization tests continue to pass without changing expected data contracts.
  - [ ] No Telegram sends or `--send` usage occurs during verification.
- Out of Scope:
  - Live external portal/API calls.

### F-003 Closeout and handoff
- Scope:
  - Run full test suite if the focused test passes.
  - Update `progress.md`, `decision.md`, `architecture.md`, `docs/backlog.md`, and `reports/backlog-agent-loop.md`.
  - Create a final handoff document if the backlog item reaches `Done`.
- Acceptance Criteria:
  - [ ] `python -m unittest discover -s tests -v` passes or any failure is documented with exact remaining work.
  - [ ] `BL-20260618-002` is `Done` only if implementation and verification are complete.
  - [ ] `reports/backlog-agent-loop.md` records timestamp, selected ID, route, files changed, verification, and remaining work/blocker.
- Out of Scope:
  - PR creation unless lifecycle closeout reaches the required done stage and credentials/network allow it.

## Execution Order
1. F-001
2. F-002
3. F-003

## Revision Policy
- Plan revision is allowed only when scope, constraints, risks, or sequencing change.
- Any revision must run through `/large-task-orchestrator revise listing-source-adapters`.
- Revisions must update affected feature IDs in both `plan.md` and `progress.md`.

## Revision Log
| Version | Date | Changed Feature IDs | Changed Backlog IDs | Why Revised | Author |
|---------|------|---------------------|---------------------|-------------|--------|
| v1 | 2026-06-19 | F-001,F-002,F-003 | BL-20260618-002 | Initial planning baseline | Codex |
