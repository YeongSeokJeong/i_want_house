# decision.md Schema

```markdown
# Session Decisions

## Task Context
- Task Name: <user-facing task name>
- Task ID: <kebab-case id>

## Decision Log
| Session | Feature ID | Feature | Decision | Rationale | Impact | Date |
|---------|------------|---------|----------|-----------|--------|------|
| 1 | PLAN | Planning | Split into 4 features | Minimize cross-feature coupling | Enables parallel-safe sequencing | <date> |

## Session <N>
- Feature ID: <feature id>
- Feature: <feature name>
- Decisions:
  - <decision 1>
  - <decision 2>
- Alternatives Considered:
  - <alternative>: <why not chosen>
- Risks Introduced:
  - <risk or "None">
- Follow-up Notes:
  - <note or "None">
```
