# Development Cycle Workflow

Use this workflow for:

- `/large-task-orchestrator next <task-name>`
- `/large-task-orchestrator status <task-name>`
- `/large-task-orchestrator done <task-name>`
- `/large-task-orchestrator resume <task-name>` (legacy alias of `next`)

Revision updates for `plan.md`, `progress.md`, and `decision.md` are handled by:

- `/large-task-orchestrator revise <task-name>` → `workflows/revision-cycle.md`

## Required Reading

- `../references/progress-schema.md`
- `../references/decision-schema.md`
- `../references/architecture-schema.md`
- `../references/plan-schema.md`
- `../references/feature-slicing.md`
- `../checklist/next.md`
- `../checklist/status.md`
- `../checklist/done.md`
- [Wiki Write Skill](../../wiki-write/SKILL.md)
- [Backlog Management Skill](../../backlog-management/SKILL.md)
- `../../../../docs/backlog.md` (if present)
- [SCM Agent](../../../agents/scm.agent.md)
- [Backend Agent](../../../agents/backend.agent.md)
- [QA Agent](../../../agents/qa.agent.md)
- [Handoff Agent](../../../agents/handoff.agent.md)
- [Feature Implementation Skill](../../feature-implementation/SKILL.md)

## Agent Execution Contract

This workflow owns agent usage for `/large-task-orchestrator next`, `status`, `done`, and `resume`.

- Load every linked `.codex/agents/*.agent.md` spec in this file before executing the matching section below.
- Use the named agent whenever a section assigns one; do not infer agent usage from `SKILL.md`.
- Do not silently substitute or skip the named agent unless the user explicitly changes the workflow.

---

## A) `/large-task-orchestrator next`

`next` is a dual-mode lifecycle command.

Select one mode first:

1. **Open Mode (start/resume execution)**: use when beginning a new session or resuming unfinished feature implementation.
2. **Close Mode (end session/handoff)**: use when current feature work is finished and ready to hand off to the next session.

If mode is ambiguous from user intent, ask one question:

`Should I run next in start/resume mode or close/handoff mode?`

`/large-task-orchestrator resume <task-name>` MUST execute this same section in **Open Mode**.

### Step A0: Context Load (required for both modes)

Read, in order:

1. Resolve `<task-name>` and use `./docs/orchestration/<task-name>/`.
2. `./docs/orchestration/<task-name>/plan.md` (feature IDs, current plan version, revision log)
3. Read the recorded task branch and task worktree from `plan.md` and/or `progress.md`.
4. `./docs/orchestration/<task-name>/progress.md` (find current and next pending feature IDs)
5. `./docs/orchestration/<task-name>/decision.md` (prior decisions and constraints)
6. `./docs/orchestration/<task-name>/architecture.md` (system and dependency context)
7. `docs/backlog.md` if present, using `backlog-management` to find linked `BL-*` items from `plan.md`/`progress.md`.
8. Verify the current work continues on that task branch and, when recorded, in that task worktree. If docs are missing the branch or worktree, repair the docs before continuing implementation.

### Step A1: Open Mode (start/resume execution)

Session start behavior:

1. Identify the feature to implement now (typically next pending feature ID).
2. If no pending feature exists, stop implementation and suggest `/large-task-orchestrator done <task-name>`.
3. If linked backlog items are `Todo`, set the relevant task-level item to `Doing` before implementation begins. Do not create session-log backlog rows.

### Step A2: Session Briefing Output (Open Mode)

Output this exact block:

```markdown
## 🚀 Session <N> Started

### 📖 Context Loaded
- Previous Session: <N-1>
- Completed Features: <list>
- Remaining Features: <list>

### 🎯 This Session Goal
- Task: <task-name>
- Branch: <task-branch>
- Worktree: <task-worktree path, or "current checkout">
- Feature ID: <feature-id>
- Feature: <feature name>
- Backlog: <BL-* id and route, or "None">
- Description: <description>
- Acceptance Criteria:
  - [ ] <criteria 1>
  - [ ] <criteria 2>

### 📁 Relevant Files
- <file path>: <description>

### ▶️ Starting implementation...
```

### Step A3: Immediate Implementation (Open Mode)

Run this implementation sequence (same stage order as feature-implementation, but the task-branch policy here overrides feature-branch creation):

