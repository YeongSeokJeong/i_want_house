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
- lowercase kebab-case를 사용한다.
- 도메인 폴더는 업무 개념 이름을 사용한다.
- 모든 도메인 폴더는 `overview.md`를 포함한다.

## 금지 폴더
명시적 요청 없이 `raw/`, `queries/`, `progress/`, `sessions/` 폴더를 만들지 않는다.

## 에이전트 결정 처리
에이전트 판단은 별도 결정 문서로 만들지 않는다. 필요하면 관련 페이지의 `Agent note` 섹션에만 기록한다.
