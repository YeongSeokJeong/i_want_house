# JeonseLoop Telegram Backlog Local Intake Prompt

You are running the local Telegram backlog intake loop for JeonseLoop.

Read `AGENTS.md`, `docs/backlog.md`, `.codex/mcp/README.md`, and the relevant skill instructions before taking action.

## Goal

Fetch recent Telegram bot updates from the local operator environment, triage them into backlog items or ops proposals, and leave an auditable local report.

## Hard Constraints

- Do not send Telegram alerts.
- Do not use `--send`.
- Do not commit, push, open PRs, or run GitHub Actions.
- Do not write raw Telegram update payloads to tracked files.
- Do not overwrite unrelated user changes.
- If the git worktree is dirty, inspect the changes and stop if intake writes would conflict.
- Keep runtime secrets in the local environment or untracked `.env` only.

## Preflight

1. Check `git status --short`.
2. Read `docs/backlog.md` and confirm no unrelated `Doing` backlog item is active.
3. Check whether `reports/telegram-backlog-local-intake.md` exists and whether it indicates another active local intake run.
4. Choose a raw update path under the OS temp directory, such as `$env:TEMP\jeonseloop-telegram-updates.json`.

## Execution

1. Use the Telegram MCP `telegram_save_recent_updates` tool to save recent updates to the temp update path.
2. Dry-run backlog intake first:

   ```powershell
   $env:PYTHONPATH = "src"
   python -m jeonseloop.telegram_backlog_intake --updates-path <temp-update-path> --dry-run
   ```

3. Dry-run ops proposal intake next:

   ```powershell
   $env:PYTHONPATH = "src"
   python -m jeonseloop.telegram_ops --updates-path <temp-update-path> --dry-run
   ```

4. If the dry-run result is clear and does not conflict with existing work, run the same two commands without `--dry-run` to update `docs/backlog.md`, `data/state/telegram-intake.json`, and `data/state/telegram-ops.json` as applicable.
5. If clarification is needed or the result is ambiguous, do not write backlog changes; record the blocker in the report.

## Verification

- Run a focused syntax or test check only when files changed.
- Inspect `git diff -- docs/backlog.md data/state/telegram-intake.json data/state/telegram-ops.json`.
- Confirm the temp raw update file is not tracked.
- Confirm no command used `--send`.

## Reporting

Write or update `reports/telegram-backlog-local-intake.md` with:

- timestamp
- temp update path used
- action taken
- files changed
- verification commands and results
- remaining work or blocker

Stop after one bounded local intake pass.
