# Session Decisions

## Task Context
- Task Name: Loop diagnostics service
- Task ID: loop-diagnostics-service

## Decision Log
| Session | Feature ID | Feature | Decision | Rationale | Impact | Date |
|---------|------------|---------|----------|-----------|--------|------|
| 1 | PLAN | Planning | Use a single feature for diagnostic projection extraction | The backlog item is a bounded refactor with existing regression coverage around health and collector diagnostics | Keeps this hourly loop reviewable and finishable | 2026-06-19 |
| 1 | PLAN | Planning | Use stacked branch `task/loop-diagnostics-service-stacked` on `task/listing-source-adapters-closeout` | `origin/main` still records BL-20260618-002 as Doing, while closeout PR #15 marks it Done | Keeps this task diff scoped while respecting the backlog concurrency guard | 2026-06-19 |

## Session 1
- Feature ID: F-001
- Feature: Diagnostic projection service
- Decisions:
  - Preserve all existing diagnostic JSON keys and values.
  - Make the diagnostics service injectable through `LoopCoordinator` for deterministic tests.
  - Keep environment reading inside the diagnostics service boundary.
- Alternatives Considered:
  - Keep module-level helper functions in `loop.py`: rejected because it does not complete the backlog goal.
  - Move health persistence into the new module: rejected because persistence splitting is a separate backlog item.
- Risks Introduced:
  - A subtle source-kind inference change could alter dashboard diagnostics.
- Follow-up Notes:
  - If durable enough after implementation, update the JeonseLoop wiki architecture note during closeout.
