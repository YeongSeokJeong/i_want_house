# Handoff: Dashboard History Clarity

## Summary
- Added a static dashboard panel that renders recent collection/search executions from `data/state/health.json` `runs`.
- Reframed the chart from generic market trend to collected listing asking price history.
- Added a selected-complex summary that reports latest listing counts and prices, or clearly states when recent collections recorded zero sale listings.
- Replaced the placeholder dashboard complex list with the current watchlist complexes.
- Added backlog item `BL-20260617-002` for a future Hogangnono zero-sale-listing cross-check and diagnostics improvement.

## Files Changed
- `index.html`
- `assets/dashboard.js`
- `assets/dashboard.css`
- `tests/test_dashboard_static.py`
- `docs/backlog.md`
- `docs/wiki/domains/jeonseloop/overview.md`
- `docs/orchestration/dashboard-history-clarity/`

## Verification
- `node --check assets/dashboard.js`
- `python -m unittest discover -s tests -v`
- Local static HTTP smoke check:
  - `/`
  - `/assets/dashboard.js`
  - `/assets/dashboard.css`
  - `/data/state/health.json`
  - `/data/history/baengnyeonsan-hillstate-3.json`
  - `/data/history/bulgwang-miseong.json`

## Notes
- In-app Browser was unavailable in this environment and no local Playwright/Chrome/Edge binary was installed, so visual browser verification was not completed.
- No Telegram send path, GitHub Actions secret, repository variable, or state schema was changed.
