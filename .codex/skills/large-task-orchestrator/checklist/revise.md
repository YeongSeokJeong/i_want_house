# /large-task-orchestrator revise Checklist

Exit criteria for documentation-only continuity updates.

## Checklist

- [ ] `<task-name>` is resolved and `./docs/orchestration/<task-name>/` is selected.
- [ ] `plan.md`, `progress.md`, `decision.md`, `architecture.md` are loaded before revision.
- [ ] Linked `BL-*` items are checked in `docs/backlog.md` when present.
- [ ] Workflow runs in strict order: Brainstorming -> PM -> Architecture -> QA.
- [ ] No code implementation is performed.
- [ ] Revised feature IDs and dependency impacts are explicitly listed.
- [ ] `plan.md` revision includes version bump + revision log when scope/structure changed.
- [ ] `Task Branch` and `Task Worktree` metadata are preserved and synchronized between `plan.md` and `progress.md`.
- [ ] `BL-*` links and routes stay synchronized between orchestration docs and `docs/backlog.md`.
- [ ] `progress.md` status/session impacts are synchronized with revised plan.
- [ ] Backlog rows are updated only when route, status, blocker, or follow-up scope changed.
- [ ] `decision.md` captures rationale and decision timestamp.
- [ ] QA gate result for the revision package is recorded.
