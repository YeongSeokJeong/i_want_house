---
name: large-task-orchestrator
description: |
  Orchestrates large multi-session development tasks by decomposing work into features,
  enforcing test/QA gates, and preserving continuity through task-scoped plan/progress/decision/architecture files.
  Use this skill for /large-task-orchestrator start <task-name>, /large-task-orchestrator next <task-name>,
  /large-task-orchestrator revise <task-name>, /large-task-orchestrator status <task-name>, and /large-task-orchestrator done <task-name>.
  /large-task-orchestrator resume <task-name> is kept as a legacy alias of next.
---

# Large Task Orchestrator

## Objective

Manage large, complex development tasks across multiple sessions by splitting work into discrete feature units (with feature IDs), preserving continuity through task-scoped markdown artifacts, and keeping all feature commits on one task-scoped branch.

## Trigger Prefix

`/large-task-orchestrator`

## Command Form

- `/large-task-orchestrator start <task-name>`
- `/large-task-orchestrator next <task-name>`
- `/large-task-orchestrator revise <task-name>`
- `/large-task-orchestrator status <task-name>`
- `/large-task-orchestrator done <task-name>`
- `/large-task-orchestrator resume <task-name>` (legacy alias of `next`)

## Required Continuity Files

Use one task-scoped directory per large task:

- `./docs/orchestration/<task-name>/plan.md`
- `./docs/orchestration/<task-name>/progress.md`
- `./docs/orchestration/<task-name>/decision.md`
- `./docs/orchestration/<task-name>/architecture.md`

`<task-name>` is the directory key under `./docs/orchestration/`.

## Core Behavior Rules

1. **Always resolve `<task-name>` first by asking the user when it is missing or ambiguous.**
2. **Always read `./docs/orchestration/<task-name>/progress.md` and `./docs/orchestration/<task-name>/plan.md` at the start of each session if they exist.**
3. **If task continuity files do not exist, treat the current session as Session 1 and initialize them.**
4. **For `/large-task-orchestrator start <task-name>` with sparse requirements, run a short user interview first; do not start deep code reading before interview results are captured.**
5. **For new requirements, run related-document discovery from `graphify-out/GRAPH_REPORT.md` and `graphify-out/graph.json` before planning. If artifacts are missing or stale, request `/graphify . --update` first.**
6. **Never skip test and QA steps before committing.**
7. **Never proceed to the next feature until the current feature passes test + QA and is committed.**
8. **Plan revision is allowed, but only with explicit version bump and revision log update in `plan.md`, and MUST run via `/large-task-orchestrator revise <task-name>`.**
9. **Always update `plan.md`, `progress.md`, and `decision.md` before ending a session, using `/large-task-orchestrator revise <task-name>` when updates are needed.**
10. **`plan.md` must assign stable Feature IDs (for example `F-001`, `F-002`), and `progress.md` must track implementation status by the same IDs.**
11. **`start` must create exactly one task branch for the whole large task and record it in continuity docs.**
12. **`next`/`resume` must reuse that recorded task branch; do not create per-feature branches.**
13. **Each feature must land as one feature-scoped commit on the shared task branch before moving to the next feature.**
14. **Every commit message must follow Conventional Commits and reference the task + feature scope.**
   - Example: `feat(checkout-funnel/f-002): add invoice retry worker`
15. **`next` is the execution lifecycle command: it handles session start/resume and session close/handoff for implementation flow.**
16. **`revise` is documentation-only: it updates `plan.md`, `progress.md`, and `decision.md` without code implementation.**
17. **`done` must write a final summary file in `./docs/handoff/` and trigger `/graphify . --update`; do not update `README.md` in this step.**

## Workflow-Owned Agent Policy

- This router must not enumerate workflow-specific agent specs.
- Each routed workflow MUST explicitly list the `.codex/agents/*.agent.md` specs it uses and require those agents during execution.
- Follow the selected workflow's agent instructions instead of inferring agent usage from `SKILL.md`.

## Routing

Use command intent to route to workflow docs:

| Command | Workflow |
|---|---|
| `/large-task-orchestrator start <task-name>` | [workflows/start-orchestration.md](workflows/start-orchestration.md) |
| `/large-task-orchestrator next <task-name>` | [workflows/development-cycle.md](workflows/development-cycle.md) |
| `/large-task-orchestrator revise <task-name>` | [workflows/revision-cycle.md](workflows/revision-cycle.md) |
| `/large-task-orchestrator status <task-name>` | [workflows/development-cycle.md](workflows/development-cycle.md) |
| `/large-task-orchestrator done <task-name>` | [workflows/development-cycle.md](workflows/development-cycle.md) |
| `/large-task-orchestrator resume <task-name>` (legacy alias) | [workflows/development-cycle.md](workflows/development-cycle.md) |

If the user omits the command suffix, ask one question:

`Which command should I run: start, next, revise, status, or done?`

If `<task-name>` is missing for the selected command, ask one question:

`What should we call this large task?`

---

## Commit Policy

- Use Conventional Commits.
- Use the single task branch created by `/large-task-orchestrator start <task-name>`.
- Scope must include `<task-name>/<feature-id>`.
- Each completed feature is represented by one final commit on that task branch.
- Do not commit feature work without passing tests and QA.

Examples:

```text
feat(checkout-funnel/f-001): implement login API and token issuer
fix(checkout-funnel/f-002): correct retry idempotency key behavior
refactor(checkout-funnel/f-003): separate aggregation service
```

---

## References

- [references/document-schemas.md](references/document-schemas.md)
- [references/feature-slicing.md](references/feature-slicing.md)
