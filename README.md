# JeonseLoop

JeonseLoop는 관심 아파트 단지의 매매/전세 매물과 실거래 기준선을 주기적으로 수집하고, 급매 후보를 판정해 Telegram 알림과 Git 저장소 기반 상태 파일로 남기는 개인용 무인 감시 루프입니다.

이 저장소는 별도 DB 없이 JSON/Markdown 파일을 상태 저장소로 사용하고, GitHub Actions와 GitHub Pages 정적 대시보드로 운영하는 것을 목표로 합니다.

## 핵심 원칙
- `--dry-run`은 알림 전송과 상태 쓰기를 모두 막습니다.
- Telegram 알림은 `--send`가 명시되고 `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`가 모두 있을 때만 전송됩니다.
- 상태 JSON은 validate-before-replace 방식으로 기록해 실패 시 이전 정상 상태를 보존합니다.
- 외부 서비스 연결 상태는 저장소만으로 증명하지 않습니다. GitHub Secrets, 실제 Actions 실행, Telegram 실전송, 외부 포털/API 응답은 운영 환경에서 별도 확인해야 합니다.

## 빠른 시작

테스트:

```powershell
python -m unittest discover -s tests
```

상태 쓰기와 알림 없이 fixture로 한 사이클 실행:

```powershell
powershell -File scripts/run-loop.ps1 -DryRun -Fixture tests\fixtures\listings.json
```

Python 모듈로 직접 실행:

```powershell
$env:PYTHONPATH = "src"
python -m jeonseloop.run --dry-run --fixture tests\fixtures\listings.json
```

임시 디렉터리에 상태를 쓰는 검증 실행:

```powershell
$env:PYTHONPATH = "src"
$root = Join-Path $env:TEMP "jeonseloop-check"
python -m jeonseloop.run --fixture tests\fixtures\listings.json --data-dir "$root\data" --logs-dir "$root\logs"
```

Linux/macOS:

```bash
PYTHONPATH=src python -m jeonseloop.run --dry-run --fixture tests/fixtures/listings.json
```

## 실행 진입점
- `scripts/run-loop.ps1`: Windows/PowerShell 운영 진입점
- `scripts/run-loop.sh`: shell 운영 진입점
- `src/jeonseloop/run.py`: Python CLI entrypoint
- `.github/workflows/jeonseloop.yml`: GitHub Actions 정기/수동 실행 workflow

CLI 주요 옵션:

```text
--watchlist <path>  감시 설정 파일 경로, 기본값 config/watchlist.yaml
--data-dir <path>   JSON 상태 출력 디렉터리, 기본값 data
--logs-dir <path>   Markdown 로그 출력 디렉터리, 기본값 logs
--fixture <path>    테스트/검증용 매물 fixture
--dry-run           알림 전송과 상태 쓰기 금지
--send              Telegram 전송 허용, secrets 필요
```

## Watchlist 설정

감시 대상은 `config/watchlist.yaml`에서 관리합니다.

```yaml
version: 1
request_interval_seconds: 2
complexes:
  - complex_id: sample-apt
    name: Sample Apartment
    area_m2: 84.9
    target_price_krw: 850000000
    urgent_discount_ratio: 0.12
    exclude:
      - basement
```

중요 제약:
- `request_interval_seconds`는 2초 미만으로 설정할 수 없습니다.
- 필수 필드가 없거나 형식이 잘못되면 수집 단계로 진행하지 않고 health 실패로 기록합니다.
- `exclude` 조건에 걸린 매물은 가격 조건을 만족해도 알림 대상이 되지 않습니다.

## 상태 파일

주요 산출물:

| 경로 | 내용 |
|---|---|
| `data/state/health.json` | 마지막 실행 상태, 실패 연속 횟수, 마지막 성공 실행, 알림 가능 health 상태 |
| `data/state/notified.json` | Telegram dedup 상태 |
| `data/state/urgent-feed.json` | 후보 판정 결과, 보류/제외/중복 사유, 알림 계획 여부 |
| `data/state/criteria-suggestions.json` | 충분한 판정 로그가 쌓였을 때 생성되는 수동 검토용 기준 개선 제안 |
| `data/listings/{complex_id}.json` | 단지별 현재 매물 snapshot |
| `data/history/{complex_id}.json` | 단지별 시세 history |
| `data/trades/{complex_id}.json` | 최근 실거래 기준선 cache |
| `logs/criteria-log.md` | 후보 판정과 격리 사유 로그 |

