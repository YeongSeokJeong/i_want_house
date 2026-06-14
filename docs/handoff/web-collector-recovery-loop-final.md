# Web Collector Recovery Loop Final Handoff

## Summary
Implemented a reviewable Naver Real Estate collection and recovery loop for JeonseLoop.

The task adds:
- Source selection through `JEONSELOOP_LISTING_SOURCE_KIND`.
- Best-effort Naver listing collection through public complex article payloads.
- Sanitized collector diagnostics at `data/state/collector-diagnostics.json`.
- GitHub Actions artifact upload for failed collector diagnostics.
- Manual `Collector Recovery` workflow that generates a reviewable recovery report from a failed run artifact.
- Korean operator documentation in `README.md` and durable domain notes in `docs/wiki/domains/jeonseloop/overview.md`.

## Branch and Commits
- Branch: `task/web-collector-recovery-loop`
- Planning: `e1605ff`
- F-001 source contract: `2557f80`
- F-002 Naver adapter: `c44962d`
- F-003 diagnostics: `ca535f9`
- F-004 recovery workflow: `b0c63a4`
- F-005 documentation: `cc505e1`

## Verification
- `python -m unittest discover -s tests` -> 59 tests passed.
- `powershell -File scripts/run-loop.ps1 -DryRun -Fixture tests\fixtures\listings.json` -> success.

## Operational Notes
- Configure Naver mode with repository variables:
  - `JEONSELOOP_LISTING_SOURCE_KIND=naver`
  - `JEONSELOOP_NAVER_COMPLEX_NO_MAP={"baengnyeonsan-hillstate-3":"100123","bulgwang-miseong":"738"}`
  - `JEONSELOOP_NAVER_TRADE_TYPE=A1`
  - `JEONSELOOP_NAVER_REAL_ESTATE_TYPE=APT`
  - `JEONSELOOP_NAVER_MAX_PAGES=3`
- The active watchlist now tracks sale listings for:
  - `baengnyeonsan-hillstate-3`, area `78.87`, target price `850000000`.
  - `bulgwang-miseong`, area `86.47`, target price `850000000`.
- Live Naver access returned HTTP 429 from the local environment during implementation. The collector treats this as a transient source failure and does not bypass access controls.
- The recovery loop creates reports/artifacts only. It does not push to `main`.

## Changed Wiki Content
- `docs/wiki/domains/jeonseloop/overview.md` added `## 네이버부동산 수집과 복구 루프`.
