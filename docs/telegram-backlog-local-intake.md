# Telegram 백로그 로컬 intake 운영 절차

Telegram 백로그 intake는 GitHub Actions 정기 실행이 아니라 운영자의 로컬 Codex 세션에서 실행한다. Bot token과 chat ID는 로컬 환경 변수나 추적되지 않는 `.env`에만 둔다.

## 실행 명령

```powershell
codex exec --sandbox workspace-write `
  "$(Get-Content .codex\prompts\telegram-backlog-local-intake.md -Raw)" `
  -o reports\telegram-backlog-local-intake.md
```

이 프롬프트는 Telegram MCP로 최근 update를 임시 경로에 저장한 뒤, `telegram_backlog_intake`와 `telegram_ops`를 먼저 dry-run으로 확인한다. 결과가 명확할 때만 로컬 파일에 반영한다.

## 변경 대상

- 충분히 구체적인 요청: `docs/backlog.md`에 `Todo` 항목 추가
- 중복 처리 상태: `data/state/telegram-intake.json`
- 운영 제안 상태: `data/state/telegram-ops.json`
- 실행 보고: `reports/telegram-backlog-local-intake.md`

raw Telegram update 파일은 OS 임시 디렉터리에 저장하고 커밋하지 않는다.

## 안전 규칙

- Telegram 메시지를 보내지 않는다.
- `--send`를 사용하지 않는다.
- GitHub Actions workflow를 실행하거나 커밋, push, PR 생성을 하지 않는다.
- 작업트리에 관련 없는 변경이 있으면 먼저 확인하고, 충돌 가능성이 있으면 중단한다.
- `Doing` 상태의 다른 백로그 항목이 있으면 새 항목을 시작하지 않는다.

## GitHub Actions의 역할

`.github/workflows/telegram-backlog-intake.yml`은 정기 실행을 하지 않는다. 필요할 때 수동 dry-run 점검으로만 사용하며, 백로그나 상태 파일을 커밋하지 않는다.