## 후보 판정 흐름

1. `config/watchlist.yaml`을 읽고 검증합니다.
2. watchlist에 포함된 단지만 수집합니다.
3. 매물 record schema를 검증하고 잘못된 record는 격리 로그로 보냅니다.
4. 실거래 기준선이 있으면 기준선 대비 할인율로 판정하고, 없으면 watchlist 목표가로 폴백합니다.
5. 제외 조건, 중복 보류, 평균가 급변 차단, 선택적 LLM 검수를 알림 계획 전에 적용합니다.
6. 승인 후보가 5건을 넘으면 최대 5건만 알림 계획에 포함하고 overflow를 health/feed에 기록합니다.
7. 실제 전송은 `--send`와 Telegram secrets가 있을 때만 수행합니다.
8. dry-run이 아니면 JSON 상태와 Markdown 로그를 기록합니다.

## GitHub Actions 운영

Workflow: `.github/workflows/jeonseloop.yml`

동작:
- cron: `0 0,9 * * *` UTC, 즉 09:00/18:00 KST 실행
- `workflow_dispatch` 수동 실행 지원
- 수동 실행은 기본 dry-run입니다.
- schedule 실행은 상태를 쓰고 `data`, `logs` 변경분을 commit/push합니다.
- concurrency group은 `jeonseloop-product-loop`이며 `cancel-in-progress: false`입니다.

필요한 repository secrets:

```text
JEONSELOOP_LISTING_SOURCE_URL
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

선택 repository secrets/variables:

```text
JEONSELOOP_TRADE_SOURCE_URL
JEONSELOOP_SOURCE_BEARER_TOKEN
JEONSELOOP_SOURCE_TIMEOUT_SECONDS
OPENAI_API_KEY
JEONSELOOP_LLM_REVIEW
JEONSELOOP_LLM_MODEL
```

실제 Telegram 전송은 workflow input `send=true` 또는 CLI `--send`가 있어야 합니다.

## 선택적 LLM 검수

LLM 검수는 기본 비활성입니다. 다음 환경 변수가 모두 있을 때만 승인 후보에 대해 검수를 시도합니다.

```text
JEONSELOOP_LLM_REVIEW=true
OPENAI_API_KEY=<secret>
JEONSELOOP_LLM_MODEL=gpt-4.1
```

안전 동작:
- LLM 검수는 OpenAI Responses API를 사용하며, 실제 API 접근 권한과 과금 상태는 운영 환경에서 별도로 확인해야 합니다.
- JSON 파싱 실패, 필수 필드 누락, 네트워크 오류는 후보를 `hold` 처리합니다.
- 실패한 LLM 응답은 Telegram 알림으로 이어지지 않습니다.
- 기준 개선 제안은 `criteria-suggestions.json`에만 기록되고 `config/watchlist.yaml`은 자동 수정하지 않습니다.

## 실서비스 데이터 소스 설정

fixture 없이 실행하는 운영 루프는 live 매물 소스가 필요합니다. `JEONSELOOP_LISTING_SOURCE_URL`이 없으면 빈 수집을 성공으로 처리하지 않고 `listing_source_unconfigured` health 실패를 기록합니다.

지원하는 HTTP JSON 계약:

```text
JEONSELOOP_LISTING_SOURCE_URL=https://example.invalid/listings/{complex_id}
JEONSELOOP_TRADE_SOURCE_URL=https://example.invalid/trades/{complex_id}
JEONSELOOP_SOURCE_BEARER_TOKEN=<optional-secret>
JEONSELOOP_SOURCE_TIMEOUT_SECONDS=15
```

- URL에는 `{complex_id}`, `{name}`, `{area_m2}` placeholder를 사용할 수 있습니다.
- 매물 응답은 JSON list 또는 `{ "listings": [...] }` 형식이어야 합니다.
- 실거래 응답은 JSON list 또는 `{ "trades": [...] }` 형식이어야 합니다.
- 매물 레코드는 기존 schema 검증을 통과해야 하며, 필수 필드는 `price_krw`, `area_m2`, `floor`, `link`입니다.
- 실거래 레코드는 `price_krw` 또는 `trade_price_krw`를 사용합니다.
- 실제 포털/API credentials, 약관, 응답 유효성은 운영 환경에서 별도 검증해야 합니다.

## 대시보드

루트 `index.html`과 `assets/dashboard.*`는 GitHub Pages에서 정적으로 제공되는 대시보드입니다.

대시보드는 다음 JSON을 fetch합니다.
- `data/state/health.json`
- `data/history/{complex_id}.json`
- `data/state/urgent-feed.json`

로컬에서 정적 파일만 확인하려면 간단한 HTTP 서버로 열 수 있습니다.

```powershell
python -m http.server 8000
```

이후 브라우저에서 `http://localhost:8000/`을 엽니다.

