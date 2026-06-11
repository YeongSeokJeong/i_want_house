# Requirements Document: JeonseLoop 부동산 급매 감시 루프

| 항목 | 내용 |
|---|---|
| 문서 버전 | v0.1 (Draft) |
| 작성일 | 2026-06-11 |
| 작성자 | 영석 |
| 시스템 유형 | 개인용 무인 감시 루프 (Loop Engineering 토이 프로젝트) |
| 대상 독자 | 본인 (개발자 겸 운영자 겸 사용자) |

## 1. 개요

JeonseLoop는 관심 아파트 단지의 매물 호가와 실거래가를 정기 수집하고, 유의미하게 낮은 급매 후보를 판정하여 Telegram으로 알림하는 개인용 무인 감시 루프이다. 시스템은 GitHub Actions, Git 저장소 내 JSON/Markdown 상태, GitHub Pages 정적 대시보드, Telegram Bot API를 기반으로 운영된다.

1차 릴리스 범위는 워치리스트 기반 수집, 룰 기반 급매 판정, Telegram 급매 알림, dedup 상태 저장, 정적 JSON 기반 대시보드 렌더링이다. 다중 사용자, 인증/계정, 대출 가능액 계산, 협상 시뮬레이션, 매수 의사결정 자동화, 모바일 앱은 제외한다.

## 2. 용어 사전

| 용어 | 정의 |
|---|---|
| 급매 | 동일 단지·동일 평형의 최근 실거래 평균가 대비 호가가 설정 임계율 이하이거나 워치리스트 희망가 상한 이하인 매물 |
| 워치리스트 | 감시 대상 단지·평형·조건을 선언한 `config/watchlist.yaml` |
| 기준선(Baseline) | 급매 판정의 비교 기준이 되는 최근 3~6개월 실거래 평균가 |
| 루프 1사이클 | Trigger 발화부터 Persist/Escalate 완료까지의 1회 무인 실행 |
| 오탐(False Positive) | 급매로 알림됐으나 실제로는 허위매물 또는 조건 결함이 있는 경우 |
| 루프 헬스 | 수집 성공률, 데이터 신선도, 실패 횟수 등 루프 자체의 동작 상태 |
| 급매 후보 | 신규 또는 가격인하 매물 중 1차 가격 조건을 통과해 검증 단계로 전달되는 매물 |

## 3. 기능 요구사항

### [FR-TR-01] 정기 실행

**User Story**: As a 운영자, I want GitHub Actions cron이 하루 2~3회 루프를 실행하기를 원한다, so that 매물을 사람 개입 없이 감시할 수 있다.

**Acceptance Criteria** (EARS):
- WHEN 예약된 GitHub Actions cron 시각이 도래하면 THE SYSTEM SHALL JeonseLoop 1사이클을 자동 시작한다.
- WHEN 기본 스케줄이 적용되면 THE SYSTEM SHALL 09:00 KST와 18:00 KST 실행을 포함한다.
- IF 예약 실행이 GitHub Actions 설정 오류로 시작되지 않으면 THE SYSTEM SHALL 해당 실패가 다음 정상 실행의 상태 파일을 손상시키지 않도록 한다. [제안]

**입력/데이터**: `.github/workflows/*`, cron schedule.

**예외/실패 모드**: 예약 미실행은 GitHub Actions 실행 이력으로 확인 가능해야 한다.

**우선순위**: Must

**의존성**: 없음

### [FR-TR-02] 수동 실행

**User Story**: As a 운영자, I want workflow_dispatch로 루프를 수동 실행하기를 원한다, so that 필요 시 즉시 감시 사이클을 돌릴 수 있다.

**Acceptance Criteria** (EARS):
- WHEN 운영자가 GitHub Actions UI 또는 API에서 workflow_dispatch를 실행하면 THE SYSTEM SHALL JeonseLoop 1사이클을 시작한다.
- IF 수동 실행 입력값이 제공되지 않으면 THE SYSTEM SHALL 기본 설정 파일을 사용해 실행한다.
- IF 수동 실행이 실패하면 THE SYSTEM SHALL 실패 상태를 루프 헬스 기록에 반영한다. [제안]

**입력/데이터**: GitHub Actions `workflow_dispatch`.

**예외/실패 모드**: 수동 실행 실패는 급매 알림으로 전환하지 않는다.

**우선순위**: Must

**의존성**: 없음

### [FR-TR-03] 동시 실행 제어

**User Story**: As a 운영자, I want 겹치는 루프 실행이 정리되기를 원한다, so that 상태 파일 commit 충돌을 줄일 수 있다.

**Acceptance Criteria** (EARS):
- WHILE 선행 루프가 실행 중일 때 후행 루프가 시작되면 THE SYSTEM SHALL 후행 실행을 취소한다.
- IF 취소된 후행 실행이 있으면 THE SYSTEM SHALL 상태 JSON 또는 알림 dedup 파일을 변경하지 않는다.
- IF 동시 실행 취소가 발생하면 THE SYSTEM SHALL GitHub Actions 실행 결과에서 취소 사유를 확인할 수 있게 한다. [제안]

**입력/데이터**: GitHub Actions `concurrency`.

**예외/실패 모드**: 취소된 실행은 실패 횟수로 집계하지 않는다. [제안]

**우선순위**: Should

**의존성**: FR-TR-01, FR-TR-02

### [FR-DC-01] 워치리스트 설정

