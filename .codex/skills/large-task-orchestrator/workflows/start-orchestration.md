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

### Stage 3: Brainstorm

| | |
|---|---|
| **Agent** | [Brainstorm Agent](../../../agents/brainstorm.agent.md) |
| **Goal** | Analyze the large task and identify candidate features with stable feature IDs (`F-001..F-00N`) and trade-offs |
| **Output** | Feature candidates (with IDs) + recommended split |

### Stage 4: PM Planning

| | |
|---|---|
| **Agent** | [PM Agent](../../../agents/pm.agent.md) |
| **Goal** | Finalize discrete functional units, assign feature IDs, define acceptance criteria, and produce `plan.md` v1 |
| **Output** | Ordered feature backlog with IDs + acceptance criteria + plan v1 |

### Stage 5: Architecture Review

| | |
|---|---|
| **Agent** | [Architecture Agent](../../../agents/architecture.agent.md) |
| **Goal** | Validate stack fit, boundaries, dependency map, and major risks aligned to feature IDs |
| **Output** | Architecture decisions and risk register mapped to feature IDs |

### Stage 6: Continuity File Initialization

Create/initialize:

1. `./docs/orchestration/<task-name>/plan.md` from `references/plan-schema.md`
2. `./docs/orchestration/<task-name>/progress.md` from `references/progress-schema.md`
3. `./docs/orchestration/<task-name>/decision.md` from `references/decision-schema.md` (create if missing)
4. `./docs/orchestration/<task-name>/architecture.md` from `references/architecture-schema.md`

### Stage 7: Plan Revision Policy Initialization

Seed `plan.md` revision controls from Session 1:

- Start at `Plan Version: v1`.
- Include a revision log table.
- Mark that plan revision is allowed only when scope/constraints/risks change.
- Any revision must update affected feature IDs in both `plan.md` and `progress.md`.

### Stage 8: Task Branch Initialization

Create one task-scoped working branch for the whole orchestration:

1. Use [SCM Agent](../../../agents/scm.agent.md) to create and check out the task branch.
2. Follow repository branch conventions if they exist; otherwise default to `task/<task-name>`.
3. Record the resolved task branch name in both `plan.md` and `progress.md`.
4. Do not create per-feature branches after this point; feature separation happens by commit.

### Stage 9: Session 1 Summary

Output Session 1 summary to chat with:

- task name, task directory, and task branch
- feature list (with feature IDs) and execution order
- acceptance criteria highlights
- architecture and risk highlights by feature ID
- first implementation target feature ID

## Success Criteria

- Interview-first clarification is completed when start input is sparse/ambiguous.
- Related wiki discovery is executed from `docs/wiki/` using the `wiki-write` routing model.
- Features are decomposed into independent functional units.
- Every feature has a stable feature ID and acceptance criteria.
- Architecture review is complete and documented with feature-ID mapping.
- `./docs/orchestration/<task-name>/plan.md`, `./docs/orchestration/<task-name>/progress.md`, `./docs/orchestration/<task-name>/decision.md`, `./docs/orchestration/<task-name>/architecture.md` exist and are initialized.
- Plan revision policy is explicit in `plan.md`.
- A single task branch is created and recorded for reuse across sessions.
- Session 1 summary is delivered.
