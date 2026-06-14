# /large-task-orchestrator next Checklist

Exit criteria for running `next` as the single lifecycle command.

## Checklist

### Common (Both Modes)

- [ ] `<task-name>` is resolved and `./docs/orchestration/<task-name>/` is selected.
- [ ] `plan.md`, `progress.md`, `decision.md`, `architecture.md` are loaded before action.
- [ ] Linked `BL-*` items are loaded from `docs/backlog.md` when present.
- [ ] The recorded task branch is loaded and reused; no per-feature branch is created.
- [ ] The recorded task worktree is verified or explicitly recorded as the current checkout; no per-feature worktree is created.

### Open Mode (start/resume execution)

- [ ] Feature for this session is identified (next pending by default).
- [ ] Relevant task-level backlog item is set to `Doing` if it was `Todo`.
- [ ] Session Briefing block printed in required format.
- [ ] Session goal explicitly includes task name, feature ID, description, and acceptance criteria.
- [ ] Session goal includes task branch and task worktree.
- [ ] Relevant files listed with rationale.
- [ ] Implementation started immediately after briefing on the recorded task branch.

### Close Mode (end session/handoff)

- [ ] Current session outcome summarized (what was completed vs deferred).
- [ ] Current feature verified with test and QA completion before done-marking.
- [ ] Next Session Briefing block printed in required format.
- [ ] The completed feature is represented by one final commit on the shared task branch.
- [ ] Backlog updates are applied only for real backlog-level outcome changes.
- [ ] Completed backlog items include `Completed`, `Artifact`, and `Result`.
- [ ] Wiki-related backlog `Result` entries name the wiki file, heading/section, and concrete change.
- [ ] Continuity doc updates (plan/progress/decision) are handled via `/large-task-orchestrator revise <task-name>` when needed.
