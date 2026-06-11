# /large-task-orchestrator next Checklist

Exit criteria for running `next` as the single lifecycle command.

## Checklist

### Common (Both Modes)

- [ ] `<task-name>` is resolved and `./docs/orchestration/<task-name>/` is selected.
- [ ] `plan.md`, `progress.md`, `decision.md`, `architecture.md` are loaded before action.
- [ ] The recorded task branch is loaded and reused; no per-feature branch is created.

### Open Mode (start/resume execution)

- [ ] Feature for this session is identified (next pending by default).
- [ ] Session Briefing block printed in required format.
- [ ] Session goal explicitly includes task name, feature ID, description, and acceptance criteria.
- [ ] Relevant files listed with rationale.
- [ ] Implementation started immediately after briefing on the recorded task branch.

### Close Mode (end session/handoff)

- [ ] Current session outcome summarized (what was completed vs deferred).
- [ ] Current feature verified with test and QA completion before done-marking.
- [ ] Next Session Briefing block printed in required format.
- [ ] The completed feature is represented by one final commit on the shared task branch.
- [ ] Continuity doc updates (plan/progress/decision) are handled via `/large-task-orchestrator revise <task-name>` when needed.
