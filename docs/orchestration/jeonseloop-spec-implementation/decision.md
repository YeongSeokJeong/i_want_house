# Session Decisions

## Task Context
- Task Name: JeonseLoop spec implementation
- Task ID: jeonseloop-spec-implementation

## Decision Log
| Session | Feature ID | Feature | Decision | Rationale | Impact | Date |
|---------|------------|---------|----------|-----------|--------|------|
| 1 | PLAN | Planning | Use `feature/jeonseloop-automation` as the shared task branch | The branch already exists and contains the initial automation skeleton history | Avoids branch churn and preserves one branch for all feature commits | 2026-06-12 |
| 1 | PLAN | Planning | Slice implementation into six feature IDs aligned to spec phases | Phase 1 Must work needs an executable foundation before workflow, dashboard, and reliability additions | Enables feature-scoped commits and QA gates | 2026-06-12 |
| 1 | PLAN | Planning | Treat external services as external-state evidence | GitHub Secrets, live Telegram delivery, portal/API availability, and actual Actions history cannot be proven from repository files alone | Verification will separate repo-verifiable behavior from external state | 2026-06-12 |
| 1 | PLAN | Planning | Use local `.codex/agents/*.toml` specs where workflow docs reference missing `.agent.md` files | The checkout contains TOML agent specs and no `.agent.md` files | Keeps orchestrator execution unblocked while documenting the mismatch | 2026-06-12 |
| 2 | F-001 | Executable loop foundation | Restore the standard-library loop foundation and keep live portal/API adapters out of F-001 | The spec needs a repo-verifiable safe baseline before live external integrations | Enables deterministic fixture tests and protects against unintended external requests | 2026-06-12 |
| 2 | F-001 | Executable loop foundation | Treat `--dry-run` as an absolute no-write and no-send mode | AGENTS.md forbids Telegram sends unless explicitly enabled, and dry-run should be safe for operator checks | Tests verify dry-run skips state writes and Telegram notifier initialization | 2026-06-12 |
| 2 | F-002 | Product trigger workflow | Scheduled workflow runs are non-dry-run state persistence runs, while manual dispatch remains dry-run by default | Product-loop scheduled execution must produce state for dashboard/health, but manual UI runs should remain safe by default | Scheduled runs can commit `data` and `logs`; manual writes require `dry_run=false` | 2026-06-12 |
| 2 | F-002 | Product trigger workflow | Keep Telegram sends behind the explicit workflow `send` input | Repository hard constraint requires `--send` before Telegram delivery | Scheduled runs persist state but do not send Telegram unless a future explicit schedule policy is added | 2026-06-12 |
| 2 | F-002 | Product trigger workflow | Use one concurrency group with `cancel-in-progress: false` | This prevents concurrent state writes without cancelling an active product loop midway | Later queued runs wait instead of racing JSON commits | 2026-06-12 |
| 3 | F-003 | Static dashboard baseline | Implement the dashboard as root-level static HTML/CSS/JS with no build step | GitHub Pages can serve committed files and JSON directly | Dashboard can be opened from repository Pages without package installation | 2026-06-12 |
| 3 | F-003 | Static dashboard baseline | Render section-local empty/error states from committed JSON files | Future fetch failures should not blank the whole dashboard | Status, chart, and feed sections fail independently | 2026-06-12 |
| 3 | F-003 | Static dashboard baseline | Commit realistic sample health, history, and listing JSON | F-003 acceptance requires visible last-run status and history state from committed static files | Static tests now prove sample state can render non-empty dashboard sections | 2026-06-12 |
| 4 | F-004 | Reliability and baseline pricing | Keep live fetcher retry/pacing behind injectable adapter boundaries | Live portal/API adapters are still external and should be testable without network calls | Collector reliability can be verified with deterministic unit tests before live integration | 2026-06-13 |
| 4 | F-004 | Reliability and baseline pricing | Use recent trade cache averages as the primary baseline and target price as fallback | The spec requires recent transaction baselines while still allowing operation when trade data is absent | Candidate reasons now distinguish `baseline_price` from `target_price` decisions | 2026-06-13 |
| 4 | F-004 | Reliability and baseline pricing | Treat abnormal listing average jumps as data-quality failures that block urgent alerts and preserve prior snapshots | Sudden average-price shifts can indicate bad data or source changes | Failed runs update health only and do not replace listing/history snapshots | 2026-06-13 |
| 4 | F-004 | Reliability and baseline pricing | Expose `failure_streak`, last-success metadata, and health alert eligibility in health JSON | Operators and dashboard code need durable failure context across runs | Health state can distinguish isolated failures from repeated failures needing escalation | 2026-06-13 |
| 5 | F-005 | Candidate quality controls | Evaluate watchlist exclusions before approval | Exclusion terms must block alerts even when price criteria pass | Excluded listings appear as rejected candidates with queryable reasons | 2026-06-13 |
| 5 | F-005 | Candidate quality controls | Represent equivalent duplicates as held candidates instead of silently dropping them | Operators need to inspect duplicate rationale later in logs/feed data | One representative remains eligible while duplicate reasons stay queryable | 2026-06-13 |
| 5 | F-005 | Candidate quality controls | Publish `data/state/urgent-feed.json` as the dashboard feed contract | Raw listing snapshots do not include enough decision context for review | Dashboard can render approved, rejected, held, and capped candidate states from one JSON file | 2026-06-13 |
| 5 | F-005 | Candidate quality controls | Count all approved candidates separately from capped planned notifications | Alert cap overflow must be visible without sending more than five Telegram alerts | Health counts expose `alert_cap_overflow` and feed items mark `alert_planned` | 2026-06-13 |
| 6 | F-006 | Optional LLM review and improvement suggestions | Keep LLM review disabled unless both `JEONSELOOP_LLM_REVIEW` and `ANTHROPIC_API_KEY` are present | The spec and hard constraints require safe default operation without secrets | Default runs do not invoke network review and continue deterministic rule-based decisions | 2026-06-13 |
| 6 | F-006 | Optional LLM review and improvement suggestions | Hold candidates on invalid LLM JSON or review errors | Failed secondary review must not turn into Telegram approval | Invalid responses produce `llm_invalid_response` hold reasons before notification planning | 2026-06-13 |
| 6 | F-006 | Optional LLM review and improvement suggestions | Generate criteria suggestions as a separate artifact requiring human approval | Criteria changes should not mutate `config/watchlist.yaml` automatically | `criteria-suggestions.json` can be reviewed without changing operator configuration | 2026-06-13 |

