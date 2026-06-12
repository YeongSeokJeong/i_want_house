# Task Plan

## Task Metadata
- Task Name: JeonseLoop spec implementation
- Task ID: jeonseloop-spec-implementation
- Task Branch: feature/jeonseloop-automation
- Plan Version: v1
- Last Updated: 2026-06-12

## Planning Assumptions
- `jeonseloop-spec.md` is the authoritative product requirement source.
- The task name is derived from the objective because no explicit `/large-task-orchestrator start <task-name>` suffix was provided.
- The existing `feature/jeonseloop-automation` branch is the shared task branch for all feature commits.
- Live portal/API availability, GitHub Secrets, and actual Telegram delivery are external state; repo-verifiable implementation and dry-run tests are the acceptance evidence.
- Phase 1 Must requirements are implemented before Should/Could requirements unless a later feature is needed to keep the loop usable.

## Related Wiki Discovery
- `docs/wiki/SCHEMA.md`: wiki routing requires durable domain knowledge under `docs/wiki/domains/` and workflow rules under `docs/wiki/rules/workflow/`.
- `docs/wiki/rules/workflow/loop-engineering-routing.md`: separates product-loop evidence from development inspection evidence and marks external service state as non-repo-verifiable.
- `docs/wiki/rules/workflow/development-automation-loop.md`: defines the Codex inspection loop as a development check, not the JeonseLoop product trigger.
- Wiki gap: no `docs/wiki/domains/jeonseloop/overview.md` exists yet. Add it during closeout or a documentation feature if durable product-domain knowledge needs wiki publication.

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | Executable loop foundation | Restore and harden a runnable Python loop with watchlist loading, fixture collection, validation, candidate decisions, safe JSON/Markdown persistence, dry-run behavior, and Telegram send gating. | None | Medium | Backend Agent |
| F-002 | Product trigger workflow | Align GitHub Actions, shell entrypoints, concurrency, permissions, and execution summary with scheduled/manual product-loop requirements. | F-001 | Medium | Backend Agent |
| F-003 | Static dashboard baseline | Add a serverless static dashboard that fetches committed JSON state and shows loop status, history, and urgent-deal feed states. | F-001 | Medium | Frontend Agent |
| F-004 | Reliability and baseline pricing | Add request pacing/retry scaffolding, trade baseline support, health failure tracking, and data quality blocking behavior. | F-001,F-002 | High | Backend Agent |
| F-005 | Candidate quality controls | Add duplicate handling, exclusion rules, alert caps, richer decision logs, and feed JSON for dashboard review. | F-001,F-003 | Medium | Backend Agent |
| F-006 | Optional LLM review and improvement suggestions | Add disabled-by-default LLM review, JSON parsing safeguards, and human-approved criteria suggestion generation. | F-005 | High | Backend Agent |

## Feature Detail
### F-001 Executable loop foundation
- Scope:
  - Restore `src/jeonseloop/`, `scripts/run-loop.*`, fixture data, and unit tests.
  - Load and validate `config/watchlist.yaml`, including empty-watchlist and invalid-config behavior.
  - Limit fixture collection to watchlist complexes and keep live portal calls out of the first baseline.
  - Validate listing records, quarantine invalid records in criteria logs, and avoid persisting invalid records as normal state.
  - Classify target-price candidates, respect notified-state dedup, cap planned sends to five, and block real sends unless `--send` and secrets are available.
  - Persist JSON with validate-before-replace writes and keep dry-run from writing state.
- Acceptance Criteria:
  - [ ] `python -m unittest discover -s tests` passes.
  - [ ] `python -m jeonseloop.run --dry-run --fixture tests/fixtures/listings.json` exits successfully without writing state.
  - [ ] A fixture-backed non-dry run writes health, listing, history, notified, and criteria-log artifacts under caller-provided temp directories.
  - [ ] Invalid watchlist configuration records health failure without sending alerts.
  - [ ] Telegram sends remain disabled unless `--send` is explicitly passed and environment secrets are set.
- Out of Scope:
  - Live portal scraping, real trade API integration, static dashboard UI, and GitHub Pages deployment.

