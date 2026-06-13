# Loop Engineering Routing

## 목적
JeonseLoop 관련 작업을 제품 실행 루프와 개발 검사 루프로 나누어 판단한다.
`AGENTS.md`에는 반드시 지켜야 할 실행 제약만 두고, repo 검증 범위와 외부 상태 판단은 이 문서로 라우팅한다.

## 라우팅 패턴
| 질문 | 라우팅 | 확인 대상 |
|---|---|---|
| 제품이 한 사이클을 어떻게 실행하는가 | Product loop | `scripts/run-loop.*`, `src/jeonseloop/run.py`, `.github/workflows/jeonseloop.yml` |
| 매물 수집, 판정, 알림, 상태 저장이 구현됐는가 | Product loop | `src/jeonseloop/`, `config/watchlist.yaml`, `tests/` |
| 요구사항 대비 누락이나 위험을 검사하는가 | Development inspection loop | `.codex/prompts/loop-review.md`, `reports/*.md`, `docs/wiki/rules/workflow/development-automation-loop.md` |
| `codex exec`가 제품을 대신 실행하는가 | Development inspection loop | 아니오. `codex exec`는 개발 검사 도구로만 취급한다. |
| 실제 운영 연결이 되어 있는가 | External state | GitHub Actions 설정, GitHub Secrets, Telegram 실전송, 외부 포털/API 상태는 실행 환경에서 별도 확인한다. |

## 판정 규칙
- 코드 구현 여부와 실제 운영 연결 상태를 분리해서 말한다.
- 저장소에서 확인한 것은 `repo-verifiable`로 보고하고, 외부 서비스 접속이나 계정 설정이 필요한 것은 `external state`로 표시한다.
- 제품 루프의 Trigger와 `codex exec` 실행 여부를 섞지 않는다.
- 하드 제약은 `AGENTS.md`에 남기고, 검사 관점과 보고 방식은 이 문서를 따른다.

## 관련 문서
- [[development-automation-loop]]
- [[../../index]]
