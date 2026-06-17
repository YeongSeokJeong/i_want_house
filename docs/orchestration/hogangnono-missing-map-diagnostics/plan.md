# Task Plan

## Task Metadata
- Task Name: Hogangnono missing map diagnostics
- Task ID: hogangnono-missing-map-diagnostics
- Task Branch: task/hogangnono-missing-map-diagnostics
- Task Worktree: D:\git\i_want_house
- Plan Version: v1
- Last Updated: 2026-06-17

## Planning Assumptions
- The task is driven by `BL-20260615-005`.
- Missing Hogangnono mapping currently fails collection, but the operator needs a clearer missing-target list and example env entry.
- Runtime secrets must not be logged.

## Requirement Brief
- In scope:
  - Improve Hogangnono missing mapping error message.
  - Add collector diagnostics fields for missing mapping targets and required env name.
  - Add tests for source error and cycle diagnostics.
- Out of scope:
  - Automatically discovering Hogangnono apt hashes.
  - Changing source collection behavior when mapping is missing.

## Related Backlog Items
| Backlog ID | Route | Status | Relationship |
|------------|-------|--------|--------------|
| BL-20260615-005 | source-code | Doing | Parent task item for this orchestration |

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | Missing map diagnostics | Make missing Hogangnono apt hash mapping actionable | None | Medium | Backend Agent |

## Feature Detail
### F-001 Missing map diagnostics
- Scope:
  - Include missing `complex_id` and JSON example in the source error message.
  - Add `required_env` and `missing_mapping_targets` to collector diagnostics for Hogangnono mapping failures.
  - Preserve redaction and previous state behavior.
- Acceptance Criteria:
  - [x] Source error names `JEONSELOOP_HOGANGNONO_APT_HASH_MAP`, the missing complex ID, and an example mapping entry.
  - [x] Failure diagnostics list every watchlist complex that still needs a Hogangnono apt hash.
  - [x] Existing source and loop tests pass.
- Out of Scope:
  - Live external validation.

## Execution Order
1. F-001

## Revision Log
| Version | Date | Changed Feature IDs | Changed Backlog IDs | Why Revised | Author |
|---------|------|---------------------|---------------------|-------------|--------|
| v1 | 2026-06-17 | F-001 | BL-20260615-005 | Initial planning baseline from backlog item | Codex |
