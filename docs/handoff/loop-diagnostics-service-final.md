# Loop Diagnostics Service Final Handoff

## Summary
- Backlog: BL-20260618-003
- Route: source-code
- Branch: `task/loop-diagnostics-service-stacked`
- Worktree: `D:\git\i_want_house_loop_diagnostics_service`
- Pull Request: https://github.com/YeongSeokJeong/i_want_house/pull/16
- Stacked Base: `task/listing-source-adapters-closeout` / PR #15

## Delivered
- Added `src/jeonseloop/diagnostics.py` with `LoopDiagnostics`.
- Moved collector failure diagnostics, successful listing diagnostics, listing source kind inference, and Hogangnono mapping diagnostic projection out of `LoopCoordinator`.
- Kept existing `health.json` and `collector-diagnostics.json` field contracts compatible.
- Added focused tests for the new diagnostics service boundary in `tests/test_loop.py`.
- Updated `docs/wiki/domains/jeonseloop/overview.md` `## 아키텍처 메모` to include `LoopDiagnostics`.

## Commits
- `e167790` - `refactor(loop-diagnostics-service/f-001): extract loop diagnostics service`

## Verification
- `python -m unittest tests.test_loop tests.test_reliability -v` - PASS, 33 tests.
- `python -m unittest discover -s tests -v` - PASS, 86 tests.

## Decisions
- Preserve diagnostic JSON contracts exactly and only move projection responsibility.
- Keep persistence responsibility in `LoopStateRepository`; persistence splitting remains a separate backlog item.
- Use a stacked PR on PR #15 because `origin/main` did not yet contain the BL-20260618-002 closeout row.

## Unresolved Risks
- None for this task.

## Telegram Safety
- Telegram alerts were not sent.
- `--send` was not used.
