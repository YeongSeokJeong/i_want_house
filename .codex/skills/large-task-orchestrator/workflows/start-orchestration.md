# Start Orchestration Workflow

Use this workflow for:

- `/large-task-orchestrator start <task-name>`

## Required Reading

- `../references/feature-slicing.md`
- `../references/plan-schema.md`
- `../references/progress-schema.md`
- `../references/decision-schema.md`
- `../references/architecture-schema.md`
- `../checklist/start.md`
- [Wiki Write Skill](../../wiki-write/SKILL.md)
- [Backlog Management Skill](../../backlog-management/SKILL.md)
- `../../../../docs/backlog.md` (if present)
- `../../../../docs/wiki/SCHEMA.md` (if present)
- `../../../../docs/wiki/init.md` (if present)
- `../../../../docs/wiki/index.md` (if present)
- `../../../../docs/wiki/decisions.md` (if present)
- [Clarify Agent](../../../agents/clarify.agent.md)
- [Brainstorm Agent](../../../agents/brainstorm.agent.md)
- [PM Agent](../../../agents/pm.agent.md)
- [Architecture Agent](../../../agents/architecture.agent.md)
- [SCM Agent](../../../agents/scm.agent.md)

## Agent Execution Contract

This workflow owns agent usage for `/large-task-orchestrator start <task-name>`.

- Load every linked `.codex/agents/*.agent.md` spec in this file before executing its matching stage.
- Use the named agent for the matching stage below; do not infer agents from `SKILL.md`.
- Do not silently substitute or skip the named agent unless the user explicitly changes the workflow.

## Process (strict order)

### Stage 0: Task Naming

1. Resolve `<task-name>` from the user. If missing, ask exactly one question: `What should we call this large task?`
2. Define task directory: `./docs/orchestration/<task-name>/`.

### Stage 1: Requirement Interview First

| | |
|---|---|
| **Agent** | [Clarify Agent](../../../agents/clarify.agent.md) |
| **Goal** | Clarify scope before implementation planning, especially when the user only provided `/large-task-orchestrator start <task-name>` or otherwise sparse requirements |
| **Rules** | Ask 1-5 high-impact questions, then summarize in-scope/out-of-scope, constraints, and testable acceptance criteria. Do not start deep repository code reading before this stage is complete. |
| **Output** | Interviewed requirement brief (scope + constraints + initial acceptance criteria) |

### Stage 2: Related Wiki Discovery (wiki-write)

| | |
|---|---|
| **Agent** | [Brainstorm Agent](../../../agents/brainstorm.agent.md) |
| **Goal** | Find requirement-related docs/decisions before feature slicing |
| **Rules** | Use the `wiki-write` skill routing model and inspect `docs/wiki/SCHEMA.md`, `docs/wiki/init.md`, `docs/wiki/index.md`, `docs/wiki/decisions.md`, and relevant `docs/wiki/**` pages before planning. Produce an evidence list of related docs, decisions, reusable rules, and wiki gaps. If durable knowledge should be added or updated, record the proposed wiki target path and defer actual wiki edits to the appropriate orchestration feature or closeout unless the user explicitly asks to update it now. |
| **Output** | Related wiki evidence list with relevance notes and proposed wiki update targets |

### Stage 3: Backlog Routing and Linkage (backlog-management)

| | |
|---|---|
| **Agent** | [PM Agent](../../../agents/pm.agent.md) |
| **Goal** | Connect the large task to repo-level backlog tracking before feature slicing is finalized |
| **Rules** | Use `backlog-management` routing patterns. Read `docs/backlog.md` if present, search for duplicate or related `BL-*` items, classify the large task route (`source-code`, `wiki-*`, `operator-doc`, `skill-agent`, `spec`, or `backlog`), then either link an existing backlog item or create a new task-level `Todo` item. Do not treat `docs/backlog.md` as the feature plan; it records work/result status only. |
| **Output** | Related Backlog Items list with `BL-*` ID, route, status, and whether each item is existing or newly created |

### Stage 4: Brainstorm