### F-002 Product trigger workflow
- Scope:
  - Ensure `.github/workflows/jeonseloop.yml` includes 09:00 and 18:00 KST cron coverage and manual dispatch.
  - Configure concurrency to avoid overlapping state writes.
  - Decide and implement safe write/commit behavior for state updates on scheduled/manual runs.
  - Keep default/manual dry-run semantics explicit.
- Acceptance Criteria:
  - [ ] Workflow has schedule and `workflow_dispatch`.
  - [ ] Overlapping runs cannot modify state concurrently.
  - [ ] Repository writes use safe permissions and do not run during dry-run.
  - [ ] Workflow command paths match `scripts/run-loop.*` or `python -m jeonseloop.run`.
- Out of Scope:
  - Proving actual GitHub Actions execution history or secret configuration.

### F-003 Static dashboard baseline
- Scope:
  - Add static HTML/CSS/JS assets for GitHub Pages.
  - Fetch `data/state/health.json`, `data/history/*.json`, and dashboard feed data.
  - Show empty/error states per section without requiring a server or build step.
- Acceptance Criteria:
  - [ ] Dashboard renders from committed static files only.
  - [ ] Missing or failed JSON fetches show section-local error states.
  - [ ] Last execution status and history state are visible from sample JSON.
- Out of Scope:
  - Authentication, accounts, or a dynamic backend.

### F-004 Reliability and baseline pricing
- Scope:
  - Add request interval enforcement and retry/backoff scaffolding for external fetchers.
  - Add recent trade cache loading and baseline-price decision support.
  - Track consecutive failures and health alert eligibility.
  - Block urgent alerts when abnormal average-price jumps are detected.
- Acceptance Criteria:
  - [ ] Request interval cannot be configured below two seconds.
  - [ ] Transient fetch failures retry up to three times where external fetchers are enabled.
  - [ ] Baseline and target-price fallback decisions are both test-covered.
  - [ ] Health state tracks failure streaks and last-success context.
- Out of Scope:
  - Guaranteeing live external API availability.

### F-005 Candidate quality controls
- Scope:
  - Apply watchlist exclusion conditions to candidate decisions.
  - Deduplicate equivalent listings and record duplicate rationale.
  - Produce dashboard-friendly urgent-deal feed JSON.
  - Record alert-cap overflow in health or execution summary.
- Acceptance Criteria:
  - [ ] Excluded listings never alert even if price conditions pass.
  - [ ] Equivalent duplicate listings produce one representative candidate.
  - [ ] More than five approved candidates plans/sends only five Telegram alerts and exposes overflow to dashboard data.
  - [ ] Decision reasons are queryable from logs or feed JSON.
- Out of Scope:
  - User-approved automatic criteria updates.

### F-006 Optional LLM review and improvement suggestions
- Scope:
  - Add disabled-by-default LLM review configuration and safe JSON parsing.
  - Hold candidates on LLM failure or invalid JSON.
  - Generate criteria improvement suggestions after sufficient decision-log volume without auto-applying changes.
- Acceptance Criteria:
  - [ ] LLM review is not invoked unless configured with required secrets.
  - [ ] Invalid LLM responses do not result in Telegram alerts.
  - [ ] Criteria suggestions do not modify `config/watchlist.yaml` without explicit approval.
- Out of Scope:
  - Selecting the final human approval channel without user decision.

## Execution Order
1. F-001
2. F-002
3. F-003
4. F-004
5. F-005
6. F-006

## Revision Policy
- Plan revision is allowed only when scope, constraints, risks, or sequencing change.
- Any revision must run through `/large-task-orchestrator revise jeonseloop-spec-implementation`.
- Revisions must update affected feature IDs in both `plan.md` and `progress.md`.

## Revision Log
| Version | Date | Changed Feature IDs | Why Revised | Author |
|---------|------|---------------------|-------------|--------|
| v1 | 2026-06-12 | F-001,F-002,F-003,F-004,F-005,F-006 | Initial planning baseline from `jeonseloop-spec.md` | Codex |
