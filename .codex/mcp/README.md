# Telegram Bot MCP Tool

## 백로그 intake
저장된 update 파일은 다음 명령으로 백로그 후보로 분석할 수 있다. 이 명령은 Telegram 메시지를 보내지 않고 `docs/backlog.md`와 `data/state/telegram-intake.json`만 갱신한다.

```powershell
$env:PYTHONPATH="src"
python -m jeonseloop.telegram_backlog_intake --updates-path data/state/telegram-updates.json
```

운영 자동화는 로컬 Codex 실행으로 수행한다. 권장 명령은 `docs/telegram-backlog-local-intake.md`에 있으며, `.codex/prompts/telegram-backlog-local-intake.md` 프롬프트가 최근 `getUpdates` 저장, dry-run 확인, 로컬 backlog/state 반영, 보고서 작성을 순서대로 지시한다. 이미 처리한 `update_id`는 다시 백로그에 추가하지 않는다. 요청이 충분히 구체적이지 않으면 백로그 행 대신 `clarification_needed` 초안을 상태 파일에 남긴다.

`.github/workflows/telegram-backlog-intake.yml`은 정기 실행하지 않으며, 필요할 때 수동 dry-run 점검으로만 사용한다. 이 workflow는 backlog/state 변경을 커밋하지 않는다.
MCP에서는 `telegram_triage_saved_updates` 도구로 같은 saved update triage를 실행할 수 있다.

이 repo-local MCP 서버는 Telegram Bot API 점검용 도구를 제공한다. 실제 토큰과 chat ID는 환경 변수 또는 로컬 `.env`에서만 읽고 저장소에 기록하지 않는다.

## 실행 명령

```powershell
python .codex\mcp\telegram_bot_server.py
```

Codex MCP 설정에 등록할 때는 위 명령을 stdio 서버로 연결한다.

## 제공 도구
- `telegram_get_me`: Bot API `getMe` 확인
- `telegram_get_updates`: 최근 `getUpdates` 조회
- `telegram_get_chat`: `chat_id` 또는 `TELEGRAM_CHAT_ID`의 chat metadata 조회
- `telegram_save_recent_updates`: 최근 update를 `data/state/telegram-updates.json` 같은 로컬 JSON으로 저장
- `telegram_read_saved_updates`: 저장된 update JSON 읽기
- `telegram_inspect_send_result`: `sendMessage` 응답 JSON에서 message/chat metadata 요약

## 제한
- Telegram Bot API는 bot이 볼 수 없는 임의 과거 대화 전체를 스크래핑할 수 없다.
- 메시지 전송은 이 MCP 서버에서 제공하지 않는다. 전송은 기존 JeonseLoop `--send` 경로만 사용한다.
- update 저장 파일에는 Bot API 응답이 들어가므로 공개 전 개인정보 포함 여부를 확인해야 한다.