## 개발 검증

전체 unit test:

```powershell
python -m unittest discover -s tests
```

대시보드 JavaScript syntax check:

```powershell
node --check assets\dashboard.js
```

fixture 기반 제품 루프 dry-run:

```powershell
powershell -File scripts/run-loop.ps1 -DryRun -Fixture tests\fixtures\listings.json
```

개발 검사 프롬프트:

```powershell
Get-Content .codex\prompts\loop-review.md -Raw | codex exec --sandbox read-only - -o reports\loop-review.md
```

## 문서

- 제품 요구사항: `jeonseloop-spec.md`
- 최종 구현 handoff: `docs/handoff/jeonseloop-spec-implementation-final.md`
- 제품 도메인 wiki: `docs/wiki/domains/jeonseloop/overview.md`
- Loop Engineering routing: `docs/wiki/rules/workflow/loop-engineering-routing.md`
- 오케스트레이션 기록: `docs/orchestration/`

## 운영 전 확인할 외부 상태

저장소에서 구현과 dry-run 동작은 검증할 수 있지만, 다음은 운영자가 실제 환경에서 확인해야 합니다.

- GitHub Actions가 대상 branch에서 활성화되어 있는지
- repository `contents: write` 권한과 workflow push 권한이 동작하는지
- GitHub Pages가 원하는 branch/path를 서빙하는지
- Telegram secrets가 정확하고 `--send` 실행 시 실제 메시지가 도착하는지
- 외부 매물/실거래 데이터 소스 접근 정책과 응답이 유효한지
## 네이버부동산 웹 수집 설정

정기 실행에서 네이버부동산을 직접 수집하려면 GitHub repository variables에 다음 값을 넣습니다.

```text
JEONSELOOP_LISTING_SOURCE_KIND=naver
JEONSELOOP_NAVER_COMPLEX_NO_MAP={"sample-apt":"111515"}
JEONSELOOP_NAVER_TRADE_TYPE=A1
JEONSELOOP_NAVER_REAL_ESTATE_TYPE=APT
JEONSELOOP_NAVER_MAX_PAGES=3
```

- `JEONSELOOP_NAVER_COMPLEX_NO_MAP`은 watchlist의 `complex_id`를 네이버 단지번호로 연결하는 JSON 객체입니다.
- `JEONSELOOP_NAVER_TRADE_TYPE=A1`은 매매 매물을 뜻합니다. 전세로 바꾸려면 `B1`을 사용합니다.
- 네이버부동산 수집은 공개 응답에 대한 best-effort 방식입니다. HTTP 429, CAPTCHA, 로그인 요구, 구조 변경이 발생하면 우회하지 않고 실패로 기록합니다.
- 실패 시 이전 정상 `data/listings`와 `data/history` 상태는 보존하고, `data/state/collector-diagnostics.json`에 진단 정보를 남깁니다.

수집 실패 후 보고서를 만들려면 GitHub Actions의 `Collector Recovery` workflow를 수동 실행하고, 실패한 `JeonseLoop` run ID를 `run_id`에 입력합니다. 이 workflow는 `collector-diagnostics` artifact를 내려받아 `collector-recovery-report` artifact를 생성합니다. 이 보고서는 수정 후보를 검토하기 위한 자료이며 `main`에 자동 push하지 않습니다.
