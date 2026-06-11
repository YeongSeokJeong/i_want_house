---
name: wiki-write
description: Use when creating or updating this repo's `docs/wiki/` knowledge base, including domain docs, overview pages, human decision records, common rules, workflow guides, and wiki indexes, so they follow the local wiki schema and stay easy to navigate.
---

# Wiki Agent - docs/wiki Writer

## When to use
- Writing new documents under `docs/wiki/`
- Updating existing wiki pages to match the local structure
- Creating or expanding a domain directory under `docs/wiki/domains/`
- Recording an important human decision in `docs/wiki/decisions/`
- Adding shared rules under `docs/wiki/rules/common/`
- Adding repeatable procedures under `docs/wiki/rules/workflow/`
- Refreshing `init.md`, `index.md`, `SCHEMA.md`, or `decisions.md` after structural changes

## When NOT to use
- Raw progress logging, sprint history, or session transcripts
- Broad architecture or product planning outside the wiki artifact itself -> use `oma-architecture` or `oma-pm` first, then return to `wiki-write` only to record the finalized durable knowledge.
- Free-form note dumping that does not need to fit the wiki structure

## Core Rules
1. Treat `docs/wiki/SCHEMA.md` as the authoritative writing and routing rulebook.
2. Keep all wiki documents under `docs/wiki/`; do not introduce new top-level wiki folders unless explicitly requested.
3. Route content by document class:
   - domain knowledge -> `domains/<business-domain>/`
   - human decisions -> `decisions/` and surface in `decisions.md`
   - shared principles/conventions -> `rules/common/`
   - repeatable procedures/checklists -> `rules/workflow/`
4. Use business concepts for domain names, not temporary task or implementation labels.
5. Every domain directory must have `overview.md` before or alongside subtopic pages.
6. Do not create `raw/`, `queries/`, `progress/`, or `sessions/` unless the user explicitly changes the schema.
7. Agent decisions are not standalone docs; record them only in an `Agent note` section inside the relevant domain/subtopic page when useful.
8. When structure changes, update the navigation pages in the same task: `init.md`, `index.md`, `SCHEMA.md`, and/or `decisions.md` as applicable.
9. If `docs/wiki/SCHEMA.md` conflicts with this skill's resource files, follow `SCHEMA.md` and update the resource file if the task includes maintaining this skill.
10. Prefer concise Korean prose for wiki content unless the surrounding wiki section is already using another language.

## How to Execute
Follow `resources/execution-protocol.md` step by step.
Use `resources/document-templates.md` for canonical page shapes.
Before finalizing, run `resources/checklist.md`.
Use `resources/examples.md` for routing examples.
Use `resources/error-playbook.md` when the request does not cleanly fit the schema.

## Routing Summary
- `docs/wiki/init.md`: explain structure and main entry points
- `docs/wiki/index.md`: catalog of documents, folder-first navigation
- `docs/wiki/SCHEMA.md`: naming, routing, and update rules
- `docs/wiki/decisions.md`: list page for important human decisions
- `docs/wiki/domains/<domain>/overview.md`: domain hub page
- `docs/wiki/domains/<domain>/<subtopic>.md`: focused domain detail page
- `docs/wiki/decisions/<decision>.md`: one durable human decision per file
- `docs/wiki/rules/common/<rule>.md`: shared rules/principles
- `docs/wiki/rules/workflow/<workflow>.md`: repeatable workflows/checklists

## Linking Summary
- In `index.md` and `decisions.md`, use path-style wikilinks from `docs/wiki/`, e.g. `[[domains/auth/login-flow]]`.
- Inside a domain directory, use local links for sibling pages when clear, e.g. `[[login-flow]]`.
- When linking across domains or folders, use path-style links.

## References
- Execution protocol: `resources/execution-protocol.md`
- Templates: `resources/document-templates.md`
- Checklist: `resources/checklist.md`
- Examples: `resources/examples.md`
- Error handling: `resources/error-playbook.md`
- Local schema: `../../../docs/wiki/SCHEMA.md`
- Local init guide: `../../../docs/wiki/init.md`
- Current index: `../../../docs/wiki/index.md`
- Human decision index: `../../../docs/wiki/decisions.md`
