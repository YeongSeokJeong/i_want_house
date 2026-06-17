# Session Decisions

## Task Context
- Task Name: Dashboard data readiness
- Task ID: dashboard-data-readiness

## Decision Log
| Session | Feature ID | Feature | Decision | Rationale | Impact | Date |
|---------|------------|---------|----------|-----------|--------|------|
| 1 | PLAN | Planning | Compute readiness client-side from existing JSON | Required data is already present in health, history, diagnostics, and urgent feed | Avoids new persistence contracts while improving operator visibility | 2026-06-17 |

## Session 1
- Feature ID: F-001
- Feature: Data readiness panel
- Decisions:
  - Use latest history entries for collection count and trade baseline readiness.
  - Use consecutive trailing zero-listing history entries for zero streak.
  - Infer quality blocks from feed reasons that start with `average_price_jump`.
- Alternatives Considered:
  - Persist a dedicated readiness file: deferred because dashboard projection is sufficient for current needs.
- Risks Introduced:
  - Quality block inference only covers current feed reasons.
- Follow-up Notes:
  - Verification passed with `node --check assets/dashboard.js`, `python -m unittest discover -s tests -v`, and local static HTTP smoke (`/`, `/assets/dashboard.js`, `/data/state/health.json` returned 200).
