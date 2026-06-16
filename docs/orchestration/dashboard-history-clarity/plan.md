# Plan: Dashboard History Clarity

## Task
Expose JeonseLoop collection/search run history in the static dashboard and clarify that the trend chart is based on collected listing asking prices, not an authoritative market index.

## Backlog
- `BL-20260617-001`: Dashboard run history and price trend clarity.
- Related future work: `BL-20260617-002`: Cross-check Hogangnono zero-sale-listing complexes and improve diagnostics.

## Features
- `F-001`: Render recent GitHub Actions collection/search runs from `data/state/health.json`.
- `F-002`: Clarify the chart label, explanation, legend, and selected-complex summary.
- `F-003`: Replace placeholder dashboard complex metadata with current watchlist complexes.

## Acceptance Criteria
- The dashboard has a visible "recent collection/search history" section populated from `health.runs`.
- The chart heading and copy explain that the values are collected listing asking price history.
- A selected complex with zero listing history shows a clear "0 listings recorded" summary instead of a generic missing-history message only.
- Static tests cover the new UI affordances and data fetch expectations.
- Existing unittest suite passes.

## Verification Plan
- `node --check assets/dashboard.js`
- `python -m unittest discover -s tests`
- Local static HTTP smoke check for `index.html`, dashboard assets, and committed JSON state.
