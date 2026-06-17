# Session Decisions

## Task Context
- Task Name: Telegram message context
- Task ID: telegram-message-context

## Decision Log
| Session | Feature ID | Feature | Decision | Rationale | Impact | Date |
|---------|------------|---------|----------|-----------|--------|------|
| 1 | PLAN | Planning | Add message context as candidate listing metadata | Notifier only receives candidates, while analyzer has target and baseline context | Keeps notifier simple and avoids new service dependencies | 2026-06-17 |

## Session 1
- Feature ID: F-001
- Feature: Rich Telegram message
- Decisions:
  - Keep Telegram messages as plain text.
  - Preserve `complex_id` and reason in the message for troubleshooting.
- Alternatives Considered:
  - Make notifier load watchlist/trades directly: rejected because it would couple notification to storage and config.
- Risks Introduced:
  - Existing tests expecting exact message text need to assert durable content rather than full formatting.
- Follow-up Notes:
  - Verification passed with targeted notifier/analyzer tests and `python -m unittest discover -s tests -v`.
