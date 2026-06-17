# Session Decisions

## Task Context
- Task Name: Hogangnono missing map diagnostics
- Task ID: hogangnono-missing-map-diagnostics

## Decision Log
| Session | Feature ID | Feature | Decision | Rationale | Impact | Date |
|---------|------------|---------|----------|-----------|--------|------|
| 1 | PLAN | Planning | Keep missing mapping as collector failure with richer diagnostics | Missing mapping is an operator configuration problem, not a recoverable collection success | Preserves previous state while making the fix clear | 2026-06-17 |

## Session 1
- Feature ID: F-001
- Feature: Missing map diagnostics
- Decisions:
  - Add actionable example JSON entries instead of trying to infer hashes.
  - Keep diagnostics secret-safe and only include complex IDs and placeholder values.
- Alternatives Considered:
  - Auto-search hashes from Hogangnono: rejected because it adds live external discovery and risk.
- Risks Introduced:
  - None beyond existing collector failure path.
- Follow-up Notes:
  - Verification passed with targeted reliability tests and `python -m unittest discover -s tests -v`.
