# Architecture Review

## Task Context
- Task Name: Telegram message context
- Task ID: telegram-message-context
- Last Updated: 2026-06-17

## System Context
- Current Stack: Python analyzer/notifier, unittest suite.
- Existing Patterns: analyzer creates immutable `Candidate` values; notifier formats messages from candidate fields only.
- Integration Points: `src/jeonseloop/analyzer.py`, `src/jeonseloop/notifier.py`, `tests/test_loop.py`, `tests/test_reliability.py`.

## Feature Decomposition Map
| Feature ID | Feature | Description | Depends On | Complexity | Risk |
|------------|---------|-------------|------------|------------|------|
| F-001 | Rich Telegram message | Add price context and readable formatting to candidate alerts | None | Medium | Medium |

## Dependency Map
- `CandidateAnalyzer.classify` knows watchlist target and trade baseline.
- `format_candidate_message` renders Telegram text from candidate listing metadata.
- Telegram send gating remains in `NotificationService`.

## Technical Decisions
- Decision: Enrich listing metadata during classification.
  - Rationale: This is the narrowest way to make notifier context-rich without new dependencies.
  - Trade-offs: Candidate listing dictionaries now include derived context fields.

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| Message context drifts from approval logic | Medium | Derive context in the same analyzer pass that makes the approval decision | Backend Agent |
