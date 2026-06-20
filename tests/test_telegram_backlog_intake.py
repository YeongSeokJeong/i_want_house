from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jeonseloop.telegram_backlog_intake import IntakeOptions, run_intake, triage_message


class TelegramBacklogIntakeTests(unittest.TestCase):
    def test_sufficient_update_adds_backlog_item_and_records_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            backlog = root / "docs" / "backlog.md"
            updates = root / "data" / "state" / "telegram-updates.json"
            state = root / "data" / "state" / "telegram-intake.json"
            _write_backlog(backlog)
            _write_updates(
                updates,
                [
                    _update(
                        100,
                        "대시보드에 텔레그램 요청 수집 이력을 보여주는 기능을 추가해줘",
                    )
                ],
            )

            result = run_intake(
                IntakeOptions(
                    updates_path=updates,
                    state_path=state,
                    backlog_path=backlog,
                    today="2026-06-17",
                )
            )

            self.assertEqual(result["accepted_count"], 1)
            text = backlog.read_text(encoding="utf-8")
            self.assertIn("BL-20260617-001", text)
            self.assertIn("Todo", text)
            self.assertIn("Telegram 요청 처리", text)
            intake = json.loads(state.read_text(encoding="utf-8"))
            self.assertEqual(intake["processed_update_ids"], [100])
            self.assertEqual(intake["accepted"][0]["backlog_id"], "BL-20260617-001")

    def test_processed_update_is_skipped_on_second_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            backlog = root / "docs" / "backlog.md"
            updates = root / "data" / "state" / "telegram-updates.json"
            state = root / "data" / "state" / "telegram-intake.json"
            _write_backlog(backlog)
            _write_updates(updates, [_update(100, "텔레그램 백로그 자동 수집 기능을 구현해줘")])

            options = IntakeOptions(
                updates_path=updates,
                state_path=state,
                backlog_path=backlog,
                today="2026-06-17",
            )
            first = run_intake(options)
            second = run_intake(options)

            self.assertEqual(first["accepted_count"], 1)
            self.assertEqual(second["accepted_count"], 0)
            self.assertEqual(backlog.read_text(encoding="utf-8").count("BL-20260617-001"), 1)

    def test_insufficient_update_records_clarification_without_backlog_row(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            backlog = root / "docs" / "backlog.md"
            updates = root / "data" / "state" / "telegram-updates.json"
            state = root / "data" / "state" / "telegram-intake.json"
            _write_backlog(backlog)
            _write_updates(updates, [_update(101, "이거 좀 봐줘")])

            result = run_intake(
                IntakeOptions(
                    updates_path=updates,
                    state_path=state,
                    backlog_path=backlog,
                    today="2026-06-17",
                )
            )

            self.assertEqual(result["accepted_count"], 0)
            self.assertEqual(result["clarification_needed_count"], 1)
            self.assertNotIn("BL-20260617-001", backlog.read_text(encoding="utf-8"))
            intake = json.loads(state.read_text(encoding="utf-8"))
            self.assertEqual(intake["clarification_needed"][0]["status"], "clarification_needed")
            self.assertIn("더 구체화", intake["clarification_needed"][0]["draft_question"])

    def test_fetch_updates_uses_offset_without_sending_messages(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            backlog = root / "docs" / "backlog.md"
            updates = root / "data" / "state" / "telegram-updates.json"
            state = root / "data" / "state" / "telegram-intake.json"
            env_file = root / ".env"
            _write_backlog(backlog)
            state.parent.mkdir(parents=True, exist_ok=True)
            state.write_text(json.dumps({"processed_update_ids": [200], "last_update_id": 200}), encoding="utf-8")
            env_file.write_text("TELEGRAM_BOT_TOKEN=token-placeholder\n", encoding="utf-8")

            with patch("jeonseloop.telegram_backlog_intake.fetch_telegram_updates") as fetch:
                fetch.return_value = {
                    "generated_at": "2026-06-17T00:00:00+00:00",
                    "source": "telegram_getUpdates",
                    "updates": [_update(201, "네이버 매물 수집 상태를 대시보드에 보여줘")],
                }
                result = run_intake(
                    IntakeOptions(
                        updates_path=updates,
                        state_path=state,
                        backlog_path=backlog,
                        env_file=env_file,
                        fetch_updates=True,
                        today="2026-06-17",
                    )
                )

            self.assertEqual(result["accepted_count"], 1)
            fetch.assert_called_once()
            self.assertEqual(fetch.call_args.kwargs["offset"], 201)
            self.assertTrue(updates.exists())

    def test_fetch_updates_uses_env_file_when_process_env_token_is_empty(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            backlog = root / "docs" / "backlog.md"
            updates = root / "data" / "state" / "telegram-updates.json"
            state = root / "data" / "state" / "telegram-intake.json"
            env_file = root / ".env"
            _write_backlog(backlog)
            env_file.write_text("TELEGRAM_BOT_TOKEN=token-placeholder\n", encoding="utf-8")

            with (
                patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": ""}),
                patch("jeonseloop.telegram_backlog_intake.fetch_telegram_updates") as fetch,
            ):
                fetch.return_value = {
                    "generated_at": "2026-06-17T00:00:00+00:00",
                    "source": "telegram_getUpdates",
                    "updates": [_update(202, "텔레그램 백로그 자동 수집 기능을 수정해줘")],
                }
                result = run_intake(
                    IntakeOptions(
                        updates_path=updates,
                        state_path=state,
                        backlog_path=backlog,
                        env_file=env_file,
                        fetch_updates=True,
                        today="2026-06-17",
                    )
                )

            self.assertEqual(result["accepted_count"], 1)
            fetch.assert_called_once()
            self.assertTrue(updates.exists())

    def test_dry_run_fetch_triages_fetched_payload_without_writing_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            backlog = root / "docs" / "backlog.md"
            updates = root / "runner-temp" / "telegram-updates.json"
            state = root / "data" / "state" / "telegram-intake.json"
            env_file = root / ".env"
            _write_backlog(backlog)
            env_file.write_text("TELEGRAM_BOT_TOKEN=token-placeholder\n", encoding="utf-8")

            with patch("jeonseloop.telegram_backlog_intake.fetch_telegram_updates") as fetch:
                fetch.return_value = {
                    "generated_at": "2026-06-17T00:00:00+00:00",
                    "source": "telegram_getUpdates",
                    "updates": [_update(300, "텔레그램 백로그 자동 수집 기능을 구현해줘")],
                }
                result = run_intake(
                    IntakeOptions(
                        updates_path=updates,
                        state_path=state,
                        backlog_path=backlog,
                        env_file=env_file,
                        fetch_updates=True,
                        dry_run=True,
                        today="2026-06-17",
                    )
                )

            self.assertEqual(result["accepted_count"], 1)
            self.assertFalse(updates.exists())
            self.assertFalse(state.exists())
            self.assertNotIn("BL-20260617-001", backlog.read_text(encoding="utf-8"))

    def test_triage_redacts_secret_like_text(self) -> None:
        result = triage_message("텔레그램 백로그 자동 수집 기능을 추가해줘 token=secret-value")

        self.assertEqual(result["status"], "accepted")
        self.assertIn("token=[redacted]", result["excerpt"])
        self.assertNotIn("secret-value", result["excerpt"])

    def test_ops_messages_are_skipped_by_backlog_intake(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            backlog = root / "docs" / "backlog.md"
            updates = root / "data" / "state" / "telegram-updates.json"
            state = root / "data" / "state" / "telegram-intake.json"
            _write_backlog(backlog)
            _write_updates(updates, [_update(500, "/ops source naver")])

            result = run_intake(
                IntakeOptions(
                    updates_path=updates,
                    state_path=state,
                    backlog_path=backlog,
                    today="2026-06-17",
                )
            )

            self.assertEqual(result["accepted_count"], 0)
            self.assertEqual(result["clarification_needed_count"], 0)
            self.assertEqual(result["skipped_count"], 1)
            persisted = json.loads(state.read_text(encoding="utf-8"))
            self.assertEqual(persisted["processed_update_ids"], [500])


def _write_backlog(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Backlog\n\n"
        "## Items\n"
        "| ID | Status | Route | Task | Context | Created | Completed | Artifact | Result |\n"
        "|---|---|---|---|---|---|---|---|---|\n",
        encoding="utf-8",
    )


def _write_updates(path: Path, updates: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"updates": updates}, ensure_ascii=False), encoding="utf-8")


def _update(update_id: int, text: str) -> dict[str, object]:
    return {
        "update_id": update_id,
        "message": {
            "message_id": update_id + 10,
            "chat": {"id": 1234, "type": "private"},
            "text": text,
        },
    }


if __name__ == "__main__":
    unittest.main()
