# Telegram Message Context Handoff

## Summary
- Completed backlog item `BL-20260615-006`.
- Telegram candidate messages now carry enough price context to evaluate the alert quickly.

## Delivered
- `CandidateAnalyzer` now enriches candidate listing metadata with target price, target gap, recent trade baseline, discount urgent line, and urgent-line gap.
- `format_candidate_message` now renders readable plain text with formatted KRW values, target gap, baseline/urgent-line context, area/floor, reason, listing link, and `complex_id`.
- Existing send gating is unchanged: no Telegram send happens without `--send` and required secrets.
- Added tests for message content and analyzer metadata.
- Updated the JeonseLoop domain wiki.

## Verification
- Targeted notifier/analyzer tests.
- `python -m unittest discover -s tests -v`

## Follow-up
- The message remains plain text and does not use Telegram parse modes.
