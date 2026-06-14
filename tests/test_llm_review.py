from pathlib import Path
import json
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jeonseloop.analyzer import Candidate, approved_candidates
from jeonseloop.review import LlmReviewConfig, OpenAiCandidateReviewer, apply_llm_review, parse_review_response
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


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")


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

    def test_openai_reviewer_posts_responses_api_payload(self) -> None:
        seen: dict[str, object] = {}

        def opener(req, timeout: int):
            seen["url"] = req.full_url
            seen["timeout"] = timeout
            seen["headers"] = dict(req.header_items())
            seen["payload"] = json.loads(req.data.decode("utf-8"))
            return FakeResponse(
                {
                    "output": [
                        {
                            "type": "message",
                            "content": [
                                {
                                    "type": "output_text",
                                    "text": json.dumps({"decision": "hold", "reason": "verify_price"}),
                                }
                            ],
                        }
                    ]
                }
            )

        config = LlmReviewConfig(enabled=True, api_key="openai-secret", model="gpt-4.1")
        response_text = OpenAiCandidateReviewer(config, opener=opener).review(candidate())

        self.assertEqual(json.loads(response_text), {"decision": "hold", "reason": "verify_price"})
        self.assertEqual(seen["url"], "https://api.openai.com/v1/responses")
        self.assertEqual(seen["timeout"], 30)
        self.assertEqual(seen["headers"]["Authorization"], "Bearer openai-secret")
        payload = seen["payload"]
        self.assertEqual(payload["model"], "gpt-4.1")
        self.assertEqual(payload["text"]["format"]["type"], "json_schema")
        self.assertEqual(payload["text"]["format"]["name"], "jeonseloop_candidate_review")
        self.assertTrue(payload["text"]["format"]["strict"])
        self.assertEqual(payload["input"][0]["content"][0]["type"], "input_text")
        self.assertIn("sample-apt", payload["input"][0]["content"][0]["text"])

    def test_openai_output_text_shortcut_is_supported(self) -> None:
        def opener(_req, timeout: int):
            return FakeResponse({"output_text": json.dumps({"decision": "approve", "reason": "ok"})})

        config = LlmReviewConfig(enabled=True, api_key="openai-secret")

        response_text = OpenAiCandidateReviewer(config, opener=opener).review(candidate())

        self.assertEqual(json.loads(response_text), {"decision": "approve", "reason": "ok"})

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
        self.assertEqual(suggestions["metrics"]["total_decisions"], 30)
        self.assertEqual(suggestions["metrics"]["approved_decisions"], 0)
        self.assertEqual(suggestions["metrics"]["false_positive_signals"], 0)
        self.assertEqual(suggestions["metrics"]["false_positive_ratio"], 0.0)
        self.assertTrue(all(item["requires_human_approval"] for item in suggestions["suggestions"]))
        self.assertEqual(after, before)

    def test_criteria_suggestions_track_false_positive_review_signals(self) -> None:
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
            for index in range(12):
                lines.append(
                    f"| 2026-06-13T00:00:00+00:00 | sample-apt | approved-{index} | approve | target_price | 830000000 |"
                )
            for index in range(10):
                lines.append(
                    f"| 2026-06-13T00:00:00+00:00 | sample-apt | llm-{index} | hold | llm_invalid_response | 830000000 |"
                )
            for index in range(5):
                lines.append(
                    f"| 2026-06-13T00:00:00+00:00 | sample-apt | jump-{index} | hold | average_price_jump:-23.53% | 650000000 |"
                )
            for index in range(3):
                lines.append(
                    f"| 2026-06-13T00:00:00+00:00 | sample-apt | rejected-{index} | reject | above_target_price | 900000000 |"
                )
            (logs_dir / "criteria-log.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

            payload = write_criteria_suggestions(
                logs_dir=logs_dir,
                data_dir=root / "data",
                generated_at="2026-06-13T00:00:01+00:00",
            )

        self.assertIsNotNone(payload)
        assert payload is not None
        metrics = payload["metrics"]
        self.assertEqual(metrics["total_decisions"], 30)
        self.assertEqual(metrics["approved_decisions"], 12)
        self.assertEqual(metrics["false_positive_signals"], 15)
        self.assertEqual(metrics["reviewed_decisions"], 27)
        self.assertEqual(metrics["false_positive_ratio"], 0.5556)
        self.assertEqual(metrics["false_positive_reason_counts"]["llm_invalid_response"], 10)
        self.assertEqual(metrics["false_positive_reason_counts"]["average_price_jump:-23.53%"], 5)
        self.assertEqual(payload["suggestions"][0]["signal"], "false_positive")
        self.assertEqual(payload["suggestions"][0]["reason"], "llm_invalid_response")
        self.assertTrue(all(item["requires_human_approval"] for item in payload["suggestions"]))


if __name__ == "__main__":
    unittest.main()