**User Story**: As a 운영자, I want `config/watchlist.yaml`만 수정해 감시 대상을 바꾸기를 원한다, so that 코드 변경 없이 단지와 조건을 관리할 수 있다.

**Acceptance Criteria** (EARS):
- WHEN 루프가 시작되면 THE SYSTEM SHALL `config/watchlist.yaml`에서 단지명, 단지 식별자, 평형, 희망가 상한, 제외 조건을 로드한다.
- IF 필수 필드가 누락되거나 형식이 잘못되면 THE SYSTEM SHALL 해당 루프를 수집 단계로 진행하지 않고 헬스 실패로 기록한다.
- IF 워치리스트가 비어 있으면 THE SYSTEM SHALL 매물 수집을 수행하지 않고 헬스 상태에 빈 워치리스트 사유를 기록한다. [제안]

**입력/데이터**: `config/watchlist.yaml`.

**예외/실패 모드**: 잘못된 설정은 급매 알림을 발생시키지 않는다.

**우선순위**: Must

**의존성**: 없음

### [FR-DC-02] 현재 매물 수집

**User Story**: As a 운영자, I want 워치리스트 단지의 현재 매물 정보를 수집하기를 원한다, so that 호가 기반 급매 판정을 할 수 있다.

**Acceptance Criteria** (EARS):
- WHEN 워치리스트 단지가 로드되면 THE SYSTEM SHALL 해당 단지의 현재 매물 목록에서 호가, 동/층, 면적, 등록일, 설명, 링크를 수집한다.
- IF 일부 매물 필드가 누락되면 THE SYSTEM SHALL 스키마 검증 단계에서 해당 레코드를 실패 레코드로 분리한다.
- IF 수집 결과가 0건이면 THE SYSTEM SHALL 급매 알림을 보내지 않고 헬스 지표에 0건 수집 상태를 기록한다.

**입력/데이터**: 워치리스트 단지 식별자, 부동산 포털 매물 정보.

**예외/실패 모드**: 외부 페이지 구조 변경 또는 접근 실패는 헬스 실패로 기록한다.

**우선순위**: Must

**의존성**: FR-DC-01, FR-EX-01

### [FR-DC-03] 실거래가 수집

**User Story**: As a 운영자, I want 최근 6개월 실거래가를 수집하기를 원한다, so that 기준선 대비 급매 여부를 판단할 수 있다.

**Acceptance Criteria** (EARS):
- WHEN 워치리스트 단지가 로드되면 THE SYSTEM SHALL 국토교통부 실거래가 공개 API에서 최근 6개월 계약일, 거래가, 면적, 층을 수집한다.
- IF API 인증 또는 요청이 실패하면 THE SYSTEM SHALL 해당 실패를 헬스 지표에 반영하고 희망가 상한 기반 판정 가능 여부를 유지한다.
- IF 최근 6개월 실거래가가 없으면 THE SYSTEM SHALL 기준선 부재 상태를 기록한다.

**입력/데이터**: 국토교통부 실거래가 API 인증키, 단지·기간 조건.

**예외/실패 모드**: 기준선 부재 시 FR-VF-01의 희망가 상한 폴백을 사용한다.

**우선순위**: Should

**의존성**: FR-DC-01, FR-EX-03

### [FR-DC-04] 수집 범위 제한

**User Story**: As a 운영자, I want 수집 범위가 워치리스트 단지로 제한되기를 원한다, so that 과도한 크롤링을 피할 수 있다.

**Acceptance Criteria** (EARS):
- WHILE 매물 수집이 진행되는 동안 THE SYSTEM SHALL `config/watchlist.yaml`에 선언된 단지만 요청한다.
- IF 수집 대상이 워치리스트에 없는 단지로 해석되면 THE SYSTEM SHALL 해당 요청을 실행하지 않고 오류로 기록한다.
- THE SYSTEM SHALL 전수 크롤링 또는 지역 전체 탐색을 수행하지 않는다.

**입력/데이터**: 워치리스트 단지 목록.

**예외/실패 모드**: 매핑 실패 단지는 수집 제외 및 헬스 경고 대상이다. [제안]

**우선순위**: Must

**의존성**: FR-DC-01

### [FR-RT-01] 매물 변화 식별

**User Story**: As a 운영자, I want 현재 매물과 직전 스냅샷을 비교하기를 원한다, so that 신규·가격변동·소멸 매물을 구분할 수 있다.

**Acceptance Criteria** (EARS):
- WHEN 현재 매물 수집이 완료되면 THE SYSTEM SHALL 직전 사이클 스냅샷과 비교해 신규, 가격변동, 소멸, 유지 매물을 식별한다.
- IF 직전 스냅샷이 없으면 THE SYSTEM SHALL 모든 현재 매물을 최초 관측 매물로 분류한다.
- IF 매물 ID가 제공되지 않으면 THE SYSTEM SHALL 단지ID, 동, 층, 면적, 가격, 링크를 조합한 비교 키를 사용한다. [제안]

**입력/데이터**: `data/listings/{단지ID}.json`, 현재 수집 매물.

**예외/실패 모드**: 비교 키 충돌은 중복 후보 검토 대상이다.

**우선순위**: Must

**의존성**: FR-DC-02, FR-PS-01

### [FR-RT-02] 급매 후보 분류

**User Story**: As a 운영자, I want 신규·가격인하 매물 중 가격 조건 통과분만 검증하기를 원한다, so that 불필요한 검수를 줄일 수 있다.

