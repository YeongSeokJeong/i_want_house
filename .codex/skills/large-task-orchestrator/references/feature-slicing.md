# Feature Slicing Guide

Use this guide during `/large-task-orchestrator start <task-name>`, `/large-task-orchestrator next <task-name>`, and `/large-task-orchestrator revise <task-name>`.

## Functional Unit Rules

Break work into features that each:

1. Deliver a user-visible or operator-visible outcome.
2. Have clear acceptance criteria and a test boundary.
3. Minimize dependencies on unfinished features.
4. Can be implemented and reviewed in one session when possible.
5. Have a stable feature ID (for example `F-001`, `F-002`) that is reused across all continuity docs.

## Acceptance Criteria Quality

A criterion is good when it is:

- Observable (expected behavior/output is explicit)
- Testable (can be validated by automated or repeatable manual checks)
- Bounded (scope and edge conditions are clear)
- Binary (pass/fail, not subjective)

## Complexity Scale (for Next Session Briefing)

- **Low**: small localized change, low cross-module impact.
- **Medium**: multi-file or multi-layer change with manageable coupling.
- **High**: broad cross-cutting change, migrations, or high operational risk.

## Sequencing Policy

- Prioritize foundational features first (shared contracts, data model, base services).
- Never start a dependent feature before prerequisites are complete and verified.
- Keep the critical path short; defer optional enhancements to later features.
