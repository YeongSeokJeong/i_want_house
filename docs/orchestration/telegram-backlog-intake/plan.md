# Task Plan

## Task Metadata
- Task Name: Telegram backlog intake
- Task ID: telegram-backlog-intake
- Task Branch: task/telegram-backlog-intake
- Task Worktree: D:\git\i_want_house
- Plan Version: v1
- Last Updated: 2026-06-17

## Planning Assumptions
- The task is driven by `BL-20260617-010`.
- Telegram reads happen through a saved `getUpdates` JSON file or the repo-local Telegram MCP helper; this task does not send Telegram messages.
- The first implementation should be conservative: deterministic triage, duplicate update prevention, and audit-friendly state before any opt-in reply workflow.
- Backlog additions are appended only for sufficiently actionable requests; unclear messages are recorded as clarification drafts in state.

## Requirement Brief
- In scope:
  - Read saved Telegram Bot API updates.
  - Filter user text messages into backlog-intake candidates.
  - Track processed `update_id` values to avoid duplicate backlog rows.
  - Append sufficient requests to `docs/backlog.md` as `Todo` rows with stable `BL-*` IDs.
  - Record insufficient requests as `clarification_needed` drafts in `data/state/telegram-intake.json`.
  - Provide a GitHub Actions workflow for scheduled/manual agent-side triage without Telegram sends.
- Out of scope:
  - Sending Telegram clarification questions.
  - Applying source-code, watchlist, or environment changes from Telegram.
  - Reading arbitrary historical Telegram chat history outside Bot API `getUpdates` data.

## Related Wiki Discovery
| Document | Relevance | Gap |
|----------|-----------|-----|
| `docs/wiki/domains/jeonseloop/overview.md` | Documents Telegram safety gates, state files, external-state boundaries, and repo-state loop behavior. | Needs a closeout note that Telegram backlog intake is read-only toward Telegram and writes auditable backlog/state. |
| `docs/wiki/rules/workflow/development-automation-loop.md` | Describes development inspection automation boundaries. | No structural change required. |
| `docs/wiki/rules/workflow/loop-engineering-routing.md` | Separates trigger/discover/execute/verify/persist/escalate responsibilities. | No structural change required. |

## Related Backlog Items
| Backlog ID | Route | Status | Relationship |
|------------|-------|--------|--------------|
| BL-20260617-010 | source-code | Done | Parent task item for this orchestration |

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | Intake triage core | Convert saved Telegram updates into backlog additions or clarification drafts | None | Medium | Backend Agent |

## Feature Detail
### F-001 Intake triage core
- Scope:
  - Add deterministic Telegram update parsing and triage code.
  - Add CLI entrypoint for saved-update intake.
  - Add workflow wiring for scheduled/manual triage.
  - Add unit and workflow tests.
- Acceptance Criteria:
  - [x] Already processed update IDs are skipped on later runs.
  - [x] Sufficient requests append exactly one `Todo` backlog row with a new stable `BL-*` ID.
  - [x] Insufficient requests are not added to backlog and are stored as `clarification_needed`.
  - [x] The implementation does not send Telegram messages and does not require Telegram secrets for saved-file tests.
  - [x] State writes validate JSON before replacing existing state.
  - [x] Full unittest suite passes.
- Out of Scope:
  - Telegram `sendMessage`.
  - Automatic operations/config changes from Telegram.

## Execution Order
1. F-001

## Revision Log
| Version | Date | Changed Feature IDs | Changed Backlog IDs | Why Revised | Author |
|---------|------|---------------------|---------------------|-------------|--------|
| v1 | 2026-06-17 | F-001 | BL-20260617-010 | Initial planning baseline from backlog item | Codex |
