# Session Decisions

## Task Context
- Task Name: Telegram ops automation
- Task ID: telegram-ops-automation

## Decision Log
| Session | Feature ID | Feature | Decision | Rationale | Impact | Date |
|---------|------------|---------|----------|-----------|--------|------|
| 1 | PLAN | Planning | Split proposal generation from workflow/discovery | The backlog item combines parsing, proposal safety, workflow, and identifier research | Allows F-001 to land a safe audited core before adding broader automation | 2026-06-17 |
| 1 | PLAN | Planning | Generate proposals, not direct config mutation | Existing project decisions require human approval for criteria/config changes | Prevents Telegram input from silently changing operating configuration | 2026-06-17 |
| 1 | F-001 | Ops proposal core | Use `/ops` prefix as the allowlist boundary | Free-form Telegram text is too ambiguous for safe operational proposals | Non-prefixed requests are rejected instead of guessed | 2026-06-17 |

## Session 1
- Feature ID: F-001
- Feature: Ops proposal core
- Decisions:
  - Use deterministic allowlist parsing for source kind, Naver map, trade type, and target price proposals.
  - Persist proposal state with processed update IDs and rollback metadata.
  - Reject or clarify unsupported free-form operations instead of guessing.
- Alternatives Considered:
  - Directly edit `.env` or GitHub Variables: rejected because secrets/operator values must not be committed and automated mutation needs explicit approval gates.
  - Use LLM command interpretation: deferred until deterministic proposal state exists.
- Risks Introduced:
  - Command syntax may be narrower than natural Telegram requests.
- Follow-up Notes:
  - F-001 verification passed with `python -m py_compile src/jeonseloop/telegram_ops.py` and `python -m unittest tests.test_telegram_ops -v`.
