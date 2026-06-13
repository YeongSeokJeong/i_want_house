# Architecture Review

## Task Context
- Task Name: JeonseLoop spec implementation
- Task ID: jeonseloop-spec-implementation
- Last Updated: 2026-06-13

## System Context
- Current Stack: Python 3.12 standard library, `unittest`, GitHub Actions, GitHub Pages static assets, JSON/Markdown repository state.
- Existing Patterns: Product loop uses a small package under `src/jeonseloop/` with separate watchlist, collector, validator, analyzer, notifier, persistence, and CLI modules.
- Integration Points: `config/watchlist.yaml`, `data/**/*.json`, `logs/*.md`, `.github/workflows/jeonseloop.yml`, Telegram Bot API, future real-estate portal/API fetchers, future trade API fetcher.

## Feature Decomposition Map
| Feature ID | Feature | Description | Depends On | Complexity | Risk |
|------------|---------|-------------|------------|------------|------|
| F-001 | Executable loop foundation | Runnable loop, config validation, fixture collection, candidate decisions, safe persistence, notification gating, tests | None | Medium | Medium |
| F-002 | Product trigger workflow | Scheduled/manual Actions and safe state write behavior | F-001 | Medium | Medium |
| F-003 | Static dashboard baseline | Static UI over committed JSON state | F-001 | Medium | Medium |
| F-004 | Reliability and baseline pricing | Request pacing, retry/backoff, trade baseline, health failure logic | F-001,F-002 | High | High |
| F-005 | Candidate quality controls | Exclusions, duplicates, alert cap details, feed JSON | F-001,F-003 | Medium | Medium |
| F-006 | Optional LLM review and improvement suggestions | Disabled-by-default LLM review and human-approved suggestions | F-005 | High | High |

## Dependency Map
- `scripts/run-loop.*` -> `src/jeonseloop/run.py` (operator entrypoints invoke one Python CLI).
- `src/jeonseloop/run.py` -> `loop.py` (CLI delegates one-cycle orchestration).
- `loop.py` -> `watchlist.py`, `collector.py`, `validator.py`, `analyzer.py`, `trades.py`, `notifier.py`, `persistence.py` (Loop Engineering stages).
- `persistence.py` -> `data/**/*.json`, `logs/*.md` (state and operator evidence).
- `trades.py` -> `data/trades/{complex_id}.json` (recent-trade cache baseline for candidate decisions).
- `persistence.py` -> `data/state/urgent-feed.json` (dashboard-friendly candidate decision feed).
- `notifier.py` -> Telegram Bot API only when explicitly enabled.
- F-002 depends on F-001 because workflow commands must run real code.
- F-003 depends on F-001 because dashboard data shape is produced by persistence.

## Technical Decisions
- Decision: Keep the first baseline standard-library only.
  - Rationale: The repo currently has no dependency manifest, and Phase 1 can be verified with fixtures and JSON files.
  - Trade-offs: YAML parsing is limited until a dependency manifest is introduced; the watchlist parser should stay intentionally narrow and test-covered.
- Decision: Use validate-before-replace JSON writes for state.
  - Rationale: `AGENTS.md` requires preserving previous JSON state on failure.
  - Trade-offs: Appending Markdown logs remains non-transactional relative to JSON writes, so failures should be reflected in health where possible.
- Decision: Treat live external fetchers as adapters added after the foundation.
  - Rationale: The spec prioritizes watchlist-limited collection and safe loop behavior; live scraping/API behavior needs additional legal and reliability checks.
  - Trade-offs: F-001 proves fixture-backed behavior, not real portal availability.
- Decision: Add retry and pacing at the collector boundary before live adapters.
  - Rationale: The minimum two-second interval and transient retry semantics should be enforced independently of any specific external source implementation.
  - Trade-offs: Without a live adapter, end-to-end external fetch behavior remains simulated by tests.
- Decision: Block urgent alerts when current listing averages shift abnormally from prior history.
  - Rationale: Sudden average-price jumps can signal source corruption or schema drift, and the hard constraint requires preserving previous JSON state on failure.
  - Trade-offs: A real market move above the fixed threshold can suppress alerts until reviewed.
- Decision: Persist candidate decisions in a dedicated urgent-feed JSON.
  - Rationale: Dashboard review needs approved, held, rejected, duplicate, exclusion, and alert-cap context that raw listings cannot express.
  - Trade-offs: Feed consumers must handle a second state file in addition to listing snapshots.
- Decision: Apply quality controls before notification planning.
  - Rationale: Exclusions and duplicate holds should never consume notification slots or trigger Telegram sends.
  - Trade-offs: More candidate records are retained for observability even when only a subset can alert.

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| Public repository state may expose sensitive personal targets | High | Keep secrets out of code/logs; review state shapes before live operation | Backend Agent |
| Live portal scraping may violate terms or break on layout changes | High | Keep collector boundary isolated and defer live adapter until review | Backend Agent |
| Workflow state commits can race or corrupt JSON | High | Use concurrency and atomic JSON writes; implement write permissions carefully in F-002 | Backend Agent |
| Missing dashboard feed contract can cause UI churn | Medium | Introduce feed JSON with tests before dashboard depends on it | Backend Agent |
| Optional LLM review can create false approvals if parsing fails | Medium | Default to hold/exclude on malformed responses | Backend Agent |
