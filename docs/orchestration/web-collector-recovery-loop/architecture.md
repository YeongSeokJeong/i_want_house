# Architecture Review

## Task Context
- Task Name: Naver Real Estate Web Collector Recovery Loop
- Task ID: web-collector-recovery-loop
- Last Updated: 2026-06-14

## System Context
- Current Stack: Python 3.12 standard library, unittest, GitHub Actions, JSON/Markdown file state.
- Existing Patterns: `LoopCoordinator` composes collector, validator, analyzer, persistence, review, notifier; external listing and trade sources live in `src/jeonseloop/sources.py`.
- Integration Points: Naver Real Estate public web endpoints/pages, GitHub Actions artifacts/workflows, repository JSON state under `data/`.

## Feature Decomposition Map
| Feature ID | Feature | Description | Depends On | Complexity | Risk |
|------------|---------|-------------|------------|------------|------|
| F-001 | Collector source contract | Source mode selection and Naver configuration contract | None | Medium | Medium |
| F-002 | Naver listing adapter | Best-effort Naver fetch and normalization | F-001 | High | High |
| F-003 | Failure diagnostics | Structured sanitized diagnostics for source failures | F-001,F-002 | Medium | Medium |
| F-004 | Actions recovery workflow | Artifact upload and repair report/PR candidate flow | F-003 | High | High |
| F-005 | Operator documentation | Korean operation guide and durable wiki notes | F-001,F-004 | Medium | Low |

## Dependency Map
- `LoopCoordinator` -> `listing_fetcher_from_env` (runtime source selection).
- `ListingCollector` -> source-specific fetcher (retry and pacing boundary).
- `Naver source adapter` -> `WatchTarget` (complex ID/name/area filtering).
- `Failure diagnostics` -> `LoopCoordinator` and `sources.py` (failure context capture).
- `Actions recovery workflow` -> diagnostics artifacts (offline repair input).

## Technical Decisions
- Decision: Keep source adapters behind the existing `Callable[[WatchTarget], list[dict[str, Any]]]` boundary.
  - Rationale: Minimizes changes to validation, analysis, persistence, and notifier code.
  - Trade-offs: Source-specific diagnostics need an additional side channel or enriched exception type.
- Decision: Add Naver source as an additive mode selected through environment variables.
  - Rationale: Avoids breaking fixture and HTTP JSON operation.
  - Trade-offs: More configuration states to validate and document.
- Decision: Make recovery workflow reviewable.
  - Rationale: Web-source changes are operationally risky and should not auto-merge.
  - Trade-offs: Human approval remains necessary for final production repair.

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| Naver blocks or changes public endpoints | High | Fixture-backed parser tests, structured diagnostics, reviewable recovery report | Codex |
| Scraper stores sensitive headers or payloads | High | Redaction and size limits in F-003 tests | Codex |
| Automated repair mutates production unsafely | High | PR/report-only workflow, no direct main pushes | Codex |
| Existing JSON source users regress | Medium | Preserve default behavior and add regression tests | Codex |
