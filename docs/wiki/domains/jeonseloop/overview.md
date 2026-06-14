# JeonseLoop 개요

## 목적
JeonseLoop는 관심 아파트 단지의 전세 매물, 실거래 기준선, 후보 판정, 알림 상태를 Git 저장소의 JSON/Markdown 상태로 남기는 개인용 무인 감시 루프다.

## 핵심 내용
- 실행 진입점은 `scripts/run-loop.*`와 `src/jeonseloop/run.py`이며 GitHub Actions가 정기/수동 실행을 담당한다.
- Telegram 알림은 `--send`와 필수 환경 변수가 모두 있을 때만 전송한다.
- `--dry-run`은 알림 전송과 상태 쓰기를 모두 막는 안전 점검 모드다.
- 상태 파일은 `data/listings/`, `data/history/`, `data/trades/`, `data/state/` 아래 JSON으로 저장한다.
- 대시보드는 정적 파일만 사용하며 `data/state/health.json`, `data/history/*.json`, `data/state/urgent-feed.json`을 fetch한다.
- fixture 없이 실행하는 운영 루프는 `JEONSELOOP_LISTING_SOURCE_URL`로 live 매물 JSON 소스를 받아야 한다. 미설정 상태에서는 빈 수집 성공이 아니라 `listing_source_unconfigured` health 실패로 기록한다.
- 선택적으로 `JEONSELOOP_TRADE_SOURCE_URL`을 설정하면 live 실거래 JSON을 기준선 계산에 사용할 수 있으며, 미설정 시 기존 `data/trades/{complex_id}.json` cache와 watchlist 목표가 폴백을 사용한다.
- 실거래 기준선이 있으면 기준선 할인율로 후보를 판정하고, 없으면 watchlist 목표가로 폴백한다.
- 후보 품질 관리는 제외 조건, 중복 보류, 알림 상한, LLM 검수 실패 보류를 알림 계획 전에 적용한다.
- 기준 개선 제안은 `data/state/criteria-suggestions.json`으로만 생성하며 `config/watchlist.yaml`은 자동 수정하지 않는다.

## 관련 문서
- [[../../rules/workflow/loop-engineering-routing]]
- [[../../rules/workflow/development-automation-loop]]
- `jeonseloop-spec.md`
- `docs/orchestration/jeonseloop-spec-implementation/`

## 아키텍처 메모
`src/jeonseloop/`의 제품 루프는 `LoopCoordinator`가 한 사이클을 조율하고, 수집(`ListingCollector`), 검증(`ListingValidator`), 후보 판정(`CandidateAnalyzer`), 상태 저장(`LoopStateRepository`), 거래 기준선(`TradeBaselineRepository`), 알림(`NotificationService`), LLM 검수(`CandidateReviewService`), 기준 제안(`CriteriaSuggestionService`) 객체를 명시적으로 조합하는 구조를 기준으로 한다. 기존 module-level 함수들은 CLI와 테스트 호환을 위한 얇은 wrapper로 유지한다.

## Agent note
외부 서비스 연결 상태는 저장소만으로 증명하지 않는다. GitHub Secrets, 실제 Actions 실행 이력, Telegram 실전송, 외부 포털/API 응답은 별도 운영 환경 확인 대상으로 남긴다.
