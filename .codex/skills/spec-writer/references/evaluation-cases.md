# Evaluation Cases

Use these prompts when validating updates to `spec-writer`.

## Test Prompts

1. Chaining input:
   - Provide a `requirements-analyzer` style feature list with a MoSCoW priority table and ask: "이걸 명세서로 만들어줘."
   - Expected: priorities preserved, `FR-XXX` IDs assigned, dependency graph added.
2. Raw idea:
   - "사내 회의실 예약 시스템 만들고 싶어. 명세서 써줘."
   - Expected: feature split first, then spec; active discovery of duplicate booking, no-show, cancellation, permissions, and invalid time ranges.
3. Quick mode:
   - "간단하게 todo 앱 스펙 빠르게 써줘."
   - Expected: no questions, complete file output, assumptions listed.
4. Vague language:
   - Include "검색은 빨라야 하고 UI는 직관적이어야 해."
   - Expected: vague phrases converted into measurable criteria or tagged `[확인 필요]`; original vague terms do not remain as AC requirements.
5. Revision:
   - Provide an existing spec and ask: "FR-003에 게스트 사용자 케이스 추가해줘."
   - Expected: only FR-003 and dependent sections updated; existing IDs preserved.

## Assertions

- Every functional requirement has an `FR-XXX` ID.
- Every non-functional requirement has an `NFR-XXX` ID.
- Every acceptance criterion includes `SHALL`.
- Each feature has at least one failure-mode AC.
- Most feature specs with meaningful risk have at least two edge/failure ACs.
- MoSCoW priority information from input is preserved.
- AC text does not contain unresolved vague terms such as `user-friendly`, `빠르게`, or `직관적` unless tagged `[확인 필요]`.