**Acceptance Criteria** (EARS):
- WHEN 신규 또는 가격인하 매물이 식별되면 THE SYSTEM SHALL 1차 가격 조건을 평가해 급매 후보 여부를 결정한다.
- IF 매물이 신규 또는 가격인하가 아니면 THE SYSTEM SHALL 해당 매물을 급매 후보로 전달하지 않는다.
- IF 가격 정보가 없거나 양수가 아니면 THE SYSTEM SHALL 해당 매물을 후보에서 제외하고 격리 로그에 기록한다.

**입력/데이터**: 변화 분류 결과, 기준선, 희망가 상한.

**예외/실패 모드**: 가격 검증 실패는 급매 알림을 발생시키지 않는다.

**우선순위**: Must

**의존성**: FR-RT-01, FR-VF-01

### [FR-RT-03] 중복 등록 제거

**User Story**: As a 운영자, I want 동일 매물의 중복 등록을 후보에서 제외하기를 원한다, so that 중복 알림과 노이즈를 줄일 수 있다.

**Acceptance Criteria** (EARS):
- WHEN 같은 동, 층, 면적, 가격을 가진 매물이 둘 이상 수집되면 THE SYSTEM SHALL 중복 등록으로 분류한다.
- IF 중복 등록으로 분류되면 THE SYSTEM SHALL 대표 매물 1건만 후보 평가 대상으로 남긴다.
- IF 중복 여부를 확정할 수 없으면 THE SYSTEM SHALL 중복 의심 사유를 판정 로그에 남긴다. [제안]

**입력/데이터**: 현재 수집 매물 목록.

**예외/실패 모드**: 서로 다른 링크의 동일 조건 매물은 대표 링크 선정 규칙이 필요하다. [확인 필요]

**우선순위**: Should

**의존성**: FR-RT-01

### [FR-EX-01] 스키마 검증과 격리 로그

**User Story**: As a 운영자, I want 저장 전 모든 레코드가 스키마 검증을 통과하기를 원한다, so that 잘못된 데이터가 판정과 대시보드를 오염시키지 않는다.

**Acceptance Criteria** (EARS):
- WHEN 수집 레코드가 저장 단계로 전달되면 THE SYSTEM SHALL 가격, 면적, 단지ID 필수 여부와 가격 양수 조건을 검증한다.
- IF 레코드가 스키마 검증에 실패하면 THE SYSTEM SHALL 정상 데이터 저장에서 제외하고 격리 로그에 원본 요약과 실패 사유를 기록한다.
- IF 한 사이클의 모든 레코드가 검증 실패하면 THE SYSTEM SHALL 급매 알림을 차단하고 헬스 실패로 기록한다.

**입력/데이터**: 수집 매물, 실거래 레코드.

**예외/실패 모드**: 실패 레코드는 정상 히스토리에 append하지 않는다.

**우선순위**: Must

**의존성**: FR-DC-02, FR-DC-03

### [FR-EX-02] 요청 간격 제한

**User Story**: As a 운영자, I want 외부 요청 사이에 최소 간격을 두기를 원한다, so that 외부 서비스에 과도한 부하를 주지 않는다.

**Acceptance Criteria** (EARS):
- WHILE 외부 데이터 요청이 진행되는 동안 THE SYSTEM SHALL 요청 간 최소 2초 간격을 보장한다.
- IF 설정 파일에 요청 간격이 지정되면 THE SYSTEM SHALL 기본 2초 대신 설정값을 사용하되 2초 미만으로 낮추지 않는다. [제안]
- IF 요청 간격 제어가 실패하면 THE SYSTEM SHALL 해당 실행을 실패로 처리하고 헬스 지표에 기록한다. [제안]

**입력/데이터**: 수집 대상 목록, 요청 간격 설정.

**예외/실패 모드**: 간격 제한 실패 시 추가 요청을 중단한다. [제안]

**우선순위**: Must

**의존성**: FR-DC-04

### [FR-EX-03] 재시도와 백오프

**User Story**: As a 운영자, I want 일시적 요청 실패를 재시도하기를 원한다, so that 단발성 네트워크 오류로 루프가 쉽게 실패하지 않게 할 수 있다.

**Acceptance Criteria** (EARS):
- IF 외부 요청이 실패하면 THE SYSTEM SHALL 지수 백오프로 최대 3회 재시도한다.
- IF 최종 재시도 후에도 요청이 실패하면 THE SYSTEM SHALL 실패를 헬스 지표에 반영한다.
- WHILE 재시도 중인 요청이 있으면 THE SYSTEM SHALL 요청 간격 제한을 계속 적용한다.

**입력/데이터**: 외부 요청 결과, 재시도 설정.

**예외/실패 모드**: 최종 실패한 소스는 해당 사이클에서 부분 실패로 기록한다.

**우선순위**: Should

**의존성**: FR-EX-02

### [FR-VF-01] 1차 룰 기반 급매 판정

**User Story**: As a 운영자, I want 기준선 또는 희망가 상한으로 급매 후보를 판정하기를 원한다, so that 명확한 가격 기준으로 알림 대상을 좁힐 수 있다.

