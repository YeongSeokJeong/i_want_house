from pathlib import Path
import json
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jeonseloop.loop import LoopOptions, run_cycle
from jeonseloop.notifier import format_candidate_message
from jeonseloop.analyzer import Candidate


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
            self.assertTrue((root / "data" / "listings" / "sample-apt.json").exists())
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

    def test_message_format_contains_required_alert_context(self) -> None:
        message = format_candidate_message(
            Candidate(
                complex_id="sample-apt",
                listing_key="listing-1",
                price_krw=830000000,
                decision="approve",
                reason="target_price",
                listing={"title": "Sample", "link": "https://example.invalid/listing-1"},
            )
        )

        self.assertIn("complex_id: sample-apt", message)
        self.assertIn("price_krw: 830000000", message)
        self.assertIn("reason: target_price", message)
        self.assertIn("https://example.invalid/listing-1", message)


if __name__ == "__main__":
    unittest.main()
