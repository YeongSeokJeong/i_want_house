# Wiki Document Templates

Use these as starting shapes. Trim sections that are unnecessary, but do not add ceremony without reason.

## 1. Domain overview
Path: `docs/wiki/domains/<domain>/overview.md`

```md
# <도메인 이름>

## 목적
- 이 도메인이 다루는 업무 개념을 짧게 설명한다.

## 핵심 주제
- [[<subtopic-1>]]
- [[<subtopic-2>]]

## 포함 범위
- 포함되는 개념
- 포함되지 않는 개념

## 관련 문서
- [[index]]
- [[SCHEMA]]
```

## 2. Domain subtopic page
Path: `docs/wiki/domains/<domain>/<subtopic>.md`

```md
# <소주제 이름>

## 목적
- 이 문서가 설명하는 대상

## 핵심 내용
- 핵심 규칙/흐름/정의
- 필요한 경우 예시

## 관련 문서
- [[overview]]
- [[<related-page>]]

## Agent note
- 필요할 때만 기록한다.
```

Notes:
- `Agent note` is optional.
- If the document grows too large, split one subtopic into multiple pages.

## 3. Human decision document
Path: `docs/wiki/decisions/<decision-name>.md`

```md
# <의사결정 제목>

- 결정 일자: YYYY-MM-DD
- 결정자: <name or group>

## 배경
- 왜 이 결정을 해야 했는지

## 결정 내용
- 채택한 방향

## 대안
- 검토했지만 채택하지 않은 선택지

## 영향 범위
- 어떤 문서/영역/운영에 영향이 있는지

## 관련 문서
- [[decisions]]
- [[<related-domain-page>]]
```

## 4. Common rule
Path: `docs/wiki/rules/common/<rule-name>.md`

```md
# <규칙 이름>

## 목적
- 이 규칙이 필요한 이유

## 규칙
- 따라야 할 원칙
- 예외가 있다면 조건

## 관련 문서
- [[SCHEMA]]
- [[<related-page>]]
```

## 5. Workflow / checklist
Path: `docs/wiki/rules/workflow/<workflow-name>.md`

```md
# <워크플로 이름>

## 목적
- 반복 수행되는 작업의 목적

## 절차
1. 첫 단계
2. 다음 단계
3. 검증 단계

## 체크리스트
- [ ] 확인 항목
- [ ] 확인 항목

## 관련 문서
- [[<related-rule>]]
- [[<related-domain-page>]]
```

## 6. `index.md` (navigation catalog)
Path: `docs/wiki/index.md`

```md
# Wiki Index

> Last updated: YYYY-MM-DD

전체 문서 목록. 폴더 구조 순서로 나열한다.

## Domains
- [[domains/<domain>/overview]] — <짧은 설명>
  - [[domains/<domain>/<subtopic>]] — <짧은 설명>

## Decisions
- [[decisions/<decision-name>]] — YYYY-MM-DD, <한 줄 요약>

## Rules
### Common
- [[rules/common/<rule-name>]] — <짧은 설명>

### Workflow
- [[rules/workflow/<workflow-name>]] — <짧은 설명>
```

Notes:
- `Last updated` is required. Update it every time the index changes.
- Keep descriptions to one short phrase — this is a catalog, not a summary.

## 7. `decisions.md` (decision list page)
Path: `docs/wiki/decisions.md`

```md
# 의사결정 목록

> Last updated: YYYY-MM-DD

프로젝트에서 내린 중요한 사람 의사결정 목록.

## 결정 목록
- [[decisions/<decision-name>]] — YYYY-MM-DD, <한 줄 요약>
```

Notes:
- `Last updated` is required. Update it every time a decision is added or changed.
- One line per decision. Details belong in the individual decision file.

## 8. `init.md` (structure guide)
Path: `docs/wiki/init.md`

```md
# Wiki 구조 안내

이 위키의 폴더 구조와 각 영역의 역할을 설명한다.

## 폴더 구조
- `domains/` — 업무 도메인별 지식 문서
- `decisions/` — 중요한 사람 의사결정 기록
- `rules/common/` — 공통 규칙/원칙
- `rules/workflow/` — 반복 절차/체크리스트

## 주요 진입점
- [[index]] — 전체 문서 목록
- [[SCHEMA]] — 작성 규칙과 라우팅 기준
- [[decisions]] — 의사결정 목록

## 작성 원칙
- 문서는 업무 개념 기준으로 분류한다.
- 파일명은 lowercase kebab-case를 사용한다.
- 위키 내용은 간결한 한국어로 작성한다.
```

## 9. `SCHEMA.md` (routing rulebook)
Path: `docs/wiki/SCHEMA.md`

```md
# Wiki Schema

이 파일이 라우팅과 작성 규칙의 최종 기준이다.

## 폴더 역할
| 폴더 | 용도 |
|---|---|
| `domains/<domain>/` | 업무 도메인 지식 |
| `decisions/` | 사람 의사결정 |
| `rules/common/` | 공통 규칙/원칙 |
| `rules/workflow/` | 반복 절차/체크리스트 |

## 파일 명명 규칙
- lowercase kebab-case
- 도메인 폴더는 업무 개념 이름 사용 (구현/태스크 이름 사용 금지)
- 모든 도메인 폴더는 `overview.md` 필수

## 금지 폴더
`raw/`, `queries/`, `progress/`, `sessions/` — 명시적 요청 없이 생성 금지

## 에이전트 결정 처리
별도 문서 금지. 관련 페이지의 `Agent note` 섹션에만 기록.
```

Notes:
- This is a minimal starting shape. Expand the rulebook as the project's schema evolves.
- If this file conflicts with the wiki-write skill's resource files, this file takes precedence.

## Index entry patterns (for updating existing pages)
### New domain in `index.md`
```md
## Domains
- [[domains/<domain>/overview]] — <짧은 설명>
  - [[domains/<domain>/<subtopic>]] — <짧은 설명>
```

### New decision in `decisions.md`
```md
- [[decisions/<decision-name>]] — YYYY-MM-DD, <한 줄 요약>
```

## Linking convention
- In `index.md` and `decisions.md`, use path-style wikilinks from `docs/wiki/`, e.g. `[[domains/auth/login-flow]]`.
- Inside a domain directory, use local links for sibling pages when clear, e.g. `[[login-flow]]`.
- When linking across domains or folders, use path-style links.
- From `rules/` to `domains/`, use path-style links, e.g. `[[../domains/auth/login-flow]]`.

## Template selection guide
- broad business topic -> domain overview
- one concept, rule, flow, or interface inside a domain -> subtopic page
- durable human choice with rationale -> human decision document
- reusable convention or policy -> common rule
- repeatable operational sequence -> workflow/checklist
- first-time wiki setup -> create `SCHEMA.md`, `init.md`, `index.md`, `decisions.md` in that order
