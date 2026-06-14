# Session Decisions

## Task Context
- Task Name: Live data adapter validation
- Task ID: live-data-adapter-validation

## Decision Log
| Session | Feature ID | Feature | Decision | Rationale | Impact | Date |
|---------|------------|---------|----------|-----------|--------|------|
| 1 | PLAN | Planning | Select BL-20260613-007 as urgent work | Live data adapters are the highest remaining source-code runtime risk in the backlog | Focuses PR on collection correctness and visible failure behavior | 2026-06-14 |
| 1 | F-001 | Live source adapter guardrails | Use configurable HTTP JSON adapters instead of hard-coded portal scraping | External service docs, credentials, and terms are not repo-verifiable in this session | Keeps implementation testable while enabling operator-provided live endpoints | 2026-06-14 |

## Session 1
- Feature ID: F-001
- Feature: Live source adapter guardrails
- Decisions:
  - Treat missing live listing source as a failed run when no fixture is provided.
  - Keep trade live source optional because target-price fallback remains valid when recent trades are unavailable.
  - Do not write live trade payloads directly from the trade repository; preserve existing persistence boundaries.
- Alternatives Considered:
  - Hard-code a specific Korean portal scraper: rejected because service structure and access policy are external-state risks.
  - Keep current silent empty-source behavior: rejected because it can hide production collection failure.
- Risks Introduced:
  - Operators running live mode without configuring a listing source will now get a failed health record instead of an empty successful cycle.
- Follow-up Notes:
  - Actual external endpoint verification should remain a separate operator check or future credentialed integration task.
  - `scripts/run-loop.ps1` now supports `PYTHON` override plus `python`/`py -3` lookup because this sandbox exposes Python inconsistently to nested PowerShell.
