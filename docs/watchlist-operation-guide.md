# Watchlist 운영 가이드

이 문서는 `config/watchlist.yaml`에 감시 단지를 추가하거나 수정할 때 확인할 절차를 정리한다. 실제 토큰, chat ID, API key, 개인별 경로는 이 문서나 저장소에 기록하지 않는다.

## 기본 원칙
- `complex_id`는 저장소 안에서 단지를 식별하는 안정적인 내부 ID다.
- 호갱노노 수집을 사용할 때 내부 `complex_id`와 호갱노노 아파트 해시는 `JEONSELOOP_HOGANGNONO_APT_HASH_MAP`으로 연결한다.
- 목표가와 제외 키워드 변경은 다음 실행부터 후보 판정에 바로 영향을 준다.
- 변경 후에는 fixture 기반 테스트와 dry-run을 먼저 실행한다.

## 단지 추가 절차
1. `config/watchlist.yaml`의 `complexes` 목록에 새 항목을 추가한다.
2. 필수 필드를 채운다.
   - `complex_id`: 영문/숫자/하이픈 중심의 내부 ID
   - `name`: 대시보드와 알림에 표시할 단지명
   - `area_m2`: 감시할 전용면적
   - `target_price_krw`: 목표 매수가 또는 관심 상한
   - `urgent_discount_ratio`: 실거래 기준선 대비 급매 할인율
3. 필요한 제외 키워드를 `exclude`에 추가한다.
4. 호갱노노 운영이면 로컬 `.env` 또는 GitHub Actions Variables/Secrets의 `JEONSELOOP_HOGANGNONO_APT_HASH_MAP`에 새 매핑을 추가한다.
5. 검증 명령을 실행한다.

## 예시

```yaml
complexes:
  - complex_id: sample-apt
    name: 샘플아파트
    area_m2: 84.9
    target_price_krw: 850000000
    urgent_discount_ratio: 0.12
    exclude:
      - 지하
      - 단기
```

호갱노노 매핑 예시:

```text
JEONSELOOP_HOGANGNONO_APT_HASH_MAP={"sample-apt":"E152"}
```

여러 단지는 하나의 JSON 객체에 모두 넣는다.

```text
JEONSELOOP_HOGANGNONO_APT_HASH_MAP={"sample-apt":"E152","second-apt":"B11b"}
```

## 목표가 수정 절차
1. `target_price_krw`를 수정한다.
2. `urgent_discount_ratio`가 함께 바뀌어야 하는지 확인한다.
3. 변경 이유를 커밋 메시지나 별도 운영 메모에 남긴다.
4. dry-run으로 후보 판정과 대시보드 상태를 확인한다.

## 제외 키워드 수정 절차
1. 실제 알림에서 제외하고 싶은 단어가 매물 제목, 설명, 동, 층, 링크에 나타나는지 확인한다.
2. `exclude`에 최소한의 키워드만 추가한다.
3. 너무 넓은 키워드는 정상 매물을 막을 수 있으므로 피한다.
4. fixture 또는 최근 수집 데이터를 기준으로 테스트한다.

## 검증 명령

```powershell
python -m unittest discover -s tests
powershell -File scripts/run-loop.ps1 -DryRun -Fixture tests\fixtures\listings.json
```

## 실패 시 확인할 것
- `collector-diagnostics.json`에 `missing_mapping_targets`가 있으면 `JEONSELOOP_HOGANGNONO_APT_HASH_MAP`에 해당 `complex_id`의 해시를 추가한다.
- `watchlist_invalid`가 기록되면 필수 필드 누락, 중복 `complex_id`, 숫자 필드 형식을 확인한다.
- `listing_source_unconfigured`가 기록되면 `JEONSELOOP_LISTING_SOURCE_KIND` 또는 live source URL 설정을 확인한다.
