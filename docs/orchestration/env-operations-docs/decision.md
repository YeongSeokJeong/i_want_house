# Session Decisions

## Task Context
- Task Name: Environment operations documentation
- Task ID: env-operations-docs

## Decision Log
| Session | Feature ID | Feature | Decision | Rationale | Impact | Date |
|---------|------------|---------|----------|-----------|--------|------|
| 1 | F-001 | `.env` operations guardrail | Keep local secrets in untracked `.env`; use GitHub Secrets for Actions. | Prevents accidental secret disclosure while preserving local and CI operation paths. | Agents and operators have a clear source-of-truth rule for env values. | 2026-06-13 |

## Session 1
- Feature ID: F-001
- Feature: `.env` operations guardrail
- Decisions:
  - Add the rule to `AGENTS.md` because the user specifically asked for agent instructions.
  - Add `.env` ignore rules so the documented practice is enforced by git defaults.
  - Add `.env.example` with placeholder variable names only.
- Alternatives Considered:
  - Add automatic `.env` loading in runtime code: not used because the request targets operating instructions, not runtime behavior.
- Risks Introduced:
  - Operators still need to load `.env` into their shell or configure their runner explicitly.
- Follow-up Notes:
  - If new env vars are added later, update `.env.example` with placeholder names only.
