# Task Plan

## Task Metadata
- Task Name: Criteria tuning loop
- Task ID: criteria-tuning-loop
- Task Branch: docs/open-requirement-decisions
- Task Worktree: D:\git\i_want_house
- Plan Version: v1
- Last Updated: 2026-06-14

## Planning Assumptions
- BL-20260613-010 is the current source-code backlog item to complete.
- The task should improve repo-verifiable tuning signals without requiring live portal data or real Telegram sends.
- Existing safety constraints remain: criteria suggestions are review artifacts only and never auto-apply watchlist changes.
- The current PR branch is reused as the task branch because PR #7 is already open and contains related backlog/wiki work.

## Related Backlog Items
| Backlog ID | Route | Status | Relationship |
|------------|-------|--------|--------------|
| BL-20260613-010 | source-code | Doing | Parent source-code item for false-positive measurement and criteria tuning |

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | Criteria metrics and suggestions | Add measurable false-positive review signals and tuning suggestions from criteria logs | None | Medium | Backend Agent |

## Feature Detail
### F-001 Criteria metrics and suggestions
- Scope:
  - Parse `logs/criteria-log.md` into decision rows with enough signal to compare pre-review approvals against final held/rejected outcomes.
  - Add false-positive metrics to `data/state/criteria-suggestions.json`.
  - Generate specific human-review suggestions for frequent hold/reject reasons while preserving `auto_applied: false`.
  - Add focused tests for metrics, suggestions, and no watchlist mutation.
- Acceptance Criteria:
  - [ ] Criteria suggestions include total decisions, approved decisions, false-positive count, false-positive ratio, and reason counts.
  - [ ] LLM hold/reject reasons after prior approvals are counted as false-positive signals.
  - [ ] Frequent false-positive reasons produce review-required suggestions.
  - [ ] `config/watchlist.yaml` is not modified by suggestion generation.
  - [ ] Full unit test suite passes.
- Out of Scope:
  - Live portal data sampling.
  - Automatic watchlist or threshold mutation.
  - Real Telegram sends.

## Execution Order
1. F-001

## Revision Log
| Version | Date | Changed Feature IDs | Changed Backlog IDs | Why Revised | Author |
|---------|------|---------------------|---------------------|-------------|--------|
| v1 | 2026-06-14 | F-001 | BL-20260613-010 | Initial planning baseline from current backlog priority | Codex |
