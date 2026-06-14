# 운영 환경 검증 메모

검증 일자: 2026-06-14

## 요약
- 로컬 정적 대시보드는 `http://127.0.0.1:8765/`에서 정상 렌더링을 확인했다.
- GitHub Actions `JeonseLoop` 워크플로는 최근 수동 dry-run 실행이 성공했다.
- GitHub Pages는 현재 저장소에 활성화되어 있지 않아 Pages API가 `404 Not Found`를 반환했다.
- Telegram secret 이름은 GitHub Secrets에 등록되어 있으나, 이번 검증에서는 `--send`를 명시하지 않았으므로 실전송을 수행하지 않았다.
- Live listing source secret은 등록되어 있지 않아 scheduled 운영 실행은 `listing_source_unconfigured`로 실패한다.

## 대시보드 렌더링
- 실행 방식: 저장소 루트에서 `python -m http.server 8765 --bind 127.0.0.1`로 정적 서버 실행.
- HTTP 확인:
  - `/` 응답 코드: `200`
  - `/data/state/health.json` 응답: `status=success`, `approved_candidates=1`, `notifications_planned=1`
  - `/data/state/urgent-feed.json` 응답: `items[0].title=Sample low price listing`, `reason=baseline_price`
- Chrome headless DOM 확인:
  - 상태 배지: `정상`
  - 단지 선택: `Sample Apartment (84.9 m2)`
  - 최근 급매 후보: `Sample low price listing`
  - 호가 표시: `830,000,000원`
  - 판정 사유: `baseline_price`, `approve`
  - 히스토리 차트 영역은 `historyChart` canvas가 노출되고 `chartEmpty`는 `hidden` 상태였다.

## GitHub Actions
- 워크플로: `JeonseLoop`
- 최근 성공 실행: `27500279934`
  - 이벤트: `workflow_dispatch`
  - 브랜치: `main`
  - 생성 시각: `2026-06-14T13:25:17Z`
  - URL: `https://github.com/YeongSeokJeong/i_want_house/actions/runs/27500279934`
  - 테스트: `python -m unittest discover -s tests` 성공
  - 제품 루프: dry-run + fixture 실행 성공, `notifications_sent=0`
- 최근 실패 실행 예:
  - `27500234272`, `workflow_dispatch`, 실패 사유: `listing_source_unconfigured`
  - `27497481708`, `schedule`, 실패 사유: `listing_source_unconfigured`

## Secrets와 외부 연동
- `gh secret list` 확인 결과:
  - `TELEGRAM_BOT_TOKEN` 등록됨
  - `TELEGRAM_CHAT_ID` 등록됨
- 다음 secret은 등록 목록에 없었다:
  - `JEONSELOOP_LISTING_SOURCE_URL`
  - `JEONSELOOP_TRADE_SOURCE_URL`
  - `JEONSELOOP_SOURCE_BEARER_TOKEN`
  - `OPENAI_API_KEY`
- Live listing source가 없으므로 fixture 없는 scheduled 운영 루프는 외부 매물 응답을 받을 수 없다.
- Telegram 실전송은 저장소 안전 규칙에 따라 `--send`가 명시되지 않아 수행하지 않았다.

## GitHub Pages
- 확인 명령: `gh api repos/YeongSeokJeong/i_want_house/pages`
- 결과: `404 Not Found`
- 해석: 현재 GitHub Pages 사이트가 활성화되어 있지 않아 Pages URL 접근 검증은 실패 상태다.

## 결론
- 로컬 대시보드 렌더링과 fixture 기반 Actions dry-run은 검증 완료.
- 운영 scheduled 실행을 성공시키려면 `JEONSELOOP_LISTING_SOURCE_URL`을 GitHub Secrets에 추가해야 한다.
- GitHub Pages 공개 접근을 사용하려면 저장소 Pages 설정을 활성화해야 한다.
- Telegram 실전송 검증은 운영자가 `--send` 실행을 명시한 별도 검증에서만 수행해야 한다.
