# Task Plan

## Task Metadata
- Task Name: Watchlist YAML Support
- Task ID: watchlist-yaml-support
- Task Branch: task/watchlist-yaml-support
- Task Worktree: D:\git\i_want_house
- Plan Version: v1
- Last Updated: 2026-06-14

## Planning Assumptions
- The backlog row `BL-20260613-008` is the highest-priority unblocked source-code item.
- The repository has no Python dependency manifest, so a third-party YAML dependency should not be introduced for this small config parser unless the existing parser cannot be made safe enough.
- The parser should support practical hand-written `config/watchlist.yaml` variants while staying narrower than the full YAML specification.
- User-managed watchlist values must still go through existing validation before a loop cycle can collect listings or send alerts.

## Related Backlog Items
| Backlog ID | Route | Status | Relationship |
|------------|-------|--------|--------------|
| BL-20260613-008 | source-code | Doing | Parent task item for this orchestration |

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | Watchlist YAML parser hardening | Decide the supported YAML subset and implement/test the needed parser improvements for operator-managed watchlists. | None | Medium | Backend Agent |

## Feature Detail
### F-001 Watchlist YAML parser hardening
- Scope:
  - Inspect the current parser, sample config, and test expectations.
  - Define the supported YAML subset in task decisions.
  - Extend `src/jeonseloop/watchlist.py` only where needed for practical watchlist syntax.
  - Add focused coverage in `tests/test_watchlist.py`.
  - Preserve invalid-watchlist failure behavior.
- Acceptance Criteria:
  - [ ] The current sample `config/watchlist.yaml` still loads successfully.
  - [ ] A realistic hand-written YAML watchlist variant that exceeds the previous simple subset loads correctly.
  - [ ] Unsupported or malformed YAML remains a `WatchlistError` rather than silently producing unsafe data.
  - [ ] `python -m unittest discover -s tests` passes.
- Out of Scope:
  - Adding a new third-party YAML package.
  - Auto-modifying `config/watchlist.yaml`.
  - Changing listing collection, analysis, notification, or dashboard behavior.

## Execution Order
1. F-001

## Revision Log
| Version | Date | Changed Feature IDs | Changed Backlog IDs | Why Revised | Author |
|---------|------|---------------------|---------------------|-------------|--------|
| v1 | 2026-06-14 | F-001 | BL-20260613-008 | Initial planning baseline | Codex |

