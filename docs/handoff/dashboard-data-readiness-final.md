# Dashboard Data Readiness Handoff

## Summary
- Completed backlog item `BL-20260617-008`.
- The dashboard now separates data readiness from price/market state for each watched complex.

## Delivered
- Added `데이터 품질/기준선 준비 상태` panel.
- Rendered latest collection time, listing count, consecutive zero-listing streak, trade baseline readiness, source collection state, and inferred quality block state.
- Reused existing `health.json`, `history/*.json`, and `urgent-feed.json` state.
- Kept collector, analyzer, and persistence behavior unchanged.
- Updated static dashboard tests and the JeonseLoop domain wiki.

## Verification
- `node --check assets/dashboard.js`
- `python -m unittest discover -s tests -v`
- Local static HTTP smoke: `/`, `/assets/dashboard.js`, and `/data/state/health.json` returned 200.

## Follow-up
- Quality block status is currently inferred from feed reasons such as `average_price_jump`.
- If quality-block contracts expand, update `qualityBlockStatus` and the wiki wording together.
