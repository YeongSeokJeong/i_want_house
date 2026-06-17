# Task Plan

## Task Metadata
- Task Name: Telegram ops automation
- Task ID: telegram-ops-automation
- Task Branch: task/telegram-ops-automation
- Task Worktree: D:\git\i_want_house
- Plan Version: v1
- Last Updated: 2026-06-17

## Planning Assumptions
- The task is driven by `BL-20260617-011`.
- Telegram operations must be allowlisted commands or clearly structured requests, not free-form automatic mutation.
- Actual source/config changes must be audit-friendly and reversible; v1 should generate proposals, not write secrets or mutate GitHub repository variables.
- Raw Telegram updates must not be committed.

## Requirement Brief
- In scope:
  - Parse Telegram ops requests from saved/fetched updates.
  - Accept allowlisted intents for source kind, Naver complex map, trade type, and target price proposals.
  - Persist deduped operation proposals to `data/state/telegram-ops.json`.
  - Provide dry-run preview and workflow support without committing raw updates.
  - Keep rollback/audit metadata in state.
- Out of scope:
  - Directly editing GitHub Secrets or repository variables.
  - Directly mutating `.env`.
  - Sending Telegram replies.
  - Committing raw Bot API updates.

## Related Wiki Discovery
| Document | Relevance | Gap |
|----------|-----------|-----|
| `docs/wiki/domains/jeonseloop/overview.md` | Documents source modes, Telegram safety gates, and Telegram backlog intake. | Needs closeout note when ops proposals are implemented. |
| `docs/wiki/decisions/jeonseloop-open-requirement-decisions.md` | Records that criteria suggestions are review artifacts and do not auto-mutate config. | Ops proposals should follow the same approval-gated pattern. |
| `docs/watchlist-operation-guide.md` | Operator guide for watchlist and mapping changes. | May need link/reference after ops automation exists. |

## Related Backlog Items
| Backlog ID | Route | Status | Relationship |
|------------|-------|--------|--------------|
| BL-20260617-011 | source-code | Done | Parent task item for this orchestration |

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | Ops proposal core | Parse allowlisted Telegram ops requests into audited, deduped proposal state | None | Medium | Backend Agent |
| F-002 | Ops discovery workflow | Add scheduled/manual workflow and richer complex lookup guidance for Naver/KB/Hogangnono identifiers | F-001 | Medium | Backend Agent |

## Feature Detail
### F-001 Ops proposal core
- Scope:
  - Add deterministic allowlist parser for Telegram ops requests.
  - Generate proposals for source kind, Naver complex map, trade type, and target price changes.
  - Persist proposals to `data/state/telegram-ops.json` with processed update IDs and rollback/audit fields.
  - Add unit tests and CLI dry-run behavior.
- Acceptance Criteria:
  - [x] Duplicate `update_id` values do not create duplicate proposals.
  - [x] Unknown or non-allowlisted requests become `rejected` or `needs_clarification` records, not config changes.
  - [x] Source kind, Naver map, trade type, and target price proposals are represented without secret values.
  - [x] Dry-run prints proposals without writing state.
  - [x] State writes validate JSON before replacing existing state.
- Out of Scope:
  - GitHub variable/secret mutation.
  - External portal crawling.

### F-002 Ops discovery workflow
- Scope:
  - Add workflow trigger for Telegram ops proposal generation.
  - Add complex lookup guidance or research task generation when identifiers are missing.
  - Document operator approval path.
- Acceptance Criteria:
  - [x] Workflow uses temporary raw update storage and commits only `data/state/telegram-ops.json`.
  - [x] Missing complex identifiers generate reviewable lookup guidance, not silent failure.
  - [x] Operator docs/wiki explain approval boundary and rollback state.
- Out of Scope:
  - Fully autonomous PR merge or live secret changes.

## Execution Order
1. F-001
2. F-002

## Revision Log
| Version | Date | Changed Feature IDs | Changed Backlog IDs | Why Revised | Author |
|---------|------|---------------------|---------------------|-------------|--------|
| v1 | 2026-06-17 | F-001,F-002 | BL-20260617-011 | Initial planning baseline from backlog item | Codex |
