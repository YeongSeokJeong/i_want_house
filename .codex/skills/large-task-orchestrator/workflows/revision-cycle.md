# Revision Cycle Workflow

Use this workflow for:

- `/large-task-orchestrator revise <task-name>`

This workflow is **documentation-only**. Do not implement code in this flow.

## Required Reading

- `../references/progress-schema.md`
- `../references/decision-schema.md`
- `../references/architecture-schema.md`
- `../references/plan-schema.md`
- `../references/feature-slicing.md`
- `../checklist/revise.md`
- [Backlog Management Skill](../../backlog-management/SKILL.md)
- `../../../../docs/backlog.md` (if present)
- [Brainstorm Agent](../../../agents/brainstorm.agent.md)
- [PM Agent](../../../agents/pm.agent.md)
- [Architecture Agent](../../../agents/architecture.agent.md)
- [QA Agent](../../../agents/qa.agent.md)

## Agent Execution Contract

This workflow owns agent usage for `/large-task-orchestrator revise <task-name>`.

- Load every linked `.codex/agents/*.agent.md` spec in this file before executing its matching stage.
- Use the named agent for the matching stage below; do not infer agents from `SKILL.md`.
- Do not silently substitute or skip the named agent unless the user explicitly changes the workflow.

## Process (strict order)

### Stage 0: Context Load

Read, in order:

1. Resolve `<task-name>` and use `./docs/orchestration/<task-name>/`.
2. `./docs/orchestration/<task-name>/plan.md`
3. `./docs/orchestration/<task-name>/progress.md`
4. `./docs/orchestration/<task-name>/decision.md`
5. `./docs/orchestration/<task-name>/architecture.md`
6. `docs/backlog.md` if present, and linked `BL-*` IDs from the orchestration docs.
7. Preserve the existing task branch and task worktree metadata in `plan.md` and `progress.md`; revisions must not switch branch or worktree strategy silently.

### Stage 1: Brainstorming

| | |
|---|---|
| **Agent** | [Brainstorm Agent](../../../agents/brainstorm.agent.md) |
| **Goal** | Identify what must change in `plan.md`, `progress.md`, and `decision.md` from new constraints, blockers, or reprioritization |
| **Output** | Candidate revision set with rationale, impacted feature IDs, and impacted backlog IDs |

### Stage 2: PM Structuring

| | |
|---|---|
| **Agent** | [PM Agent](../../../agents/pm.agent.md) |
| **Goal** | Convert candidate revisions into concrete document updates: sequencing, acceptance criteria, dependencies, feature status impacts, and backlog status/link impacts |
| **Rules** | If plan structure/scope changes, bump `Plan Version` and append revision log entry |
| **Output** | Finalized revision plan for `plan.md`, `progress.md`, `decision.md`, and related backlog rows |

### Stage 3: Architecture Validation

| | |
|---|---|
| **Agent** | [Architecture Agent](../../../agents/architecture.agent.md) |
| **Goal** | Validate dependency boundaries, risk shifts, and architectural consistency of the proposed revisions |
| **Output** | Architecture-aligned revision notes and risk updates |

### Stage 4: QA Gate

| | |
|---|---|
| **Agent** | [QA Agent](../../../agents/qa.agent.md) |
| **Goal** | Review revision quality and consistency (schema compliance, feature-ID consistency, traceability) |
| **Output** | PASS/FAIL for documentation revision package with findings |

If QA FAIL(CRITICAL/HIGH), iterate Stage 1-4 until pass or explicit user stop.

### Stage 5: Apply Document Updates

Apply approved revisions to:

1. `./docs/orchestration/<task-name>/plan.md`
2. `./docs/orchestration/<task-name>/progress.md`
3. `./docs/orchestration/<task-name>/decision.md`
4. `docs/backlog.md` only when backlog links, routes, statuses, blockers, or deferred follow-ups changed

Keep `Task Branch` and `Task Worktree` synchronized between `plan.md` and `progress.md`.
Keep `BL-*` links synchronized between `docs/backlog.md`, `plan.md`, and `progress.md`.

Do not perform code implementation, code refactoring, or code commits in this workflow.

### Stage 6: Revision Summary Output

Output:

- task name and revision timestamp
- changed feature IDs
- `Plan Version` before/after (if changed)
- summary of edits in `plan.md`, `progress.md`, `decision.md`
- summary of related backlog edits, or `None`
- QA result and unresolved blockers (or `None`)
