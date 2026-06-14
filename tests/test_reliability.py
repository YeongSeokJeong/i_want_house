from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jeonseloop.analyzer import (
    apply_quality_blocks,
    approved_candidates,
    classify_candidates,
    detect_average_price_jumps,
)
from jeonseloop.collector import ListingSourceNotConfiguredError, TransientListingFetchError, collect_listings
from jeonseloop.loop import LoopOptions, run_cycle
from jeonseloop.persistence import write_failure_health
from jeonseloop.sources import (
    HttpJsonSourceClient,
    HttpJsonSourceConfig,
    NaverListingSourceClient,
    NaverSourceConfig,
    SourceFetchError,
    TransientSourceFetchError,
    listing_fetcher_from_env,
)
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
    def test_live_collection_requires_fixture_or_configured_source(self) -> None:
        with self.assertRaises(ListingSourceNotConfiguredError):
            collect_listings((TARGET,))

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

    def test_live_fetcher_retries_transient_source_failures(self) -> None:
        attempts = 0
        sleeps: list[float] = []

        def fetcher(target: WatchTarget) -> list[dict]:
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise TransientSourceFetchError("temporary source failure")
            return [
                {
                    "listing_id": "source-retry",
                    "complex_id": target.complex_id,
                    "price_krw": 830000000,
                    "area_m2": 84.9,
                    "floor": 9,
                    "link": "https://example.invalid/source-retry",
                }
            ]

        result = collect_listings((TARGET,), fetcher=fetcher, sleeper=sleeps.append)

        self.assertEqual(attempts, 2)
        self.assertEqual(sleeps, [2])
        self.assertEqual(result["sample-apt"][0]["listing_id"], "source-retry")

    def test_http_json_listing_source_filters_to_watchlist_complex(self) -> None:
        requests: list[str] = []

        def opener(req, timeout: int) -> object:
            requests.append(req.full_url)
            return _JsonResponse(
                {
                    "listings": [
                        {
                            "listing_id": "live-1",
                            "price_krw": 830000000,
                            "area_m2": 84.9,
                            "floor": 9,
                            "link": "https://example.invalid/live-1",
                        },
                        {
                            "listing_id": "wrong-complex",
                            "complex_id": "other-apt",
                            "price_krw": 830000000,
                            "area_m2": 84.9,
                            "floor": 9,
                            "link": "https://example.invalid/wrong",
                        },
                    ]
                }
            )

        client = HttpJsonSourceClient(
            HttpJsonSourceConfig(listing_url="https://source.example/listings/{complex_id}"),
            opener=opener,
        )

        records = client.fetch_listings(TARGET)

        self.assertEqual(requests, ["https://source.example/listings/sample-apt"])
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["complex_id"], "sample-apt")
        self.assertEqual(records[0]["listing_id"], "live-1")

    def test_listing_source_kind_defaults_to_http_json_when_url_is_present(self) -> None:
        fetcher = listing_fetcher_from_env({"JEONSELOOP_LISTING_SOURCE_URL": "https://source.example/listings"})

        self.assertIsNotNone(fetcher)

    def test_naver_source_kind_requires_complex_number_mapping_for_named_targets(self) -> None:
        fetcher = listing_fetcher_from_env({"JEONSELOOP_LISTING_SOURCE_KIND": "naver"})

        self.assertIsNotNone(fetcher)
        with self.assertRaisesRegex(SourceFetchError, "JEONSELOOP_NAVER_COMPLEX_NO_MAP"):
            assert fetcher is not None
            fetcher(TARGET)

    def test_naver_source_kind_accepts_numeric_watchlist_complex_id(self) -> None:
        seen_urls: list[str] = []

        def opener(req, timeout: int) -> object:
            seen_urls.append(req.full_url)
            return _JsonResponse({"articleList": [], "isMoreData": False})

        client = NaverListingSourceClient(NaverSourceConfig({}), opener=opener)
        numeric_target = WatchTarget("111515", "Numeric Complex", 84.9, 850000000)

        records = client.fetch_listings(numeric_target)

        self.assertEqual(records, [])
        self.assertIn("/api/articles/complex/111515?", seen_urls[0])

    def test_naver_listing_source_normalizes_article_payload(self) -> None:
        requests: list[str] = []

        def opener(req, timeout: int) -> object:
            requests.append(req.full_url)
            return _JsonResponse(
                {
                    "articleList": [
                        {
                            "articleNo": "2512345678",
                            "articleName": "Sample Apartment",
                            "realEstateTypeName": "아파트",
                            "tradeTypeName": "전세",
                            "floorInfo": "12/25",
                            "dealOrWarrantPrc": "8억 3,000",
                            "area2": 84.9,
                            "buildingName": "101동",
                            "articleConfirmYmd": "20260614",
                            "articleFeatureDesc": "확인매물",
                        }
                    ],
                    "isMoreData": False,
                }
            )

        client = NaverListingSourceClient(
            NaverSourceConfig({"sample-apt": "111515"}, max_pages=5),
            opener=opener,
        )

        records = client.fetch_listings(TARGET)

        self.assertEqual(len(records), 1)
        self.assertEqual(len(requests), 1)
        self.assertIn("tradeType=B1", requests[0])
        self.assertEqual(records[0]["listing_id"], "naver:2512345678")
        self.assertEqual(records[0]["complex_id"], "sample-apt")
        self.assertEqual(records[0]["price_krw"], 830000000)
        self.assertEqual(records[0]["area_m2"], 84.9)
        self.assertEqual(records[0]["floor"], "12/25")
        self.assertEqual(records[0]["posted_at"], "2026-06-14")
        self.assertEqual(records[0]["link"], "https://new.land.naver.com/complexes/111515?articleNo=2512345678")

    def test_naver_listing_source_treats_bad_payload_as_source_failure(self) -> None:
        def opener(req, timeout: int) -> object:
            return _JsonResponse({"unexpected": []})

        client = NaverListingSourceClient(
            NaverSourceConfig({"sample-apt": "111515"}),
            opener=opener,
        )

        with self.assertRaisesRegex(SourceFetchError, "articleList"):
            client.fetch_listings(TARGET)

    def test_invalid_listing_source_kind_is_reported_as_source_error(self) -> None:
        fetcher = listing_fetcher_from_env({"JEONSELOOP_LISTING_SOURCE_KIND": "unknown"})

        self.assertIsNotNone(fetcher)
        with self.assertRaisesRegex(SourceFetchError, "unsupported JEONSELOOP_LISTING_SOURCE_KIND"):
            assert fetcher is not None
            fetcher(TARGET)

    def test_http_json_trade_source_can_feed_baseline_repository(self) -> None:
        def opener(req, timeout: int) -> object:
            self.assertEqual(req.full_url, "https://source.example/trades/sample-apt")
            return _JsonResponse({"trades": [{"trade_price_krw": 930000000}, {"price_krw": 920000000}]})

        client = HttpJsonSourceClient(
            HttpJsonSourceConfig(trade_url="https://source.example/trades/{complex_id}"),
            opener=opener,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            from jeonseloop.trades import TradeBaselineRepository

            baselines = TradeBaselineRepository(Path(temp_dir), fetcher=client.fetch_trades).load((TARGET,))

        self.assertEqual(baselines, {"sample-apt": 925000000})

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

    def test_cycle_records_missing_live_source_as_failed_health(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            with patch.dict("os.environ", {}, clear=True):
                result = run_cycle(
                    LoopOptions(
                        watchlist_path=ROOT / "config" / "watchlist.yaml",
                        data_dir=root / "data",
                        logs_dir=root / "logs",
                        dry_run=False,
                        allow_send=False,
                    )
                )

            health = json.loads((root / "data" / "state" / "health.json").read_text(encoding="utf-8"))

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["reason"], "listing_source_unconfigured")
        self.assertIn("JEONSELOOP_LISTING_SOURCE_URL", result["error"])
        self.assertEqual(health["latest"]["reason"], "listing_source_unconfigured")
        self.assertFalse((root / "data" / "listings" / "sample-apt.json").exists())

    def test_cycle_records_missing_naver_complex_mapping_as_collector_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            previous_listing = root / "data" / "listings" / "sample-apt.json"
            previous_listing.parent.mkdir(parents=True)
            previous_listing.write_text('{"listings":[{"listing_id":"previous"}]}', encoding="utf-8")

            with patch.dict(
                "os.environ",
                {
                    "JEONSELOOP_LISTING_SOURCE_KIND": "naver",
                    "JEONSELOOP_SOURCE_BEARER_TOKEN": "secret-token",
                },
                clear=True,
            ):
                result = run_cycle(
                    LoopOptions(
                        watchlist_path=ROOT / "config" / "watchlist.yaml",
                        data_dir=root / "data",
                        logs_dir=root / "logs",
                        dry_run=False,
                        allow_send=False,
                    )
                )

            health = json.loads((root / "data" / "state" / "health.json").read_text(encoding="utf-8"))
            diagnostics = json.loads(
                (root / "data" / "state" / "collector-diagnostics.json").read_text(encoding="utf-8")
            )
            preserved_listing_text = previous_listing.read_text(encoding="utf-8")

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["reason"], "collector_failed")
        self.assertIn("JEONSELOOP_NAVER_COMPLEX_NO_MAP", result["error"])
        self.assertEqual(health["latest"]["reason"], "collector_failed")
        self.assertEqual(diagnostics["source_kind"], "naver")
        self.assertEqual(diagnostics["failure_stage"], "listing_collection")
        self.assertEqual(
            diagnostics["targets"],
            [{"complex_id": "baengnyeonsan-hillstate-3"}, {"complex_id": "bulgwang-miseong"}],
        )
        self.assertNotIn("secret-token", json.dumps(diagnostics))
        self.assertEqual(preserved_listing_text, '{"listings":[{"listing_id":"previous"}]}')

    def test_failure_diagnostics_redacts_sensitive_fields(self) -> None:
        from jeonseloop.persistence import sanitize_diagnostics

        sanitized = sanitize_diagnostics(
            {
                "Authorization": "Bearer raw-secret",
                "message": "url=https://example.invalid?token=raw-secret&ok=1",
                "nested": {"api_key": "raw-secret"},
            }
        )

        text = json.dumps(sanitized)
        self.assertNotIn("raw-secret", text)
        self.assertEqual(sanitized["Authorization"], "[redacted]")
        self.assertEqual(sanitized["nested"]["api_key"], "[redacted]")

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
            (history_dir / "baengnyeonsan-hillstate-3.json").write_text(
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
        self.assertFalse((root / "data" / "listings" / "baengnyeonsan-hillstate-3.json").exists())

    def test_cycle_persists_recent_trade_baseline_in_history(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            trades_dir = root / "data" / "trades"
            trades_dir.mkdir(parents=True)
            (trades_dir / "baengnyeonsan-hillstate-3.json").write_text(
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

            history = json.loads(
                (root / "data" / "history" / "baengnyeonsan-hillstate-3.json").read_text(encoding="utf-8")
            )

        self.assertEqual(result["status"], "success")
        self.assertEqual(history["history"][-1]["recent_trade_price_krw"], 925000000)


class _JsonResponse:
    status = 200

    def __init__(self, payload: object) -> None:
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")


if __name__ == "__main__":
    unittest.main()