**Acceptance Criteria** (EARS):
- WHEN 급매 후보가 검증 단계에 들어오면 THE SYSTEM SHALL 호가가 동일 평형 기준선 대비 설정 임계율 이하인지 평가한다.
- WHEN 워치리스트 희망가 상한이 존재하면 THE SYSTEM SHALL 호가가 희망가 상한 이하인지 평가한다.
- IF 기준선이 없으면 THE SYSTEM SHALL 희망가 상한 조건만 적용한다.
- IF 기준선 조건 또는 희망가 상한 조건 중 하나를 통과하면 THE SYSTEM SHALL 해당 매물을 급매 확정 후보로 분류한다.

**입력/데이터**: 호가, 기준선, 기본 임계율 -5%, 워치리스트 희망가 상한.

**예외/실패 모드**: 기준선과 희망가 상한이 모두 없으면 판정 불가로 탈락 처리한다. [제안]

**우선순위**: Must

**의존성**: FR-RT-02, FR-DC-03

### [FR-VF-02] 2차 LLM 검수

**User Story**: As a 운영자, I want LLM이 급매 후보의 허위매물 의심 패턴을 검수하기를 원한다, so that 오탐 알림을 줄일 수 있다.

**Acceptance Criteria** (EARS):
- WHERE 2차 LLM 검수가 활성화되면 THE SYSTEM SHALL 후보 매물의 설명, 동, 층, 가격, 기준선 대비 괴리율을 입력으로 검수 요청을 생성한다.
- WHEN LLM 응답을 받으면 THE SYSTEM SHALL 승인, 보류, 탈락 중 하나와 사유를 JSON으로 파싱한다.
- IF LLM 응답이 JSON으로 파싱되지 않으면 THE SYSTEM SHALL 해당 후보를 보류 처리하고 급매 알림에서 제외한다. [제안]
- IF 후보가 승인되지 않으면 THE SYSTEM SHALL Telegram 급매 알림을 보내지 않고 판정 사유를 기록한다.

**입력/데이터**: Anthropic API 키, 후보 매물 요약.

**예외/실패 모드**: LLM API 실패는 후보 보류와 로그 기록으로 처리한다. [제안]

**우선순위**: Could

**의존성**: FR-VF-01, FR-PS-03

### [FR-VF-03] 데이터 품질 센서

**User Story**: As a 운영자, I want 비정상적인 평균 호가 급변을 감지하기를 원한다, so that 수집 이상으로 인한 잘못된 급매 알림을 막을 수 있다.

**Acceptance Criteria** (EARS):
- WHEN 단지 평균 호가가 계산되면 THE SYSTEM SHALL 직전 사이클 평균 호가와 비교한다.
- IF 단지 평균 호가가 직전 사이클 대비 ±15%를 초과해 변동하면 THE SYSTEM SHALL 해당 사이클의 급매 알림을 전면 차단한다.
- IF 알림이 차단되면 THE SYSTEM SHALL 수집 이상 헬스 알림으로 전환하고 차단 사유를 기록한다.

**입력/데이터**: 현재 평균 호가, 직전 사이클 평균 호가.

**예외/실패 모드**: 직전 평균 호가가 없으면 급변 센서를 적용하지 않는다. [제안]

**우선순위**: Should

**의존성**: FR-PS-01, FR-ES-02

### [FR-VF-04] 제외 조건 적용

**User Story**: As a 운영자, I want 워치리스트 제외 조건에 맞는 매물을 탈락시키기를 원한다, so that 비선호 조건 매물이 알림되지 않게 할 수 있다.

**Acceptance Criteria** (EARS):
- WHEN 후보 매물이 검증 단계에 들어오면 THE SYSTEM SHALL 워치리스트의 제외 조건과 동, 층, 기타 선언 조건을 비교한다.
- IF 후보 매물이 제외 조건에 해당하면 THE SYSTEM SHALL 급매 조건 충족 여부와 무관하게 탈락 처리하고 사유를 기록한다.
- IF 제외 조건 형식이 잘못되면 THE SYSTEM SHALL 워치리스트 검증 실패로 처리하고 수집을 중단한다. [제안]

**입력/데이터**: 워치리스트 제외 조건, 후보 매물 속성.

**예외/실패 모드**: 제외 조건 판정 실패는 알림 차단 대상이다. [제안]

**우선순위**: Should

**의존성**: FR-DC-01, FR-VF-01

### [FR-PS-01] 시세 히스토리 저장

**User Story**: As a 운영자, I want 사이클마다 시세 요약을 저장하기를 원한다, so that 대시보드에서 추이를 볼 수 있다.

**Acceptance Criteria** (EARS):
- WHEN 사이클의 정상 수집과 검증이 완료되면 THE SYSTEM SHALL 단지·평형별 일자, 최저호가, 평균호가, 매물수, 최근 실거래가를 `data/history/{단지ID}.json`에 append한다.
- IF 히스토리 파일이 없으면 THE SYSTEM SHALL 새 파일을 생성한다.
- IF 저장 또는 commit이 실패하면 THE SYSTEM SHALL 실패를 헬스 상태에 기록하고 다음 사이클이 기존 상태 파일로 실행 가능하게 한다.

**입력/데이터**: 수집 매물, 실거래 캐시, 히스토리 JSON.

**예외/실패 모드**: 부분 저장으로 JSON이 깨지지 않도록 원자적 쓰기 또는 검증 후 교체가 필요하다. [제안]

**우선순위**: Must

**의존성**: FR-EX-01

### [FR-PS-02] 알림 dedup 상태 저장

