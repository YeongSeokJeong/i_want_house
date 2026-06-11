# /large-task-orchestrator start Checklist

Exit criteria for initializing a large multi-session task.

## Checklist

- [ ] Task name is confirmed with user for `./docs/orchestration/<task-name>/`.
- [ ] If start input is sparse (for example only `/large-task-orchestrator start <task-name>`), requirement interview is completed before deep code reading.
- [ ] Interview output includes explicit in-scope/out-of-scope boundaries, constraints, and testable acceptance criteria.
- [ ] Related-document discovery for the new requirement is run from `graphify-out/GRAPH_REPORT.md` and `graphify-out/graph.json`.
- [ ] If graphify artifacts are missing/stale, `/graphify . --update` refresh is requested and temporary limitations are recorded.
- [ ] Large task is decomposed into discrete functional features with stable IDs (`F-001..F-00N`).
- [ ] Every feature has explicit acceptance criteria.
- [ ] Architecture review includes stack fit, boundaries, dependencies, and major risks.
- [ ] `./docs/orchestration/<task-name>/plan.md` created from schema (`Plan Version: v1`).
- [ ] `./docs/orchestration/<task-name>/progress.md` created from schema and marked `IN_PROGRESS`.
- [ ] `./docs/orchestration/<task-name>/architecture.md` created with decisions, dependency map, and risk register.
- [ ] `./docs/orchestration/<task-name>/decision.md` initialized (or confirmed existing).
- [ ] Plan revision policy is initialized in `plan.md`.
- [ ] A single task branch is created at start and recorded in `plan.md` and `progress.md`.
- [ ] Session 1 summary posted with prioritized feature order and task branch.
