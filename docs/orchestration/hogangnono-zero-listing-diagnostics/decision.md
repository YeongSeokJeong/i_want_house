# Session Decisions

## Task Context
- Task Name: Hogangnono zero-listing diagnostics
- Task ID: hogangnono-zero-listing-diagnostics

## Decision Log
| Session | Feature ID | Feature | Decision | Rationale | Impact | Date |
|---------|------------|---------|----------|-----------|--------|------|
| 1 | PLAN | Planning | Split source diagnostics from dashboard visibility | The data contract should be stable before UI copy and live evidence are added | Keeps F-001 testable and limits risk | 2026-06-17 |
| 1 | F-001 | Source diagnostic contract | Record current checkout as the task worktree | The workspace already contains related uncommitted backlog rows, so moving to another worktree would risk losing context | All feature commits will land on `task/hogangnono-zero-listing-diagnostics` | 2026-06-17 |

## Session 1
- Feature ID: F-001
- Feature: Source diagnostic contract
- Decisions:
  - Successful empty Hogangnono responses will be treated as a collection diagnostic status, not a failed run.
  - External live API state will be recorded as evidence, but code behavior will remain repo-verifiable through fixtures/mocked openers.
  - `listing_diagnostics` is stored inside the normal run record so `health.latest` and `health.runs` share the same contract.
- Alternatives Considered:
  - Fail the run when a complex returns zero listings: rejected because a real no-listing market state should not be a runtime failure.
  - Store diagnostics only in `collector-diagnostics.json`: rejected because that file currently represents failures, while this task needs successful empty-response evidence in normal health.
- Risks Introduced:
  - If too much source-specific detail leaks into the generic health contract, dashboard code may couple to Hogangnono internals.
- Follow-up Notes:
  - `python -m unittest discover -s tests -v` passed 67 tests on 2026-06-17.
  - F-002 should keep UI copy focused on operator interpretation, not raw implementation details.
