# 개발 자동화 검사 루프

## 목적
JeonseLoop 구현이 요구사항과 Loop Engineering 구조에서 벗어나지 않도록 `codex exec`로 반복 검사하는 개발 자동화 구조를 정의한다.

이 문서의 자동화는 JeonseLoop 서비스를 실행하는 운영 루프가 아니다. 저장소의 문서, 코드, workflow, 상태 파일 설계를 읽고 개발 상태를 점검하는 메타 루프다.

## 루프 구분
### Codex 개발 검사 루프
- Trigger: 사람이 `codex exec`를 실행하거나 GitHub Actions, Windows Task Scheduler, crontab 같은 외부 스케줄러가 `codex exec`를 실행한다.
- Discover/Route: 저장소의 `AGENTS.md`, `jeonseloop-spec.md`, 코드, workflow, 설정 파일을 읽고 검사 대상을 정한다.
- Execute: Loop Engineering 단계별로 누락, 위험, 불일치를 리뷰한다.
- Verify: 요구사항 ID, 테스트 가능성, 상태 저장 안전성, 알림 경로를 기준으로 판단한다.
- Persist: 결과를 `reports/*.md` 또는 CI artifact로 남긴다.
- Escalate: 중요한 누락이나 위험을 사람에게 보고한다.

### JeonseLoop 제품 루프
- Trigger: GitHub Actions cron, `workflow_dispatch`, 또는 문서화된 외부 스케줄러가 감시 사이클을 시작한다.
- Discover/Route: `config/watchlist.yaml`을 읽고 매물/실거래 소스를 선택하며 후보를 분류한다.
- Execute: 수집, 스키마 검증, 가격 판정, 알림 생성을 수행한다.
- Verify: dry-run, 테스트, JSON schema, 실패 격리로 결과를 검증한다.
- Persist: `data/**/*.json`, `logs/*.md`, dashboard용 정적 파일을 갱신한다.
- Escalate: Telegram 급매 알림과 health 실패 알림을 보낸다.

## Trigger 검사 의미
Trigger 검사는 `codex exec`가 실행됐는지 확인하는 절차가 아니다. 저장소 안에서 JeonseLoop 제품 루프의 실행 경로가 검토 가능한 형태로 선언되어 있는지 확인하는 절차다.

저장소만 보고 확인 가능한 항목:
- `.github/workflows/*.yml`에 `schedule`이 선언되어 있는가
- 수동 실행을 위한 `workflow_dispatch`가 있는가
- 중복 실행을 막는 `concurrency` 설정이 있는가
- 실행 명령이 저장소의 스크립트나 문서와 연결되는가
- 필요한 secret 이름과 실패 동작이 문서화되어 있는가
- 실패한 실행이 기존 상태 파일을 손상하지 않도록 설계되어 있는가

저장소만 보고 확인할 수 없는 항목:
- Windows Task Scheduler에 실제 작업이 등록되어 있는가
- crontab에 실제 작업이 등록되어 있는가
- 사용자의 PC나 서버가 예약 시각에 켜져 있었는가
- GitHub Actions 또는 외부 스케줄러가 최근 실제로 성공했는가
- 외부 스케줄러 로그가 정상인지 여부

외부 스케줄러를 쓰는 경우 Trigger 검사는 실제 등록 상태를 증명하지 않는다. 대신 repo에 다음 중 하나가 있어야 검토 가능하다.

- `ops/scheduler.md`
- `ops/windows-task-jeonseloop.xml`
- `ops/crontab.example`
- `scripts/run-loop.ps1`
- `scripts/run-loop.sh`

이런 파일이 없다면 검사 결과는 `Trigger: not verifiable from repository`로 보고한다.

## 권장 실행 방식
초기에는 read-only 검사만 수행한다.

```powershell
codex exec --sandbox read-only `
  "Review this repository as a JeonseLoop development inspection loop. Do not evaluate whether this Codex run was triggered. Evaluate whether the JeonseLoop product loop has implemented or documented Trigger, Discover/Route, Execute, Verify, Persist, and Escalate. Report repo-verifiable findings and explicitly mark external scheduler state as not verifiable." `
  -o reports\loop-review.md
```

구현이 쌓인 뒤에도 자동 수정은 제한적으로만 허용한다.

```powershell
codex exec --sandbox workspace-write `
  "Fix only low-risk documentation or test fixture issues found by the loop review. Do not change production state files. Summarize the diff and verification result." `
  -o reports\loop-fix.md
```

## 검사 출력 기준
검사 보고서는 다음 순서를 따른다.

1. Findings: 버그, 누락, 회귀 위험을 우선순위로 나열한다.
2. Not verifiable from repo: 외부 스케줄러, 외부 secret, 실제 실행 이력처럼 repo만으로 확인할 수 없는 항목을 분리한다.
3. Next actions: 사람이 다음에 구현하거나 결정할 항목을 짧게 적는다.
4. Evidence: 확인한 파일 경로를 적는다.

## 체크리스트
- [ ] 검사 프롬프트가 `codex exec` 실행 자체와 JeonseLoop 제품 Trigger를 구분한다.
- [ ] repo-only로 검증 가능한 항목과 외부 상태를 분리해 보고한다.
- [ ] Trigger가 GitHub Actions가 아니라면 외부 스케줄러 증거 문서를 repo에 둔다.
- [ ] 결과는 `reports/*.md` 또는 CI artifact로 남긴다.
- [ ] 자동 수정은 read-only 검사 결과가 안정된 뒤 제한적으로 도입한다.

## 관련 문서
- [[../../index]]
- [[../../SCHEMA]]
