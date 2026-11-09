#!/usr/bin/env python3
"""Collect open Obsidian tasks from Markdown files.

Run:
    python task_collector.py PATH [PATH ...]
    python task_collector.py PATH --priority highest --due-before 2026-09-01

Import:
    from task_collector import collect_tasks
    tasks = collect_tasks(["/path/to/vault"])

The script is read-only and uses only the Python standard library.
"""


import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Task:
    text: str
    priority: str
    due_date: date | None
    scheduled_date: date | None
    file: Path
    line_number: int
    raw_line: str


PRIORITIES = {
    "🔺": "highest",
    "⏫": "high",
    "🔼": "medium",
    "🔽": "low",
    "⏬": "lowest",
}

TASK_PATTERN = re.compile(r"^\s*[-+*]\s+\[ \](?:\s+(.*))?$")
COMPLETED_TASK_PATTERN = re.compile(r"^\s*[-+*]\s+\[x\](?:\s+(.*))?$")
CANCELLED_TASK_PATTERN = re.compile(r"^\s*[-+*]\s+\[-\](?:\s+(.*))?$")
PRIORITY_PATTERN = re.compile("|".join(map(re.escape, PRIORITIES)))
DUE_PATTERN = re.compile(r"📅\s*(\d{4}-\d{2}-\d{2})(?=\s|$)")
SCHEDULED_PATTERN = re.compile(r"⏳\s*(\d{4}-\d{2}-\d{2})(?=\s|$)")
FENCE_PATTERN = re.compile(r"^\s*(`{3,}|~{3,})")
FLAGS = ["🔺", "⏫", "🔼", "🔽", "⏬", "📅",  "⏳", "✅"]




def parse_task(line: str, file: Path, line_number: int, pattern: str) -> Task | None:
    """Turn one open Markdown checkbox line into a Task."""
    raw_line = line.rstrip("\r\n")
    match = pattern.match(raw_line)
    if not match:
        return None

    text = match.group(1) or ""
    priority_matches = list(PRIORITY_PATTERN.finditer(text))
    priority = (
        PRIORITIES[priority_matches[-1].group()] if priority_matches else "normal"
    )

    sched_date = None
    sched_matches = list(SCHEDULED_PATTERN.finditer(text))
    valid_sched_matches = []
    for sched_match in sched_matches:
        try:
            parsed_date = date.fromisoformat(sched_match.group(1))
        except ValueError:
            continue
        valid_sched_matches.append((sched_match, parsed_date))
    if valid_sched_matches:
        sched_date = valid_sched_matches[-1][1]

    due_date = None
    due_matches = list(DUE_PATTERN.finditer(text))
    valid_due_matches = []
    for due_match in due_matches:
        try:
            parsed_date = date.fromisoformat(due_match.group(1))
        except ValueError:
            continue
        valid_due_matches.append((due_match, parsed_date))
    if valid_due_matches:
        due_date = valid_due_matches[-1][1]

    metadata_spans = [item.span() for item in priority_matches]
    metadata_spans.extend(item.span() for item, _ in valid_due_matches)
    for start, end in sorted(metadata_spans, reverse=True):
        text = text[:start] + text[end:]
    text = re.sub(r"\s+", " ", text).strip()

    text = re.split("|".join(FLAGS), text)[0] or ""


    return Task(
        text=text,
        priority=priority,
        due_date=due_date,
        scheduled_date=sched_date,
        file=file,
        line_number=line_number,
        raw_line=raw_line,
    )


def markdown_files(paths: Iterable[str | Path]) -> list[Path]:
    """Return unique Markdown files found beneath the supplied paths."""
    files: set[Path] = set()
    for value in paths:
        path = Path(value).expanduser()
        if not path.exists():
            raise FileNotFoundError(path)
        if path.is_file():
            if path.suffix.lower() == ".md":
                files.add(path.resolve())
            continue
        for file in path.rglob("*.md"):
            if ".obsidian" not in file.parts:
                files.add(file.resolve())
    return sorted(files)


def collect_tasks(
    paths: Iterable[str | Path],
    *,
    priorities: set[str] | None = None,
    due_on: date | None = None,
    due_before: date | None = None,
    due_after: date | None = None,
    scheduled_on: date | None = None,
    scheduled_before: date | None = None,
    scheduled_after: date | None = None,
    completed : bool = False,
    cancelled : bool = False
) -> list[Task]:
    """Collect and filter open tasks from files or directories."""
    tasks: list[Task] = []

    for file in markdown_files(paths):
        in_code_block = False
        fence_character = ""
        with file.open(encoding="utf-8") as markdown:
            for line_number, line in enumerate(markdown, start=1):
                fence_match = FENCE_PATTERN.match(line)
                if fence_match:
                    character = fence_match.group(1)[0]
                    if not in_code_block:
                        in_code_block = True
                        fence_character = character
                    elif character == fence_character:
                        in_code_block = False
                    continue
                if in_code_block:
                    continue

                pattern = TASK_PATTERN
                if cancelled: 
                    pattern = CANCELLED_TASK_PATTERN
                if completed:
                    pattern = COMPLETED_TASK_PATTERN
                
                task = parse_task(line, file, line_number, pattern)
                
                if task is None:
                    continue
                if priorities and task.priority not in priorities:
                    continue
                if due_on and task.due_date != due_on:
                    continue
                if due_before and (
                    task.due_date is None or task.due_date >= due_before
                ):
                    continue
                if due_after and (
                    task.due_date is None or task.due_date <= due_after
                ):
                    continue
                if scheduled_on and task.scheduled_date != scheduled_on:
                    continue
                if scheduled_before and (
                    task.scheduled_date is None or task.scheduled_date > scheduled_before
                ):
                    continue
                if scheduled_after and (
                    task.scheduled_date is None or task.scheduled_date <= scheduled_after
                ):
                    continue
                tasks.append(task)

    return tasks

