from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "jeonseloop.yml"


class WorkflowTests(unittest.TestCase):
    def test_workflow_has_required_triggers_and_kst_schedule(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn('cron: "0 0,9 * * *"', text)
        self.assertIn("workflow_dispatch:", text)

    def test_workflow_can_persist_state_on_non_dry_runs(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertRegex(text, re.compile(r"permissions:\s+contents: write", re.MULTILINE))
        self.assertIn("Persist loop state", text)
        self.assertIn("git add data logs", text)
        self.assertIn("steps.run-loop.outputs.dry_run == 'false'", text)

    def test_scheduled_runs_are_not_forced_to_dry_run(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn('${{ github.event_name }}" != "schedule"', text)
        self.assertNotIn('${{ github.event_name }}" = "schedule" ] ||', text)

    def test_workflow_serializes_product_loop_runs(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertRegex(text, re.compile(r"concurrency:\s+group: jeonseloop-product-loop", re.MULTILINE))
        self.assertIn("cancel-in-progress: false", text)

    def test_telegram_send_still_requires_explicit_send_flag(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn('if [ "${{ inputs.send }}" = "true" ]; then', text)
        self.assertIn('args="$args --send"', text)

    def test_manual_dry_run_uses_fixture_by_default(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("fixture:", text)
        self.assertIn('default: "tests/fixtures/listings.json"', text)
        self.assertIn('args="$args --fixture ${{ inputs.fixture }}"', text)

    def test_workflow_passes_live_source_configuration(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("JEONSELOOP_LISTING_SOURCE_URL: ${{ secrets.JEONSELOOP_LISTING_SOURCE_URL }}", text)
        self.assertIn("JEONSELOOP_LISTING_SOURCE_KIND: ${{ vars.JEONSELOOP_LISTING_SOURCE_KIND || '' }}", text)
        self.assertIn("JEONSELOOP_NAVER_COMPLEX_NO_MAP: ${{ vars.JEONSELOOP_NAVER_COMPLEX_NO_MAP || '' }}", text)
        self.assertIn("JEONSELOOP_TRADE_SOURCE_URL: ${{ secrets.JEONSELOOP_TRADE_SOURCE_URL }}", text)
        self.assertIn("JEONSELOOP_SOURCE_BEARER_TOKEN: ${{ secrets.JEONSELOOP_SOURCE_BEARER_TOKEN }}", text)


if __name__ == "__main__":
    unittest.main()
