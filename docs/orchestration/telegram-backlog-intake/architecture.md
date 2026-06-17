# Architecture Review

## Task Context
- Task Name: Telegram backlog intake
- Task ID: telegram-backlog-intake
- Last Updated: 2026-06-17

## System Context
- Current Stack: Python 3.12 standard library, `unittest`, GitHub Actions, Markdown backlog, JSON state files, repo-local Telegram MCP helper.
- Existing Patterns: state writes use validate-before-replace JSON, source changes are covered by unittest, and Telegram sends require explicit opt-in elsewhere.
- Integration Points: saved Telegram updates JSON, `docs/backlog.md`, `data/state/telegram-intake.json`, `.github/workflows/telegram-backlog-intake.yml`.

## Feature Decomposition Map
| Feature ID | Feature | Description | Depends On | Complexity | Risk |
|------------|---------|-------------|------------|------------|------|
| F-001 | Intake triage core | Parse saved updates, dedupe update IDs, append backlog rows, and persist clarification drafts | None | Medium | Medium |

## Dependency Map
- `telegram_save_recent_updates` or a workflow step writes saved updates JSON.
- `telegram_backlog_intake` reads saved updates and existing intake state.
- `telegram_backlog_intake` writes `docs/backlog.md` and `data/state/telegram-intake.json` through validated paths.
- GitHub Actions persists generated backlog/state changes only when files differ.

## Technical Decisions
- Decision: Implement intake as a Python module under `src/jeonseloop`.
  - Rationale: It can reuse repo test conventions and persistence helpers without coupling to the product monitoring loop.
  - Trade-offs: The module is agent automation code inside the product package, but it remains isolated from the runtime alert path.
- Decision: Use deterministic keyword-based sufficiency and route classification.
  - Rationale: Tests can prove duplicate prevention and backlog output without external LLM state.
  - Trade-offs: Some valid requests may require manual review or later LLM-assisted triage.

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| Duplicate backlog rows from repeated updates | High | Persist processed update IDs and skip them before triage | Backend Agent |
| Poorly specified Telegram messages pollute backlog | Medium | Require action/object signals and store insufficient messages as clarification drafts | Backend Agent |
| Secrets leak through update payloads | Medium | Do not persist full raw updates in intake state; store message excerpts only | Backend Agent |
| Workflow accidentally sends Telegram messages | High | Do not call sendMessage; workflow only reads updates and runs local triage | Backend Agent |