| | |
|---|---|
| **Agent** | [Brainstorm Agent](../../../agents/brainstorm.agent.md) |
| **Goal** | Analyze the large task and identify candidate features with stable feature IDs (`F-001..F-00N`) and trade-offs |
| **Output** | Feature candidates (with IDs) + recommended split |

### Stage 5: PM Planning

| | |
|---|---|
| **Agent** | [PM Agent](../../../agents/pm.agent.md) |
| **Goal** | Finalize discrete functional units, assign feature IDs, define acceptance criteria, map related `BL-*` IDs, and produce `plan.md` v1 |
| **Output** | Ordered feature backlog with IDs + acceptance criteria + related backlog IDs + plan v1 |

### Stage 6: Architecture Review

| | |
|---|---|
| **Agent** | [Architecture Agent](../../../agents/architecture.agent.md) |
| **Goal** | Validate stack fit, boundaries, dependency map, and major risks aligned to feature IDs |
| **Output** | Architecture decisions and risk register mapped to feature IDs |

### Stage 7: Continuity File Initialization

Create/initialize:

1. `./docs/orchestration/<task-name>/plan.md` from `references/plan-schema.md`
2. `./docs/orchestration/<task-name>/progress.md` from `references/progress-schema.md`
3. `./docs/orchestration/<task-name>/decision.md` from `references/decision-schema.md` (create if missing)
4. `./docs/orchestration/<task-name>/architecture.md` from `references/architecture-schema.md`

Record linked `BL-*` IDs and routes in `plan.md` and `progress.md` using the schema sections for related backlog items.

### Stage 8: Plan Revision Policy Initialization

Seed `plan.md` revision controls from Session 1:

- Start at `Plan Version: v1`.
- Include a revision log table.
- Mark that plan revision is allowed only when scope/constraints/risks change.
- Any revision must update affected feature IDs in both `plan.md` and `progress.md`.

### Stage 9: Task Worktree and Branch Initialization

Create or select one independent task-scoped worktree and one task-scoped working branch for the whole orchestration:

1. Use [SCM Agent](../../../agents/scm.agent.md) to propose a dedicated task worktree path separate from the primary repository checkout.
2. Record the current checkout only when the user explicitly designates it as the task worktree or the session is already running inside a previously recorded task worktree; record the rationale in `decision.md`.
3. Otherwise create or prepare the independent task worktree with a safe `git worktree add <path> <branch>` workflow before implementation begins, requesting any required filesystem approval when the path is outside the current writable workspace.
4. If the independent worktree cannot be created or used, stop before implementation and report the blocker; do not silently continue in the primary checkout.
5. Use [SCM Agent](../../../agents/scm.agent.md) to create and check out the task branch in the selected worktree.
6. Follow repository branch conventions if they exist; otherwise default to `task/<task-name>`.
7. Record the resolved task branch name and task worktree path in both `plan.md` and `progress.md`.
8. Do not create per-feature branches or worktrees after this point; feature separation happens by commit.

### Stage 10: Session 1 Summary

Output Session 1 summary to chat with:

- task name, task directory, and task branch
- task worktree path
- related backlog IDs and routes
- feature list (with feature IDs) and execution order
- acceptance criteria highlights
- architecture and risk highlights by feature ID
- first implementation target feature ID

## Success Criteria

- Interview-first clarification is completed when start input is sparse/ambiguous.
- Related wiki discovery is executed from `docs/wiki/` using the `wiki-write` routing model.
- Related backlog routing is executed using `backlog-management`, and linked `BL-*` IDs are recorded.
- Features are decomposed into independent functional units.
- Every feature has a stable feature ID and acceptance criteria.
- Architecture review is complete and documented with feature-ID mapping.
- `./docs/orchestration/<task-name>/plan.md`, `./docs/orchestration/<task-name>/progress.md`, `./docs/orchestration/<task-name>/decision.md`, `./docs/orchestration/<task-name>/architecture.md` exist and are initialized.
- Plan revision policy is explicit in `plan.md`.
- A single task branch and independent task worktree are selected or created and recorded for reuse across sessions.
- Session 1 summary is delivered.
