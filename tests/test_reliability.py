from pathlib import Path
import json
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jeonseloop.analyzer import (
    apply_quality_blocks,
    approved_candidates,
    classify_candidates,
    detect_average_price_jumps,
)
from jeonseloop.collector import TransientListingFetchError, collect_listings
from jeonseloop.loop import LoopOptions, run_cycle
from jeonseloop.persistence import write_failure_health
from jeonseloop.trades import load_trade_baselines
from jeonseloop.watchlist import WatchTarget


TARGET = WatchTarget(
    complex_id="sample-apt",
    name="Sample Apartment",
    area_m2=84.9,
    target_price_krw=840000000,
    urgent_discount_ratio=0.1,
)


class ReliabilityTests(unittest.TestCase):
    def test_live_fetcher_retries_transient_failures_and_paces_requests(self) -> None:
        targets = (
            TARGET,
            WatchTarget("other-apt", "Other", 84.9, 850000000),
        )
        calls: list[str] = []
        sleeps: list[float] = []
        attempts = {"sample-apt": 0, "other-apt": 0}

        def fetcher(target: WatchTarget) -> list[dict]:
            calls.append(target.complex_id)
            attempts[target.complex_id] += 1
            if target.complex_id == "sample-apt" and attempts[target.complex_id] < 3:
                raise TransientListingFetchError("temporary")
            return [
                {
                    "listing_id": f"{target.complex_id}-1",
                    "complex_id": target.complex_id,
                    "price_krw": 830000000,
                    "area_m2": 84.9,
                    "floor": 9,
                    "link": "https://example.invalid/listing",
                }
            ]

        result = collect_listings(
            targets,
            fetcher=fetcher,
            request_interval_seconds=2,
            retry_attempts=3,
            sleeper=sleeps.append,
        )

        self.assertEqual(attempts["sample-apt"], 3)
        self.assertEqual(attempts["other-apt"], 1)
        self.assertEqual(calls, ["sample-apt", "sample-apt", "sample-apt", "other-apt"])
        self.assertEqual(sleeps, [2, 2, 2])
        self.assertEqual(len(result["sample-apt"]), 1)

    def test_trade_baseline_and_target_price_fallback_are_both_supported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "data"
            trades_dir = data_dir / "trades"
            trades_dir.mkdir(parents=True)
            (trades_dir / "sample-apt.json").write_text(
                json.dumps({"trades": [{"price_krw": 930000000}, {"price_krw": 920000000}]}),
                encoding="utf-8",
            )

            baselines = load_trade_baselines(data_dir, (TARGET,))

        self.assertEqual(baselines, {"sample-apt": 925000000})

        baseline_candidates = classify_candidates(
            (TARGET,),
            {
                "sample-apt": [
                    {
                        "listing_id": "baseline",
                        "complex_id": "sample-apt",
                        "price_krw": 832000000,
                        "area_m2": 84.9,
                        "floor": 9,
                        "link": "https://example.invalid/baseline",
                    }
                ]
            },
            {"notified": {}},
            baselines,
        )
        self.assertEqual(baseline_candidates[0].decision, "approve")
        self.assertEqual(baseline_candidates[0].reason, "baseline_price")

        fallback_candidates = classify_candidates(
            (TARGET,),
            {
                "sample-apt": [
                    {
                        "listing_id": "fallback",
                        "complex_id": "sample-apt",
                        "price_krw": 839000000,
                        "area_m2": 84.9,
                        "floor": 9,
                        "link": "https://example.invalid/fallback",
                    }
                ]
            },
            {"notified": {}},
            {},
        )
        self.assertEqual(fallback_candidates[0].decision, "approve")
        self.assertEqual(fallback_candidates[0].reason, "target_price")

    def test_health_tracks_failure_streak_and_last_success(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "data"
            success = {
                "run_id": "success-1",
                "started_at": "2026-06-12T00:00:00+00:00",
                "finished_at": "2026-06-12T00:00:02+00:00",
                "status": "success",
                "reason": "completed",
                "counts": {},
            }
            from jeonseloop.persistence import persist_cycle

            persist_cycle(
                data_dir=data_dir,
                logs_dir=Path(temp_dir) / "logs",
                run_record=success,
                records_by_complex={},
                candidates=[],
                invalid_records=[],
                notified_updates={},
            )

            failure = {
                "run_id": "failure-1",
                "started_at": "2026-06-12T01:00:00+00:00",
                "finished_at": "2026-06-12T01:00:02+00:00",
                "status": "failed",
                "reason": "watchlist_invalid",
                "counts": {},
            }
            write_failure_health(data_dir, failure)

            health = json.loads((data_dir / "state" / "health.json").read_text(encoding="utf-8"))

        self.assertEqual(health["failure_streak"], 1)
        self.assertFalse(health["health_alert_eligible"])
        self.assertEqual(health["last_success_run_id"], "success-1")
        self.assertEqual(health["last_success_at"], "2026-06-12T00:00:02+00:00")
        self.assertEqual(health["latest"]["run_id"], "failure-1")

    def test_health_alert_becomes_eligible_after_three_consecutive_failures(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "data"
            for index in range(3):
                write_failure_health(
                    data_dir,
                    {
                        "run_id": f"failure-{index}",
                        "started_at": "2026-06-12T01:00:00+00:00",
                        "finished_at": "2026-06-12T01:00:02+00:00",
                        "status": "failed",
                        "reason": "collector_failed",
                        "counts": {},
                    },
                )

            health = json.loads((data_dir / "state" / "health.json").read_text(encoding="utf-8"))

        self.assertEqual(health["failure_streak"], 3)
        self.assertTrue(health["health_alert_eligible"])

    def test_average_price_jump_blocks_approved_alerts(self) -> None:
        records = {
            "sample-apt": [
                {
                    "listing_id": "jump",
                    "complex_id": "sample-apt",
                    "price_krw": 650000000,
                    "area_m2": 84.9,
                    "floor": 9,
                    "link": "https://example.invalid/jump",
                }
            ]
        }

        blocks = detect_average_price_jumps(records, {"sample-apt": 850000000})
        candidates = classify_candidates((TARGET,), records, {"notified": {}}, {})
        blocked = apply_quality_blocks(candidates, blocks)

        self.assertEqual(blocked[0].decision, "hold")
        self.assertIn("average_price_jump", blocked[0].reason)
        self.assertEqual(approved_candidates(blocked), [])

    def test_cycle_records_quality_block_as_failure_without_replacing_snapshots(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            history_dir = root / "data" / "history"
            history_dir.mkdir(parents=True)
            (history_dir / "sample-apt.json").write_text(
                json.dumps({"history": [{"average_price_krw": 1200000000}]}),
                encoding="utf-8",
            )

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

            health = json.loads((root / "data" / "state" / "health.json").read_text(encoding="utf-8"))

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["reason"], "data_quality_blocked")
        self.assertEqual(result["counts"]["data_quality_blocks"], 1)
        self.assertEqual(health["failure_streak"], 1)
        self.assertFalse((root / "data" / "listings" / "sample-apt.json").exists())

    def test_cycle_persists_recent_trade_baseline_in_history(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            trades_dir = root / "data" / "trades"
            trades_dir.mkdir(parents=True)
            (trades_dir / "sample-apt.json").write_text(
                json.dumps({"trades": [{"price_krw": 930000000}, {"price_krw": 920000000}]}),
                encoding="utf-8",
            )

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

            history = json.loads((root / "data" / "history" / "sample-apt.json").read_text(encoding="utf-8"))

        self.assertEqual(result["status"], "success")
        self.assertEqual(history["history"][-1]["recent_trade_price_krw"], 925000000)


if __name__ == "__main__":
    unittest.main()
