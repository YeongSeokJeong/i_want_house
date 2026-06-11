# architecture.md Schema

```markdown
# Architecture Review

## Task Context
- Task Name: <user-facing task name>
- Task ID: <kebab-case id>
- Last Updated: <date>

## System Context
- Current Stack: <languages, framework, runtime>
- Existing Patterns: <architecture style, layering>
- Integration Points: <APIs, DBs, queues, external services>

## Feature Decomposition Map
| Feature ID | Feature | Description | Depends On | Complexity | Risk |
|------------|---------|-------------|------------|------------|------|
| F-001 | <name> | <desc> | None | Medium | Low |

## Dependency Map
- <component A> -> <component B> (reason)
- <feature N> depends on <feature M> (reason)

## Technical Decisions
- Decision: <what>
  - Rationale: <why>
  - Trade-offs: <cost/benefit>

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| <risk> | High | <mitigation> | <owner> |
```
