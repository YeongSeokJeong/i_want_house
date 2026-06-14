# Task Plan

## Task Metadata
- Task Name: Naver Real Estate Web Collector Recovery Loop
- Task ID: web-collector-recovery-loop
- Task Branch: task/web-collector-recovery-loop
- Task Worktree: D:\git\i_want_house
- Plan Version: v1
- Last Updated: 2026-06-14

## Planning Assumptions
- The user wants Naver Real Estate as the first live web source.
- The implementation must not bypass CAPTCHA, login, paywalls, rate limits, or anti-abuse controls.
- The collector should be best-effort and fail with actionable diagnostics when Naver changes or blocks access.
- Automatic improvement means creating diagnostic artifacts and a reviewable repair proposal path, not unreviewed self-modifying production changes.
- GitHub Actions must continue to avoid Telegram sends unless `send=true` and required secrets are present.

## Related Backlog Items
| Backlog ID | Route | Status | Relationship |
|------------|-------|--------|--------------|
| BL-20260614-003 | source-code | Doing | Parent task item for this orchestration |

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | Collector source contract | Add an operator-facing source mode contract for Naver web collection and diagnostics | None | Medium | Codex |
| F-002 | Naver listing adapter | Fetch and normalize Naver Real Estate listing payloads into JeonseLoop listing records | F-001 | High | Codex |
| F-003 | Failure diagnostics | Persist safe collector failure evidence for Actions artifacts and later repair analysis | F-001,F-002 | Medium | Codex |
| F-004 | Actions recovery workflow | Upload diagnostics and run a recovery workflow that prepares a reviewable repair report or PR candidate | F-003 | High | Codex |
| F-005 | Operator documentation | Document Naver source configuration, limitations, and recovery-loop operation | F-001,F-004 | Medium | Codex |

## Feature Detail
### F-001 Collector source contract
- Scope:
  - Add explicit `JEONSELOOP_LISTING_SOURCE_KIND` source selection without breaking the existing HTTP JSON source.
  - Define Naver configuration inputs needed by the adapter.
  - Add tests proving existing HTTP JSON mode still works.
- Acceptance Criteria:
  - [x] Existing `JEONSELOOP_LISTING_SOURCE_URL` HTTP JSON mode remains supported.
  - [x] Naver source mode can be selected through environment/configuration without hard-coded operator values.
  - [x] Missing Naver configuration produces a clear health failure reason.
  - [x] `.env.example` contains placeholders only.
- Out of Scope:
  - Real Naver payload parsing beyond the minimal contract.

### F-002 Naver listing adapter
- Scope:
  - Implement a best-effort Naver adapter for public listing endpoints/pages.
  - Normalize records to `price_krw`, `area_m2`, `floor`, `link`, and optional metadata.
  - Add fixture-backed tests for representative Naver responses.
- Acceptance Criteria:
  - [x] Adapter returns valid JeonseLoop listing records from a fixture that resembles Naver data.
  - [x] Adapter filters records to the watchlist complex and jeonse listing type.
  - [x] Adapter handles missing or changed fields as source failures rather than silent success.
  - [x] Rate limiting and User-Agent behavior are explicit.
- Out of Scope:
  - CAPTCHA, login, session bypass, stealth automation, or scraping protected content.

### F-003 Failure diagnostics
- Scope:
  - Capture structured diagnostics for collector failures.
  - Redact secrets and limit stored response samples.
  - Persist diagnostics through validate-before-replace paths or Actions artifacts without replacing good state.
- Acceptance Criteria:
  - [x] Collector failures include source kind, target, failure stage, and sanitized evidence.
  - [x] Diagnostics never include bearer tokens or Telegram/OpenAI secrets.
  - [x] Failed collector runs preserve previous listing/history JSON state.
  - [x] Tests cover redaction and artifact shape.
- Out of Scope:
  - Automated code editing.

### F-004 Actions recovery workflow
- Scope:
  - Add a workflow or job path that consumes diagnostics after failures.
  - Produce a deterministic repair report and optionally a branch/PR candidate when enabled.
  - Keep automatic changes reviewable.
- Acceptance Criteria:
  - [ ] Actions upload diagnostics when collection fails.
  - [ ] Recovery workflow can be manually dispatched against a failed run artifact.
  - [ ] The workflow does not push to `main` directly.
  - [ ] Tests or static checks verify workflow wiring.
- Out of Scope:
  - Fully autonomous merge/deploy to production.

### F-005 Operator documentation
- Scope:
  - Document configuration, expected limits, failure modes, and recovery workflow usage.
  - Update wiki/domain notes if durable operation knowledge changes.
- Acceptance Criteria:
  - [ ] Korean operator docs explain required GitHub Secrets/Variables.
  - [ ] Documentation states that Naver collection is best-effort and does not bypass access controls.
  - [ ] Recovery-loop operation is documented with concrete runbook steps.
- Out of Scope:
  - Legal advice or guarantee of Naver availability.

## Execution Order
1. F-001
2. F-002
3. F-003
4. F-004
5. F-005

## Revision Log
| Version | Date | Changed Feature IDs | Changed Backlog IDs | Why Revised | Author |
|---------|------|---------------------|---------------------|-------------|--------|
| v1 | 2026-06-14 | F-001,F-002,F-003,F-004,F-005 | BL-20260614-003 | Initial planning baseline | Codex |
