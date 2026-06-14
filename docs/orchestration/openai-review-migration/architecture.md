# Architecture Review

## Task Context
- Task Name: OpenAI review migration
- Task ID: openai-review-migration
- Last Updated: 2026-06-14

## System Context
- Current Stack: Python standard library CLI/background job, unittest tests, JSON/Markdown persistence, GitHub Actions schedule.
- Existing Patterns: `LoopCoordinator` composes service classes; `CandidateReviewService` accepts an injected reviewer; optional LLM review is disabled by default and gated by environment configuration.
- Integration Points: `src/jeonseloop/review.py`, loop candidate filtering, Telegram notification gating, `.env.example`, GitHub Actions secrets, README operator guidance.

## Feature Decomposition Map
| Feature ID | Feature | Description | Depends On | Complexity | Risk |
|------------|---------|-------------|------------|------------|------|
| F-001 | OpenAI candidate reviewer | Replace Anthropic optional review path with OpenAI Responses API configuration, request/response handling, tests, and docs | None | Medium | Medium |

## Dependency Map
- `LoopCoordinator` -> `CandidateReviewService` (candidate decisions are reviewed before notification planning)
- `CandidateReviewService` -> OpenAI reviewer callable (only when review is enabled and the API key is configured)
- `OpenAI candidate reviewer` -> OpenAI Responses API (external live service, not repo-verifiable)
- GitHub Actions -> environment secrets (operator-provided `OPENAI_API_KEY`)

## Technical Decisions
- Decision: Keep `CandidateReviewService` as the stable boundary and replace only the default live reviewer implementation.
  - Rationale: Tests and callers already rely on injected reviewers, so the provider migration can be local to review configuration and HTTP handling.
  - Trade-offs: This does not create a provider plugin architecture, but that is not needed for the current requested migration.
- Decision: Use structured output instructions in the OpenAI payload and continue validating returned JSON locally.
  - Rationale: The API can request schema-shaped output, but local validation remains the final safety gate before Telegram sends.
  - Trade-offs: Mocked tests prove request/parse behavior, not live model compliance.

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| Live OpenAI account or model access is unavailable | Medium | Keep LLM review optional and document operator-owned credential validation | Operator |
| Response body shape differs from mocked examples | Medium | Implement tolerant output text extraction and hold candidates on invalid responses | Backend Agent |
| Old Anthropic environment variables linger in docs or workflow secrets | Low | Search repository for Anthropic references before QA closeout | Backend Agent |
