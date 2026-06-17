# Session Decisions

## Task Context
- Task Name: Dashboard pre urgent grades
- Task ID: dashboard-pre-urgent-grades

## Decision Log
| Session | Feature ID | Feature | Decision | Rationale | Impact | Date |
|---------|------------|---------|----------|-----------|--------|------|
| 1 | PLAN | Planning | Implement pre-urgent grading as dashboard projection | Existing feed items can be combined with dashboard urgent-line helpers and latest history | Avoids changing analyzer or persistence behavior for a presentation-only task | 2026-06-17 |

## Session 1
- Feature ID: F-001
- Feature: Pre urgent grades
- Decisions:
  - Use urgent-line distance thresholds in the dashboard: at/below urgent line is `급매`, within 5% is `근접`, within 15% is `관심`, otherwise `멀리 있음`.
  - Keep alert planning unchanged and only split rendered feed sections.
- Alternatives Considered:
  - Persist grades in `urgent-feed.json`: deferred until another consumer needs the grade contract.
- Risks Introduced:
  - Dashboard grades are presentation logic and can drift from future analyzer changes.
- Follow-up Notes:
  - Verification passed with `node --check assets/dashboard.js`, `python -m unittest discover -s tests -v`, and local static HTTP smoke (`/`, `/assets/dashboard.js`, `/data/history/baengnyeonsan-hillstate-3.json` returned 200).
