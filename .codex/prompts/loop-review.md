# JeonseLoop Loop Engineering Read-Only Review Prompt

You are reviewing the JeonseLoop repository in read-only mode.

This review inspects the JeonseLoop product loop, not the Codex execution loop. Do not evaluate whether this `codex exec` command was triggered correctly. Evaluate whether the JeonseLoop service itself is implemented or documented in a repository-verifiable way according to the Loop Engineering cycle:

- Trigger
- Discover/Route
- Execute
- Verify
- Persist
- Escalate

## Required Context

Read these documents before reviewing anything else:

1. `AGENTS.md`
2. `jeonseloop-spec.md`
3. `docs/wiki/rules/workflow/development-automation-loop.md`

Use them as the baseline for intended behavior, vocabulary, and review scope.

## Operating Mode

- Default mode is read-only review.
- Do not run the JeonseLoop service.
- Do not run external schedulers.
- Do not send Telegram messages.
- Do not modify code, documents, config, JSON state, Markdown state, logs, dashboard files, or reports.
- Do not create or update any files.
- Do not infer implementation from intent alone.
- If something cannot be confirmed from repository contents, put it under `Not verifiable from repo`.

The repository may currently contain little or no implementation. Treat absence as an implementation-order signal, not as a moral failure. Report missing pieces as prioritized next implementation work, especially when they block later Loop Engineering stages.

## Critical Distinction

This inspection is not checking whether `codex exec` ran, whether this prompt was scheduled, or whether Codex itself has a Trigger.

For the Trigger stage, check whether the JeonseLoop product loop has a reviewable execution path declared in the repository. A valid repo-verifiable Trigger may include GitHub Actions workflow configuration, a documented external scheduler contract, or scripts/docs that clearly describe how a JeonseLoop monitoring cycle starts.

## Repo-Verifiable vs External State

Separate findings into two categories:

- Repo-verifiable: can be confirmed from files committed in this repository.
- Not verifiable from repo: requires live external systems, local OS scheduler state, GitHub account settings, GitHub Actions run history, secrets, Telegram, or other external state.

Always report the following as not verifiable from repo unless the repository contains only documentation/examples about them:

- Whether Windows Task Scheduler actually has a registered task.
- Whether `crontab` actually has a registered job.
- Whether GitHub Actions actually ran recently or succeeded in the GitHub UI.
- Whether GitHub repository secrets are actually registered.
- Whether Telegram Bot API credentials are valid.
- Whether live portal/API calls currently succeed.

Repository files may document expected secret names, scheduler examples, workflow definitions, or operational contracts. Those are repo-verifiable as documentation or configuration, but they do not prove the external system is actually configured.

## Review Scope

Inspect the repository for the following Loop Engineering stages.

### Trigger

Check whether the JeonseLoop monitoring cycle start path is declared in a repo-verifiable way:

- GitHub Actions `schedule`.
- GitHub Actions `workflow_dispatch`.
- GitHub Actions `concurrency` or equivalent overlap protection.
- Workflow command that points to a concrete JeonseLoop entrypoint.
- External scheduler documentation or examples, such as Windows Task Scheduler docs/XML, crontab examples, or run scripts.
- Failure behavior that avoids corrupting previous state when a cycle fails or overlaps.

Do not treat "Codex was invoked" as a valid JeonseLoop Trigger.

### Discover/Route

Check whether the repository declares how the loop discovers work and routes candidates:

- Watchlist configuration, especially `config/watchlist.yaml` or an equivalent documented path.
- Required watchlist fields and validation expectations.
- Data source selection for listings and transaction baselines.
- Rules that limit collection to watched complexes.
- Candidate classification path, such as new listing, price change, disappeared listing, duplicate listing, urgent-sale candidate, hold, reject, or approve.
- Separation between listing collection, transaction baseline collection, and candidate routing.

### Execute

Check for concrete entrypoints or modules that perform loop work:

- Collector entrypoint.
- Validator entrypoint.
- Analyzer or price-decision entrypoint.
- Notifier entrypoint.
- A top-level run-loop command or orchestration script connecting the stages.
- Clear dependency on repository config rather than hard-coded private state.

### Verify

Check how the implementation proves a cycle result is safe to persist or escalate:

- Tests for watchlist parsing, schema validation, candidate classification, dedup, persistence, and notifier formatting.
- Dry-run mode or no-send mode.
- JSON schema validation or structured validation.
- Quarantine or failure isolation for malformed records.
- Protection against corrupting prior known-good state.
- Handling of empty watchlist, zero listings, API failures, and malformed external data.

### Persist

Check whether state and dashboard data are defined and updated safely:

- `data/state/*.json`, including health and dedup state.
- `data/listings/*.json`, `data/history/*.json`, `data/trades/*.json`, or equivalent paths.
- Markdown or structured logs, including criteria or decision logs.
- Static JSON used by a GitHub Pages dashboard.
- Atomic write, validate-before-replace, or rollback strategy.
- Dedup state that prevents repeated alerts for the same listing unless meaningful price changes occur.

### Escalate

Check whether human-facing escalation paths are implemented or documented:

- Telegram urgent-sale alert path.
- Telegram or other health failure alert path.
- Required secret names documented without exposing secret values.
- Alert deduplication and maximum alert count behavior.
- Human-readable report path, such as dashboard data, logs, Markdown reports, GitHub Actions summary, artifact, or issue.

## Finding Priorities

Prioritize findings by operational and development risk:

1. Bugs that could send false alerts, duplicate alerts, or corrupt state.
2. Missing Trigger/entrypoint wiring that prevents unattended operation.
3. Missing validation or failure isolation that could persist bad data.
4. Regression risks where a later stage assumes a prior stage exists but it is absent or incompatible.
5. Operational risks around secrets, scheduler ambiguity, unavailable observability, or unclear human escalation.
6. Missing tests or dry-run coverage for risky behavior.

Do not list cosmetic issues unless they create operational ambiguity.

## Evidence Rules

- Every repo-verifiable statement must include file path evidence.
- Evidence must use paths as they appear in the repository, for example `.github/workflows/loop.yml`, `config/watchlist.yaml`, or `scripts/run-loop.ps1`.
- If possible, include line numbers.
- Do not cite files you did not inspect.
- Do not use guesses as evidence.
- If no evidence exists for an expected item, say so in the relevant finding or next action and do not invent a path.

## Required Output Format

Return the report in exactly this section order:

## Findings

List prioritized findings first. Use severity labels such as `High`, `Medium`, or `Low`.

For each finding, include:

- Title
- Risk
- Evidence
- Why it matters
- Suggested next action

If there are no findings, write `None.` under this section.

## Not verifiable from repo

List external or live-state questions that cannot be proven from repository files. Include, at minimum when relevant:

- Actual Windows Task Scheduler registration.
- Actual crontab registration.
- Actual GitHub Actions run history or recent success/failure.
- Actual GitHub secret registration.
- Actual Telegram credential validity or message delivery.
- Actual current external API/portal availability.

If none apply, write `None.`

## Next actions

List the next implementation or review steps in practical order. If implementation is mostly absent, order the work as a build sequence rather than treating every absence as an equal failure.

Prefer concise, actionable steps that move the repository toward a working JeonseLoop product loop.

## Evidence

List every inspected file path that materially informed the report. Include a short note about what was checked in each path.

## Recommended Execution Example

Use this prompt with `codex exec` like this:

```powershell
Get-Content .codex\prompts\loop-review.md -Raw |
  codex exec --sandbox read-only - -o reports\loop-review.md
```
