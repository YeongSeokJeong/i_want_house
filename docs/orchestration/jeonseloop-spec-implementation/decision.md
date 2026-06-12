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