## Session 1
- Feature ID: PLAN
- Feature: Planning and orchestration initialization
- Decisions:
  - Derived task key `jeonseloop-spec-implementation` from the user objective.
  - Recorded wiki discovery and deferred product-domain wiki creation until durable implementation knowledge exists.
  - Started F-001 because the current worktree has deleted product-loop files required by the spec.
- Alternatives Considered:
  - Ask for a task key: not used because the active objective is already specific and continuation should keep moving.
  - Create `task/jeonseloop-spec-implementation`: not used because an implementation branch already exists with related history.
- Risks Introduced:
  - Some worktree changes predate this session; code restoration must avoid overwriting unrelated user edits outside the implementation surface.
- Follow-up Notes:
  - Update this file before each feature commit with QA and implementation decisions.

## Session 2
- Feature ID: F-001
- Feature: Executable loop foundation
- Decisions:
  - Restored `src/jeonseloop/`, `scripts/run-loop.*`, fixture data, and unit tests as the executable product-loop baseline.
  - Added focused tests for request interval minimum, dry-run send blocking, invalid-watchlist health persistence, and expected persistence outputs.
  - Kept real Telegram delivery behind `--send` plus environment secrets; dry-run overrides send attempts.
- Alternatives Considered:
  - Implement live portal scraping in F-001: deferred to later features because external source behavior and legal constraints need separate review.
  - Add third-party YAML parsing dependency: deferred because the current sample watchlist fits the limited parser and the repo has no dependency manifest yet.
- Risks Introduced:
  - Limited YAML parser supports only the current simple watchlist shape.
  - F-001 target-price decisions do not yet include recent-trade baseline support; that remains in F-004.
- Follow-up Notes:
  - F-002 should revisit workflow permissions and scheduled dry-run/write behavior because the current workflow is not yet the full production state-persisting trigger.

## Session 2 F-002 Addendum
- Feature ID: F-002
- Feature: Product trigger workflow
- Decisions:
  - Changed `.github/workflows/jeonseloop.yml` to grant `contents: write` for state persistence.
  - Added a `Persist loop state` step that commits only `data` and `logs` when the loop is not a dry run and those paths changed.
  - Changed schedule behavior so cron runs do not automatically add `--dry-run`; manual dispatch still defaults to dry-run unless `dry_run=false`.
  - Added workflow tests covering triggers, KST cron, write permissions, dry-run behavior, concurrency, and explicit Telegram send gating.
- Alternatives Considered:
  - Keep scheduled runs dry-run only: rejected because it would not satisfy product-loop persistence requirements.
  - Set `cancel-in-progress: true`: rejected because it can interrupt the active run rather than simply avoiding concurrent state writes.
- Risks Introduced:
  - Scheduled runs can now commit state; F-004 should strengthen health/failure semantics before live adapters are enabled.
  - GitHub Actions push permissions depend on repository settings and remain external state.
- Follow-up Notes:
  - F-003 can now rely on committed JSON state shapes for dashboard rendering.

## Session 3 F-003 Addendum
- Feature ID: F-003
- Feature: Static dashboard baseline
- Decisions:
  - Added `index.html`, `assets/dashboard.css`, and `assets/dashboard.js` as a no-build dashboard.
  - Fetches `data/state/health.json`, `data/history/sample-apt.json`, and `data/listings/sample-apt.json`.
  - Uses a canvas line chart when history exists and empty/error states when JSON is missing or empty.
  - Added static contract tests for asset references, JSON fetch paths, section-local error states, and committed sample data.
  - Guarded chart rendering so a history file without numeric price points shows an empty state instead of invalid canvas values.
