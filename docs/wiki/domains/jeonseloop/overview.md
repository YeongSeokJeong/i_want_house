# JeonseLoop 개요

## 목적
JeonseLoop는 관심 아파트 단지의 매매/전세 매물, 실거래 기준선, 후보 판정, 알림 상태를 Git 저장소의 JSON/Markdown 상태로 남기는 개인용 무인 감시 루프다.

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
- 선택적 LLM 검수는 `OPENAI_API_KEY`와 `JEONSELOOP_LLM_REVIEW=true`가 있을 때만 OpenAI Responses API로 실행하며, 응답 JSON 검증 실패나 네트워크 오류는 후보 보류로 처리한다.
- 기준 개선 제안은 `data/state/criteria-suggestions.json`으로만 생성하며 `config/watchlist.yaml`은 자동 수정하지 않는다. 제안 JSON은 판정 사유 빈도와 LLM 보류, 평균가 급변, 중복 보류 같은 오탐 신호의 건수/비율을 함께 담아 검수 전후 변화를 비교할 수 있게 한다.

## 관련 문서
- [[../../rules/workflow/loop-engineering-routing]]
- [[../../rules/workflow/development-automation-loop]]
- `jeonseloop-spec.md`
- `docs/orchestration/jeonseloop-spec-implementation/`

## 아키텍처 메모
`src/jeonseloop/`의 제품 루프는 `LoopCoordinator`가 한 사이클을 조율하고, 수집(`ListingCollector`), 검증(`ListingValidator`), 후보 판정(`CandidateAnalyzer`), 상태 저장(`LoopStateRepository`), 거래 기준선(`TradeBaselineRepository`), 알림(`NotificationService`), LLM 검수(`CandidateReviewService`), 기준 제안(`CriteriaSuggestionService`) 객체를 명시적으로 조합하는 구조를 기준으로 한다. 기존 module-level 함수들은 CLI와 테스트 호환을 위한 얇은 wrapper로 유지한다.

## Agent note
외부 서비스 연결 상태는 저장소만으로 증명하지 않는다. GitHub Secrets, 실제 Actions 실행 이력, Telegram 실전송, 외부 포털/API 응답은 별도 운영 환경 확인 대상으로 남긴다.
## 네이버부동산 수집과 복구 루프
- `JEONSELOOP_LISTING_SOURCE_KIND=naver`를 설정하면 live listing source로 네이버부동산 어댑터를 사용한다.
- `JEONSELOOP_NAVER_COMPLEX_NO_MAP`은 watchlist의 `complex_id`를 네이버 단지번호로 매핑하는 JSON 객체다. 예: `{"sample-apt":"111515"}`.
- 현재 운영 수집값은 매매 기준 `JEONSELOOP_NAVER_TRADE_TYPE=A1`, 주거 유형 `JEONSELOOP_NAVER_REAL_ESTATE_TYPE=APT`, 조회 페이지 수 `JEONSELOOP_NAVER_MAX_PAGES=3`이다. 전세 수집이 필요하면 `B1`을 사용한다.
- 네이버부동산 응답은 환경과 시점에 따라 HTTP 429, 로그인 요구, CAPTCHA, 스키마 변경이 발생할 수 있다. 이 경우 우회하지 않고 실패로 기록한다.
- 수집 실패 시 `data/state/collector-diagnostics.json`에 source kind, failure stage, error type, target complex_id를 redaction 후 저장한다.
- GitHub Actions의 `JeonseLoop` workflow는 실패 시 `collector-diagnostics` artifact를 업로드하고, `Collector Recovery` workflow는 실패 run ID를 받아 `collector-recovery-report` artifact를 생성한다.
- 복구 보고서는 사람이 검토할 수 있는 진단 자료이며 `main`에 자동 push하지 않는다.

## 호갱노노 매물 수집
- `JEONSELOOP_LISTING_SOURCE_KIND=hogangnono`를 설정하면 live listing source로 호갱노노 공개 JSON 어댑터를 사용한다.
- `JEONSELOOP_HOGANGNONO_APT_HASH_MAP`은 watchlist의 `complex_id`를 호갱노노 아파트 해시로 매핑하는 JSON 객체다. 예: `{"baengnyeonsan-hillstate-3":"E152","bulgwang-miseong":"B11b"}`.
- watchlist `complex_id`가 `E152`처럼 호갱노노 아파트 해시 자체이면 별도 매핑 없이 조회할 수 있다.
- 기본 수집은 매매 기준 `JEONSELOOP_HOGANGNONO_TRADE_TYPES=0`, 페이지 크기 `JEONSELOOP_HOGANGNONO_PAGE_SIZE=50`, 페이지 수 `JEONSELOOP_HOGANGNONO_MAX_PAGES=3`이다.
- 호갱노노 매물 응답의 `deposit`은 만원 단위로 해석해 `price_krw`로 정규화하고, `privateArea`/`sizeM2` 계열 필드를 `area_m2`로 사용한다.
- 호갱노노 공개 endpoint가 HTTP 429, 로그인 요구, 스키마 변경을 반환하면 우회하지 않고 collector failure로 기록하며 이전 JSON 상태를 보존한다.
