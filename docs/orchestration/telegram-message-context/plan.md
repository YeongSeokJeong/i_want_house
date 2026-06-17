# Task Plan

## Task Metadata
- Task Name: Telegram message context
- Task ID: telegram-message-context
- Task Branch: task/telegram-message-context
- Task Worktree: D:\git\i_want_house
- Plan Version: v1
- Last Updated: 2026-06-17

## Planning Assumptions
- The task is driven by `BL-20260615-006`.
- Telegram sending remains gated by `--send` and required secrets.
- Candidate messages can use target and baseline metadata added during classification without changing approval behavior.

## Requirement Brief
- In scope:
  - Add target price and trade baseline context to candidate listing metadata.
  - Format Telegram messages with readable price, target gap, baseline/urgent line context, and listing link.
  - Add tests for enriched candidate metadata and message text.
- Out of scope:
  - Sending Telegram during tests.
  - Changing analyzer approval rules.
  - Changing Telegram Bot API configuration.

## Related Backlog Items
| Backlog ID | Route | Status | Relationship |
|------------|-------|--------|--------------|
| BL-20260615-006 | source-code | Doing | Parent task item for this orchestration |

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | Rich Telegram message | Make alert messages easier to evaluate quickly | None | Medium | Backend Agent |

## Feature Detail
### F-001 Rich Telegram message
- Scope:
  - Add target/baseline context to candidate listing dictionaries in analyzer output.
  - Format Telegram message lines with Korean labels, formatted KRW, target gap, reason, and link.
  - Keep legacy key details such as `complex_id` visible for troubleshooting.
- Acceptance Criteria:
  - [x] Message includes target gap, trade baseline or fallback state, and link.
  - [x] Message remains plain text safe for Telegram.
  - [x] Existing no-send safety behavior remains intact.
  - [x] Full unittest suite passes.
- Out of Scope:
  - Markdown/HTML parse mode.

## Execution Order
1. F-001

## Revision Log
| Version | Date | Changed Feature IDs | Changed Backlog IDs | Why Revised | Author |
|---------|------|---------------------|---------------------|-------------|--------|
| v1 | 2026-06-17 | F-001 | BL-20260615-006 | Initial planning baseline from backlog item | Codex |
