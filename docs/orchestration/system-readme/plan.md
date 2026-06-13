# Task Plan

## Task Metadata
- Task Name: System README 작성
- Task ID: system-readme
- Task Branch: feature/jeonseloop-automation
- Plan Version: v1
- Last Updated: 2026-06-13

## Planning Assumptions
- 루트 `README.md`가 없으므로 새로 작성한다.
- README는 구현된 JeonseLoop 시스템의 목적, 실행 방법, 안전 제약, 상태 산출물, 운영 설정, 검증 명령을 다룬다.
- 기존 `jeonseloop-spec.md`, 최종 handoff, wiki overview, 코드와 workflow를 authoritative source로 사용한다.
- 외부 서비스 설정 여부는 저장소에서 증명하지 않고 운영자 확인 대상으로 표시한다.

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | Root README 작성 | 저장소 첫 화면에서 JeonseLoop 실행, 검증, 운영 방식을 이해할 수 있게 한다. | None | Low | Codex |

## Feature Detail
### F-001 Root README 작성
- Scope:
  - `README.md`를 새로 작성한다.
  - quick start, 안전 제약, 구성 파일, 상태 파일, GitHub Actions, Telegram/LLM 설정, dashboard, 테스트 명령을 포함한다.
  - 현재 구현과 맞지 않는 운영 보장을 쓰지 않는다.
- Acceptance Criteria:
  - [ ] `README.md`가 존재한다.
  - [ ] dry-run, test, fixture-backed 실행 명령이 포함된다.
  - [ ] Telegram 전송 조건과 dry-run no-write/no-send 제약이 명시된다.
  - [ ] 주요 상태 파일과 dashboard entrypoint가 설명된다.
  - [ ] 최종 QA 명령이 통과한다.
- Out of Scope:
  - 코드 동작 변경, 실제 외부 서비스 연결 증명, wiki 구조 변경.

## Execution Order
1. F-001

## Revision Policy
- Plan revision is allowed only when scope, constraints, risks, or sequencing change.
- Any revision must update affected feature IDs in both `plan.md` and `progress.md`.

## Revision Log
| Version | Date | Changed Feature IDs | Why Revised | Author |
|---------|------|---------------------|-------------|--------|
| v1 | 2026-06-13 | F-001 | Initial README task plan | Codex |