- Alternatives Considered:
  - Add a bundled charting dependency: rejected because the repo has no frontend build or package manifest and a lightweight canvas chart is sufficient for the baseline.
  - Generate dashboard HTML from Python during each loop: deferred because F-003 requires static JSON rendering without a build step.
- Risks Introduced:
  - Complex discovery is currently hardcoded to `sample-apt`; a future feature should emit dashboard metadata from the watchlist.
  - Browser visual automation could not run because the local in-app browser runtime failed to start under the Windows sandbox.
- Follow-up Notes:
  - F-004 should enrich the state JSON so the chart can include recent trade baselines and better health details.

## Session 4 F-004 Addendum
- Feature ID: F-004
- Feature: Reliability and baseline pricing
- Decisions:
  - Added request interval enforcement and retry/backoff scaffolding to the collector with an injectable live fetcher and sleeper.
  - Added recent-trade cache loading from `data/trades/{complex_id}.json` and persisted the calculated recent-trade baseline into history entries.
  - Updated candidate classification to approve by recent-trade baseline when present and fall back to configured target price otherwise.
  - Added previous-average loading, average-price jump detection, and quality-block application so abnormal data shifts hold otherwise approved alerts.
  - Added health `failure_streak`, `last_success_at`, `last_success_run_id`, and `health_alert_eligible` metadata.
- Alternatives Considered:
  - Introduce a real MOLIT API client in F-004: deferred because live API credentials and endpoint behavior are external state, while the feature can be repo-verified through cache loading and adapter boundaries.
  - Persist snapshots during data-quality failures: rejected because preserving prior known-good JSON is safer when source data may be corrupt.
- Risks Introduced:
  - Average-jump threshold is fixed at 15 percent and may need tuning with real listing volatility.
  - Trade baseline currently averages all cached trade records in the file; rolling six-month filtering should be added with the live trade collector.
- Follow-up Notes:
  - F-005 should publish dashboard-friendly candidate/feed data that includes hold/reject reasons, duplicate rationale, and alert-cap overflow.

## Session 5 F-005 Addendum
- Feature ID: F-005
- Feature: Candidate quality controls
- Decisions:
  - Added exclusion matching against title, description, building, floor, and link text before price approval.
  - Changed duplicate handling so equivalent listings with the same complex, building, floor, area, and price keep one representative and record duplicate holds.
  - Added capped notification planning with `alert_cap_overflow` while preserving the hard limit of five planned Telegram alerts.
  - Persisted `data/state/urgent-feed.json` with decision, reason, price, listing context, and `alert_planned` for dashboard review.
  - Updated the static dashboard feed section to read `urgent-feed.json` and show decision/reason metadata.
- Alternatives Considered:
  - Continue using `data/listings/{complex_id}.json` as the dashboard feed: rejected because raw snapshots cannot represent rejects, holds, duplicate rationale, or alert-cap overflow clearly.
  - Drop duplicate records entirely during dedupe: rejected because F-005 requires decision reasons to remain queryable.
- Risks Introduced:
  - Exclusion matching is simple substring matching and may need field-specific rules for real portal text.
  - Duplicate representative selection follows current input order after listing-key dedupe; a future source adapter may need a stronger broker/source priority rule.
- Follow-up Notes:
  - F-006 can use the criteria log and urgent feed as the input corpus for optional LLM review and improvement suggestions.

## Session 6 F-006 Addendum
- Feature ID: F-006
- Feature: Optional LLM review and improvement suggestions
- Decisions:
  - Added `review.py` with disabled-by-default configuration from environment variables and a standard-library Anthropic review adapter.
  - Added safe JSON parsing that accepts only `approve`, `hold`, or `reject` with a required reason.
  - Inserted LLM review before notification planning so invalid or failed review responses hold candidates and cannot trigger Telegram sends.
  - Added `suggestions.py` to generate `data/state/criteria-suggestions.json` only after sufficient criteria-log volume.
  - Suggestions are explicitly marked `requires_human_approval` and `auto_applied: false`; `config/watchlist.yaml` is not modified.
- Alternatives Considered:
  - Add a dependency-backed Anthropic SDK integration: rejected because the repo remains standard-library only and no dependency manifest exists.
  - Auto-apply threshold or exclusion suggestions: rejected because the spec requires human approval before criteria changes.
- Risks Introduced:
  - The live Anthropic adapter is not exercised without secrets and network access; tests cover gating and parser behavior.
  - Deterministic suggestions are simple frequency summaries and may need richer domain logic after real decision volume accumulates.
- Follow-up Notes:
  - Final closeout should run the full QA suite, produce `docs/handoff/jeonseloop-spec-implementation-final.md`, and perform the wiki-write closeout check.
