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

    def test_dashboard_fetches_committed_json_state(self) -> None:
        script = (ROOT / "assets" / "dashboard.js").read_text(encoding="utf-8")

        self.assertIn('fetchJson("data/state/health.json")', script)
        self.assertIn('fetchJson("data/state/urgent-feed.json")', script)
        self.assertIn("data/history/${complexId}.json", script)

    def test_dashboard_has_section_local_error_and_empty_states(self) -> None:
        script = (ROOT / "assets" / "dashboard.js").read_text(encoding="utf-8")

        self.assertIn("히스토리 데이터가 아직 없습니다.", script)
        self.assertIn("히스토리 데이터를 불러오지 못했습니다.", script)
        self.assertIn("후보 데이터를 불러오지 못했습니다.", script)
        self.assertIn("상태 파일을 불러오지 못했습니다.", script)

    def test_committed_sample_state_can_render_last_run_and_history(self) -> None:
        health = json.loads((ROOT / "data" / "state" / "health.json").read_text(encoding="utf-8"))
        history = json.loads((ROOT / "data" / "history" / "sample-apt.json").read_text(encoding="utf-8"))
        listings = json.loads((ROOT / "data" / "listings" / "sample-apt.json").read_text(encoding="utf-8"))
        feed = json.loads((ROOT / "data" / "state" / "urgent-feed.json").read_text(encoding="utf-8"))

        self.assertEqual(health["latest"]["status"], "success")
        self.assertGreater(health["latest"]["counts"]["valid_listings"], 0)
        self.assertGreater(len(history["history"]), 0)
        self.assertTrue(any(item["min_price_krw"] for item in history["history"]))
        self.assertGreater(len(listings["listings"]), 0)
        self.assertGreater(len(feed["items"]), 0)
        self.assertTrue(all("reason" in item for item in feed["items"]))


if __name__ == "__main__":
    unittest.main()
