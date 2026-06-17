# Dashboard Criteria Thresholds Handoff

## Summary
- Completed backlog item `BL-20260617-004`.
- The dashboard monitoring summary now explains which urgent threshold criterion is applied and how far the current minimum listing price remains above the urgent line.

## Delivered
- Added `적용 기준` and `급매선까지` columns to the first-screen monitoring summary.
- Added dashboard helpers for criterion calculation and remaining-to-urgent-line formatting.
- Kept calculations client-side because the dashboard already has watchlist metadata and latest history values.
- Updated static dashboard tests for the new labels and helper functions.
- Updated `docs/wiki/domains/jeonseloop/overview.md` `## 핵심 내용` with the dashboard interpretation rule.

## Verification
- `node --check assets/dashboard.js`
- `python -m unittest discover -s tests -v`
- Local static HTTP smoke: `/` and `/assets/dashboard.js` returned 200.

## Follow-up
- `BL-20260617-006` remains the backlog item for pre-urgent grading and should not be treated as covered by this threshold-detail task.
