# Dashboard Pre Urgent Grades Handoff

## Summary
- Completed backlog item `BL-20260617-006`.
- The dashboard now grades feed candidates by urgent-line distance and separates alert-planned candidates from observation candidates.

## Delivered
- Added dashboard projection grades: `급매`, `근접`, `관심`, `멀리 있음`, and `기준 부족`.
- Split the selected-complex feed into `알림 대상` and `관찰 대상` sections.
- Added grade badges and urgent-line distance text to feed items.
- Kept analyzer, Telegram, and persistence behavior unchanged.
- Updated static dashboard tests and the JeonseLoop domain wiki.

## Verification
- `node --check assets/dashboard.js`
- `python -m unittest discover -s tests -v`
- Local static HTTP smoke: `/`, `/assets/dashboard.js`, and `/data/history/baengnyeonsan-hillstate-3.json` returned 200.

## Follow-up
- Persisted grade fields were intentionally deferred until another consumer needs a stable grade contract.
- Dashboard grade thresholds should be revisited if the analyzer approval policy changes.
