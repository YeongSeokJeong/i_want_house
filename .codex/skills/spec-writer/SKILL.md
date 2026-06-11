---
name: spec-writer
description: "Create or update implementation-ready requirements documents from product ideas, feature lists, requirements-analyzer outputs, user stories, acceptance criteria requests, SRS requests, 기능정의서 requests, or existing spec files, including specs that should be written into this repo's docs/wiki through wiki-write routing. Use when the user says 요구사항 명세서 써줘, 스펙 문서 만들어줘, 기능 명세 작성해줘, 이 기능 목록을 개발 가능한 수준으로 구체화해줘, 이걸 명세로 만들어줘, user story, acceptance criteria, write a spec, requirements document, SRS, or asks to revise an existing requirements/spec file. Do not use when the user only wants idea decomposition or MoSCoW prioritization without a spec; that belongs to requirements-analyzer. Do not use when the user asks for code implementation rather than requirements."
---

# Spec Writer

Turn a product idea or feature list into a Markdown requirements document that a developer can implement without more discovery. Prefer one feature-sized spec over one large epic spec; if the input is too broad, propose a split and write the highest-priority feature spec first unless the user asks otherwise. When the document should live in this repo's wiki, compose it through the `wiki-write` workflow so the result follows `docs/wiki/` schema and navigation rules.

## Required References

- Read `references/spec-template.md` before creating or updating a requirements document.
- Read `references/ears-guide.md` before writing acceptance criteria or running the self-check.
- Read `references/evaluation-cases.md` only when validating or improving this skill.

## Workflow

1. Classify the input state.
   - Raw idea: lightly split it into feature-sized units, then continue. If the idea is broad and prioritization is the real task, suggest using `requirements-analyzer` first.
   - Decomposed feature list, including `requirements-analyzer` output: preserve feature names, MoSCoW priorities, and any stated constraints.
   - Existing spec revision: update only the requested sections and preserve existing requirement IDs.
2. Decide the document destination.
   - If the user asks to write to the repo wiki, mentions `docs/wiki/`, durable knowledge, wiki, or a wiki index, invoke/use `wiki-write` for routing and page-shape rules before writing.
   - If writing under `docs/wiki/`, follow `wiki-write` strictly: read its required `docs/wiki/SCHEMA.md` when present, route requirements content to the correct domain page or workflow/rules page, and update navigation pages when the wiki structure changes.
   - If the user asks for a standalone implementation spec, save `requirements.md` by default, or `<feature-name>-spec.md` when a clear feature name exists.
   - If `docs/wiki/` does not exist and the user requested wiki output, ask whether to initialize wiki structure with `wiki-write` unless in Quick mode; in Quick mode, write a standalone spec and mark wiki initialization as `[확인 필요]`.
3. Choose the spec mode.
   - Standard: default; feature-level user stories and acceptance criteria.
   - Full SRS: use when the user asks for a formal document, SRS, 기능정의서, or complete requirements document. Include overview, glossary, NFRs, dependencies, and constraints.
   - Quick: use when the user says 간단히, 빠르게, quick, rough, or similar. Do not ask questions; make reasonable assumptions and list them at the end.
4. Ask at most 3 clarification questions only when the actor, scope boundary, platform constraint, or wiki destination would materially change the spec. Skip questions when the input is sufficient. Never ask in Quick mode.
5. Draft the spec as a single Markdown artifact at the chosen destination.
   - Standalone destination: use the structure in `references/spec-template.md`.
   - Wiki destination: keep the same FR/NFR rigor, but embed it into the document class, headings, links, and index updates required by `wiki-write`.
6. For each feature requirement:
   - Assign a stable `FR-XXX` ID.
   - Use the fixed requirement block from `spec-template.md`.
   - Write testable EARS acceptance criteria with `WHEN`, `IF`, and `WHILE` forms.
   - Include at least two proposed edge-case or failure-mode criteria per feature when relevant; tag unstated additions as `[제안]`.
   - Preserve MoSCoW priority when present.
   - Avoid implementation choices. Record only user-stated technical constraints in the constraints section.
7. Add cross-cutting sections.
   - Glossary when terminology may drift or in Full SRS mode.
   - NFRs only when grounded in user input or necessary from the domain; do not invent numeric performance targets.
   - Text dependency graph using requirement IDs.
8. Self-check before finalizing.
   - Every requirement has `FR-XXX` or `NFR-XXX`.
   - Every AC contains an EARS trigger and `SHALL`.
   - ACs are testable and do not preserve vague words such as "빠르게", "직관적", "user-friendly", "robust", or "seamless" unless marked `[확인 필요]`.
   - Requirements do not contradict each other.
   - Each feature has at least one failure-mode AC, preferably two when the feature has meaningful risk.
   - Input priority information is preserved.
   - If writing under `docs/wiki/`, the `wiki-write` checklist passes and required navigation updates are included.
9. Output and review gate.
   - Save the Markdown file.
   - In chat, summarize the file path, whether `wiki-write` routing was used, covered features, and only the `[확인 필요]` / `[제안]` items.
   - End with a review loop: ask the user to confirm those items, and on reply update only affected requirements while preserving IDs.

## Writing Rules

- Respond and write the spec in the user's language. For Korean specs, EARS keywords may remain `WHEN`, `IF`, `WHILE`, `THE SYSTEM SHALL` unless the user asks for Korean-only wording.
- Keep requirements at roughly one developer task per requirement. Do not decompose into micro-steps.
- Do not transcribe vague phrases. Convert them into measurable criteria when justified by input, otherwise mark `[확인 필요]`.
- Do not fabricate business rules, personas, limits, pricing, legal policies, or performance numbers. Use `[확인 필요]` or `[제안]`.
- When modifying an existing spec, do not renumber existing IDs unless the user explicitly requests a global cleanup.
