# Telegram Bot MCP Tool

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
