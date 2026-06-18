# JeonseLoop Hourly Backlog Agent Loop Prompt

You are running the JeonseLoop hourly backlog agent loop.

Read `AGENTS.md`, `docs/backlog.md`, and the relevant skill instructions before taking action.

## Goal

Complete at most one unfinished backlog item all the way to `Done`, including verification, backlog closeout, and required handoff artifacts.

Timebox this run to about 45 minutes. If the selected task cannot be completed to `Done` within that time, stop only after recording concrete progress, the exact remaining work, and the blocker or reason it could not be completed.

## Hard Constraints

- Do not send Telegram alerts.
- Do not use `--send`.
- Do not commit, push, or open PRs for unrelated work. Commit, push, or open PRs only when they are required by the selected backlog item or the applicable lifecycle closeout rules.
- Do not overwrite unrelated user changes.
- If the git worktree is dirty, inspect the changes and work around them. Stop if the selected task would conflict with existing unrelated changes.
- Preserve existing JSON state on failure. Use validate-before-replace paths for state writes.
- For any source-code task, follow the `large-task-orchestrator` lifecycle before editing source files.
- For wiki work, use the `wiki-write` rules.
- For backlog lifecycle changes, use the `backlog-management` rules.

## Concurrency Guard

- Before starting work, check `git status`, `docs/backlog.md`, `reports/backlog-agent-loop.md`, and any relevant `docs/orchestration/<task>/progress.md` files.
- If another backlog loop appears to be active, or if an existing `Doing` item cannot be confidently attributed to this run, write a no-op report and stop.
- Do not start a new `Todo` item while any unrelated `Doing` item exists.
- Do not run concurrent source-code tasks in the same worktree.

## Scope Guard

- Do not make broad architecture decisions in this unattended loop.
- Do not change public behavior, environment variable contracts, secrets handling, workflow schedules, or large module boundaries unless the selected backlog item explicitly requires that scope.
- Do not rewrite large modules opportunistically.
- If the selected task appears larger than this run can safely complete, still work toward `Done`; stop only at a clean verification boundary with explicit remaining work and a reason completion was not possible.
- If human judgment is needed for product direction, architecture tradeoffs, or operating policy, mark or keep the item `Blocked` or `Doing` with a clear question instead of guessing.

## Stacked Branch Remediation

- Before stopping because a task branch contains unrelated stacked commits, classify the commits in `git log <base>..HEAD` by backlog ID, task name, and touched file surface.
- If unrelated commits are complete, clean, and already pushed to a remote task branch, create or update their PR first instead of silently treating them as a blocker.
- If the selected source-code task has a small, identifiable commit set, create a clean PR branch from the current default branch and cherry-pick only the selected task commits. Do this only when the worktree is clean and the commit set can be identified from commit messages, orchestration docs, or file paths.
- After creating a clean branch, rerun the focused and required broad verification for the selected task, then continue `/large-task-orchestrator done` on the clean branch.
- If cherry-pick conflicts, tests fail, or the selected task commits cannot be separated confidently, write the exact blocker and the command that should be retried. Do not open a mixed-scope PR.
- Record any superseded dirty/stacked branch and the clean PR branch in `reports/backlog-agent-loop.md` and the task orchestration progress file.

## Task Selection

1. Prefer an existing `Doing` item if it can be safely continued.
2. Otherwise select the oldest `Todo` item from `docs/backlog.md`.
3. Select only one item.
4. If no `Todo` or `Doing` item exists, write a short no-op report and stop.
5. If the selected item is `Blocked`, do not work on it unless the blocker is clearly resolved from local repo evidence.

## Execution

- Classify the selected item by `Route`.
- For `source-code` route:
  - Use `/large-task-orchestrator start` or `/large-task-orchestrator next` with a stable task name derived from the backlog item.
  - Continue through `/large-task-orchestrator done` when the selected backlog item is complete.
  - Make the smallest coherent set of changes needed to complete the selected backlog item.
  - Run focused tests first, then broader tests if the touched surface warrants it.
- For non-source routes:
  - Make the smallest durable documentation, skill, prompt, or backlog update needed to complete the selected backlog item.
  - Verify links, paths, status values, and required result fields.

## Backlog Update Rules

- Change `Todo` to `Doing` only when actual work has started, then continue toward `Done` in the same run.
- Mark `Done` only when the backlog task is actually complete, verified, and the `Completed`, `Artifact`, and `Result` fields are specific.
- If the work is incomplete but progress was made, keep or set `Doing` and record progress, remaining work, and the reason completion was not possible in the appropriate orchestration or report artifact.
- If blocked, set `Blocked` only when the blocker is concrete and cannot be resolved in this run.
- If verification fails, do not revert unrelated changes. Keep the worktree as-is only if the changes are useful and documented; otherwise stop and report the failing verification clearly.

## Reporting

Write or update `reports/backlog-agent-loop.md` with:

- timestamp
- selected backlog ID
- route
- action taken
- files changed
- verification commands and results
- remaining work or blocker

Stop after the selected backlog item is `Done`, or after recording why it could not be completed to `Done` in this run.

## Recommended Execution Example

```powershell
codex exec --sandbox workspace-write `
  "$(Get-Content .codex\prompts\backlog-agent-loop.md -Raw)" `
  -o reports\backlog-agent-loop.md
```
