# Session Decisions

## Task Context
- Task Name: Dashboard criteria thresholds
- Task ID: dashboard-criteria-thresholds

## Decision Log
| Session | Feature ID | Feature | Decision | Rationale | Impact | Date |
|---------|------------|---------|----------|-----------|--------|------|
| 1 | PLAN | Planning | Extend client-side monitoring summary | The required data is already available to the static dashboard | Avoids backend churn while satisfying UI clarity | 2026-06-17 |

## Session 1
- Feature ID: F-001
- Feature: Criteria threshold details
- Decisions:
  - Show applied criterion as either `희망가 상한` or `실거래 할인선` depending on which value forms the urgent line.
  - Keep remaining amount as positive over-line amount and show `도달/초과` when the current listing is already at or below the urgent line.
- Alternatives Considered:
  - Add a persisted projection in `data/state/`: deferred because static calculation is sufficient and avoids introducing another state contract.
- Risks Introduced:
  - Client-side criterion labels must remain aligned with analyzer behavior.
- Follow-up Notes:
  - Verification passed with `node --check assets/dashboard.js`, `python -m unittest discover -s tests -v`, and local static HTTP smoke (`/`, `/assets/dashboard.js` returned 200).
