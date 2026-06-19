# Architecture Review

## Task Context
- Task Name: Backlog markdown store extraction
- Task ID: backlog-store
- Last Updated: 2026-06-19

## System Context
- Current Stack: Python standard library, unittest, Markdown files as durable repo state.
- Existing Patterns: Small modules with dataclasses and explicit helper boundaries; JSON state writes use validate-before-replace semantics.
- Integration Points: `telegram_backlog_intake.py` generates backlog rows from Telegram triage results; `docs/backlog.md` is the durable backlog artifact.

## Feature Decomposition Map
| Feature ID | Feature | Description | Depends On | Complexity | Risk |
|------------|---------|-------------|------------|------------|------|
| F-001 | Backlog markdown store | Extract backlog row creation, next ID allocation, insertion, and validation into `backlog_store.py` | None | Medium | Low |

## Dependency Map
- `telegram_backlog_intake.py` -> `backlog_store.py` for Markdown backlog persistence.
- `backlog_store.py` -> filesystem only; no Telegram or intake dependencies.
- `tests/test_telegram_backlog_intake.py` and focused store tests verify compatibility.

## Technical Decisions
- Decision: Create a reusable store module with a narrow API.
  - Rationale: The immediate coupling is Markdown table mechanics inside Telegram intake, not all backlog lifecycle state changes.
  - Trade-offs: Keeps implementation small, but does not solve every future backlog editing use case.
- Decision: Preserve current table format and row text.
  - Rationale: This is a structural extraction and should not change accepted Telegram intake output.
  - Trade-offs: Markdown parsing remains simple and contract-specific.

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| Row formatting changes could break existing tests or operator expectations | Medium | Keep compatibility assertions and add focused store tests | Codex |
| Duplicate ID validation could become weaker during extraction | Medium | Add direct duplicate validation regression test | Codex |
| Source-code task branch could mix unrelated commits | Low | Work from dedicated `task/backlog-store` worktree based on `origin/main` | Codex |
