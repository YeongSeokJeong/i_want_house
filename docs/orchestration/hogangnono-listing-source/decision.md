# Session Decisions

## Task Context
- Task Name: Switch listing source to Hogangnono
- Task ID: hogangnono-listing-source

## Decision Log
| Session | Feature ID | Feature | Decision | Rationale | Impact | Date |
|---------|------------|---------|----------|-----------|--------|------|
| 1 | F-001 | Hogangnono listing source | Use `JEONSELOOP_HOGANGNONO_APT_HASH_MAP` for named watchlist IDs and allow direct apt hashes | Watchlist IDs are local stable IDs, while Hogangnono uses apt hashes such as `E152` | Operators can migrate without changing internal complex IDs | 2026-06-15 |
| 1 | F-001 | Hogangnono listing source | Use `/api/v2/apts/{aptHash}/items?tradeTypes=0` as the primary listing API | Hogangnono public web assets define this endpoint and live `E152` requests return sale listings | Keeps implementation API-based and avoids HTML scraping | 2026-06-15 |
| 1 | F-001 | Hogangnono listing source | Treat empty result arrays as successful collection | Some valid apt hashes may currently have no sale items | Avoids false failures for temporarily empty complexes | 2026-06-15 |

## Session 1
- Feature ID: F-001
- Feature: Hogangnono listing source
- Decisions:
  - Add Hogangnono as a third listing source kind alongside HTTP JSON and Naver.
  - Keep all operator-specific apt hashes in environment configuration.
  - Keep network failure handling consistent with existing source clients.
- Alternatives Considered:
  - Scrape `item-catalog` HTML: rejected because the public API endpoint is available and more structured.
  - Replace Naver code entirely: rejected because source selection should remain configurable and reversible.
- Risks Introduced:
  - Hogangnono public endpoints may change schema or access behavior without notice.
- Follow-up Notes:
  - Closeout should update JeonseLoop wiki domain knowledge with the new source mode.
