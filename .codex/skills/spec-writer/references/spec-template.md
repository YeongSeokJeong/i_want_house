# Spec Template

Use this structure for generated Markdown requirements documents. Omit sections only when the selected mode does not need them, but preserve section numbering when practical.

```markdown
# Requirements Document: <feature-or-product-name>

## 1. 개요

<2-3 sentences: goal, included scope, excluded scope.>

## 2. 용어 사전

| 용어 | 정의 |
|---|---|
| <term> | <definition> |

## 3. 기능 요구사항

### [FR-001] <기능명>

**User Story**: As a <persona>, I want <goal>, so that <benefit>.

**Acceptance Criteria** (EARS):
- WHEN <condition/event> THE SYSTEM SHALL <expected observable behavior>.
- IF <exception/failure condition> THEN THE SYSTEM SHALL <observable exception handling behavior>.
- IF <edge case> THEN THE SYSTEM SHALL <observable handling behavior>. [제안]
- WHILE <state> THE SYSTEM SHALL <ongoing behavior>. <!-- use only when relevant -->

**입력/데이터**: <fields, constraints, validation rules>

**예외/실패 모드**: <failure behavior, error handling, fallback, retry, rollback, audit behavior>

**우선순위**: <Must/Should/Could/Won't or [확인 필요]>

**의존성**: <FR-XXX IDs or 없음>

## 4. 비기능 요구사항

### [NFR-001] <품질 속성>

**Requirement**: <testable non-functional requirement>

**근거**: <user-stated source or domain necessity; use [확인 필요] if uncertain>

## 5. 의존성 및 제약

### 의존성 그래프

- FR-001 -> FR-002
- FR-001 -> FR-003

### 제약사항

- <User-stated platform, policy, data, compliance, or operational constraint>

## 6. 확인 필요 사항

| ID | 유형 | 항목 | 이유 |
|---|---|---|---|
| FR-001 | [확인 필요] | <question or assumption> | <why it matters> |
| FR-002 | [제안] | <suggested edge case/rule> | <why it is useful> |
```

## Mode Guidance

- Standard mode: include sections 1, 3, 5, and 6. Add glossary/NFRs only when useful.
- Full SRS mode: include all sections.
- Quick mode: include sections 1, 3, 5, 6, and an assumptions list in section 6.
- Wiki destination: do not force this exact top-level structure if `wiki-write` requires a domain, decision, rule, workflow, index, or schema page shape. Preserve the FR/NFR blocks, EARS criteria, dependency graph, and confirmation table inside the wiki page shape selected by `wiki-write`.

## Revision Rules

- Preserve existing requirement IDs.
- Add new IDs at the end of the relevant sequence.
- Mark deprecated requirements as `Deprecated` only when removal would break traceability.
- Update the dependency graph when any dependency changes.
