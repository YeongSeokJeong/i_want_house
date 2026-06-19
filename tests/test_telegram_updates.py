from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jeonseloop.telegram_updates import (
    extract_updates,
    load_env_with_file,
    merge_by_update_id,
    message_from_update,
    sanitize_text,
    update_id,
)


class TelegramUpdatesTests(unittest.TestCase):
    def test_extract_updates_accepts_saved_and_raw_shapes(self) -> None:
        saved = {"updates": [{"update_id": 1}, "bad"]}
        raw = {"result": [{"update_id": 2}]}

        self.assertEqual(extract_updates(saved), [{"update_id": 1}])
        self.assertEqual(extract_updates(raw), [{"update_id": 2}])
        self.assertEqual(extract_updates([{"update_id": 3}, None]), [{"update_id": 3}])

    def test_update_id_and_message_filtering_are_shared(self) -> None:
        update = {
            "update_id": "10",
            "edited_message": {
                "message_id": 20,
                "chat": {"id": 1234},
                "text": "hello",
            },
        }

        self.assertEqual(update_id(update), 10)
        self.assertIsNone(message_from_update(update, "9999", message_keys=("edited_message",)))
        self.assertEqual(
            message_from_update(update, "1234", message_keys=("edited_message",)),
            {"text": "hello", "message_id": 20},
        )

    def test_merge_by_update_id_replaces_existing_item_and_sorts(self) -> None:
        result = merge_by_update_id(
            [{"update_id": 2, "value": "old"}, {"update_id": "bad"}],
            [{"update_id": 1, "value": "new"}, {"update_id": 2, "value": "replaced"}],
        )

        self.assertEqual(
            result,
            [{"update_id": 1, "value": "new"}, {"update_id": 2, "value": "replaced"}],
        )

    def test_sanitize_text_redacts_and_compacts(self) -> None:
        result = sanitize_text("please check\n token=secret-value")

        self.assertEqual(result, "please check token=[redacted]")
        self.assertNotIn("secret-value", result)

    def test_load_env_with_file_preserves_existing_environment_precedence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            env_file.write_text("TELEGRAM_BOT_TOKEN=file-token\nNEW_VALUE=from-file\n", encoding="utf-8")
            original = dict(__import__("os").environ)
            try:
                __import__("os").environ["TELEGRAM_BOT_TOKEN"] = "existing-token"
                env = load_env_with_file(env_file)
            finally:
                __import__("os").environ.clear()
                __import__("os").environ.update(original)

        self.assertEqual(env["TELEGRAM_BOT_TOKEN"], "existing-token")
        self.assertEqual(env["NEW_VALUE"], "from-file")


if __name__ == "__main__":
    unittest.main()