**User Story**: As a 운영자, I want 이미 알림한 매물이 중복 알림되지 않기를 원한다, so that Telegram 알림 피로를 줄일 수 있다.

**Acceptance Criteria** (EARS):
- WHEN 급매 알림이 성공적으로 발송되면 THE SYSTEM SHALL 매물 ID와 알림 당시 가격을 `data/state/notified.json`에 기록한다.
- IF 동일 매물이 다음 사이클에 다시 감지되고 가격이 추가 인하되지 않았으면 THE SYSTEM SHALL Telegram 급매 알림을 보내지 않는다.
- IF 동일 매물의 가격이 추가 인하되면 THE SYSTEM SHALL 재알림 대상으로 허용하고 새 가격을 상태 파일에 기록한다.

**입력/데이터**: 매물 ID, 알림 발송 결과, `data/state/notified.json`.

**예외/실패 모드**: Telegram 발송 실패 시 dedup 상태를 성공으로 기록하지 않는다. [제안]

**우선순위**: Must

**의존성**: FR-ES-01

### [FR-PS-03] 판정 사유 로그

**User Story**: As a 운영자, I want 모든 급매 후보의 판정과 사유가 누적되기를 원한다, so that 오탐과 기준 개선을 추적할 수 있다.

**Acceptance Criteria** (EARS):
- WHEN 급매 후보 판정이 완료되면 THE SYSTEM SHALL 일시, 매물 요약, 판정, 사유, 적용 임계율을 `logs/criteria-log.md`에 append한다.
- IF 후보가 탈락 또는 보류되면 THE SYSTEM SHALL 탈락 또는 보류 사유를 기록한다.
- IF 로그 파일이 없으면 THE SYSTEM SHALL 헤더를 포함한 새 Markdown 파일을 생성한다.

**입력/데이터**: 후보 판정 결과, 적용 기준.

**예외/실패 모드**: 로그 저장 실패는 헬스 경고로 기록한다. [제안]

**우선순위**: Could

**의존성**: FR-VF-01, FR-VF-02

### [FR-PS-04] 기준 개선 제안

**User Story**: As a 운영자, I want 판정 로그가 쌓이면 기준 개선 제안을 받기를 원한다, so that 오탐과 누락을 줄이는 human-in-the-loop 개선을 할 수 있다.

**Acceptance Criteria** (EARS):
- WHEN `criteria-log.md`에 판정 사유가 30건 누적되면 THE SYSTEM SHALL 임계율과 제외 조건 개선 제안을 생성한다.
- IF 개선 제안이 생성되면 THE SYSTEM SHALL 사용자 승인 전에는 `config/watchlist.yaml` 또는 판정 기준을 자동 변경하지 않는다.
- IF 사용자가 개선 제안을 승인하면 THE SYSTEM SHALL 승인된 변경만 반영할 수 있어야 한다.

**입력/데이터**: `logs/criteria-log.md`, 사용자 승인.

**예외/실패 모드**: 승인 경로와 반영 방식은 구현 전 확정이 필요하다. [확인 필요]

**우선순위**: Could

**의존성**: FR-PS-03

### [FR-ES-01] 급매 Telegram 알림

**User Story**: As a 운영자, I want 급매 확정 매물을 Telegram으로 받기를 원한다, so that 발견 직후 확인할 수 있다.

**Acceptance Criteria** (EARS):
- WHEN 급매 매물이 최종 승인되면 THE SYSTEM SHALL Telegram Bot API `sendMessage`로 알림을 발송한다.
- WHEN 급매 알림을 발송하면 THE SYSTEM SHALL 단지명, 평형, 동/층, 호가, 기준선 대비 괴리율, 최근 실거래가, 매물 링크를 포함한다.
- IF Telegram API 호출이 실패하면 THE SYSTEM SHALL 발송 실패를 헬스 지표에 기록하고 dedup 성공 상태를 기록하지 않는다.

**입력/데이터**: Telegram Bot Token, chat_id, 승인 매물.

**예외/실패 모드**: 토큰과 chat_id는 GitHub Secrets에서만 읽는다.

**우선순위**: Must

**의존성**: FR-VF-01, FR-PS-02

### [FR-ES-02] 루프 헬스 알림

**User Story**: As a 운영자, I want 루프 고장과 수집 이상을 급매 알림과 구분해 받기를 원한다, so that 시스템 문제를 즉시 인지할 수 있다.

**Acceptance Criteria** (EARS):
- IF 수집이 3회 연속 실패하면 THE SYSTEM SHALL Telegram으로 루프 헬스 알림을 발송한다.
- IF 수집 결과가 0건이면 THE SYSTEM SHALL 급매 알림과 구분되는 헬스 알림을 발송한다.
- WHEN 헬스 알림을 발송하면 THE SYSTEM SHALL 실패 소스, 연속 실패 횟수, 마지막 성공 시각을 포함한다. [제안]

**입력/데이터**: `data/state/health.json`, 수집 결과.

**예외/실패 모드**: 헬스 알림 실패는 GitHub Actions 로그에 남긴다. [제안]

**우선순위**: Should

**의존성**: FR-EX-03, FR-VF-03

### [FR-ES-03] 사이클당 알림 상한

**User Story**: As a 운영자, I want 한 사이클의 급매 알림 수를 제한하기를 원한다, so that 알림 피로를 줄일 수 있다.

