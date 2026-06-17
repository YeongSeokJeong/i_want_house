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

        self.assertIn("단지별 감시 상태", html)
        self.assertLess(html.index("단지별 감시 상태"), html.index("최근 급매 후보"))
        self.assertIn("monitoringSummaryBody", html)
        self.assertIn("희망가", html)
        self.assertIn("최근 최저 호가", html)
        self.assertIn("실거래 기준선", html)
        self.assertIn("급매선", html)
        self.assertIn("적용 기준", html)
        self.assertIn("급매선까지", html)
        self.assertIn("괴리율", html)
        self.assertIn("최근 수집/검색 이력", html)
        self.assertIn("runHistoryList", html)
        self.assertIn("수집 매물 가격 추이", html)
        self.assertIn("최저 호가와 평균 호가", html)
        self.assertIn("historySummary", html)
        self.assertIn("단지별 수집 진단", html)
        self.assertIn("collectionDiagnosticsList", html)
        self.assertIn("탈락/보류 사유 요약", html)
        self.assertIn("decisionReasonSummary", html)
        self.assertIn("complexDecisionSummary", html)
        self.assertLess(html.index("탈락/보류 사유 요약"), html.index("최근 급매 후보"))

    def test_dashboard_fetches_committed_json_state(self) -> None:
        script = (ROOT / "assets" / "dashboard.js").read_text(encoding="utf-8")

        self.assertIn('fetchJson("data/state/health.json")', script)
        self.assertIn('fetchJson("data/state/urgent-feed.json")', script)
        self.assertIn("data/history/${complexId}.json", script)
        self.assertIn("renderMonitoringSummary", script)
        self.assertIn("criteriaThresholds", script)
        self.assertIn("remainingToUrgentLine", script)
        self.assertIn("formatRemaining", script)
        self.assertIn("urgentLinePrice", script)
        self.assertIn("priceGapRatio", script)
        self.assertIn("monitoringStatus", script)
        self.assertIn("renderRunHistory", script)
        self.assertIn("renderCollectionDiagnostics", script)
        self.assertIn("renderDecisionSummary", script)
        self.assertIn("decisionSummary", script)
        self.assertIn("reasonLabel", script)
        self.assertIn("complexSummaryReason", script)
        self.assertIn("health?.runs", script)
        self.assertIn("listing_diagnostics", script)

    def test_dashboard_has_section_local_error_and_empty_states(self) -> None:
        script = (ROOT / "assets" / "dashboard.js").read_text(encoding="utf-8")

        self.assertIn("히스토리 데이터가 아직 없습니다.", script)
        self.assertIn("히스토리 데이터를 불러오지 못했습니다.", script)
        self.assertIn("후보 데이터를 불러오지 못했습니다.", script)
        self.assertIn("상태 파일을 불러오지 못했습니다.", script)
        self.assertIn("수집/검색 이력을 불러오지 못했습니다.", script)
        self.assertIn("최근 실행에 단지별 수집 진단이 없습니다.", script)
        self.assertIn("호갱노노 매매 API가 정상 응답했지만 매물이 0건입니다.", script)
        self.assertIn("단지별 감시 상태를 불러오지 못했습니다.", script)
        self.assertIn("매물 0건", script)
        self.assertIn("희망가 상한", script)
        self.assertIn("실거래 할인선", script)
        self.assertIn("도달/초과", script)
        self.assertIn("탈락/보류 사유를 불러오지 못했습니다.", script)
        self.assertIn("최근 후보 사유가 아직 없습니다.", script)
        self.assertIn("가격 기준 초과", script)
        self.assertIn("중복 매물 보류", script)

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
        self.assertIn("listing_diagnostics", health["latest"])
        self.assertTrue(any(item["status"] == "empty_response" for item in health["latest"]["listing_diagnostics"]["targets"]))
        self.assertGreater(len(history["history"]), 0)
        self.assertTrue(any(item["min_price_krw"] for item in history["history"]))
        self.assertGreater(len(zero_history["history"]), 0)
        self.assertTrue(all(item["listing_count"] == 0 for item in zero_history["history"]))
        self.assertGreater(len(listings["listings"]), 0)
        self.assertGreater(len(feed["items"]), 0)
        self.assertTrue(all("reason" in item for item in feed["items"]))
        self.assertTrue(all("decision" in item for item in feed["items"]))
        self.assertTrue(any(item["decision"] in {"approve", "hold", "reject"} for item in feed["items"]))

    def test_dashboard_summary_has_watchlist_threshold_metadata(self) -> None:
        script = (ROOT / "assets" / "dashboard.js").read_text(encoding="utf-8")

        self.assertIn("targetPriceKrw: 850000000", script)
        self.assertIn("urgentDiscountRatio: 0.12", script)
        self.assertIn("Math.min(targetLine, baselineDiscountLine)", script)


if __name__ == "__main__":
    unittest.main()
