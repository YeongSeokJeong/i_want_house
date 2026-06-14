# JeonseLoop 확인 필요 요구사항 운영 기본 결정

- 결정 일자: 2026-06-14
- 결정자: 운영자 위임에 따른 현행 기본 정책

## 배경
- `jeonseloop-spec.md` 섹션 10의 `[확인 필요]` 항목은 중복 대표 링크, 기준 개선 제안 승인 경로, 5건 초과 알림 정렬 기준, 급매 피드 데이터 소스 형식을 확정해야 한다.
- 현재 구현은 안전한 무인 운영을 위해 보수적 기본값을 이미 적용하고 있으므로, 운영자가 별도 지시하기 전까지 사용할 기준을 문서화한다.

## 결정 내용
- 중복 매물 대표 링크는 동일 조건 묶음에서 수집 입력 순서상 첫 대표 매물을 사용한다. 동일 listing key가 여러 번 들어오면 더 낮은 가격의 레코드를 대표로 남긴다.
- 기준 개선 제안은 `data/state/criteria-suggestions.json`에 `review_required` 상태로만 생성하고, `config/watchlist.yaml`이나 판정 기준은 자동 변경하지 않는다.
- 한 사이클에서 Telegram 발송 대상이 5건을 초과하면 가격이 낮은 후보 5건을 먼저 발송 대상으로 삼고, 나머지는 대시보드 피드에서 검토한다.
- 대시보드의 최근 급매 피드는 Markdown 로그를 직접 fetch하지 않고 `data/state/urgent-feed.json`을 계약 데이터로 사용한다.

## 대안
- 중복 대표 링크를 포털, 중개사, 등록시각, 링크 품질 점수로 고르는 방식은 실제 소스별 메타데이터가 안정화된 뒤 재검토한다.
- 개선 제안을 GitHub Issue 또는 PR로 자동 생성하는 방식은 운영자 승인 흐름이 과해질 수 있어 현 단계에서는 채택하지 않는다.
- 알림 정렬을 괴리율 우선으로 두는 방식은 실거래 기준선이 없는 목표가 폴백 후보와 섞일 때 비교 기준이 불균일해 현 단계에서는 채택하지 않는다.
- 급매 피드를 `logs/criteria-log.md`에서 직접 렌더링하는 방식은 보류, 중복, 알림 상한, 링크 필드를 안정적으로 표현하기 어려워 채택하지 않는다.

## 영향 범위
- `src/jeonseloop/analyzer.py`의 중복 처리와 `approved_candidates` 정렬 기준을 운영 기본 정책으로 해석한다.
- `src/jeonseloop/suggestions.py`의 `criteria-suggestions.json` 생성 결과는 승인 요청 자료이며 설정 변경 입력이 아니다.
- `src/jeonseloop/persistence.py`의 `urgent-feed.json`은 대시보드 후보 검토 계약으로 유지한다.
- 실제 운영 데이터에서 중개사 신뢰도, 등록시각, 괴리율 우선순위가 필요해지면 별도 요구사항과 백로그 항목으로 재검토한다.

## 관련 문서
- [[decisions]]
- [[domains/jeonseloop/overview]]
- `jeonseloop-spec.md`
- `docs/backlog.md`
