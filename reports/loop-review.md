## Findings

**High - Live listing and transaction collection are still fixture-only**

- Risk: The loop can be executed and tested, but it cannot yet monitor real Jeonse listings or transaction baselines.
- Evidence: `src/jeonseloop/collector.py:13` documents that the first implementation avoids live portal calls, and `src/jeonseloop/collector.py:20` returns empty listing sets when no fixture is supplied. `data/trades/sample-apt.json` is an initialized trade-cache shape, but no transaction collector exists yet.
- Why it matters: Discover/Route and Execute are now reviewable in the repo, but real monitoring depends on source adapters, rate limiting, retries, and malformed-record quarantine for live data.
- Suggested next action: Add listing and transaction source adapters behind the existing collector boundary, keeping fixture mode for tests and dry-runs.

**Medium - Scheduled workflow is wired but intentionally dry-run**

- Risk: The product Trigger is repo-verifiable, but scheduled runs will not send alerts or write state while the workflow forces `--dry-run`.
- Evidence: `.github/workflows/jeonseloop.yml:4` declares `schedule`, `.github/workflows/jeonseloop.yml:6` declares `workflow_dispatch`, `.github/workflows/jeonseloop.yml:17` declares `concurrency`, and `.github/workflows/jeonseloop.yml:40` adds `--dry-run` for scheduled runs.
- Why it matters: This is a safe bootstrap posture, but it is not yet unattended production monitoring.
- Suggested next action: Make a human decision on when scheduled runs may leave dry-run mode and whether state updates are committed, uploaded as artifacts, or handled by a separate persistence job.

**Medium - Health escalation is not implemented beyond state recording**

- Risk: Failed runs can be recorded, but repeated collection failures do not yet trigger a Telegram health alert.
- Evidence: `src/jeonseloop/loop.py:106` records invalid-watchlist failure health, and `src/jeonseloop/persistence.py:58` writes failure health state. `src/jeonseloop/notifier.py:22` implements Telegram credential validation for sends, but there is no consecutive-failure health alert path.
- Why it matters: The product spec requires health escalation, and silent repeated failures would defeat unattended monitoring.
- Suggested next action: Add a health-alert evaluator that reads `data/state/health.json`, detects consecutive failures, formats a Telegram health message, and tests no-send/send behavior.

**Low - Dashboard output contract is not implemented yet**

- Risk: JSON state paths exist, but there is no GitHub Pages-readable dashboard feed or UI.
- Evidence: `data/state/health.json`, `data/state/notified.json`, `data/listings/sample-apt.json`, `data/history/sample-apt.json`, and `data/trades/sample-apt.json` define seed state shapes. No `public/`, `docs/dashboard/`, or dashboard renderer path is present in `rg --files`.
- Why it matters: Persist is partly implemented for loop state, but the human inspection surface remains incomplete.
- Suggested next action: Add a static dashboard data contract first, then a minimal Pages UI once the JSON shape is stable.

## Not verifiable from repo

- Actual Windows Task Scheduler registration.
- Actual crontab registration.
- Actual GitHub Actions run history or recent success/failure.
- Actual GitHub secret registration for `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.
- Actual Telegram credential validity or message delivery.
- Actual current external real-estate portal/API availability.
- Actual GitHub Pages deployment status.
- Whether this environment's `codex exec --sandbox read-only` can perform future file-content inspection until the missing Windows sandbox helper is restored.

## Next actions

1. Implement real listing and transaction collectors behind `src/jeonseloop/collector.py`, keeping fixture-backed tests.
2. Decide when scheduled workflow runs may stop forcing `--dry-run`, and record that operating-policy decision if it changes production behavior.
3. Add health Telegram escalation for consecutive failures, with no-send tests and dedup-safe behavior.
4. Add dashboard JSON generation and a minimal GitHub Pages-readable surface.
5. Re-run `.codex/prompts/loop-review.md` after the Windows sandbox helper issue is fixed, or switch the review prompt to a bundled-content mode for this environment.

## Evidence

- `AGENTS.md`: Quick-start commands, safety constraints, and topic links now identify the product entrypoints and review prompt.
- `.codex/prompts/loop-review.md`: Reusable read-only review prompt; execution example now uses stdin to avoid PowerShell quoting failures.
- `.github/workflows/jeonseloop.yml`: Product trigger has `schedule`, `workflow_dispatch`, `concurrency`, test execution, secret names, and a concrete `python -m jeonseloop.run` entrypoint.
- `scripts/run-loop.ps1` and `scripts/run-loop.sh`: Local scheduler-compatible entrypoints set `PYTHONPATH` and invoke the Python loop.
- `config/watchlist.yaml`: Minimal watchlist config with complex ID, name, area, target price, threshold, and exclude list.
- `src/jeonseloop/watchlist.py`: Watchlist parsing and validation, including empty-watchlist handling and malformed-field errors.
- `src/jeonseloop/collector.py`: Fixture-backed collector boundary that limits records to watched complexes.
- `src/jeonseloop/validator.py`: Listing schema validation and fallback listing-key generation.
- `src/jeonseloop/analyzer.py`: Candidate classification, duplicate suppression, target-price approval, and dedup hold behavior.
- `src/jeonseloop/notifier.py`: Telegram message formatting and send path guarded by explicit `--send` credentials.
- `src/jeonseloop/persistence.py`: Validate-before-replace JSON writes using temp files and `os.replace`, health state, dedup state, listing snapshots, history, and criteria log persistence.
- `src/jeonseloop/run.py` and `src/jeonseloop/loop.py`: CLI and orchestration path for one loop cycle with `--dry-run`, `--send`, and fixture support.
- `tests/test_watchlist.py` and `tests/test_loop.py`: Unit coverage for watchlist validation, empty watchlist handling, dry-run no-write behavior, no-send persistence, and alert formatting.
- Verification run: `python -m unittest discover -s tests` passed with 6 tests.
- Verification run: `python -m jeonseloop.run --dry-run --fixture tests\fixtures\listings.json` returned `status: success`, 2 valid listings, 1 approved candidate, and 0 sent notifications.
