from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re


BACKLOG_HEADER = "| ID | Status | Route | Task | Context | Created | Completed | Artifact | Result |"


@dataclass(frozen=True)
class BacklogItem:
    backlog_id: str
    status: str
    route: str
    task: str
    context: str
    created: str
    completed: str = "-"
    artifact: str = "-"
    result: str = "-"

    def to_markdown_row(self) -> str:
        return (
            f"| {self.backlog_id} | {self.status} | {self.route} | {_cell(self.task)} | "
            f"{_cell(self.context)} | {self.created} | {self.completed} | {self.artifact} | {_cell(self.result)} |"
        )


class BacklogStore:
    def __init__(self, path: Path) -> None:
        self._path = path

    @property
    def path(self) -> Path:
        return self._path

    def next_sequence(self, today: str) -> int:
        return next_backlog_sequence(self._path, today)

    def append_items(self, items: list[BacklogItem]) -> None:
        append_backlog_rows(self._path, [item.to_markdown_row() for item in items])


def append_backlog_rows(path: Path, rows: list[str]) -> None:
    if not rows:
        return
    text = path.read_text(encoding="utf-8") if path.exists() else empty_backlog_text()
    lines = text.splitlines()
    if not any(line.startswith(BACKLOG_HEADER) for line in lines):
        raise ValueError("backlog table header was not found")
    insert_at = _find_insert_index(lines)
    updated = lines[:insert_at] + rows + lines[insert_at:]
    new_text = "\n".join(updated).rstrip() + "\n"
    validate_backlog_text(new_text)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp")
    temp.write_text(new_text, encoding="utf-8")
    os.replace(temp, path)


def validate_backlog_text(text: str) -> None:
    ids = re.findall(r"\|\s*(BL-\d{8}-\d{3})\s*\|", text)
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate backlog IDs detected")


def next_backlog_sequence(path: Path, today: str) -> int:
    if not path.exists():
        return 1
    prefix = f"BL-{today.replace('-', '')}-"
    max_seen = 0
    for match in re.finditer(r"BL-\d{8}-(\d{3})", path.read_text(encoding="utf-8")):
        full = match.group(0)
        if full.startswith(prefix):
            max_seen = max(max_seen, int(match.group(1)))
    return max_seen + 1


def empty_backlog_text() -> str:
    return (
        "# Backlog\n\n"
        "> Last updated: 2026-06-17\n\n"
        "## Items\n"
        f"{BACKLOG_HEADER}\n"
        "|---|---|---|---|---|---|---|---|---|\n"
    )


def _find_insert_index(lines: list[str]) -> int:
    for index, line in enumerate(lines):
        if line.startswith("| BL-"):
            return index
    return len(lines)


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()
