---
name: large-task-orchestrator
description: |
  Orchestrates large multi-session development tasks by decomposing work into features,
  enforcing test/QA gates, preserving continuity through task-scoped plan/progress/decision/architecture files,
  and synchronizing task outcomes with repo backlog items.
  Use this skill for /large-task-orchestrator start TASK_NAME, /large-task-orchestrator next TASK_NAME,
  /large-task-orchestrator revise TASK_NAME, /large-task-orchestrator status TASK_NAME, and /large-task-orchestrator done TASK_NAME.
  /large-task-orchestrator resume TASK_NAME is kept as a legacy alias of next.
---

# Large Task Orchestrator

## Objective

Manage large, complex development tasks across multiple sessions by splitting work into discrete feature units (with feature IDs), preserving continuity through task-scoped markdown artifacts, and keeping all implementation work in one independent task worktree on one task-scoped branch.

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
5. **For new requirements, run related-document discovery from `docs/wiki/` and the `wiki-write` routing rules before planning; capture relevant wiki pages, gaps, and any durable knowledge that should be added or updated.**
6. **Use `backlog-management` for repo backlog integration: classify the large task with a backlog route, link or create related `BL-*` items in `docs/backlog.md`, and record those IDs in orchestration docs.**
7. **Keep the orchestration feature backlog separate from `docs/backlog.md`: Feature IDs (`F-*`) track implementation sequencing; Backlog IDs (`BL-*`) track repo-level work/result status.**
8. **Never skip test and QA steps before committing.**
9. **Never proceed to the next feature until the current feature passes test + QA and is committed.**
10. **Plan revision is allowed, but only with explicit version bump and revision log update in `plan.md`, and MUST run via `/large-task-orchestrator revise <task-name>`.**
11. **Always update `plan.md`, `progress.md`, `decision.md`, and related backlog items before ending a session, using `/large-task-orchestrator revise <task-name>` when continuity docs need structural updates.**
12. **`plan.md` must assign stable Feature IDs (for example `F-001`, `F-002`), and `progress.md` must track implementation status by the same IDs.**
13. **`start` must ask SCM Agent to request or prepare one independent task worktree and one task branch for the whole large task, then record both in continuity docs. The task worktree must be separate from the primary repository checkout unless the user explicitly designates the current checkout as the task worktree or the session is already running inside the recorded task worktree.**
14. **`next`/`resume` must reuse the recorded task branch and task worktree; do not create per-feature branches or worktrees, and do not implement from the primary checkout when a task worktree is recorded.**
15. **Each feature must land as one feature-scoped commit on the shared task branch before moving to the next feature.**
16. **Every feature commit message must follow Conventional Commits and reference the task + feature scope.**
   - Example: `feat(checkout-funnel/f-002): add invoice retry worker`
17. **`next` is the execution lifecycle command: it handles session start/resume and session close/handoff for implementation flow.**
18. **`revise` is documentation-only: it updates `plan.md`, `progress.md`, `decision.md`, and backlog links/status when scope changes require it; it does not implement code.**
19. **`done` must write a final summary file in `./docs/handoff/`, run the `wiki-write` closeout check for durable wiki updates, close linked backlog items with `Artifact` and `Result`, push the task branch, create or update a pull request, record the PR URL, and create a closeout commit when files changed; do not update `README.md` in this step.**

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
- Use the independent task worktree recorded by `/large-task-orchestrator start <task-name>` when one is available.
- Do not implement or commit large-task work from the primary repository checkout when a task worktree is recorded.
- Scope must include `<task-name>/<feature-id>`.
- Each completed feature is represented by one final commit on that task branch.
- `/large-task-orchestrator done` may add one closeout commit with scope `<task-name>/closeout` after final docs, wiki, backlog updates, and PR URL recording are complete.
- Do not commit feature work without passing tests and QA.

Examples:

```text
feat(checkout-funnel/f-001): implement login API and token issuer
fix(checkout-funnel/f-002): correct retry idempotency key behavior
refactor(checkout-funnel/f-003): separate aggregation service
chore(checkout-funnel/closeout): finalize orchestration closeout
```

---

## Pull Request Policy

- `/large-task-orchestrator done <task-name>` must push the task branch and create or update a pull request against the repository default branch.
- Reuse an existing open PR for the task branch when one exists; otherwise create a new PR.
- Before opening a PR, inspect `git log <base>..HEAD` and classify commits by backlog ID, task name, and touched file surface.
- Do not open a mixed-scope PR when unrelated stacked commits would be included. First create or update PRs for complete prerequisite branches, or create a clean PR branch from the appropriate base and cherry-pick only the selected task commits.
- Open stacked PRs against their prerequisite task branch only when that keeps each PR reviewable and the dependency is stated in the PR body.
- Record the PR URL in `progress.md`, the final handoff document, and related backlog `Artifact`/`Result` fields.
- Do not mark the orchestration fully done unless a PR URL is recorded or the user explicitly waives PR creation.
- If PR creation is blocked by missing GitHub CLI, authentication, remote configuration, branch protection, network access, cherry-pick conflicts, failing verification, or a task commit set that cannot be separated confidently, stop and report the exact blocker plus the command that should be retried.

---

## References

- [references/document-schemas.md](references/document-schemas.md)
- [references/feature-slicing.md](references/feature-slicing.md)
- [../wiki-write/SKILL.md](../wiki-write/SKILL.md)
- [../backlog-management/SKILL.md](../backlog-management/SKILL.md)
