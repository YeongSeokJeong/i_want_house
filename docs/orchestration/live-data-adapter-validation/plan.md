# Task Plan

## Task Metadata
- Task Name: Live data adapter validation
- Task ID: live-data-adapter-validation
- Task Branch: task/live-data-adapter-validation
- Task Worktree: D:\git\i_want_house
- Plan Version: v1
- Last Updated: 2026-06-14

## Planning Assumptions
- BL-20260613-007 is the highest-priority source-code backlog item because live listing and trade inputs are the main remaining runtime risk.
- Real external portal/API availability, credentials, and terms compliance remain external-state checks and cannot be proven from this repository alone.
- The repository should fail visibly when live listing collection is requested without a configured live source instead of silently treating an empty adapter as success.
- A generic HTTP JSON adapter contract is safer than hard-coding a portal scraper in this repository without verified source documentation and credentials.

## Related Backlog Items
| Backlog ID | Route | Status | Relationship |
|------------|-------|--------|--------------|
| BL-20260613-007 | source-code | Doing | Parent task item for this orchestration |

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | Live source adapter guardrails | Add repo-verifiable adapter configuration, visible missing-source failure, and tests for live listing/trade adapter paths | None | Medium | Backend Agent |

## Feature Detail
### F-001 Live source adapter guardrails
- Scope:
  - Add a configurable HTTP JSON listing adapter for live collection.
  - Add a configurable HTTP JSON trade adapter for recent trade baselines.
  - Make unconfigured live listing collection fail with health state instead of returning empty success.
  - Document required environment placeholders without committing secrets.
  - Add unit tests for adapter payload parsing, missing-source failure, and loop health behavior.
- Acceptance Criteria:
  - [ ] Without fixture and without live listing source configuration, a non-dry run records failed health with a source configuration reason.
  - [ ] A configured HTTP JSON listing source can return watchlist-limited listing records through the existing collector.
  - [ ] A configured HTTP JSON trade source can feed trade baseline calculation without replacing local cache files.
  - [ ] Existing fixture-backed loop behavior and tests keep passing.
  - [ ] `.env.example` documents only placeholder environment variables.
- Out of Scope:
  - Hard-coded scraping of a specific real-estate portal.
  - Live credential validation against external services from this repo session.
  - Automatic mutation of `config/watchlist.yaml`.

## Execution Order
1. F-001

## Revision Log
| Version | Date | Changed Feature IDs | Changed Backlog IDs | Why Revised | Author |
|---------|------|---------------------|---------------------|-------------|--------|
| v1 | 2026-06-14 | F-001 | BL-20260613-007 | Initial planning baseline from current backlog priority | Codex |