**Acceptance Criteria** (EARS):
- WHEN 한 사이클에서 급매 확정 매물이 5건을 초과하면 THE SYSTEM SHALL Telegram 알림을 최대 5건만 발송한다.
- IF 급매 확정 매물이 5건을 초과하면 THE SYSTEM SHALL 초과분을 대시보드 급매 피드에만 노출한다.
- WHEN 알림 상한이 적용되면 THE SYSTEM SHALL 헬스 또는 실행 요약에 초과 건수를 기록한다. [제안]

**입력/데이터**: 급매 확정 매물 목록.

**예외/실패 모드**: 5건 선정 정렬 기준은 확정이 필요하다. [확인 필요]

**우선순위**: Should

**의존성**: FR-ES-01, FR-UI-02

### [FR-UI-01] 시세 추이 차트

**User Story**: As a 운영자, I want 단지·평형별 시세 추이를 차트로 보기를 원한다, so that 최근 가격 흐름을 확인할 수 있다.

**Acceptance Criteria** (EARS):
- WHEN 대시보드가 열리면 THE SYSTEM SHALL 단지·평형별 최저호가, 평균호가, 실거래가 추이 차트를 표시한다.
- IF 히스토리 데이터가 없으면 THE SYSTEM SHALL 차트 대신 데이터 없음 상태를 표시한다. [제안]
- IF 일부 날짜의 실거래가가 없으면 THE SYSTEM SHALL 호가 추이를 표시하고 실거래가 누락을 구분한다. [제안]

**입력/데이터**: `data/history/{단지ID}.json`.

**예외/실패 모드**: JSON fetch 실패 시 대시보드에 오류 상태를 표시한다. [제안]

**우선순위**: Should

**의존성**: FR-PS-01, FR-UI-04

### [FR-UI-02] 최근 급매 피드

**User Story**: As a 운영자, I want 최근 급매와 판정 사유를 시간 역순으로 보기를 원한다, so that 알림 밖의 후보도 검토할 수 있다.

**Acceptance Criteria** (EARS):
- WHEN 대시보드가 열리면 THE SYSTEM SHALL 최근 급매 피드를 시간 역순으로 표시한다.
- WHEN 피드 항목을 표시하면 THE SYSTEM SHALL 판정 사유를 함께 표시한다.
- IF 급매 피드가 비어 있으면 THE SYSTEM SHALL 빈 상태를 표시한다. [제안]

**입력/데이터**: 판정 로그 또는 대시보드용 급매 피드 JSON.

**예외/실패 모드**: Markdown 로그를 직접 fetch할지 JSON으로 변환할지 확정이 필요하다. [확인 필요]

**우선순위**: Should

**의존성**: FR-PS-03, FR-UI-04

### [FR-UI-03] 마지막 실행 상태 표시

**User Story**: As a 운영자, I want 마지막 루프 실행 시각과 상태를 보기를 원한다, so that 감시 루프가 살아 있는지 확인할 수 있다.

**Acceptance Criteria** (EARS):
- WHEN 대시보드가 열리면 THE SYSTEM SHALL 마지막 루프 실행 시각과 성공/실패 상태 배지를 표시한다.
- IF 마지막 실행이 실패이면 THE SYSTEM SHALL 실패 요약을 표시한다.
- IF 헬스 데이터가 없으면 THE SYSTEM SHALL 상태 미확인 배지를 표시한다. [제안]

**입력/데이터**: `data/state/health.json`.

**예외/실패 모드**: 상태 파일 fetch 실패 시 대시보드 오류 상태를 표시한다. [제안]

**우선순위**: Should

**의존성**: FR-ES-02, FR-UI-04

### [FR-UI-04] 정적 JSON 기반 렌더링

**User Story**: As a 운영자, I want 대시보드가 서버 없이 정적 JSON을 fetch해 렌더링되기를 원한다, so that GitHub Pages만으로 운영할 수 있다.

**Acceptance Criteria** (EARS):
- WHEN GitHub Pages에서 대시보드가 제공되면 THE SYSTEM SHALL 별도 서버 없이 정적 JSON 파일을 fetch해 화면을 렌더링한다.
- IF 빌드 단계가 실행되지 않아도 THE SYSTEM SHALL 저장소에 commit된 정적 파일만으로 대시보드를 표시한다.
- IF JSON fetch가 실패하면 THE SYSTEM SHALL 해당 섹션에 오류 상태를 표시하고 나머지 섹션 렌더링을 계속한다. [제안]

**입력/데이터**: 정적 HTML/CSS/JS, `data/**/*.json`.

**예외/실패 모드**: CORS 또는 Pages 경로 문제는 대시보드 오류 상태로 확인 가능해야 한다. [제안]

**우선순위**: Must

**의존성**: FR-PS-01, FR-PS-02

## 4. 비기능 요구사항

### [NFR-01] 비용과 실행 시간

**Requirement**: THE SYSTEM SHALL GitHub Actions 무료 한도 월 2,000분 내 운영을 목표로 하며, 1사이클 실행 시간 목표를 5분 이하로 관리하고, LLM 호출은 급매 후보에 한정해 사이클당 평균 10회 이하로 제한한다.

**근거**: 사용자 입력의 비용 제약.

### [NFR-02] 루프 실패 격리

**Requirement**: IF 루프 1사이클이 실패하면 THE SYSTEM SHALL 다음 사이클이 직전 정상 상태 파일을 기준으로 실행될 수 있게 상태 파일 손상을 방지한다.

**근거**: 사용자 입력의 신뢰성 제약.

