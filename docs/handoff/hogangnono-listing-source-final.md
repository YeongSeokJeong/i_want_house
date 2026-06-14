# Hogangnono Listing Source Final Handoff

**Date**: 2026-06-15
**Branch**: task/hogangnono-listing-source
**Author**: Codex

## Summary
- Implemented `JEONSELOOP_LISTING_SOURCE_KIND=hogangnono` as a live listing source mode.
- Added `JEONSELOOP_HOGANGNONO_APT_HASH_MAP` so local watchlist complex IDs can map to Hogangnono apt hashes such as `E152` and `B11b`.
- Queried Hogangnono sale listings through `/api/v2/apts/{aptHash}/items` with `tradeTypes=0`, pagination, and bounded page size/page count.
- Normalized Hogangnono payload fields into JeonseLoop listing records: stable listing ID, KRW price, m2 area, floor, link, source, dates, and description.
- Wired GitHub Actions, `.env.example`, README, and wiki domain documentation for the new source mode.

## Delivered Feature
| Feature ID | Feature | Status | Evidence |
|------------|---------|--------|----------|
| F-001 | Hogangnono listing source | Done | `python -m unittest discover -s tests` passed 64 tests; fixture dry-run passed; live `E152` API smoke returned 1 normalized record. |

## Key Files
- `src/jeonseloop/sources.py`: `HogangnonoSourceConfig`, `HogangnonoListingSourceClient`, source selection, and normalization helpers.
- `tests/test_reliability.py`: mapping, direct apt hash, normalization, bad payload, and failure preservation coverage.
- `tests/test_workflow.py`: GitHub Actions environment variable wiring coverage.
- `.github/workflows/jeonseloop.yml`: Hogangnono variables passed into scheduled/manual runs.
- `.env.example`: placeholder-only Hogangnono settings.
- `README.md`: Korean operator setup guide for Hogangnono source mode.
- `docs/wiki/domains/jeonseloop/overview.md`: durable domain note under `## 호갱노노 매물 수집`.

## Decisions
- Use configurable apt hash mapping instead of hard-coding operator values.
- Allow direct alphanumeric apt hashes in watchlist `complex_id` for simple single-source setups.
- Treat empty Hogangnono item arrays as successful collection.
- Do not bypass rate limits, login prompts, or schema/access changes; record them as collector failures.

## Verification
- `python -m unittest discover -s tests`: 64 tests passed.
- `powershell -File scripts/run-loop.ps1 -DryRun -Fixture tests\fixtures\listings.json`: success, 1 planned notification, 0 sends.
- Live smoke with `HogangnonoListingSourceClient(HogangnonoSourceConfig({}, page_size=1, max_pages=1))` and `WatchTarget('E152', ...)`: returned 1 normalized record with `listing_id=hogangnono:177322`, `price_krw=1300000000`, `area_m2=114.65`.

## Residual Risks
- Hogangnono public endpoints may change without notice.
- Operator must set `JEONSELOOP_LISTING_SOURCE_KIND=hogangnono` and `JEONSELOOP_HOGANGNONO_APT_HASH_MAP` in GitHub variables/secrets for local complex IDs.
- Telegram live sends were not executed because `--send` was not requested.
