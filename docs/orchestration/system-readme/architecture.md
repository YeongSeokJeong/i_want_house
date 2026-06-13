# Architecture Review

## Task Context
- Task Name: System README 작성
- Task ID: system-readme
- Last Updated: 2026-06-13

## System Context
- Current Stack: Python 3.12 standard library, `unittest`, GitHub Actions, GitHub Pages static assets, JSON/Markdown repository state.
- Existing Patterns: Product loop code lives under `src/jeonseloop/`; operator entrypoints are scripts and `python -m jeonseloop.run`; state is committed JSON/Markdown.
- Integration Points: `config/watchlist.yaml`, `.github/workflows/jeonseloop.yml`, `scripts/run-loop.*`, `data/**/*.json`, `logs/*.md`, Telegram Bot API, optional Anthropic API.

## Feature Decomposition Map
| Feature ID | Feature | Description | Depends On | Complexity | Risk |
|------------|---------|-------------|------------|------------|------|
| F-001 | Root README 작성 | Document run, verification, operation, and safety guidance | None | Low | Low |

## Dependency Map
- `README.md` -> `scripts/run-loop.ps1`, `scripts/run-loop.sh`, `src/jeonseloop/run.py` (run commands).
- `README.md` -> `.github/workflows/jeonseloop.yml` (scheduled/manual execution behavior).
- `README.md` -> `docs/wiki/domains/jeonseloop/overview.md` and final handoff (durable implementation summary).

## Technical Decisions
- Decision: README documents current repo-verifiable behavior only.
  - Rationale: External services are not guaranteed by repository files.
  - Trade-offs: Operators still need to configure and verify live services separately.

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| README becomes stale after future implementation changes | Medium | Keep README checks in future documentation tasks | Codex |
