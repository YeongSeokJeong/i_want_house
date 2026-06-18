# Requirement Handoff

## 1. Request Summary
- Original request: Improve listing collection/UI so each listing can be distinguished by area/pyung, make the dashboard easier to scan, and remove collection-history information that is not useful. Confirm improvements through an interview.
- Interpreted objective: Clarify a dashboard and listing-data improvement scope before source-code implementation.
- In-scope: Area/pyung visibility for individual listings, listing-level browsing/filtering, dashboard information hierarchy, removal or demotion of collection-history/source-diagnostic UI.
- Out-of-scope: Source-code implementation until the interview resolves decision-critical ambiguity and the large-task-orchestrator lifecycle is started.

## 2. Functional Requirements
- FR-1: The dashboard shall expose individual listing records in a way that lets the user distinguish listings by complex, area/pyung, price, building/floor, and link.
- FR-2: The dashboard shall present current listing state more prominently than collection mechanics or run-history details.
- FR-3: The dashboard shall remove, hide, or demote collection/run-history information that does not support investment screening.

## 3. Non-Functional Requirements
- Performance: The static dashboard should continue to load committed JSON state without a build step.
- Reliability: Existing JSON state must remain backward compatible or have a tested fallback for missing area fields.
- Security: No Telegram sends, secrets, or operator-specific values are involved in this clarification step.
- Maintainability: UI changes should reuse existing static dashboard structure unless the interview confirms a broader redesign.

## 4. Constraints and Dependencies
- Architecture/layer constraints: Source-code changes must use the repository large-task-orchestrator lifecycle.
- API/DTO constraints: Current listing JSON already includes `area_m2` for some records, while watchlist targets include configured `area_m2`; the desired display unit and matching behavior are unresolved.
- Tooling/runtime constraints: Dashboard is static HTML/CSS/JS backed by committed JSON files.
- External dependencies: Live listing source may not always provide complete area, building, floor, or title metadata.

## 5. Assumptions
- A-1: The user wants Korean user-facing UI copy.
- A-2: "평수" means user-readable Korean pyung display derived from `area_m2`, unless source-provided supply/exclusive area distinctions are required.
- A-3: "데이터를 어떻게 수집했는가에 대한 이력" refers primarily to recent run history and collection diagnostics panels, not price trend history.

## 6. Open Questions
- Q-1: Should pyung be shown as converted Korean pyung only, or as both square meters and pyung?
- Q-2: Should the listing view show all collected listings, only candidates/near-urgent listings, or the latest listings for the selected complex?
- Q-3: Should collection/run history and source diagnostics be fully removed from the dashboard, hidden behind a troubleshooting view, or kept only in JSON/docs?
- Q-4: What should be the primary first-screen workflow: compare complexes, inspect individual listings, or tune alert criteria?
- Q-5: What specific UI readability issue matters most: visual density, color/contrast, terminology, table layout, or mobile layout?

## 7. Acceptance Criteria
- AC-1: Pending interview answer.
- AC-2: Pending interview answer.
- AC-3: Pending interview answer.

## 8. Validation Plan
- Unit tests: Pending implementation planning; likely static dashboard tests for required labels/elements.
- Integration tests: Pending implementation planning; likely committed JSON render smoke check.
- Manual checks: Verify the dashboard at desktop and mobile widths with current sample state.

## 9. Risks and Mitigations
- Risk: Source listings and watchlist target areas can differ, causing misleading pyung displays.
- Mitigation: Clarify whether UI should display source listing area, target watch area, or both.

## 10. Next Agent Brief
- Recommended next agent: Planner after interview completion, then large-task-orchestrator before implementation.
- Why: Requirements affect source code and dashboard behavior, so implementation must be lifecycle-compliant.
- Input package for next agent: This handoff, user interview answers, current `index.html`, `assets/dashboard.js`, `assets/dashboard.css`, `data/listings/*.json`, and `config/watchlist.yaml`.
