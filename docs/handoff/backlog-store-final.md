# Backlog Store Final Handoff

## Summary
- Backlog: BL-20260618-005
- Route: source-code
- Branch: `task/backlog-store`
- Worktree: `D:\git\i_want_house_backlog_store`
- Pull Request: https://github.com/YeongSeokJeong/i_want_house/pull/18

## Delivered
- Added `src/jeonseloop/backlog_store.py` with `BacklogItem`, `BacklogStore`, next sequence allocation, row insertion, table validation, and validate-before-replace Markdown writes.
- Updated `src/jeonseloop/telegram_backlog_intake.py` so Telegram triage builds `BacklogItem` records and delegates all `docs/backlog.md` table writes to `BacklogStore`.
- Added `tests/test_backlog_store.py` for next ID allocation, row insertion, Markdown cell escaping, duplicate ID failure, missing header failure, and preservation of existing backlog text on validation failure.
- Updated `docs/wiki/domains/jeonseloop/overview.md` `## Telegram 백로그 intake` with the new backlog store module boundary and safety rule.

## Commits
- `427009d` - `refactor(backlog-store/f-001): extract backlog markdown store`

## Verification
- `python -m py_compile src\jeonseloop\backlog_store.py src\jeonseloop\telegram_backlog_intake.py tests\test_backlog_store.py` - PASS.
- `python -m unittest tests.test_backlog_store tests.test_telegram_backlog_intake -v` - PASS, 11 tests.
- `python -m unittest discover -s tests -v` - PASS, 95 tests.

## Decisions
- Keep the repository API narrow: append/create behavior only, no broad lifecycle editor.
- Preserve the existing Markdown table contract and generated Telegram intake row shape.
- Continue validate-before-replace writes for backlog Markdown so failed validation preserves the previous file.

## Unresolved Risks
- None for this task.
- Broader backlog quality gate improvements remain tracked separately in BL-20260618-008.

## Telegram Safety
- Telegram alerts were not sent.
- `--send` was not used.
