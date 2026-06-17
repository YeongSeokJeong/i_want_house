# Dashboard Rejection Summary Handoff

## Summary
- Completed backlog item `BL-20260617-005`.
- The dashboard now explains why alerts were absent or limited by summarizing candidate decisions and reasons from `data/state/urgent-feed.json`.

## Delivered
- Added a `탈락/보류 사유 요약` dashboard panel above the urgent feed.
- Added aggregate reason counts with Korean labels for common analyzer/review reason strings.
- Added per-complex summaries with approved, held, rejected, and alert-planned counts plus top reasons.
- Kept persistence unchanged because the existing urgent feed already contains `decision`, `reason`, `complex_id`, and `alert_planned`.
- Updated static dashboard tests and the JeonseLoop domain wiki.

## Verification
- `node --check assets/dashboard.js`
- `python -m unittest discover -s tests -v`
- Local static HTTP smoke: `/`, `/assets/dashboard.js`, and `/data/state/urgent-feed.json` returned 200.

## Follow-up
- Browser DOM automation was not run because Playwright is not available in the current Node environment.
- Future analyzer/review reason strings should update `reasonLabel` so the dashboard remains operator-friendly.
