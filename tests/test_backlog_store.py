from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jeonseloop.backlog_store import BacklogItem, BacklogStore, append_backlog_rows


class BacklogStoreTests(unittest.TestCase):
    def test_next_sequence_uses_highest_id_for_today(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            backlog = Path(temp_dir) / "docs" / "backlog.md"
            _write_backlog(
                backlog,
                "| BL-20260617-009 | Todo | source-code | old | ctx | 2026-06-17 | - | `src/` | - |\n"
                "| BL-20260618-002 | Todo | source-code | new | ctx | 2026-06-18 | - | `src/` | - |\n",
            )

            self.assertEqual(BacklogStore(backlog).next_sequence("2026-06-18"), 3)

    def test_append_items_inserts_rows_before_existing_items(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            backlog = Path(temp_dir) / "docs" / "backlog.md"
            _write_backlog(backlog, "| BL-20260618-001 | Todo | source-code | old | ctx | 2026-06-18 | - | `src/` | - |\n")

            BacklogStore(backlog).append_items(
                [
                    BacklogItem(
                        backlog_id="BL-20260618-002",
                        status="Todo",
                        route="backlog",
                        task="task | escaped",
                        context="line one\nline two",
                        created="2026-06-18",
                        artifact="`docs/backlog.md`",
                    )
                ]
            )

            lines = backlog.read_text(encoding="utf-8").splitlines()
            first_item = next(line for line in lines if line.startswith("| BL-"))
            self.assertIn("BL-20260618-002", first_item)
            self.assertIn("task \\| escaped", first_item)
            self.assertIn("line one line two", first_item)

    def test_duplicate_ids_fail_before_replace(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            backlog = Path(temp_dir) / "docs" / "backlog.md"
            _write_backlog(backlog, "| BL-20260618-001 | Todo | source-code | old | ctx | 2026-06-18 | - | `src/` | - |\n")
            before = backlog.read_text(encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "duplicate backlog IDs"):
                append_backlog_rows(
                    backlog,
                    ["| BL-20260618-001 | Todo | source-code | dup | ctx | 2026-06-18 | - | `src/` | - |"],
                )

            self.assertEqual(backlog.read_text(encoding="utf-8"), before)

    def test_missing_header_fails_clearly(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            backlog = Path(temp_dir) / "docs" / "backlog.md"
            backlog.parent.mkdir(parents=True, exist_ok=True)
            backlog.write_text("# Backlog\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "backlog table header"):
                append_backlog_rows(
                    backlog,
                    ["| BL-20260618-001 | Todo | source-code | task | ctx | 2026-06-18 | - | `src/` | - |"],
                )


def _write_backlog(path: Path, rows: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Backlog\n\n"
        "## Items\n"
        "| ID | Status | Route | Task | Context | Created | Completed | Artifact | Result |\n"
        "|---|---|---|---|---|---|---|---|---|\n"
        f"{rows}",
        encoding="utf-8",
    )


if __name__ == "__main__":
    unittest.main()
