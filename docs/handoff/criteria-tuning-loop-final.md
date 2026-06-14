# Criteria Tuning Loop Final Handoff

**Date**: 2026-06-14
**Branch**: docs/open-requirement-decisions
**Author**: Codex

## Summary
- Completed BL-20260613-010 by extending criteria suggestion generation with false-positive measurement signals.
- `criteria-suggestions.json` now includes decision totals, approved counts, reviewed counts, false-positive signal counts, false-positive ratio, reason counts, and false-positive reason counts.
- Suggestion items now distinguish `false_positive` signals from general `criteria_frequency` signals while preserving `requires_human_approval: true` and `auto_applied: false`.

## Delivered Files
| File | Result |
|------|--------|
| `src/jeonseloop/suggestions.py` | Adds metrics and reason-based false-positive suggestion generation from `logs/criteria-log.md`. |
| `tests/test_llm_review.py` | Adds coverage for metrics, false-positive reason counts, suggestion signals, and no watchlist mutation. |
| `docs/wiki/domains/jeonseloop/overview.md` | Records the durable domain behavior for criteria suggestion metrics. |
| `docs/orchestration/criteria-tuning-loop/` | Captures task plan, progress, decisions, and architecture notes. |
| `docs/backlog.md` | Closes BL-20260613-010 with artifacts and result. |

## Verification
| Command | Result |
|---------|--------|
| `python -m unittest tests.test_llm_review` | PASS: 7 tests. |
| `python -m unittest discover -s tests` | PASS: 49 tests. |
| `$env:PYTHONPATH='src'; python -m jeonseloop.run --dry-run --fixture tests\fixtures\listings.json` | PASS: success, 2 valid listings, 1 approved candidate, 0 sends. |

## Decisions
- False-positive signals are inferred from final non-approve rows with reason prefixes such as `llm_`, `average_price_jump`, and `duplicate_listing`.
- General rejection reasons such as `above_target_price` remain frequency signals, not false-positive signals.
- Suggestions stay review-only and do not mutate `config/watchlist.yaml`.

## Unresolved Risks
- Real-data calibration may need explicit operator labels later to separate confirmed 허위매물 from conservative holds.
