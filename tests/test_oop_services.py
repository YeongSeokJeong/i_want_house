from pathlib import Path
import json
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jeonseloop.analyzer import Candidate, CandidateAnalyzer
from jeonseloop.collector import ListingCollector
from jeonseloop.loop import LoopCoordinator, LoopOptions
from jeonseloop.notifier import NotificationService
from jeonseloop.persistence import JsonStateStore, LoopStateRepository
from jeonseloop.review import CandidateReviewService, LlmReviewConfig
from jeonseloop.suggestions import CriteriaSuggestionService
from jeonseloop.trades import TradeBaselineRepository
from jeonseloop.validator import ListingValidator
from jeonseloop.watchlist import WatchTarget


TARGET = WatchTarget(
    complex_id="sample-apt",
    name="Sample Apartment",
    area_m2=84.9,
    target_price_krw=840000000,
    urgent_discount_ratio=0.1,
)


def listing(listing_id: str = "listing-1", price: int = 830000000) -> dict:
    return {
        "listing_id": listing_id,
        "complex_id": "sample-apt",
        "title": "Sample",
        "price_krw": price,
        "area_m2": 84.9,
        "building": "101",
        "floor": 9,
        "link": f"https://example.invalid/{listing_id}",
    }


class OopServiceTests(unittest.TestCase):
    def test_listing_collector_and_validator_classes_cover_fixture_records(self) -> None:
        collector = ListingCollector()
        targets = (
            WatchTarget("baengnyeonsan-hillstate-3", "백련산힐스테이트3차", 78.87, 850000000),
            WatchTarget("bulgwang-miseong", "불광 미성아파트", 86.47, 850000000),
        )
        records = collector.collect(targets, ROOT / "tests" / "fixtures" / "listings.json")

        valid, invalid = ListingValidator().validate(records)

        self.assertEqual(len(valid["baengnyeonsan-hillstate-3"]), 1)
        self.assertEqual(len(valid["bulgwang-miseong"]), 1)
        self.assertEqual(invalid, [])

    def test_listing_validator_keeps_existing_rejection_reasons_with_model_boundary(self) -> None:
        valid, invalid = ListingValidator().validate(
            {
                "sample-apt": [
                    {
                        "listing_id": "bad",
                        "complex_id": "sample-apt",
                        "price_krw": "bad",
                        "area_m2": 84.9,
                        "floor": 9,
                        "link": "https://example.invalid/bad",
                    },
                    {
                        "listing_id": "missing",
                        "complex_id": "sample-apt",
                        "price_krw": 830000000,
                        "area_m2": 84.9,
                        "floor": 9,
                    },
                ]
            }
        )

        self.assertEqual(valid, {"sample-apt": []})
        self.assertEqual([issue.reason for issue in invalid], ["invalid_price_krw", "missing_link"])

    def test_candidate_analyzer_class_classifies_and_limits_approved_candidates(self) -> None:
        analyzer = CandidateAnalyzer()
        candidates = analyzer.classify(
            (TARGET,),
            {"sample-apt": [listing("expensive", 900000000), listing("cheap", 820000000)]},
            {"notified": {}},
            {},
        )

        approved = analyzer.approved(candidates)

        self.assertEqual([candidate.listing_key for candidate in approved], ["cheap"])
        self.assertEqual(approved[0].reason, "target_price")

    def test_candidate_analyzer_normalizes_listing_numbers_at_boundary(self) -> None:
        analyzer = CandidateAnalyzer()
        record = listing("cheap", price=820000000)
        record["price_krw"] = "820000000"
        record["area_m2"] = "84.9"

        candidates = analyzer.classify((TARGET,), {"sample-apt": [record]}, {"notified": {}}, {})

        self.assertEqual(candidates[0].price_krw, 820000000)
        self.assertEqual(candidates[0].listing["price_krw"], 820000000)
        self.assertEqual(candidates[0].listing["area_m2"], 84.9)

    def test_notification_review_and_suggestion_classes_keep_safe_defaults(self) -> None:
        candidate = Candidate(
            complex_id="sample-apt",
            listing_key="listing-1",
            price_krw=830000000,
            decision="approve",
            reason="target_price",
            listing=listing(),
        )

        notifications = NotificationService().send_candidates([candidate], allow_send=False)
        reviewed = CandidateReviewService(config=LlmReviewConfig(enabled=False)).apply([candidate])

        self.assertEqual(notifications[0].reason, "no_send")
        self.assertEqual(reviewed[0], candidate)

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            logs_dir = root / "logs"
            logs_dir.mkdir()
            rows = [
                "# Criteria Log",
                "",
                "| time | complex_id | listing_key | decision | reason | price_krw |",
                "|---|---|---|---|---|---|",
                "| 2026-06-13T00:00:00+00:00 | sample-apt | listing-1 | reject | above_target_price | 900000000 |",
            ]
            (logs_dir / "criteria-log.md").write_text("\n".join(rows) + "\n", encoding="utf-8")

            payload = CriteriaSuggestionService(
                logs_dir=logs_dir,
                data_dir=root / "data",
                min_decisions=1,
            ).write(generated_at="2026-06-13T00:00:01+00:00")

        self.assertIsNotNone(payload)
        self.assertFalse(payload["auto_applied"])

    def test_state_and_trade_repositories_encapsulate_file_access(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_dir = root / "data"
            logs_dir = root / "logs"
            trades_dir = data_dir / "trades"
            trades_dir.mkdir(parents=True)
            (trades_dir / "sample-apt.json").write_text(
                json.dumps({"trades": [{"price_krw": 930000000}, {"price_krw": 920000000}]}),
                encoding="utf-8",
            )

            baselines = TradeBaselineRepository(data_dir).load((TARGET,))
            run_record = {
                "run_id": "run-1",
                "started_at": "2026-06-13T00:00:00+00:00",
                "finished_at": "2026-06-13T00:00:02+00:00",
                "status": "success",
                "reason": "completed",
                "counts": {},
            }
            LoopStateRepository(data_dir=data_dir, logs_dir=logs_dir).persist_cycle(
                run_record=run_record,
                records_by_complex={"sample-apt": [listing()]},
                candidates=[],
                invalid_records=[],
                notified_updates={},
                trade_baselines=baselines,
            )

            health = json.loads((data_dir / "state" / "health.json").read_text(encoding="utf-8"))
            history = json.loads((data_dir / "history" / "sample-apt.json").read_text(encoding="utf-8"))

        self.assertEqual(baselines, {"sample-apt": 925000000})
        self.assertEqual(health["latest"]["run_id"], "run-1")
        self.assertEqual(history["history"][0]["recent_trade_price_krw"], 925000000)

    def test_loop_coordinator_runs_with_explicit_service_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_dir = root / "data"
            logs_dir = root / "logs"
            store = JsonStateStore()
            result = LoopCoordinator(
                LoopOptions(
                    watchlist_path=ROOT / "config" / "watchlist.yaml",
                    data_dir=data_dir,
                    logs_dir=logs_dir,
                    fixture_path=ROOT / "tests" / "fixtures" / "listings.json",
                    dry_run=False,
                    allow_send=False,
                ),
                collector=ListingCollector(),
                validator=ListingValidator(),
                analyzer=CandidateAnalyzer(),
                state_store=store,
                state_repository=LoopStateRepository(data_dir=data_dir, logs_dir=logs_dir, store=store),
                trade_repository=TradeBaselineRepository(data_dir),
                review_service=CandidateReviewService(config=LlmReviewConfig(enabled=False)),
                notification_service=NotificationService(),
                run_id_factory=lambda: "explicit-run",
            ).run()

            health = json.loads((data_dir / "state" / "health.json").read_text(encoding="utf-8"))

        self.assertEqual(result["run_id"], "explicit-run")
        self.assertEqual(result["status"], "success")
        self.assertEqual(health["latest"]["run_id"], "explicit-run")


if __name__ == "__main__":
    unittest.main()
