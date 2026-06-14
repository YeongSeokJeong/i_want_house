# Session Decisions

## Task Context
- Task Name: Criteria tuning loop
- Task ID: criteria-tuning-loop

## Decision Log
| Session | Feature ID | Feature | Decision | Rationale | Impact | Date |
|---------|------------|---------|----------|-----------|--------|------|
| 1 | F-001 | Criteria metrics and suggestions | Treat final non-approve rows that preserve an approval-origin reason as false-positive signals | The current log has one row per final candidate decision and reasons such as `llm_invalid_response` or `average_price_jump` identify candidates that would otherwise have been approved | Enables repo-verifiable NFR-07 tracking without storing separate review-stage logs | 2026-06-14 |
| 1 | F-001 | Criteria metrics and suggestions | Keep suggestions as review artifacts only | Existing product safety requires human approval before criteria changes | `criteria-suggestions.json` gains metrics and proposals while `config/watchlist.yaml` remains unchanged | 2026-06-14 |

## Session 1
- Feature ID: F-001
- Feature: Criteria metrics and suggestions
- Decisions:
  - Count `llm_*`, `average_price_jump`, `duplicate_listing`, and exclusion-derived post-approval blocks as false-positive review signals when they appear in the criteria log.
  - Surface metrics in JSON so future dashboard or operator review can compare review effectiveness over time.
- Alternatives Considered:
  - Add a second Markdown log for pre-review decisions: rejected for now because the existing backlog asks for tuning loop support and current `criteria-log.md` can be extended without a new state contract.
  - Auto-update thresholds from frequent reasons: rejected because criteria changes require human approval.
- Risks Introduced:
  - Reason-prefix heuristics can undercount false positives until real data reason taxonomy stabilizes.
- Follow-up Notes:
  - Real-data calibration may later add explicit operator labels for confirmed false positives.
