# Task Plan

## Task Metadata
- Task Name: OpenAI review migration
- Task ID: openai-review-migration
- Task Branch: task/openai-review-migration
- Task Worktree: D:\git\i_want_house
- Plan Version: v1
- Last Updated: 2026-06-14

## Planning Assumptions
- BL-20260614-002 is the next source-code backlog item after live data adapter validation.
- The migration should stay narrow: replace the Anthropic live reviewer with an OpenAI Responses API reviewer while preserving the existing optional LLM review gate and safe hold-on-failure behavior.
- The repository should not add a new SDK dependency unless the existing runtime already uses one; standard-library HTTP keeps deployment and tests simple.
- Live OpenAI API calls, billing, rate limits, and account access are external-state checks and cannot be proven from repository-only tests.
- Official OpenAI documentation confirms the Responses API `POST /v1/responses` shape with bearer auth, `model`, and `input`, and structured outputs can request JSON schema output.

## Related Backlog Items
| Backlog ID | Route | Status | Relationship |
|------------|-------|--------|--------------|
| BL-20260614-002 | source-code | Doing | Parent task item for this orchestration |

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | OpenAI candidate reviewer | Replace Anthropic review configuration and HTTP request path with OpenAI Responses API behavior, tests, and operator docs | None | Medium | Backend Agent |

## Feature Detail
### F-001 OpenAI candidate reviewer
- Scope:
  - Replace `ANTHROPIC_API_KEY` with `OPENAI_API_KEY` for optional LLM review activation.
  - Replace the Anthropic-specific reviewer class with an OpenAI Responses API reviewer that posts to `/v1/responses`.
  - Preserve existing reviewer injection, disabled-by-default behavior, JSON parsing, and hold-on-invalid/error behavior.
  - Update unit tests for disabled secret behavior, payload shape, response text extraction, and failure handling.
  - Update `.env.example`, GitHub Actions secret wiring, and README operator guidance with placeholders only.
- Acceptance Criteria:
  - [x] With `JEONSELOOP_LLM_REVIEW=true` but no `OPENAI_API_KEY`, the reviewer is disabled and does not call the live reviewer.
  - [x] A configured OpenAI reviewer sends a Responses API-compatible JSON payload containing model, instructions/input, and structured JSON output requirements.
  - [x] OpenAI response output text is parsed through the existing decision/reason validator.
  - [x] Invalid OpenAI responses or request failures keep candidates on hold and do not approve Telegram sends.
  - [x] No `ANTHROPIC_API_KEY`, Anthropic class names, or Anthropic operator instructions remain in current source/config/operator docs/spec/wiki.
  - [x] Existing fixture-backed loop behavior and tests keep passing.
- Out of Scope:
  - Live API credential validation against OpenAI.
  - Adding the OpenAI Python SDK dependency.
  - Changing the candidate decision schema beyond existing `approve`, `hold`, and `reject`.

## Execution Order
1. F-001

## Revision Log
| Version | Date | Changed Feature IDs | Changed Backlog IDs | Why Revised | Author |
|---------|------|---------------------|---------------------|-------------|--------|
| v1 | 2026-06-14 | F-001 | BL-20260614-002 | Initial planning baseline from current source-code backlog priority | Codex |
