# Decisions: Dashboard History Clarity

## D-001: Use Existing Persisted State
- Date: 2026-06-17
- Decision: The dashboard will render run/search history from `data/state/health.json` and per-complex summaries from `data/history/*.json`.
- Rationale: The requested history already exists in committed state files from the Actions loop. Reusing it avoids adding a new persistence path and keeps GitHub Pages static.

## D-002: Rename Trend Semantics
- Date: 2026-06-17
- Decision: The chart will be labeled as collected listing asking price history instead of generic market price trend.
- Rationale: Current values are derived from collected listing minimum/average asking prices, with recent trade price only available when a baseline source provides it. Calling it market trend overstates the data.
