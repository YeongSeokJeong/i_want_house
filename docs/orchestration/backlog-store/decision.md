# Session Decisions

## Task Context
- Task Name: Backlog markdown store extraction
- Task ID: backlog-store

## Decision Log
| Session | Feature ID | Feature | Decision | Rationale | Impact | Date |
|---------|------------|---------|----------|-----------|--------|------|
| 1 | PLAN | Planning | Implement as one feature | The backlog item is a bounded extraction with one clear test boundary | Keeps the unattended loop reviewable within one PR | 2026-06-19 |
| 1 | F-001 | Backlog markdown store | Keep Markdown table contract unchanged | Existing docs, tests, and intake output depend on the current table shape | Reduces behavior risk and keeps the change structural | 2026-06-19 |

## Session 1
- Feature ID: F-001
- Feature: Backlog markdown store
- Decisions:
  - Use a small reusable module instead of expanding Telegram intake.
  - Preserve validate-before-replace writes by continuing to write through a temporary file and `os.replace`.
  - Do not add new lifecycle editing APIs beyond the needed append/create operations.
- Alternatives Considered:
  - Full backlog lifecycle repository: deferred because BL-20260618-005 only requires extracting current table manipulation, and broader status transitions belong to backlog-management skill work.
  - Leave helper functions in `telegram_backlog_intake.py`: rejected because it preserves the coupling identified by the backlog item.
- Risks Introduced:
  - The Markdown parser remains intentionally narrow and tied to the existing table shape.
- Follow-up Notes:
  - A future backlog-management quality gate can reuse this store if it needs source-code access to backlog rows.
