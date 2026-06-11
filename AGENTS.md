# Optical Solution Agent - Copilot Instructions

## Project Overview
JeonseLoop is a personal unattended real-estate monitoring loop that collects watched apartment listings and transaction baselines, detects meaningfully underpriced deals, and sends Telegram alerts.
It persists JSON/Markdown state for a GitHub Pages dashboard while practicing the Loop Engineering cycle: Trigger, Discover/Route, Execute, Verify, Persist, and Escalate.

## Quick Start Commands
- Run the product loop without sends or writes:
  `powershell -File scripts/run-loop.ps1 -DryRun`
- Run the fixture-backed verification tests:
  `python -m unittest discover -s tests`
- Run the development inspection prompt:
  `Get-Content .codex\prompts\loop-review.md -Raw | codex exec --sandbox read-only - -o reports\loop-review.md`

## Global HARD Constraints
- Do not send Telegram alerts unless `--send` is explicitly passed and `TELEGRAM_BOT_TOKEN` plus `TELEGRAM_CHAT_ID` are set.
- Keep scheduled/product execution separate from `codex exec` development inspection.
- Preserve previous JSON state on failure; write state through validate-before-replace paths.
- Treat external scheduler registration, GitHub Secrets, live Telegram delivery, and portal/API availability as external state, not repo-verifiable facts.

## Topic Document Links
- Product requirements: `jeonseloop-spec.md`
- Development inspection loop: `docs/wiki/rules/workflow/development-automation-loop.md`
- Product trigger workflow: `.github/workflows/jeonseloop.yml`
- Product entrypoints: `scripts/run-loop.ps1`, `scripts/run-loop.sh`, `src/jeonseloop/run.py`
- Watchlist config: `config/watchlist.yaml`
