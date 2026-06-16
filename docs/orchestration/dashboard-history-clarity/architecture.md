# Architecture: Dashboard History Clarity

## Data Sources
- `data/state/health.json`
  - `latest`: latest loop run status and counts.
  - `runs`: historical loop executions used for the collection/search history panel.
- `data/history/<complex_id>.json`
  - `history`: per-run complex listing counts and collected price aggregates.
- `data/state/urgent-feed.json`
  - Existing candidate feed source; unchanged.

## UI Flow
1. `initComplexSelect` renders current watchlist complex options.
2. `renderHealth` loads `health.json`, updates latest status metrics, and renders recent runs.
3. `renderSelectedComplex` loads the selected complex history and feed.
4. `renderHistory` updates the selected-complex summary and chart/empty state.

## Non-Goals
- No new external data collection.
- No Telegram send behavior changes.
- No modification to Actions secrets, repository variables, or persisted state schemas.
