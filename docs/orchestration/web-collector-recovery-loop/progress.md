# Task Progress

## Overview
- Task Name: Naver Real Estate Web Collector Recovery Loop
- Task ID: web-collector-recovery-loop
- Task Branch: task/web-collector-recovery-loop
- Task Worktree: D:\git\i_want_house
- Status: IN_PROGRESS
- Plan Version: v1
- Current Session: 1
- Last Updated: 2026-06-14

## Related Backlog Items
| Backlog ID | Route | Status | Artifact | Result |
|------------|-------|--------|----------|--------|
| BL-20260614-003 | source-code | Doing | `docs/orchestration/web-collector-recovery-loop/` | Planning initialized; implementation pending |

## Feature Implementation Status
| Feature ID | Feature Name | Status | Last Session | Commit | Updated |
|------------|--------------|--------|--------------|--------|---------|
| F-001 | Collector source contract | DONE | 1 | - | 2026-06-14 |
| F-002 | Naver listing adapter | TODO | 1 | - | 2026-06-14 |
| F-003 | Failure diagnostics | TODO | 1 | - | 2026-06-14 |
| F-004 | Actions recovery workflow | TODO | 1 | - | 2026-06-14 |
| F-005 | Operator documentation | TODO | 1 | - | 2026-06-14 |

## Session Log
| Session | Feature ID | Feature | Status | Commit | Date |
|---------|------------|---------|--------|--------|------|
| 1 | PLAN | Planning | Done | - | 2026-06-14 |
| 1 | F-001 | Collector source contract | Done | - | 2026-06-14 |

## Next Session Instructions
- Next Feature ID: F-002
- Next Feature: Naver listing adapter
- Description: Implement fixture-backed Naver listing fetch/normalization using the source mode contract from F-001.
- Key Files: `src/jeonseloop/sources.py`, `tests/test_reliability.py`, `tests/fixtures/`
- Dependencies Ready: yes
- Known Issues: Naver endpoint shape is unstable and must be treated as best-effort.
