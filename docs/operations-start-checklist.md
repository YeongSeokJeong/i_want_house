# 운영 시작 전 체크리스트

이 체크리스트는 dry-run 해제, GitHub Actions 운영, GitHub Pages 공개, Telegram 실전송 검증 전에 확인할 항목을 정리한다.

## 1. 저장소 상태
- [ ] `config/watchlist.yaml`의 단지, 면적, 목표가, 제외 키워드가 최신이다.
- [ ] `README.md`와 운영 문서가 현재 source kind와 맞다.
- [ ] 최신 변경 후 `python -m unittest discover -s tests`가 통과했다.
- [ ] fixture dry-run이 통과했다.

```powershell
powershell -File scripts/run-loop.ps1 -DryRun -Fixture tests\fixtures\listings.json
```

## 2. GitHub Actions 설정
- [ ] `JEONSELOOP_LISTING_SOURCE_KIND=hogangnono`를 Variables 또는 실행 환경에 설정했다.
- [ ] `JEONSELOOP_HOGANGNONO_APT_HASH_MAP`에 모든 watchlist `complex_id` 매핑이 있다.
- [ ] `JEONSELOOP_HOGANGNONO_TRADE_TYPES=0`이 매매 수집 의도와 맞다.
- [ ] `JEONSELOOP_HOGANGNONO_PAGE_SIZE`와 `JEONSELOOP_HOGANGNONO_MAX_PAGES`가 과도하지 않다.
- [ ] workflow 수동 실행 시 `dry_run=false`, `send=false`로 첫 운영 수집을 검증한다.

## 3. GitHub Secrets
- [ ] `TELEGRAM_BOT_TOKEN`이 GitHub Secrets에 있다.
- [ ] `TELEGRAM_CHAT_ID`가 GitHub Secrets에 있다.
- [ ] OpenAI 검수를 사용할 경우에만 `OPENAI_API_KEY`가 있다.
- [ ] 실제 secret 값은 README, docs, workflow, backlog에 기록하지 않았다.

## 4. 첫 수집 검증
- [ ] Actions run이 성공했다.
- [ ] `data/state/health.json`의 `latest.status`가 `success`다.
- [ ] `listing_diagnostics.targets[]`에서 각 단지의 `status`, `listing_count`, `source_id`를 확인했다.
- [ ] 매물이 0건인 단지는 `empty_response`와 source diagnostics를 보고 수집 문제인지 실제 무매물인지 구분했다.
- [ ] 이전 JSON 상태가 실패 run으로 덮이지 않았는지 확인했다.

## 5. 대시보드 검증
- [ ] 로컬 정적 서버 또는 GitHub Pages에서 `index.html`이 열린다.
- [ ] `data/state/health.json`, `data/state/urgent-feed.json`, `data/history/*.json` fetch가 성공한다.
- [ ] `단지별 감시 상태`, `데이터 품질/기준선 준비 상태`, `탈락/보류 사유 요약`이 최신 상태를 반영한다.
- [ ] GitHub Pages를 사용할 경우 Pages 설정의 branch/path가 현재 공개하려는 branch/path와 맞다.

## 6. Telegram 실전송 검증
- [ ] 반드시 사람이 의도적으로 `--send` 또는 workflow input `send=true`를 선택했다.
- [ ] dry-run이 아닌 실행인지 확인했다.
- [ ] 첫 실전송은 후보가 적은 시점에 수행한다.
- [ ] 메시지에 호가, 목표가 차이, 실거래 기준, 급매선, 링크가 표시되는지 확인한다.
- [ ] 전송 후 `data/state/notified.json`에 중복 방지 상태가 기록되는지 확인한다.

## 7. 중단 기준
- [ ] HTTP 429, 로그인 요구, CAPTCHA, 스키마 변경이 보이면 우회하지 않고 수집 실패로 처리한다.
- [ ] `collector-diagnostics.json`에 secret이 노출되면 즉시 secret을 교체하고 redaction 테스트를 보강한다.
- [ ] 알림이 과도하거나 기준이 맞지 않으면 `send=false`로 되돌리고 watchlist 기준을 조정한다.
