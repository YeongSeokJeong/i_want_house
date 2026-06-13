# Task Plan

## Task Metadata
- Task Name: Environment operations documentation
- Task ID: env-operations-docs
- Task Branch: feature/jeonseloop-automation
- Plan Version: v1
- Last Updated: 2026-06-13

## Planning Assumptions
- The user requested that environment-variable-like values be operated through `.env`.
- The immediate requested target is `AGENTS.md`.
- Secrets must remain untracked and must not be committed into repo documentation, source, or workflow files.
- GitHub Actions still requires repository Secrets; local `.env` is for local operator sessions.

## Related Document Discovery
- `docs/wiki/rules/workflow/loop-engineering-routing.md`: relevant workflow routing context.
- `docs/wiki/rules/workflow/development-automation-loop.md`: relevant development inspection context.
- Gap: no wiki update is required for this small operator-instruction change because the durable rule belongs in `AGENTS.md` and `.gitignore`.

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | `.env` operations guardrail | Document `.env` use for local environment values and prevent accidental secret commits. | None | Low | Codex |

## Feature Detail
### F-001 `.env` operations guardrail
- Scope:
  - Add an `AGENTS.md` hard constraint requiring runtime secrets and local environment values to live in untracked `.env`.
  - Clarify that GitHub Actions values belong in GitHub Secrets, not committed files.
  - Add `.env` ignore patterns while allowing `.env.example`.
  - Add `.env.example` with placeholder variable names only.
- Acceptance Criteria:
  - [x] `AGENTS.md` tells agents/operators to keep secrets and operator-specific env values in local `.env`.
  - [x] `AGENTS.md` distinguishes local `.env` from GitHub Secrets.
  - [x] `.gitignore` excludes `.env` and `.env.*` while allowing `.env.example`.
  - [x] `.env.example` lists known environment variables without real secret values.
  - [x] Markdown and ignore-file changes are reviewed.
- Out of Scope:
  - Adding real secrets.
  - Changing runtime code to parse `.env` automatically.
  - Changing GitHub Actions behavior.

## Execution Order
1. F-001

## Revision Policy
- Plan revision is allowed only when scope or acceptance criteria change.

## Revision Log
| Version | Date | Changed Feature IDs | Why Revised | Author |
|---------|------|---------------------|-------------|--------|
| v1 | 2026-06-13 | F-001 | Initial plan for `.env` operator guardrail | Codex |
