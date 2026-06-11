# EARS Guide

EARS acceptance criteria must be observable and testable. Prefer concrete system behavior over intent.

## Core Patterns

| Pattern | Use When | Form |
|---|---|---|
| Event-driven | A trigger causes behavior | `WHEN <event> THE SYSTEM SHALL <response>.` |
| Ubiquitous | Always true system property | `THE SYSTEM SHALL <always-on behavior>.` |
| State-driven | Behavior applies during a state | `WHILE <state> THE SYSTEM SHALL <behavior>.` |
| Optional feature | Behavior applies only if a feature/config is enabled | `WHERE <feature/config> <condition> THE SYSTEM SHALL <behavior>.` |
| Unwanted behavior | Exception, invalid input, or failure | `IF <condition> THEN THE SYSTEM SHALL <handling behavior>.` |

## Good Examples

- WHEN a user submits a reservation with a valid room, date, time range, and attendee count THE SYSTEM SHALL create the reservation and display its confirmation ID.
- IF the requested room is already reserved for any overlapping time range THEN THE SYSTEM SHALL reject the request and identify the conflicting time range.
- WHILE a payment request is pending THE SYSTEM SHALL prevent duplicate submissions for the same order ID.
- WHERE guest checkout is enabled THE SYSTEM SHALL allow checkout without account registration.

## Vague-to-Testable Rewrites

| Vague Input | Better AC |
|---|---|
| 검색은 빨라야 한다 | `[확인 필요] WHEN a user submits a search query THE SYSTEM SHALL return results within an agreed latency target.` |
| UI는 직관적이어야 한다 | `[확인 필요] WHEN a first-time user opens the form THE SYSTEM SHALL show required fields, validation messages, and the primary submit action without requiring documentation.` |
| user-friendly errors | `IF validation fails THEN THE SYSTEM SHALL show the failed field, the reason, and the required correction.` |
| robust sync | `IF synchronization fails THEN THE SYSTEM SHALL preserve local changes and expose retry status to the user.` |

## Edge and Failure Modes to Consider

- Duplicate submissions, idempotency, and replays.
- Missing, malformed, stale, or unauthorized input.
- Conflicting concurrent actions.
- Partial external service failure.
- Empty states and no-result states.
- Permission boundaries between roles.
- State transitions that should be blocked.
- Data retention, auditability, and recovery expectations.

## Self-Check

- Each AC has `SHALL`.
- Each AC has an observable trigger, condition, state, or always-on rule.
- The expected behavior can be tested manually or automatically.
- No AC relies on subjective adjectives unless tagged `[확인 필요]`.
- Proposed rules not stated by the user are tagged `[제안]`.
