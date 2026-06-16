from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]


class DashboardStaticTests(unittest.TestCase):
    def test_dashboard_uses_static_assets_without_build_step(self) -> None:
        html = (ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn('href="assets/dashboard.css"', html)
        self.assertIn('src="assets/dashboard.js"', html)
        self.assertNotIn("node_modules", html)

    def test_dashboard_exposes_collection_history_and_clear_trend_copy(self) -> None:
        html = (ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn("최근 수집/검색 이력", html)
        self.assertIn("runHistoryList", html)
        self.assertIn("수집 매물 가격 추이", html)
        self.assertIn("최저 호가와 평균 호가", html)
        self.assertIn("historySummary", html)

    def test_dashboard_fetches_committed_json_state(self) -> None:
        script = (ROOT / "assets" / "dashboard.js").read_text(encoding="utf-8")

        self.assertIn('fetchJson("data/state/health.json")', script)
        self.assertIn('fetchJson("data/state/urgent-feed.json")', script)
        self.assertIn("data/history/${complexId}.json", script)
        self.assertIn("renderRunHistory", script)
        self.assertIn("health?.runs", script)

    def test_dashboard_has_section_local_error_and_empty_states(self) -> None:
        script = (ROOT / "assets" / "dashboard.js").read_text(encoding="utf-8")

        self.assertIn("히스토리 데이터가 아직 없습니다.", script)
        self.assertIn("히스토리 데이터를 불러오지 못했습니다.", script)
        self.assertIn("후보 데이터를 불러오지 못했습니다.", script)
        self.assertIn("상태 파일을 불러오지 못했습니다.", script)
        self.assertIn("수집/검색 이력을 불러오지 못했습니다.", script)

    def test_dashboard_uses_current_watchlist_complexes(self) -> None:
        script = (ROOT / "assets" / "dashboard.js").read_text(encoding="utf-8")

        self.assertIn("baengnyeonsan-hillstate-3", script)
        self.assertIn("bulgwang-miseong", script)
        self.assertNotIn("sample-apt\", name: \"Sample Apartment", script)

    def test_committed_state_can_render_last_run_history_listings_and_feed(self) -> None:
        health = json.loads((ROOT / "data" / "state" / "health.json").read_text(encoding="utf-8"))
        history = json.loads((ROOT / "data" / "history" / "baengnyeonsan-hillstate-3.json").read_text(encoding="utf-8"))
        zero_history = json.loads((ROOT / "data" / "history" / "bulgwang-miseong.json").read_text(encoding="utf-8"))
        listings = json.loads((ROOT / "data" / "listings" / "baengnyeonsan-hillstate-3.json").read_text(encoding="utf-8"))
        feed = json.loads((ROOT / "data" / "state" / "urgent-feed.json").read_text(encoding="utf-8"))

        self.assertEqual(health["latest"]["status"], "success")
        self.assertGreaterEqual(len(health["runs"]), 1)
        self.assertGreater(health["latest"]["counts"]["valid_listings"], 0)
        self.assertGreater(len(history["history"]), 0)
        self.assertTrue(any(item["min_price_krw"] for item in history["history"]))
        self.assertGreater(len(zero_history["history"]), 0)
        self.assertTrue(all(item["listing_count"] == 0 for item in zero_history["history"]))
        self.assertGreater(len(listings["listings"]), 0)
        self.assertGreater(len(feed["items"]), 0)
        self.assertTrue(all("reason" in item for item in feed["items"]))


if __name__ == "__main__":
    unittest.main()
