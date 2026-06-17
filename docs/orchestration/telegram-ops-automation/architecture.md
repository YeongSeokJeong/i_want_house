# Architecture Review

## Task Context
- Task Name: Telegram ops automation
- Task ID: telegram-ops-automation
- Last Updated: 2026-06-17

## System Context
- Current Stack: Python 3.12 standard library, `unittest`, GitHub Actions, JSON state files, Telegram Bot API saved updates.
- Existing Patterns: JSON state uses validate-before-replace writes; config/criteria suggestions are review artifacts and do not mutate operator config automatically.
- Integration Points: saved Telegram updates, `data/state/telegram-ops.json`, `config/watchlist.yaml`, listing source env names, future workflow.

## Feature Decomposition Map
| Feature ID | Feature | Description | Depends On | Complexity | Risk |
|------------|---------|-------------|------------|------------|------|
| F-001 | Ops proposal core | Parse allowlisted Telegram ops commands and persist audited proposals | None | Medium | Medium |
| F-002 | Ops discovery workflow | Add scheduled/manual workflow and identifier lookup guidance | F-001 | Medium | Medium |

## Dependency Map
- F-001 reads saved updates and existing ops state.
- F-001 writes `data/state/telegram-ops.json` only.
- F-002 will reuse F-001 and add workflow/docs/discovery guidance.

## Technical Decisions
- Decision: Keep proposal generation separate from product loop execution.
  - Rationale: Telegram ops input is operator automation, not urgent-sale alert behavior.
  - Trade-offs: Operators still need an approval/apply step.
- Decision: Represent changes as structured proposal records.
  - Rationale: State can be reviewed, rolled back, and converted into a PR or manual variable update later.
  - Trade-offs: More code than directly editing env-like files.

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| Telegram message triggers unintended source change | High | Allowlist exact intents and store proposals only | Backend Agent |
| Secret/operator value is committed | High | Never write `.env`; avoid raw updates and redact excerpts | Backend Agent |
| Duplicate updates create repeated proposals | Medium | Persist processed update IDs | Backend Agent |
| Missing complex identifiers block automation | Medium | F-002 generates lookup guidance instead of guessing | Backend Agent |
