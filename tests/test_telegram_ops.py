from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jeonseloop.telegram_ops import OpsOptions, parse_ops_request, run_ops_intake


class TelegramOpsTests(unittest.TestCase):
    def test_source_kind_command_creates_audited_env_proposal(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            updates = root / "updates.json"
            state = root / "state" / "telegram-ops.json"
            _write_updates(updates, [_update(10, "/ops source naver")])

            result = run_ops_intake(OpsOptions(updates_path=updates, state_path=state, today="2026-06-17"))

            self.assertEqual(result["proposal_count"], 1)
            proposal = result["proposals"][0]
            self.assertEqual(proposal["proposal_id"], "OPS-20260617-001")
            self.assertEqual(proposal["intent"], "set_source_kind")
            self.assertEqual(
                proposal["env_changes"],
                [{"name": "JEONSELOOP_LISTING_SOURCE_KIND", "value": "naver", "sensitive": False}],
            )
            persisted = json.loads(state.read_text(encoding="utf-8"))
            self.assertEqual(persisted["processed_update_ids"], [10])

    def test_duplicate_update_does_not_create_second_proposal(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            updates = root / "updates.json"
            state = root / "state" / "telegram-ops.json"
            _write_updates(updates, [_update(10, "/ops naver-map sample-apt 111515")])
            options = OpsOptions(updates_path=updates, state_path=state, today="2026-06-17")

            first = run_ops_intake(options)
            second = run_ops_intake(options)

            self.assertEqual(first["proposal_count"], 1)
            self.assertEqual(second["proposal_count"], 0)
            persisted = json.loads(state.read_text(encoding="utf-8"))
            self.assertEqual(len(persisted["proposals"]), 1)
            self.assertEqual(persisted["proposals"][0]["env_changes"][0]["merge_json"], {"sample-apt": "111515"})

    def test_unknown_command_is_rejected_without_env_or_file_changes(self) -> None:
        parsed = parse_ops_request("네이버로 바꿔줘")

        self.assertEqual(parsed["status"], "rejected")
        self.assertEqual(parsed["reason"], "missing_ops_prefix")
        self.assertNotIn("env_changes", parsed)

    def test_target_price_and_price_cap_are_proposals_not_mutations(self) -> None:
        target = parse_ops_request("/ops target-price sample-apt 830000000")
        cap = parse_ops_request("/ops price-cap 900000000")

        self.assertEqual(target["intent"], "set_watchlist_target_price")
        self.assertEqual(target["file_changes"][0]["path"], "config/watchlist.yaml")
        self.assertEqual(target["file_changes"][0]["value"], 830000000)
        self.assertEqual(cap["intent"], "set_collection_price_cap")
        self.assertEqual(cap["follow_up_required"][0]["suggested_env"], "JEONSELOOP_NAVER_PRICE_MAX_KRW")
        self.assertTrue(target["approval_required"])
        self.assertFalse(target["auto_applied"])

    def test_trade_type_sale_sets_known_source_variables(self) -> None:
        parsed = parse_ops_request("/ops trade-type sale")

        self.assertEqual(parsed["intent"], "set_trade_type")
        self.assertEqual(
            parsed["env_changes"],
            [
                {"name": "JEONSELOOP_NAVER_TRADE_TYPE", "value": "A1", "sensitive": False},
                {"name": "JEONSELOOP_HOGANGNONO_TRADE_TYPES", "value": "0", "sensitive": False},
            ],
        )

    def test_find_complex_creates_research_task(self) -> None:
        parsed = parse_ops_request("/ops find-complex sample-apt 샘플아파트")

        self.assertEqual(parsed["intent"], "research_complex_identifier")
        self.assertEqual(parsed["research_tasks"][0]["complex_id"], "sample-apt")
        self.assertIn("네이버부동산 단지번호", parsed["research_tasks"][0]["queries"][0])

    def test_dry_run_does_not_write_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            updates = root / "updates.json"
            state = root / "state" / "telegram-ops.json"
            _write_updates(updates, [_update(10, "/ops source hogangnono")])

            result = run_ops_intake(
                OpsOptions(updates_path=updates, state_path=state, today="2026-06-17", dry_run=True)
            )

            self.assertEqual(result["proposal_count"], 1)
            self.assertTrue(result["dry_run"])
            self.assertFalse(state.exists())

    def test_secret_like_text_is_redacted_in_rejected_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            updates = root / "updates.json"
            state = root / "state" / "telegram-ops.json"
            _write_updates(updates, [_update(10, "/ops unknown token=secret-value")])

            result = run_ops_intake(OpsOptions(updates_path=updates, state_path=state, today="2026-06-17"))

            self.assertEqual(result["rejected_count"], 1)
            self.assertIn("token=[redacted]", result["rejected"][0]["excerpt"])
            self.assertNotIn("secret-value", result["rejected"][0]["excerpt"])


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