1. [SCM Agent](../../../agents/scm.agent.md): verify or switch to the recorded task worktree and task branch; create them only if the start workflow did not already do so and the user approves
2. [Backend Agent](../../../agents/backend.agent.md): implement feature + tests
3. [QA Agent](../../../agents/qa.agent.md): mandatory QA gate
4. If QA FAIL(CRITICAL/HIGH): iterate fix loop until pass or explicit stop
5. [Handoff Agent](../../../agents/handoff.agent.md): record session outcome before commit
6. [SCM Agent](../../../agents/scm.agent.md): create exactly one Conventional Commit for the completed feature on the shared task branch with `<task-name>/<feature-id>` scope
7. Use `backlog-management` to keep linked backlog state accurate without closing the whole task unless this feature completes the backlog item's requested work. If a feature creates a separate follow-up, add a new routed `Todo` or `Blocked` backlog row.

Do not proceed to another feature until test + QA pass and the feature commit is complete on the shared task branch.

---

### Step A4: Close Mode (end session/handoff)

1. Summarize what was completed in the current session.
2. Use `backlog-management` to update related `BL-*` items only when a backlog-level outcome changed:
   - keep task-level items `Doing` while more features remain
   - create `Todo`/`Blocked` rows for newly discovered follow-up work
   - if a linked backlog item is fully complete, mark it `Done` with `Completed`, `Artifact`, and `Result`
   - if wiki content was written, `Result` must include the wiki file path, heading/section, and concrete change made
3. Output this exact block:

```markdown
## 🔄 Next Session Briefing

### ✅ Completed This Session
- Session: <N>
- Task: <task-name>
- Branch: <task-branch>
- Worktree: <task-worktree path, or "current checkout">
- Feature ID: <feature-id>
- Feature: <feature name>
- Commit: <commit hash>
- Tests: <passed/failed summary>
- Backlog Updates: <BL-* status/result summary>

### 📋 Next Task
- Feature ID: <next feature id>
- Feature: <next feature name>
- Description: <what needs to be done>
- Estimated Complexity: Low | Medium | High

### 📁 Files to Review
- <file path>: <why it's relevant>

### ⚠️ Known Issues / Blockers
- <issue or "None">

### 💬 Suggested First Message for Next Session
"Read ./docs/orchestration/<task-name>/progress.md and continue from Session <N+1>.
Next task is <next feature id> <feature name>.
Key files: <file list>"
```

4. If continuity docs require updates (`plan.md`, `progress.md`, `decision.md`), run `/large-task-orchestrator revise <task-name>` before ending session.

---

## B) `/large-task-orchestrator status`

1. Use [SCM Agent](../../../agents/scm.agent.md) to verify the recorded task branch and last commit hash against repository state.
2. Use [Handoff Agent](../../../agents/handoff.agent.md) to summarize current orchestration status from `plan.md`, `progress.md`, and the SCM evidence.
3. Use `backlog-management` to include linked backlog item status from `docs/backlog.md`.
4. Output:

- task branch
- task worktree
- linked backlog IDs, routes, and statuses
- total features
- completed count
- remaining count
- current session number
- last commit hash
- known blockers
- current plan version

---

## C) `/large-task-orchestrator done`

1. Use [QA Agent](../../../agents/qa.agent.md) to verify all feature IDs are marked `DONE` in `./docs/orchestration/<task-name>/progress.md` and that continuity docs are internally consistent.
2. Use [Handoff Agent](../../../agents/handoff.agent.md) to create/update the final handoff summary document in `./docs/handoff/`:
   - file path: `./docs/handoff/<task-name>-final.md`
   - summarize delivered features and outcomes
   - summarize key decisions from `./docs/orchestration/<task-name>/decision.md`
3. Use [SCM Agent](../../../agents/scm.agent.md) to gather the full project commit list from the shared task branch and include it in the final handoff document.
4. Include unresolved risks/blockers (or `None`) in the final handoff document.
5. Set `./docs/orchestration/<task-name>/progress.md` `Status` to `COMPLETED`.
6. Run the `wiki-write` closeout check after the handoff/progress updates:
   - identify durable decisions, workflow rules, domain knowledge, or index changes created by the task
   - update the appropriate `docs/wiki/` pages only when the task produced durable knowledge that belongs in the wiki
   - refresh `docs/wiki/init.md`, `docs/wiki/index.md`, `docs/wiki/SCHEMA.md`, and/or `docs/wiki/decisions.md` when required by the wiki schema
7. Use `backlog-management` to close or update linked backlog items:
   - mark completed task-level backlog items `Done`
   - fill `Completed`, `Artifact`, and `Result`
   - if the task wrote wiki content, include exact wiki file path, heading/section, and concrete change in `Result`
   - create or leave separate `Todo`/`Blocked` rows for unresolved risks, external-state checks, or deferred follow-ups
8. Output final project summary with:
   - handoff document path
   - wiki-write closeout result
   - backlog-management closeout result
   - final QA gate result
