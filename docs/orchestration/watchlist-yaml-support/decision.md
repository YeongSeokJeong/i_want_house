# Session Decisions

## Task Context
- Task Name: Watchlist YAML Support
- Task ID: watchlist-yaml-support

## Decision Log
| Session | Feature ID | Feature | Decision | Rationale | Impact | Date |
|---------|------------|---------|----------|-----------|--------|------|
| 1 | PLAN | Planning | Use one feature for parser decision, implementation, and tests | The task is localized to watchlist loading and can be verified with focused unit tests plus the full test suite | Keeps the orchestration small and commit-scoped | 2026-06-14 |
| 1 | F-001 | Watchlist YAML parser hardening | Prefer a narrow dependency-free YAML subset over adding PyYAML | The repo currently has no dependency manifest and prior architecture notes deferred third-party YAML parsing | Implementation should remain explicit, small, and test-covered | 2026-06-14 |
| 2 | F-001 | Watchlist YAML parser hardening | Support practical scalar/list syntax, not full YAML | Operators are likely to hand-write inline exclusion lists and quoted names, while nested mappings and advanced YAML remain unnecessary | Widened parser ergonomics without adding dependency or weakening validation | 2026-06-14 |

## Session 1
- Feature ID: PLAN
- Feature: Planning
- Decisions:
  - Treat `BL-20260613-008` as the highest-priority unblocked source-code backlog item.
  - Use the current checkout `D:\git\i_want_house` as the task worktree and branch `task/watchlist-yaml-support` as the single task branch.
  - Defer durable wiki edits unless the implementation produces new domain knowledge beyond the existing note that watchlist config is user-managed and not auto-mutated.
- Alternatives Considered:
  - Add third-party YAML parsing dependency: deferred because dependency management is not established and the expected config shape is small.
  - Leave parser unchanged: rejected because the backlog records this as unresolved risk.
- Risks Introduced:
  - A custom parser can drift from operator expectations if it appears to promise full YAML.
- Follow-up Notes:
  - Keep error messages explicit for unsupported YAML structures.

## Session 2
- Feature ID: F-001
- Feature: Watchlist YAML parser hardening
- Decisions:
  - Support inline list scalars such as `exclude: ["basement", "auction"]`.
  - Preserve `#` characters inside quoted scalars while still allowing trailing comments outside quotes.
  - Parse YAML null forms as `None`, allowing existing validation defaults such as `exclude: null`.
  - Keep malformed inline lists as hard failures through `WatchlistError`.
- Alternatives Considered:
  - Full YAML support through PyYAML: not chosen because dependency management is not established and the needed operator ergonomics are narrow.
  - Supporting nested inline collections: not chosen because watchlist schema does not need nested lists or maps inside scalar fields.
- Risks Introduced:
  - None beyond the existing custom-parser maintenance risk.
- Follow-up Notes:
  - If watchlist schema grows structurally, revisit dependency-based YAML parsing with an explicit dependency manifest.
