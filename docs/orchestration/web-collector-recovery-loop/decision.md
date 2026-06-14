# Session Decisions

## Task Context
- Task Name: Naver Real Estate Web Collector Recovery Loop
- Task ID: web-collector-recovery-loop

## Decision Log
| Session | Feature ID | Feature | Decision | Rationale | Impact | Date |
|---------|------------|---------|----------|-----------|--------|------|
| 1 | PLAN | Planning | Use reviewable recovery, not direct self-modifying main pushes | Web-source failures can be caused by site controls or contract changes and need human review before production changes | Recovery loop will produce diagnostics/reports/PR candidates, not unreviewed deploys | 2026-06-14 |
| 1 | PLAN | Planning | Preserve existing HTTP JSON source mode | Existing Actions and tests rely on this contract and it remains useful for fixtures or future official APIs | Naver source is additive | 2026-06-14 |
| 1 | F-001 | Collector source contract | Select Naver through `JEONSELOOP_LISTING_SOURCE_KIND=naver` and map watchlist IDs with `JEONSELOOP_NAVER_COMPLEX_NO_MAP` | The existing watchlist ID may be a stable local ID rather than Naver's numeric complex number | Supports both local stable IDs and numeric Naver IDs without hard-coding operator data | 2026-06-14 |

## Session 1
- Feature ID: PLAN
- Feature: Planning
- Decisions:
  - Treat Naver Real Estate collection as best-effort public web collection.
  - Do not implement CAPTCHA, login, session bypass, or anti-blocking stealth behavior.
  - Keep automatic repair as a reviewable workflow artifact or branch/PR candidate.
- Alternatives Considered:
  - Direct self-healing commits to `main`: rejected because source parsing failures can produce unsafe production changes.
  - Replace HTTP JSON source entirely: rejected because the existing contract is simpler and tested.
- Risks Introduced:
  - Naver endpoint structures can change without notice.
  - Public web access can be rate limited or blocked.
- Follow-up Notes:
  - F-002 should use fixture-backed tests so local verification does not depend on live Naver availability.
