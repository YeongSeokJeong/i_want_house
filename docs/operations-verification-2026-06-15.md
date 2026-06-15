# 운영 환경 검증 메모

검증 일자: 2026-06-15

## 요약
- JeonseLoop repository variables를 호갱노노 수집 모드로 설정했다.
- GitHub Actions `JeonseLoop`를 `dry_run=false`, `send=false`로 수동 실행했고 성공했다.
- 실제 수집 실행은 상태 JSON과 로그를 원격 브랜치 `task/hogangnono-listing-source`에 커밋했다.
- Telegram 전송은 `send=false`였으므로 수행하지 않았다.
- GitHub Pages는 아직 활성화되지 않았다. Pages API는 `404 Not Found`이고, 현재 작업 브랜치 루트 공개는 명시 승인이 필요해 보류했다.

## Repository Variables
- `JEONSELOOP_LISTING_SOURCE_KIND=hogangnono`
- `JEONSELOOP_HOGANGNONO_APT_HASH_MAP`은 현재 watchlist의 두 단지를 호갱노노 apt hash에 연결하도록 설정했다.
- `JEONSELOOP_HOGANGNONO_TRADE_TYPES=0`
- `JEONSELOOP_HOGANGNONO_PAGE_SIZE=50`
- `JEONSELOOP_HOGANGNONO_MAX_PAGES=3`

주의:
- PowerShell에서 `gh variable set --body`로 JSON 값을 넣을 때 따옴표가 제거될 수 있었다.
- 최종 저장값은 REST API 원문에서 유효한 JSON 문자열로 확인했다.

## Workflow 보정
- 원인: repository variables가 job 전체 env로 주입되어 `Run tests` 단계의 단위 테스트가 live source 설정을 읽었다.
- 조치: `.github/workflows/jeonseloop.yml`의 `Run tests` 단계에서 Telegram, source, LLM env를 빈 값으로 오버라이드했다.
- 커밋: `b4dea9c fix(jeonseloop): isolate workflow tests from live env`
- 검증: 로컬 `.venv\Scripts\python.exe -m unittest discover -s tests`에서 64개 테스트가 통과했다.

## GitHub Actions 실제 수집 실행
- 최종 성공 run: `27519619085`
- URL: `https://github.com/YeongSeokJeong/i_want_house/actions/runs/27519619085`
- 브랜치: `task/hogangnono-listing-source`
- head SHA: `a42cb2f1da657d95992830e90d83d7616f6a137c`
- 실행 조건: `dry_run=false`, `send=false`, fixture 없음
- 테스트 단계: 64개 통과
- 제품 루프 결과:
  - status: `success`
  - reason: `completed`
  - watched_complexes: 2
  - valid_listings: 1
  - invalid_listings: 0
  - approved_candidates: 0
  - notifications_planned: 0
  - notifications_sent: 0
  - data_quality_blocks: 0

## Persist 결과
- Actions 상태 커밋: `42add4c chore(jeonseloop): persist loop state [skip ci]`
- 변경 파일:
  - `data/state/health.json`
  - `data/state/urgent-feed.json`
  - `data/listings/baengnyeonsan-hillstate-3.json`
  - `data/listings/bulgwang-miseong.json`
  - `data/history/baengnyeonsan-hillstate-3.json`
  - `data/history/bulgwang-miseong.json`
  - `logs/criteria-log.md`

## 상태 파일 확인
- `data/state/health.json`의 최신 실행은 `run_id=44af8bb3-1c82-4126-b376-fd47d97ef83a`, `status=success`, `last_success_at=2026-06-15T02:00:41+00:00`이다.
- `data/state/urgent-feed.json`에는 백련산힐스테이트3차 호갱노노 매물 1건이 기록되었고, 목표가 초과로 `decision=reject`, `alert_planned=false`이다.
- 불광 미성아파트는 이번 실행에서 유효 매물 0건으로 snapshot 파일이 빈 배열로 기록되었다.

## 실패 후 조치 이력
- run `27519452565`: repository variables가 테스트 단계에 주입되어 단위 테스트가 실패했다.
- run `27519521251`: 호갱노노 매핑 variable이 JSON이 아닌 형태로 저장되어 `JEONSELOOP_HOGANGNONO_APT_HASH_MAP must be a JSON object`로 실패했다.
- 위 두 원인을 수정한 뒤 run `27519576809`와 최신 run `27519619085`가 성공했다.

## GitHub Pages
- 확인 명령: `gh api repos/YeongSeokJeong/i_want_house/pages`
- 현재 결과: `404 Not Found`
- 해석: GitHub Pages 사이트가 아직 활성화되어 있지 않다.
- 보류 사유: 현재 최신 대시보드와 실제 수집 상태는 `task/hogangnono-listing-source` 브랜치에 있으므로, 이 브랜치 루트를 공개 source로 지정하면 브랜치 루트 파일이 외부 공개된다. 이 공개 범위는 명시 승인이 필요해 이번 실행에서는 활성화하지 않았다.

## 다음 승인 필요 항목
- GitHub Pages를 `task/hogangnono-listing-source` 브랜치 루트에서 공개해도 되는지 승인해야 한다.
- 또는 브랜치를 `main`에 병합한 뒤 `main` 루트로 Pages를 활성화할지 결정해야 한다.