### [NFR-03] 준법과 수집 매너

**Requirement**: WHILE 외부 매물 정보를 수집하는 동안 THE SYSTEM SHALL 워치리스트 단지 한정, 1일 2~3회 실행, 요청 간격 2초 이상, robots.txt 및 서비스 약관 변경 시 수집 방식 재검토 원칙을 따른다.

**근거**: 사용자 입력의 준법/매너 제약.

### [NFR-04] 비밀정보와 민감정보 보호

**Requirement**: THE SYSTEM SHALL Telegram Bot Token, API Key를 GitHub Secrets에서만 읽고 코드, JSON 상태, Markdown 로그, GitHub Actions 로그에 노출하지 않는다.

**근거**: 사용자 입력의 보안 제약.

### [NFR-05] 관측성

**Requirement**: WHEN 루프 1사이클이 종료되면 THE SYSTEM SHALL 수집 건수, 후보 수, 알림 수, 소요 시간을 실행 요약으로 기록한다.

**근거**: 사용자 입력의 관측성 제약.

### [NFR-06] 모듈 분리

**Requirement**: THE SYSTEM SHALL 수집기, 판정기, 알림기를 독립 모듈로 분리하여 데이터 소스 교체 시 판정 및 알림 코드 수정을 요구하지 않도록 한다.

**근거**: 사용자 입력의 유지보수성 제약.

### [NFR-07] 오탐 측정

**Requirement**: THE SYSTEM SHALL 판정 사유 로그를 통해 허위매물 알림 비율을 추적할 수 있게 하고, 2차 검수 도입 전후의 오탐 변화를 비교 가능하게 한다.

**근거**: 사용자 입력의 정확성 제약.

## 5. 데이터 요구사항

| 데이터 | 형식/위치 | 보존 | 관련 요구사항 |
|---|---|---|---|
| 워치리스트 | `config/watchlist.yaml` | 영구 (사용자 관리) | FR-DC-01 |
| 매물 스냅샷 | `data/listings/{단지ID}.json` | 최근 30사이클 | FR-RT-01 |
| 시세 히스토리 | `data/history/{단지ID}.json` | 영구 | FR-PS-01 |
| 실거래 캐시 | `data/trades/{단지ID}.json` | 6개월 롤링 | FR-DC-03 |
| 알림 dedup 상태 | `data/state/notified.json` | 영구 | FR-PS-02 |
| 판정 사유 로그 | `logs/criteria-log.md` | 영구 | FR-PS-03 |
| 실행 헬스 | `data/state/health.json` | 최근 10사이클 | FR-ES-02 |

## 6. 외부 인터페이스

| 인터페이스 | 방향 | 내용 | 관련 요구사항 |
|---|---|---|---|
| 국토교통부 실거래가 API | IN | 단지·기간별 매매 실거래 조회 | FR-DC-03 |
| 부동산 포털 매물 | IN | 워치리스트 단지 매물 호가 | FR-DC-02, FR-DC-04 |
| Anthropic API | IN/OUT | 급매 후보 2차 검수 JSON 응답 | FR-VF-02 |
| Telegram Bot API | OUT | `sendMessage` 급매 알림, 헬스 알림 | FR-ES-01, FR-ES-02 |
| GitHub Pages | OUT | 정적 대시보드 배포 | FR-UI-01~04 |

## 7. 마일스톤 및 수용 기준

### Phase 1 - 골격 (Must)

대상: FR-TR-01, FR-TR-02, FR-DC-01, FR-DC-02, FR-DC-04, FR-RT-01, FR-RT-02, FR-EX-01, FR-EX-02, FR-VF-01, FR-PS-01, FR-PS-02, FR-ES-01, FR-UI-04

**Acceptance Criteria**:
- WHEN 워치리스트에 단지 1개가 등록되고 희망가 이하 매물이 등장하면 THE SYSTEM SHALL 사람 개입 없이 Telegram 급매 알림을 발송한다.
- WHEN 동일 매물이 다음 사이클에 다시 감지되면 THE SYSTEM SHALL 가격이 추가 인하되지 않은 한 재알림하지 않는다.
- IF 매물 수집 레코드가 스키마 검증에 실패하면 THE SYSTEM SHALL 해당 레코드를 알림과 히스토리 저장에서 제외한다.

### Phase 2 - 신뢰도 (Should)

대상: FR-DC-03, FR-RT-03, FR-EX-03, FR-VF-03, FR-VF-04, FR-ES-02, FR-ES-03, FR-UI-01, FR-UI-02, FR-UI-03, FR-TR-03

**Acceptance Criteria**:
- WHEN 최근 실거래가 기준선이 존재하면 THE SYSTEM SHALL 기준선 대비 상대 판정을 수행한다.
- IF 수집기를 고의로 실패시키면 THE SYSTEM SHALL 급매 알림 대신 헬스 알림을 발송한다.
- WHEN 최근 30일 히스토리가 존재하면 THE SYSTEM SHALL 대시보드에서 시세 추이를 표시한다.

### Phase 3 - 자가 개선 (Could)

대상: FR-VF-02, FR-PS-03, FR-PS-04

**Acceptance Criteria**:
- WHEN 후보가 승인, 보류, 탈락으로 판정되면 THE SYSTEM SHALL 판정 사유를 로그에 누적한다.
- WHEN 판정 사유가 30건 누적되면 THE SYSTEM SHALL 임계율 또는 제외 조건 개선 제안을 생성한다.
- WHEN LLM 검수가 도입되면 THE SYSTEM SHALL 도입 전후 오탐 건수를 로그 기반으로 비교할 수 있게 한다.

