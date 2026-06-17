from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "jeonseloop.yml"
RECOVERY_WORKFLOW = ROOT / ".github" / "workflows" / "collector-recovery.yml"
TELEGRAM_INTAKE_WORKFLOW = ROOT / ".github" / "workflows" / "telegram-backlog-intake.yml"


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
        self.assertIn(
            "JEONSELOOP_LISTING_SOURCE_KIND: ${{ vars.JEONSELOOP_LISTING_SOURCE_KIND || secrets.JEONSELOOP_LISTING_SOURCE_KIND || '' }}",
            text,
        )
        self.assertIn(
            "JEONSELOOP_NAVER_COMPLEX_NO_MAP: ${{ vars.JEONSELOOP_NAVER_COMPLEX_NO_MAP || secrets.JEONSELOOP_NAVER_COMPLEX_NO_MAP || '' }}",
            text,
        )
        self.assertIn("JEONSELOOP_NAVER_TRADE_TYPE: ${{ vars.JEONSELOOP_NAVER_TRADE_TYPE || 'B1' }}", text)
        self.assertIn("JEONSELOOP_NAVER_REAL_ESTATE_TYPE: ${{ vars.JEONSELOOP_NAVER_REAL_ESTATE_TYPE || 'APT' }}", text)
        self.assertIn("JEONSELOOP_NAVER_MAX_PAGES: ${{ vars.JEONSELOOP_NAVER_MAX_PAGES || '3' }}", text)
        self.assertIn(
            "JEONSELOOP_HOGANGNONO_APT_HASH_MAP: ${{ vars.JEONSELOOP_HOGANGNONO_APT_HASH_MAP || secrets.JEONSELOOP_HOGANGNONO_APT_HASH_MAP || '' }}",
            text,
        )
        self.assertIn("JEONSELOOP_HOGANGNONO_TRADE_TYPES: ${{ vars.JEONSELOOP_HOGANGNONO_TRADE_TYPES || '0' }}", text)
        self.assertIn("JEONSELOOP_HOGANGNONO_PAGE_SIZE: ${{ vars.JEONSELOOP_HOGANGNONO_PAGE_SIZE || '50' }}", text)
        self.assertIn("JEONSELOOP_HOGANGNONO_MAX_PAGES: ${{ vars.JEONSELOOP_HOGANGNONO_MAX_PAGES || '3' }}", text)
        self.assertIn("JEONSELOOP_TRADE_SOURCE_URL: ${{ secrets.JEONSELOOP_TRADE_SOURCE_URL }}", text)
        self.assertIn("JEONSELOOP_SOURCE_BEARER_TOKEN: ${{ secrets.JEONSELOOP_SOURCE_BEARER_TOKEN }}", text)

    def test_workflow_uploads_collector_diagnostics_on_failure(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("Upload collector diagnostics", text)
        self.assertIn("if: failure()", text)
        self.assertIn("actions/upload-artifact@v7", text)
        self.assertIn("name: collector-diagnostics", text)
        self.assertIn("path: data/state/collector-diagnostics.json", text)

    def test_collector_recovery_workflow_generates_reviewable_report(self) -> None:
        text = RECOVERY_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("workflow_dispatch:", text)
        self.assertIn("run_id:", text)
        self.assertIn("actions/download-artifact@v8", text)
        self.assertIn("name: collector-diagnostics", text)
        self.assertIn("collector-recovery-report.md", text)
        self.assertNotIn("git push", text)

    def test_telegram_backlog_intake_workflow_is_read_only_toward_telegram(self) -> None:
        text = TELEGRAM_INTAKE_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn('cron: "0 * * * *"', text)
        self.assertIn("python -m jeonseloop.telegram_backlog_intake $args", text)
        self.assertIn("--fetch-updates", text)
        self.assertIn("--write-fetched-updates", text)
        self.assertIn("--updates-path $RUNNER_TEMP/telegram-updates.json", text)
        self.assertIn("python -m jeonseloop.telegram_ops $args", text)
        self.assertNotIn("--send", text)
        self.assertNotIn("sendMessage", text)
        self.assertNotIn("--chat-id $TELEGRAM_CHAT_ID", text)
        self.assertIn("git add docs/backlog.md data/state/telegram-intake.json", text)
        self.assertNotIn("git add docs/backlog.md data/state/telegram-intake.json data/state/telegram-updates.json", text)


if __name__ == "__main__":
    unittest.main()
