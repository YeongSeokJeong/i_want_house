from pathlib import Path
import json
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jeonseloop.analyzer import Candidate, approved_candidates
from jeonseloop.review import LlmReviewConfig, apply_llm_review, parse_review_response
from jeonseloop.suggestions import write_criteria_suggestions


def candidate() -> Candidate:
    return Candidate(
        complex_id="sample-apt",
        listing_key="listing-1",
        price_krw=830000000,
        decision="approve",
        reason="target_price",
        listing={"title": "Sample", "link": "https://example.invalid/listing-1"},
    )


class LlmReviewTests(unittest.TestCase):
    def test_review_is_disabled_without_required_secret(self) -> None:
        config = LlmReviewConfig.from_env({"JEONSELOOP_LLM_REVIEW": "true"})

        reviewed = apply_llm_review(
            [candidate()],
            config=config,
            reviewer=lambda _: self.fail("reviewer must not be called without a secret"),
        )

        self.assertFalse(config.enabled)
        self.assertEqual(reviewed[0].decision, "approve")

    def test_invalid_review_response_holds_candidate(self) -> None:
        reviewed = apply_llm_review(
            [candidate()],
            config=LlmReviewConfig(enabled=True, api_key="secret"),
            reviewer=lambda _: "not json",
        )

        self.assertEqual(reviewed[0].decision, "hold")
        self.assertEqual(reviewed[0].reason, "llm_invalid_response")
        self.assertEqual(approved_candidates(reviewed), [])

    def test_valid_review_response_requires_decision_and_reason(self) -> None:
        parsed = parse_review_response(json.dumps({"decision": "hold", "reason": "needs_human_check"}))

        self.assertEqual(parsed, {"decision": "hold", "reason": "needs_human_check"})

    def test_criteria_suggestions_do_not_modify_watchlist(self) -> None:
        watchlist_path = ROOT / "config" / "watchlist.yaml"
        before = watchlist_path.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            logs_dir = root / "logs"
            logs_dir.mkdir()
            lines = [
                "# Criteria Log",
                "",
                "| time | complex_id | listing_key | decision | reason | price_krw |",
                "|---|---|---|---|---|---|",
            ]
            for index in range(30):
                lines.append(
                    f"| 2026-06-13T00:00:00+00:00 | sample-apt | listing-{index} | reject | above_target_price | 900000000 |"
                )
            (logs_dir / "criteria-log.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

            payload = write_criteria_suggestions(
                logs_dir=logs_dir,
                data_dir=root / "data",
                generated_at="2026-06-13T00:00:01+00:00",
            )
            suggestions = json.loads((root / "data" / "state" / "criteria-suggestions.json").read_text())

        after = watchlist_path.read_text(encoding="utf-8")
        self.assertIsNotNone(payload)
        self.assertFalse(suggestions["auto_applied"])
        self.assertTrue(all(item["requires_human_approval"] for item in suggestions["suggestions"]))
        self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
