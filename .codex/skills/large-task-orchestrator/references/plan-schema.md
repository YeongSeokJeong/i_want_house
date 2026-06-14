# plan.md Schema

```markdown
# Task Plan

## Task Metadata
- Task Name: <user-facing task name>
- Task ID: <kebab-case id>
- Task Branch: <task branch name>
- Task Worktree: <task worktree path or current checkout>
- Plan Version: v1
- Last Updated: <date>

## Planning Assumptions
- <assumption 1>
- <assumption 2>

## Related Backlog Items
| Backlog ID | Route | Status | Relationship |
|------------|-------|--------|--------------|
| BL-YYYYMMDD-001 | source-code | Todo | Parent task item for this orchestration |

## Feature Catalog
| Feature ID | Feature Name | Goal | Depends On | Complexity | Owner |
|------------|--------------|------|------------|------------|-------|
| F-001 | <name> | <goal> | None | Medium | <owner> |
| F-002 | <name> | <goal> | F-001 | High | <owner> |

## Feature Detail
### F-001 <feature name>
- Scope:
  - <scope item>
- Acceptance Criteria:
  - [ ] <criteria 1>
  - [ ] <criteria 2>
- Out of Scope:
  - <item or None>

### F-002 <feature name>
- Scope:
  - <scope item>
- Acceptance Criteria:
  - [ ] <criteria 1>
  - [ ] <criteria 2>
- Out of Scope:
  - <item or None>

## Execution Order
1. F-001
2. F-002

## Revision Log
| Version | Date | Changed Feature IDs | Changed Backlog IDs | Why Revised | Author |
|---------|------|---------------------|---------------------|-------------|--------|
| v1 | <date> | F-001,F-002 | BL-YYYYMMDD-001 | Initial planning baseline | <name> |
```
