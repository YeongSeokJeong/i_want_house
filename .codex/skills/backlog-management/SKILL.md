---
name: backlog-management
description: Use when creating, updating, routing, starting, blocking, listing, or closing repo backlog items, including recording completion results, artifact links, and exact wiki document paths/sections when wiki content was written or changed.
---

# Backlog Management

Manage repo backlog items as durable work records. Use this skill for backlog lifecycle work, not for session transcripts or raw progress logs.

## Core Rules
1. Use `docs/backlog.md` as the default backlog file unless the repo already defines another backlog location.
2. Before adding a new item, search existing backlog entries for duplicates.
3. Use stable IDs: `BL-YYYYMMDD-NNN`.
4. Use exactly one status: `Todo`, `Doing`, `Blocked`, or `Done`.
5. Do not delete completed items.
6. Mark an item `Done` only after the work is completed, verified, or explicitly resolved.
7. When marking `Done`, fill `Completed`, `Artifact`, and `Result`.
8. If completed work wrote or changed wiki content, `Result` must name the wiki file, heading/section, and concrete change made.
9. Do not write vague results such as "updated wiki" or "done".
10. If the item requires source code changes in this repo, follow `large-task-orchestrator` before implementation.
11. If the item requires wiki content, use `wiki-write` for the wiki artifact, then return here to close the backlog item.

## Backlog File Shape
Use this table in `docs/backlog.md`:

```md
| ID | Status | Route | Task | Context | Created | Completed | Artifact | Result |
|---|---|---|---|---|---|---|---|---|
| BL-YYYYMMDD-001 | Todo | wiki-rule | <task> | <why it exists> | YYYY-MM-DD | - | <expected output> | - |
```

Field rules:
- `Route`: use one routing pattern from the table below.
- `Task`: describe the work to complete, not the conversation.
- `Context`: include the source request, discovery reason, or blocking fact.
- `Artifact`: for `Done`, link the main changed file, PR, report, or command result.
- `Result`: for `Done`, summarize what changed and where to inspect it.

## Routing Patterns
Classify every backlog item before writing or closing it.

| Route | Use For | Primary Artifact |
|---|---|---|
| `source-code` | Product source changes, tests, runtime behavior | `src/`, `tests/`, scripts, plus orchestration docs |
| `wiki-domain` | Durable domain knowledge | `docs/wiki/domains/<domain>/...` |
| `wiki-decision` | Human decision with rationale | `docs/wiki/decisions/<decision>.md` and `docs/wiki/decisions.md` |
| `wiki-rule` | Shared rule or principle | `docs/wiki/rules/common/...` |
| `wiki-workflow` | Repeatable procedure or checklist | `docs/wiki/rules/workflow/...` |
| `operator-doc` | User/operator guide outside the wiki | `README.md`, `docs/*.md`, `.env.example` |
| `skill-agent` | Codex skills, agents, prompts, or repo-local automation instructions | `.codex/...`, `AGENTS.md` |
| `spec` | Product requirements or implementation-ready specs | standalone spec file or wiki page, per user request |
| `backlog` | Backlog structure or backlog item maintenance | `docs/backlog.md` |

Routing constraints:
- Do not use `docs/wiki/` for backlog bookkeeping unless the user explicitly changes the repo schema.
- Do not put durable wiki knowledge in `docs/backlog.md`; only record the work item and result there.
- When route starts with `wiki-`, apply the `wiki-write` schema for the actual wiki document.
- When route is `source-code`, source changes must obey the repo's source-code workflow before edits.

## Execution Flow
1. Locate or create `docs/backlog.md`.
2. Read existing items and find duplicate or related IDs.
3. Classify the request into one routing pattern.
4. Apply the requested lifecycle action:
   - Add: create a `Todo` row.
   - Start: change `Todo` to `Doing`.
   - Block: change status to `Blocked` and explain the blocker in `Result`.
   - Close: change status to `Done`, fill `Completed`, `Artifact`, and `Result`.
   - List/status: report matching rows without editing unless asked.
5. If closing a route that produced wiki content, write `Result` in this form:

```md
`docs/wiki/<path>.md` `## <heading>`에 <added/updated/decided content>를 기록함.
```

6. Verify IDs, status values, dates, artifact paths, and result specificity.
7. Report changed backlog IDs to the user.

## Completion Examples
Wiki completion:

```md
| BL-20260613-002 | Done | wiki-workflow | 개발 검사 루프 정리 | 사용자 요청 | 2026-06-13 | 2026-06-13 | `docs/wiki/rules/workflow/development-automation-loop.md` | `docs/wiki/rules/workflow/development-automation-loop.md` `## 절차`에 read-only 검사 순서와 보고 형식을 추가함. |
```

Non-wiki completion:

```md
| BL-20260613-003 | Done | skill-agent | 백로그 관리 스킬 생성 | 사용자 요청 | 2026-06-13 | 2026-06-13 | `.codex/skills/backlog-management/SKILL.md` | 백로그 상태, 라우팅 패턴, 완료 결과 기록 규칙을 새 스킬로 분리함. |
```
