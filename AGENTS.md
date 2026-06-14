# Optical Solution Agent - Copilot Instructions

## Project Overview
JeonseLoop is a personal unattended real-estate monitoring loop that collects watched apartment listings and transaction baselines, detects meaningfully underpriced deals, and sends Telegram alerts.
It persists JSON/Markdown state for a GitHub Pages dashboard while practicing the Loop Engineering cycle: Trigger, Discover/Route, Execute, Verify, Persist, and Escalate.

## Quick Start Commands
- Run the fixture-backed product loop without sends or writes:
  `powershell -File scripts/run-loop.ps1 -DryRun -Fixture tests\fixtures\listings.json`
- Run the fixture-backed verification tests:
  `python -m unittest discover -s tests`
- Run the development inspection prompt:
  `Get-Content .codex\prompts\loop-review.md -Raw | codex exec --sandbox read-only - -o reports\loop-review.md`

## Global HARD Constraints
- Do not send Telegram alerts unless `--send` is explicitly passed and `TELEGRAM_BOT_TOKEN` plus `TELEGRAM_CHAT_ID` are set.
- Source code development work MUST follow the `large-task-orchestrator` lifecycle; route implementation through `/large-task-orchestrator start|next|revise|status|done <task-name>`, maintain the required `docs/orchestration/<task-name>/` continuity files, and do not proceed with source code changes outside that workflow. Documentation-only, agent-instruction, configuration, and operator-guidance updates do not require `large-task-orchestrator` unless the user explicitly requests it.
- Keep runtime secrets and operator-specific environment values in a local untracked `.env` file for local operation. Do not hard-code tokens, chat IDs, API keys, or machine-specific paths in AGENTS.md, source files, workflow definitions, or committed docs.
- For GitHub Actions operation, mirror required `.env` values into GitHub Secrets rather than committing them; local `.env` is only for local shell/session loading.
- When adding or changing environment variables, update `.env.example` with placeholder names only; never put real secret values in that file.
- Communicate with the user in Korean unless the user explicitly requests another language.
- Write user-facing documentation files under `docs/` in Korean. Write internal reasoning and continuity artifacts in English, including plans, progress logs, decision records, architecture notes, review reports, and handoff reasoning; when a file under `docs/` is one of these reasoning artifacts, the reasoning-artifact language rule takes precedence.
- Preserve previous JSON state on failure; write state through validate-before-replace paths.

## Topic Document Links
- Product requirements: `jeonseloop-spec.md`
- Loop Engineering routing pattern: `docs/wiki/rules/workflow/loop-engineering-routing.md`
- Development inspection loop: `docs/wiki/rules/workflow/development-automation-loop.md`
- Product trigger workflow: `.github/workflows/jeonseloop.yml`
- Product entrypoints: `scripts/run-loop.ps1`, `scripts/run-loop.sh`, `src/jeonseloop/run.py`
- Watchlist config: `config/watchlist.yaml`
