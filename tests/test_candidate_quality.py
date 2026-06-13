from pathlib import Path
import json
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jeonseloop.analyzer import approved_candidates, classify_candidates
from jeonseloop.loop import LoopOptions, run_cycle
from jeonseloop.watchlist import WatchTarget


TARGET = WatchTarget(
    complex_id="sample-apt",
    name="Sample Apartment",
    area_m2=84.9,
    target_price_krw=850000000,
    urgent_discount_ratio=0.12,
    exclude=("basement",),
)


def listing(listing_id: str, price: int = 830000000, **overrides: object) -> dict:
    record = {
        "listing_id": listing_id,
        "complex_id": "sample-apt",
        "title": f"Listing {listing_id}",
        "price_krw": price,
        "area_m2": 84.9,
        "building": "101",
        "floor": 12,
        "posted_at": "2026-06-12",
        "description": "Clean listing",
        "link": f"https://example.invalid/{listing_id}",
    }
    record.update(overrides)
    return record


class CandidateQualityTests(unittest.TestCase):
    def test_excluded_listing_never_alerts_even_when_price_passes(self) -> None:
        candidates = classify_candidates(
            (TARGET,),
            {"sample-apt": [listing("excluded", title="Basement bargain")]},
            {"notified": {}},
            {},
        )

        self.assertEqual(candidates[0].decision, "reject")
        self.assertEqual(candidates[0].reason, "excluded:basement")
        self.assertEqual(approved_candidates(candidates), [])

    def test_equivalent_duplicate_keeps_one_representative(self) -> None:
        candidates = classify_candidates(
            (TARGET,),
            {
                "sample-apt": [
                    listing("representative", link="https://example.invalid/a"),
                    listing("duplicate", link="https://example.invalid/b"),
                ]
            },
            {"notified": {}},
            {},
        )

        self.assertEqual([candidate.decision for candidate in candidates], ["approve", "hold"])
        self.assertEqual(candidates[1].reason, "duplicate_listing:representative")
        self.assertEqual(len(approved_candidates(candidates)), 1)

    def test_alert_cap_overflow_is_persisted_to_health_and_feed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            watchlist_path = root / "watchlist.json"
            fixture_path = root / "listings.json"
            watchlist_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "request_interval_seconds": 2,
                        "complexes": [
                            {
                                "complex_id": "sample-apt",
                                "name": "Sample Apartment",
                                "area_m2": 84.9,
                                "target_price_krw": 850000000,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            fixture_path.write_text(
                json.dumps(
                    {
                        "listings": [
                            listing(f"listing-{index}", building=str(100 + index), floor=index)
                            for index in range(6)
                        ]
                    }
                ),
                encoding="utf-8",
            )

            result = run_cycle(
                LoopOptions(
                    watchlist_path=watchlist_path,
                    data_dir=root / "data",
                    logs_dir=root / "logs",
                    fixture_path=fixture_path,
                    dry_run=False,
                    allow_send=False,
                )
            )

            health = json.loads((root / "data" / "state" / "health.json").read_text(encoding="utf-8"))
            feed = json.loads((root / "data" / "state" / "urgent-feed.json").read_text(encoding="utf-8"))

        self.assertEqual(result["counts"]["approved_candidates"], 6)
        self.assertEqual(result["counts"]["notifications_planned"], 5)
        self.assertEqual(result["counts"]["alert_cap_overflow"], 1)
        self.assertEqual(health["latest"]["counts"]["alert_cap_overflow"], 1)
        self.assertEqual(feed["alert_cap_overflow"], 1)
        self.assertEqual(len(feed["items"]), 6)
        self.assertEqual(sum(1 for item in feed["items"] if item["alert_planned"]), 5)
        self.assertTrue(all(item["reason"] == "target_price" for item in feed["items"]))


if __name__ == "__main__":
    unittest.main()
