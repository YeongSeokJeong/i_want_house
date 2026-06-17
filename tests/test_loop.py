from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jeonseloop.analyzer import Candidate
from jeonseloop.loop import LoopOptions, run_cycle, run_failure_health
from jeonseloop.notifier import format_candidate_message
from jeonseloop.watchlist import WatchlistError


class LoopTests(unittest.TestCase):
    def test_cycle_persists_health_and_listing_snapshot_without_sending(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            result = run_cycle(
                LoopOptions(
                    watchlist_path=ROOT / "config" / "watchlist.yaml",
                    data_dir=root / "data",
                    logs_dir=root / "logs",
                    fixture_path=ROOT / "tests" / "fixtures" / "listings.json",
                    dry_run=False,
                    allow_send=False,
                )
            )

            self.assertEqual(result["status"], "success")
            self.assertEqual(result["counts"]["valid_listings"], 2)
            self.assertEqual(result["counts"]["approved_candidates"], 1)
            self.assertEqual(result["counts"]["notifications_sent"], 0)
            self.assertTrue((root / "data" / "state" / "health.json").exists())
            self.assertTrue((root / "data" / "listings" / "baengnyeonsan-hillstate-3.json").exists())
            self.assertTrue((root / "data" / "listings" / "bulgwang-miseong.json").exists())
            self.assertTrue((root / "data" / "history" / "baengnyeonsan-hillstate-3.json").exists())
            self.assertTrue((root / "data" / "history" / "bulgwang-miseong.json").exists())
            self.assertTrue((root / "logs" / "criteria-log.md").exists())

            notified = json.loads((root / "data" / "state" / "notified.json").read_text(encoding="utf-8"))
            self.assertEqual(notified, {"notified": {}})

    def test_dry_run_does_not_write_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            result = run_cycle(
                LoopOptions(
                    watchlist_path=ROOT / "config" / "watchlist.yaml",
                    data_dir=root / "data",
                    logs_dir=root / "logs",
                    fixture_path=ROOT / "tests" / "fixtures" / "listings.json",
                    dry_run=True,
                    allow_send=False,
                )
            )

            self.assertEqual(result["status"], "success")
            self.assertFalse((root / "data").exists())
            self.assertFalse((root / "logs").exists())

    def test_dry_run_blocks_send_even_when_send_requested(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            with patch("jeonseloop.notifier.TelegramNotifier.from_env") as from_env:
                result = run_cycle(
                    LoopOptions(
                        watchlist_path=ROOT / "config" / "watchlist.yaml",
                        data_dir=root / "data",
                        logs_dir=root / "logs",
                        fixture_path=ROOT / "tests" / "fixtures" / "listings.json",
                        dry_run=True,
                        allow_send=True,
                    )
                )

            self.assertEqual(result["status"], "success")
            from_env.assert_not_called()

    def test_invalid_watchlist_health_is_written_when_not_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            options = LoopOptions(
                watchlist_path=root / "watchlist.yaml",
                data_dir=root / "data",
                logs_dir=root / "logs",
                dry_run=False,
                allow_send=False,
            )
            record = run_failure_health(options, WatchlistError("bad watchlist"))

            self.assertEqual(record["status"], "failed")
            health = json.loads((root / "data" / "state" / "health.json").read_text(encoding="utf-8"))
            self.assertEqual(health["latest"]["reason"], "watchlist_invalid")

    def test_message_format_contains_required_alert_context(self) -> None:
        message = format_candidate_message(
            Candidate(
                complex_id="sample-apt",
                listing_key="listing-1",
                price_krw=830000000,
                decision="approve",
                reason="target_price",
                listing={
                    "title": "Sample",
                    "watch_name": "Sample Apartment",
                    "target_price_krw": 840000000,
                    "target_gap_krw": -10000000,
                    "recent_trade_price_krw": 925000000,
                    "baseline_limit_krw": 832500000,
                    "baseline_gap_krw": -2500000,
                    "urgent_discount_ratio": 0.1,
                    "area_m2": 84.9,
                    "floor": 9,
                    "link": "https://example.invalid/listing-1",
                },
            )
        )

        self.assertIn("[JeonseLoop 급매 후보]", message)
        self.assertIn("단지: Sample Apartment (sample-apt)", message)
        self.assertIn("매물: Sample", message)
        self.assertIn("호가: 830,000,000원", message)
        self.assertIn("목표가보다 10,000,000원 낮음", message)
        self.assertIn("최근 실거래 기준: 925,000,000원", message)
        self.assertIn("할인 급매선: 832,500,000원", message)
        self.assertIn("급매선보다 2,500,000원 낮음", message)
        self.assertIn("판정: target_price", message)
        self.assertIn("면적/층: 84.9 m2 / 9층", message)
        self.assertIn("complex_id: sample-apt", message)
        self.assertIn("https://example.invalid/listing-1", message)


if __name__ == "__main__":
    unittest.main()
