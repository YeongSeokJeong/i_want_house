# /large-task-orchestrator revise Checklist

Exit criteria for documentation-only continuity updates.

## Checklist

- [ ] `<task-name>` is resolved and `./docs/orchestration/<task-name>/` is selected.
- [ ] `plan.md`, `progress.md`, `decision.md`, `architecture.md` are loaded before revision.
- [ ] Workflow runs in strict order: Brainstorming -> PM -> Architecture -> QA.
- [ ] No code implementation is performed.
- [ ] Revised feature IDs and dependency impacts are explicitly listed.
- [ ] `plan.md` revision includes version bump + revision log when scope/structure changed.
- [ ] `Task Branch` metadata is preserved and synchronized between `plan.md` and `progress.md`.
- [ ] `progress.md` status/session impacts are synchronized with revised plan.
- [ ] `decision.md` captures rationale and decision timestamp.
- [ ] QA gate result for the revision package is recorded.
