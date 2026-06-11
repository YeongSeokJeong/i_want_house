# Wiki Routing Examples

## Example 1
User asks: "auth 도메인 문서 하나 만들고 로그인 흐름 정리해줘"

Recommended output:
- `docs/wiki/domains/auth/overview.md`
- `docs/wiki/domains/auth/login-flow.md`
- update `docs/wiki/index.md`

Why:
- `auth` is a business/domain bucket
- `login-flow` is a subtopic page inside that domain
- new content must be discoverable from the index

## Example 2
User asks: "토큰 재발급 정책을 모두가 따르는 규칙으로 남겨줘"

Recommended output:
- `docs/wiki/rules/common/token-refresh-policy.md`
- optionally add related links from `domains/auth/overview.md` or `domains/auth/token-refresh.md`
- update `docs/wiki/index.md` if the rules section is no longer empty

Why:
- this is a shared rule/policy, not just one domain explanation

## Example 3
User asks: "세션 만료 시간을 30분으로 정한 이유를 남겨줘"

Recommended output:
- `docs/wiki/decisions/session-timeout-30m.md`
- update `docs/wiki/decisions.md`
- usually update `docs/wiki/index.md`
- link from related auth domain pages

Why:
- this is a durable human decision with rationale worth revisiting

## Example 4
User asks: "배포 전에 확인하는 절차를 위키에 적어줘"

Recommended output:
- `docs/wiki/rules/workflow/pre-release-checklist.md`
- update `docs/wiki/index.md` if needed

Why:
- repeatable operational sequence belongs in workflow rules

## Example 5
User asks: "Agent가 이번에 문서 구조를 이렇게 나눴다는 메모를 남겨줘"

Recommended output:
- add `## Agent note` to the closest relevant page
- do not create a standalone document under `decisions/`

Why:
- local schema treats agent decisions as lower-priority contextual notes

## Example 6
User asks: "위키 구조 자체를 바꾸자"

Recommended output:
- update `docs/wiki/SCHEMA.md`
- update `docs/wiki/init.md`
- update `docs/wiki/index.md`
- update any affected folder pages

Why:
- structure changes must update the navigation and rule documents together

## Example 7
User asks: "로그인 정책을 설명하고, 세션 만료 시간을 30분으로 정한 이유도 남겨줘"

Recommended output:
- `docs/wiki/domains/auth/overview.md` if the domain does not exist yet
- `docs/wiki/domains/auth/session-policy.md`
- `docs/wiki/decisions/session-timeout-30m.md`
- update `docs/wiki/decisions.md`
- update `docs/wiki/index.md`
- link the domain page and decision document to each other

Why:
- the policy explanation is domain knowledge
- the 30-minute timeout rationale is a durable human decision
- mixing both into one page would make the decision harder to find and revisit
