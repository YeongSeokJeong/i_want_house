# Task Plan

## Task Metadata
- Task Name: Switch listing source to Hogangnono
- Task ID: hogangnono-listing-source
- Task Branch: task/hogangnono-listing-source
- Task Worktree: D:\git\i_want_house
- Plan Version: v1
- Last Updated: 2026-06-15

## Planning Assumptions
- The backlog item provides enough requirement detail; no user interview is needed before implementation.
- Hogangnono apartment hashes are operator-managed configuration values and must not be hard-coded into source.
- The collector should keep the existing source client pattern and preserve validate-before-replace behavior on failures.
- Public Hogangnono endpoints may change; failures must surface as collector failures with redacted diagnostics.

## Related Wiki Discovery
- `docs/wiki/domains/jeonseloop/overview.md`: records the existing Naver source mode and collector recovery loop; needs a Hogangnono source note during closeout.
- `docs/wiki/decisions/jeonseloop-open-requirement-decisions.md`: existing data source decision remains compatible; no new human decision document is required.
- Gap: document `JEONSELOOP_LISTING_SOURCE_KIND=hogangnono`, hash mapping, trade type, and fallback risk after implementation.

## Related Backlog Items
| Backlog ID | Route | Status | Relationship |
|------------|-------|--------|--------------|
| BL-20260615-001 | source-code | Doing | Parent task item for the Hogangnono source migration |

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | Hogangnono listing source | Add Hogangnono source selection, mapping, normalization, tests, workflow configuration, and operator docs | None | High | Backend Agent |

## Feature Detail
### F-001 Hogangnono listing source
- Scope:
  - Add `JEONSELOOP_LISTING_SOURCE_KIND=hogangnono` source client.
  - Add Hogangnono apt hash mapping configuration for watchlist complex IDs.
  - Query sale listings with `tradeTypes=0`.
  - Normalize Hogangnono price, area, floor, title, description, date, and link fields into JeonseLoop listing records.
  - Pass new settings through GitHub Actions, `.env.example`, README, tests, and wiki closeout.
- Acceptance Criteria:
  - [x] `listing_fetcher_from_env` returns a Hogangnono fetcher when `JEONSELOOP_LISTING_SOURCE_KIND=hogangnono`.
  - [x] Named watchlist targets require `JEONSELOOP_HOGANGNONO_APT_HASH_MAP`; direct apt hashes are accepted without mapping.
  - [x] The client requests `/api/v2/apts/{aptHash}/items` with `tradeTypes=0`, pagination, and bounded limits.
  - [x] Hogangnono payloads normalize to JeonseLoop listing records with stable `listing_id`, KRW price, m2 area, source, and inspectable link.
  - [x] Bad payloads and HTTP failures are reported as source failures without replacing previous state.
  - [x] GitHub Actions and operator docs expose the Hogangnono configuration without committing secrets.
  - [x] Full unit test suite passes.
- Out of Scope:
  - Authenticated Hogangnono scraping or bypassing rate limits.
  - Automatic discovery of Hogangnono apt hashes from apartment names.
  - Telegram send verification.

## Execution Order
1. F-001

## Revision Policy
- Plan revision is allowed only when scope, constraints, or risks change.
- Any revision must update affected feature IDs in `plan.md` and `progress.md`.
- Use `/large-task-orchestrator revise hogangnono-listing-source` for structural plan changes.

## Revision Log
| Version | Date | Changed Feature IDs | Changed Backlog IDs | Why Revised | Author |
|---------|------|---------------------|---------------------|-------------|--------|
| v1 | 2026-06-15 | F-001 | BL-20260615-001 | Initial planning baseline from backlog item | Codex |
