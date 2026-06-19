from pathlib import Path
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jeonseloop.models import CandidateRecord, FeedItem, ModelValidationError, NormalizedListing, RunRecord


class DomainModelTests(unittest.TestCase):
    def test_normalized_listing_round_trips_existing_fixture_shape(self) -> None:
        fixture = json.loads((ROOT / "tests" / "fixtures" / "listings.json").read_text(encoding="utf-8"))
        record = dict(fixture["listings"][0])
        record["provider_payload"] = {"source": "fixture"}

        listing = NormalizedListing.from_dict(record)

        self.assertEqual(listing.complex_id, "baengnyeonsan-hillstate-3")
        self.assertEqual(listing.price_krw, 830000000)
        self.assertEqual(listing.extras, {"provider_payload": {"source": "fixture"}})
        self.assertEqual(listing.to_dict(), record)

    def test_normalized_listing_reports_missing_required_field(self) -> None:
        with self.assertRaisesRegex(ModelValidationError, "NormalizedListing.link: is required"):
            NormalizedListing.from_dict(
                {
                    "listing_id": "listing-1",
                    "complex_id": "sample-apt",
                    "price_krw": 830000000,
                    "area_m2": 84.9,
                    "floor": 12,
                }
            )

    def test_candidate_record_preserves_listing_and_candidate_extras(self) -> None:
        payload = {
            "complex_id": "sample-apt",
            "listing_key": "listing-1",
            "price_krw": 830000000,
            "decision": "approve",
            "reason": "target_price",
            "score": 0.9,
            "listing": {
                "listing_id": "listing-1",
                "complex_id": "sample-apt",
                "title": "Sample",
                "price_krw": 830000000,
                "area_m2": 84.9,
                "building": "101",
                "floor": 9,
                "description": "Clean listing",
                "link": "https://example.invalid/listing-1",
                "watch_name": "Sample Apartment",
                "target_price_krw": 840000000,
            },
        }

        candidate = CandidateRecord.from_dict(payload)

        self.assertEqual(candidate.listing.extras["watch_name"], "Sample Apartment")
        self.assertEqual(candidate.extras, {"score": 0.9})
        self.assertEqual(candidate.to_dict(), payload)

    def test_run_record_round_trips_counts_and_diagnostics(self) -> None:
        payload = {
            "run_id": "run-1",
            "started_at": "2026-06-20T00:00:00+09:00",
            "finished_at": "2026-06-20T00:00:02+09:00",
            "status": "success",
            "reason": "completed",
            "counts": {
                "watched_complexes": 1,
                "valid_listings": "2",
                "invalid_listings": 0,
                "approved_candidates": 1,
            },
            "listing_diagnostics": {"targets": []},
        }

        run = RunRecord.from_dict(payload)

        expected = dict(payload)
        expected["counts"] = {
            "watched_complexes": 1,
            "valid_listings": 2,
            "invalid_listings": 0,
            "approved_candidates": 1,
        }
        self.assertEqual(run.to_dict(), expected)

    def test_feed_item_preserves_optional_null_fields(self) -> None:
        payload = {
            "complex_id": "sample-apt",
            "listing_key": "listing-1",
            "decision": "reject",
            "reason": "above_target_price",
            "price_krw": 900000000,
            "alert_planned": False,
            "title": None,
            "description": "Sample description",
            "building": "101",
            "floor": 9,
            "area_m2": 84.9,
            "link": "https://example.invalid/listing-1",
            "grade": "interest",
        }

        item = FeedItem.from_dict(payload)

        self.assertEqual(item.extras, {"grade": "interest"})
        self.assertEqual(item.to_dict(), payload)


if __name__ == "__main__":
    unittest.main()
