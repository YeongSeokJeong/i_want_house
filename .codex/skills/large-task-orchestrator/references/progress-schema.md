# progress.md Schema

```markdown
# Task Progress

## Overview
- Task Name: <user-facing task name>
- Task ID: <kebab-case id>
- Task Branch: <task branch name>
- Status: IN_PROGRESS | COMPLETED
- Plan Version: <current plan version>
- Current Session: <N>
- Last Updated: <date>

## Related Backlog Items
| Backlog ID | Route | Status | Artifact | Result |
|------------|-------|--------|----------|--------|
| BL-YYYYMMDD-001 | source-code | Doing | <path or -> | <summary or -> |

## Feature Implementation Status
| Feature ID | Feature Name | Status | Last Session | Commit | Updated |
|------------|--------------|--------|--------------|--------|---------|
| F-001 | <name> | TODO \| IN_PROGRESS \| DONE \| BLOCKED | <N> | <hash or -> | <date> |
| F-002 | <name> | TODO \| IN_PROGRESS \| DONE \| BLOCKED | <N> | <hash or -> | <date> |

## Session Log
| Session | Feature ID | Feature | Status | Commit | Date |
|---------|------------|---------|--------|--------|------|
| 1 | PLAN | Planning | Done | - | <date> |
| 2 | F-001 | <name> | Done | abc123 | <date> |

## Next Session Instructions
- Next Feature ID: <feature id>
- Next Feature: <feature name>
- Description: <what to do>
- Key Files: <file list>
- Dependencies Ready: <yes/no + notes>
- Known Issues: <issues or "None">
```
