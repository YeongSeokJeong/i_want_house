# Watchlist YAML Support Final Handoff

**Date**: 2026-06-14
**Branch**: task/watchlist-yaml-support
**Backlog**: BL-20260613-008

## Delivered Features
| Feature ID | Feature | Outcome |
|------------|---------|---------|
| F-001 | Watchlist YAML parser hardening | Completed. The dependency-free parser now supports practical hand-written watchlist syntax while preserving fail-fast validation. |

## Implementation Outcome
- `src/jeonseloop/watchlist.py` now strips comments only outside quoted scalars.
- Inline YAML lists such as `exclude: ["basement", "auction"]` are parsed into Python lists.
- YAML null forms (`null`, `Null`, `NULL`, `~`) are parsed as `None`, preserving existing validation/default handling.
- Boolean scalar parsing accepts common YAML case variants.
- Malformed inline lists raise `WatchlistError` instead of silently producing partial data.

## Verification
- `python -m unittest tests.test_watchlist` passed: 6 tests.
- `python -m unittest discover -s tests` passed: 48 tests.

## Key Decisions
- Keep YAML support dependency-free because the repo has no Python dependency manifest and the required config shape is narrow.
- Widen only operator-relevant syntax rather than promising full YAML support.
- Keep parsing and validation separated so unsupported structures remain explicit failures.

## Wiki Closeout
- No wiki content change was required. Existing JeonseLoop domain wiki already records that `config/watchlist.yaml` is operator-managed and not auto-mutated.

## Unresolved Risks
- A future structural watchlist schema expansion should revisit full YAML parsing together with an explicit dependency manifest.
- `docs/backlog.md` contains a pre-existing unrelated uncommitted `BL-20260614-003` row; it was preserved.
