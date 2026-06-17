# Dashboard Criteria Suggestions Handoff

## Summary
- Completed backlog item `BL-20260617-007`.
- The dashboard now has a review-only criteria suggestion panel backed by optional `data/state/criteria-suggestions.json`.

## Delivered
- Added a `기준 조정 제안` panel.
- Rendered suggestion metrics: status, decision count, false-positive signals, false-positive ratio, generated time, and auto-apply state.
- Rendered suggestion items with reason labels, signal labels, decision counts, human-approval markers, and proposal text.
- Treated missing `criteria-suggestions.json` as a normal waiting state rather than a dashboard failure.
- Updated static dashboard tests and the JeonseLoop domain wiki.

## Verification
- `node --check assets/dashboard.js`
- `python -m unittest discover -s tests -v`
- Local static HTTP smoke: `/` and `/assets/dashboard.js` returned 200; `/data/state/criteria-suggestions.json` returned expected 404 for the empty-state path.

## Follow-up
- Suggestion generation remains unchanged and still requires enough `logs/criteria-log.md` volume.
- Suggestions remain review artifacts only and do not mutate `config/watchlist.yaml`.
