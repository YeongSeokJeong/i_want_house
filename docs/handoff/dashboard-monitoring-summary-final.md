# Handoff: Dashboard Monitoring Summary

**Date**: 2026-06-17
**Branch**: task/dashboard-monitoring-summary
**Task**: dashboard-monitoring-summary
**Backlog**: BL-20260617-003

## Delivered Feature
| Feature ID | Feature | Outcome |
|------------|---------|---------|
| F-001 | Monitoring summary data and layout | Dashboard first screen now centers a per-complex monitoring summary before the chart, run history, diagnostics, and urgent feed. |

## Implementation Summary
- `index.html` adds the `단지별 감시 상태` panel as the first main dashboard section.
- `assets/dashboard.js` enriches `COMPLEXES` with watchlist target price and discount ratio metadata.
- `assets/dashboard.js` computes latest minimum listing price, recent trade baseline, urgent line, gap ratio, and monitoring status from existing JSON state.
- `assets/dashboard.css` adds compact table styling and status badges for urgent, near, watch, empty, and unknown states.
- `tests/test_dashboard_static.py` verifies the first-screen ordering, required summary columns, calculation helper presence, and committed JSON compatibility.

## Wiki Closeout
- `docs/wiki/domains/jeonseloop/overview.md` `## 핵심 내용` now records that the first dashboard screen combines watchlist criteria with latest history to show target price, latest minimum listing price, trade baseline, urgent line, gap ratio, and status.

## Verification
- `node --check assets/dashboard.js`: pass.
- `python -m unittest tests.test_dashboard_static -v`: pass, 7 tests.
- `python -m unittest discover -s tests -v`: pass, 68 tests.
- Local static HTTP smoke: `/` and `/data/state/health.json` returned HTTP 200.

## Commits
- Feature commit for F-001: dashboard monitoring summary data and layout.

## Follow-up
- `BL-20260617-004` remains open for a more explicit criterion breakdown and amount remaining to urgent line.
