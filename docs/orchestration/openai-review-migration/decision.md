# Session Decisions

## Task Context
- Task Name: OpenAI review migration
- Task ID: openai-review-migration

## Decision Log
| Session | Feature ID | Feature | Decision | Rationale | Impact | Date |
|---------|------------|---------|----------|-----------|--------|------|
| 1 | PLAN | Planning | Link BL-20260614-002 as the parent task | It is the next source-code Todo item and directly matches the user's requested provider migration | Keeps implementation and closeout tied to backlog state | 2026-06-14 |
| 1 | F-001 | OpenAI candidate reviewer | Use standard-library HTTP for the OpenAI Responses API call | The project currently has no runtime dependency manifest for OpenAI SDKs and the existing live adapters use standard-library patterns | Avoids dependency churn while preserving testability | 2026-06-14 |
| 1 | F-001 | OpenAI candidate reviewer | Preserve the existing decision schema | The product only needs approve, hold, or reject plus a reason for Telegram gating | Limits migration risk and keeps existing downstream logic stable | 2026-06-14 |

## Session 1
- Feature ID: F-001
- Feature: OpenAI candidate reviewer
- Decisions:
  - Replace Anthropic configuration and reviewer naming rather than adding a provider abstraction.
  - Use OpenAI Responses API structured JSON output requirements in the request payload.
  - Treat live OpenAI API verification as external state; repo tests will verify payload creation, response extraction, and failure behavior.
- Alternatives Considered:
  - Add a generic multi-provider LLM abstraction: rejected because only one provider is currently requested and it would add unnecessary surface area.
  - Add the OpenAI Python SDK: rejected for this task because standard-library HTTP is enough and avoids dependency packaging work.
- Risks Introduced:
  - If the live API response shape changes, repository tests may still pass against mocked payloads.
- Follow-up Notes:
  - Operator-owned validation should run once real `OPENAI_API_KEY` and billing/access are configured.