## 8. 리스크 및 대응

| 리스크 | 영향 | 대응 | 관련 요구사항 |
|---|---|---|---|
| 포털 측 수집 차단 또는 구조 변경 | 매물 수집 중단 | 수집기 모듈 독립화, 헬스 알림, 대체 소스 전환 | NFR-06, FR-ES-02 |
| 실거래 데이터 희소 단지 | 기준선 산출 불가 | 희망가 상한 단독 판정 폴백 | FR-VF-01 |
| 허위매물로 인한 알림 피로 | 알림 무시 | 2차 LLM 검수, 사이클당 알림 상한 | FR-VF-02, FR-ES-03 |
| Actions 무료 한도 초과 | 루프 정지 | 사이클 시간 예산 모니터링 | NFR-01, NFR-05 |
| public 저장소의 개인 정보 노출 | 프라이버시 침해 | Secrets 관리, 민감 설정 분리 | NFR-04 |

## 9. 의존성 및 제약

### 의존성 그래프

- FR-TR-01 -> FR-DC-01
- FR-TR-02 -> FR-DC-01
- FR-TR-03 -> FR-PS-01, FR-PS-02
- FR-DC-01 -> FR-DC-02, FR-DC-03, FR-DC-04, FR-VF-04
- FR-DC-02 -> FR-EX-01 -> FR-RT-01
- FR-DC-03 -> FR-VF-01
- FR-RT-01 -> FR-RT-02 -> FR-VF-01
- FR-RT-01 -> FR-RT-03
- FR-EX-02 -> FR-EX-03
- FR-VF-01 -> FR-VF-02, FR-PS-03, FR-ES-01
- FR-VF-03 -> FR-ES-02
- FR-PS-01 -> FR-UI-01, FR-UI-04
- FR-PS-02 -> FR-ES-01
- FR-PS-03 -> FR-PS-04, FR-UI-02
- FR-ES-02 -> FR-UI-03

### 제약사항

- 실행 환경은 GitHub Actions `ubuntu-latest`이다.
- 호스팅은 GitHub Pages 정적 파일만 사용한다.
- 별도 DB 없이 Git 저장소 내 JSON/Markdown 파일을 상태 저장소로 사용한다.
- 알림 채널은 Telegram Bot API이다.
- 외부 데이터는 국토교통부 실거래가 공개 API와 부동산 포털 매물 정보이다.
- LLM 2차 검수는 Anthropic API를 사용하며 호출을 최소화한다.
- 매물 수집은 워치리스트 단지로만 제한한다.

## 10. 확인 필요 및 제안 사항

| ID | 유형 | 항목 | 이유 |
|---|---|---|---|
| FR-RT-01 | [제안] | 매물 ID가 없을 때 단지ID, 동, 층, 면적, 가격, 링크 조합 키 사용 | 포털별 매물 ID 제공 여부가 다를 수 있음 |
| FR-RT-03 | [확인 필요] | 중복 매물 대표 링크 선정 규칙 | 동일 조건의 여러 링크 중 어떤 링크를 알림할지 결정 필요 |
| FR-EX-02 | [제안] | 설정 요청 간격은 2초 미만으로 낮출 수 없음 | NFR-03의 수집 매너 제약 보존 |
| FR-VF-01 | [제안] | 기준선과 희망가 상한이 모두 없으면 판정 불가 탈락 | 알림 기준이 없는 상태의 오탐 방지 |
| FR-VF-02 | [제안] | LLM 실패 또는 JSON 파싱 실패 시 후보 보류 | 실패한 검수를 승인으로 처리하지 않기 위함 |
| FR-VF-03 | [제안] | 직전 평균 호가가 없으면 급변 센서 미적용 | 최초 실행에서 비교 기준이 없음 |
| FR-PS-01 | [제안] | 히스토리 JSON은 원자적 쓰기 또는 검증 후 교체 | 깨진 JSON commit 방지 |
| FR-PS-04 | [확인 필요] | 개선 제안 승인 경로와 반영 방식 | GitHub Issue, PR, 수동 커밋 중 선택 필요 |
| FR-ES-03 | [확인 필요] | 5건 초과 시 Telegram 발송 대상 정렬 기준 | 괴리율, 가격, 등록시각 등 우선순위 결정 필요 |
| FR-UI-02 | [확인 필요] | 급매 피드 데이터 소스 형식 | Markdown 로그 직접 fetch 또는 별도 JSON 생성 중 선택 필요 |

## 부록 A. Loop Engineering 구성 요소 매핑

| 구성 요소 | 핵심 질문 | 해당 요구사항 |
|---|---|---|
| Trigger | 무엇이 루프를 깨우는가 | FR-TR-01~03 |
| Discover | 할 일을 어떻게 발견하는가 | FR-DC-01~04 |
| Route | 누가/무엇이 맡는가 | FR-RT-01~03 |
| Execute | 어떤 하네스 안에서 도는가 | FR-EX-01~03 |
| Verify | 끝났다를 누가 판정하는가 | FR-VF-01~04 |
| Persist | 무엇을 누적해 다음 사이클을 개선하는가 | FR-PS-01~04 |
| Escalate | 언제 사람을 부르는가 | FR-ES-01~03 |
