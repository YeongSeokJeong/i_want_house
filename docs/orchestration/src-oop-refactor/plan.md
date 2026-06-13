# Task Plan

## Task Metadata
- Task Name: src OOP architecture refactor
- Task ID: src-oop-refactor
- Task Branch: task/src-oop-refactor
- Plan Version: v1
- Last Updated: 2026-06-13

## Planning Assumptions
- The user objective is to refactor code under `src/` so the architecture better matches an object-oriented paradigm.
- The task name is derived from the objective because no explicit `/large-task-orchestrator start <task-name>` suffix was provided.
- Existing CLI behavior, fixture-backed runs, dashboard data shapes, and Telegram send gating must remain backward compatible.
- Refactoring should move orchestration and business behavior behind cohesive classes without introducing third-party dependencies.
- Existing procedural public functions may remain as compatibility wrappers when tests or entrypoints already depend on them.
- Live external services remain out of scope; repo-verifiable tests and fixture-backed execution are the acceptance evidence.

## Requirement Brief
- In scope:
  - Introduce object-oriented domain/application/service boundaries under `src/jeonseloop/`.
  - Reduce broad procedural coordination by moving stateful use cases into cohesive classes.
  - Preserve all externally observable behavior and current safety constraints.
  - Add or update tests that prove compatibility and the new class boundaries.
- Out of scope:
  - Changing product requirements, alert rules, dashboard contracts, environment variable names, or workflow schedules.
  - Adding a database, web framework, dependency injection container, or non-standard-library runtime dependency.
  - Live portal/API integration.
- Initial acceptance criteria:
  - `python -m unittest discover -s tests` passes.
  - `python -m jeonseloop.run --dry-run --fixture tests/fixtures/listings.json` still exits successfully without sends or state writes.
  - Core loop behavior can be exercised through explicit classes rather than only module-level procedural functions.
  - Previous JSON state safety and Telegram send gating behavior remain intact.

## Related Wiki Discovery
- `docs/wiki/SCHEMA.md`: durable wiki updates must be routed under `domains/`, `decisions/`, or `rules/`.
- `docs/wiki/domains/jeonseloop/overview.md`: records product-loop entrypoints, safety constraints, dashboard state files, and candidate quality behavior.
- `docs/wiki/rules/workflow/loop-engineering-routing.md`: confirms product loop implementation evidence is under `src/jeonseloop/`, `config/watchlist.yaml`, and `tests/`.
- `docs/wiki/rules/workflow/development-automation-loop.md`: separates development inspection from product execution.
- Wiki gap: if the OOP boundaries become durable architecture knowledge, update `docs/wiki/domains/jeonseloop/overview.md` during closeout with a concise architecture note.

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | Domain and service object boundaries | Introduce cohesive classes for collection, validation, analysis, persistence, notification, review, and suggestions while preserving existing function APIs. | None | High | Backend Agent |
| F-002 | Object-oriented loop orchestration | Refactor the one-cycle product loop and CLI assembly to compose service objects through an application-level coordinator. | F-001 | High | Backend Agent |
| F-003 | Architecture QA and closeout | Verify behavior, remove avoidable procedural leakage, document decisions, and close the orchestration task. | F-001,F-002 | Medium | QA Agent |

## Feature Detail
### F-001 Domain and service object boundaries
- Scope:
  - Add object-oriented service classes around existing module responsibilities.
  - Keep module-level functions as thin compatibility wrappers where public tests or entrypoints use them.
  - Prefer constructor-injected configuration, paths, or clients over hidden module-level coordination.
  - Add focused tests for at least one representative class boundary in each high-risk area touched.
- Acceptance Criteria:
  - [ ] Existing tests pass.
  - [ ] Collection, validation, analysis, persistence, notification, review, and suggestion responsibilities each expose a cohesive class API.
  - [ ] Existing module-level public functions continue to work as compatibility wrappers.
  - [ ] No runtime secrets or machine-specific values are introduced.
- Out of Scope:
  - Rewriting CLI flow or changing execution summaries beyond what wrappers require.

### F-002 Object-oriented loop orchestration
- Scope:
  - Introduce an application-level loop coordinator class that owns the Trigger/Discover/Execute/Verify/Persist/Escalate cycle for one run.
  - Refactor `src/jeonseloop/run.py` or `loop.py` assembly so dependencies are explicit and replaceable.
  - Keep `python -m jeonseloop.run` command-line behavior stable.
  - Add tests proving dry-run, fixture-backed run, and send gating behavior through the coordinator.
- Acceptance Criteria:
  - [ ] Existing tests pass.
  - [ ] Fixture-backed dry-run succeeds without state writes or sends.
  - [ ] Non-dry fixture run still writes the expected temp state artifacts through validate-before-replace paths.
  - [ ] The loop coordinator can be instantiated in tests with explicit service dependencies.
- Out of Scope:
  - Changing workflow YAML behavior or dashboard rendering logic.

### F-003 Architecture QA and closeout
- Scope:
  - Review `src/` for remaining unnecessary procedural orchestration or hidden coupling.
  - Update orchestration decision/progress files with final evidence.
  - Run full unit tests and fixture-backed product-loop verification.
  - Perform wiki closeout check and update `docs/wiki/` only if durable architecture knowledge should be published.
- Acceptance Criteria:
  - [ ] `python -m unittest discover -s tests` passes.
  - [ ] Fixture-backed dry-run passes.
  - [ ] Orchestration docs record feature commits, QA evidence, and remaining risks.
  - [ ] Durable wiki update is completed or explicitly recorded as not needed.
- Out of Scope:
  - Additional product features unrelated to OOP architecture.

## Execution Order
1. F-001
2. F-002
3. F-003

## Revision Policy
- Plan revision is allowed only when scope, constraints, risks, or sequencing change.
- Any revision must run through `/large-task-orchestrator revise src-oop-refactor`.
- Revisions must update affected feature IDs in both `plan.md` and `progress.md`.

## Revision Log
| Version | Date | Changed Feature IDs | Why Revised | Author |
|---------|------|---------------------|-------------|--------|
| v1 | 2026-06-13 | F-001,F-002,F-003 | Initial OOP refactor planning baseline from user objective | Codex |
