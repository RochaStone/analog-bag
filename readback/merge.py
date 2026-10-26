#!/usr/bin/env python3
"""Merge a page read back from a photo into tasks.md.

    python3 readback/merge.py tasks.md new.md            # merge new.md into tasks.md
    python3 readback/merge.py tasks.md new.md --dry-run  # show the result, write nothing
    python3 readback/merge.py --check new.md             # validate one file

The format (see SKILL.md):

    # Tasks
    ## This week 2026-11-02
    - [ ] write the welcome email {due: 2026-11-03}
    - [x] tell the origin story
    > number: waitlist 40 to 60

Rules: a task that already exists anywhere in tasks.md is never added twice. Done
wins: once a task is ticked in either file it stays ticked. New sections are added
at the end. Notes are kept and never duplicated.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

TASK_RE = re.compile(r"^- \[([ xX])\] (.+?)\s*$")
DUE_RE = re.compile(r"\s*\{due:\s*([^}]*)\}")


class FormatError(ValueError):
    pass


@dataclass
class Task:
    text: str
    done: bool = False
    due: str | None = None

    @property
    def key(self) -> str:
        return " ".join(re.sub(r"[^a-z0-9 ]+", " ", self.text.lower()).split())

    def render(self) -> str:
        due = f" {{due: {self.due}}}" if self.due else ""
        return f"- [{'x' if self.done else ' '}] {self.text}{due}"


@dataclass
class Section:
    name: str
    items: list = field(default_factory=list)  # Task or str (a note line without "> ")


@dataclass
class Doc:
    title: str = "Tasks"
    sections: list[Section] = field(default_factory=list)


def parse(text: str, source: str = "input") -> Doc:
    doc, current, errors = Doc(), None, []
    seen_title = False
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith("# ") and not line.startswith("## "):
            if seen_title or doc.sections:
                errors.append(f"{source}:{n}: only one '# ' title, at the top")
            doc.title, seen_title = line[2:].strip() or "Tasks", True
            continue
        if line.startswith("## "):
            name = line[3:].strip()
            if not name:
                errors.append(f"{source}:{n}: section heading has no name")
                continue
            current = Section(name)
            doc.sections.append(current)
            continue
        if current is None:
            errors.append(f"{source}:{n}: put a '## Section' heading before tasks or notes")
            continue
        m = TASK_RE.match(line)
        if m:
            body, due = m.group(2), None
            dm = DUE_RE.search(body)
            if dm:
                due = dm.group(1).strip()
                body = DUE_RE.sub("", body).strip()
                try:
                    date.fromisoformat(due)
                except ValueError:
                    errors.append(f"{source}:{n}: due date must look like 2026-11-02, got '{due}'")
            if not body:
                errors.append(f"{source}:{n}: empty task")
                continue
            current.items.append(Task(body, m.group(1) in "xX", due))
            continue
        if line.startswith("> "):
            current.items.append(line[2:].strip())
            continue
        errors.append(f"{source}:{n}: not a task, note or heading: {line[:60]!r}")
    if errors:
        raise FormatError("\n".join(errors))
    return doc


def render(doc: Doc) -> str:
    out = [f"# {doc.title}"]
    for s in doc.sections:
        out += ["", f"## {s.name}"]
        out += [i.render() if isinstance(i, Task) else f"> {i}" for i in s.items]
    return "\n".join(out) + "\n"


def merge(old: Doc, new: Doc) -> tuple[Doc, dict]:
    stats = {"added": 0, "ticked": 0, "duplicates": 0, "notes": 0, "sections": 0}
    index: dict[str, Task] = {}
    for s in old.sections:
        for i in s.items:
            if isinstance(i, Task) and i.key not in index:
                index[i.key] = i
    by_name = {s.name.lower(): s for s in old.sections}
    created: list[Section] = []
    for ns in new.sections:
        target = by_name.get(ns.name.lower())
        if target is None:
            target = Section(ns.name)
            old.sections.append(target)
            by_name[ns.name.lower()] = target
            created.append(target)
        for item in ns.items:
            if isinstance(item, str):
                if item not in [x for x in target.items if isinstance(x, str)]:
                    target.items.append(item)
                    stats["notes"] += 1
                continue
            existing = index.get(item.key)
            if existing:
                stats["duplicates"] += 1
                if item.done and not existing.done:
                    existing.done = True
                    stats["ticked"] += 1
                if item.due and not existing.due:
                    existing.due = item.due
                continue
            task = Task(item.text, item.done, item.due)
            target.items.append(task)
            index[task.key] = task
            stats["added"] += 1
    for s in created:
        if not s.items:
            old.sections.remove(s)
            by_name.pop(s.name.lower(), None)
    stats["sections"] = sum(1 for s in created if s.items)
    return old, stats


def read(path: Path) -> Doc:
    try:
        return parse(path.read_text(encoding="utf-8"), str(path))
    except OSError as exc:
        raise SystemExit(f"Could not read {path}: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Merge a read-back page into tasks.md.")
    ap.add_argument("tasks", nargs="?", help="the running tasks.md (created if missing)")
    ap.add_argument("new", nargs="?", help="the new page, in the same format")
    ap.add_argument("--check", metavar="FILE", help="only validate this file")
    ap.add_argument("--dry-run", action="store_true", help="print the merged file, write nothing")
    a = ap.parse_args(argv)
    try:
        if a.check:
            doc = read(Path(a.check))
            count = sum(isinstance(i, Task) for s in doc.sections for i in s.items)
            print(f"OK: {a.check} has {len(doc.sections)} sections and {count} tasks.")
            return 0
        if not (a.tasks and a.new):
            ap.error("give tasks.md and new.md, or --check FILE")
        tasks_path = Path(a.tasks)
        old = read(tasks_path) if tasks_path.exists() else Doc()
        merged, stats = merge(old, read(Path(a.new)))
    except FormatError as exc:
        sys.stderr.write(f"Format problem, nothing written:\n{exc}\n")
        return 2
    text = render(merged)
    if a.dry_run:
        sys.stdout.write(text)
    else:
        tasks_path.write_text(text, encoding="utf-8")
    print(f"Merged into {a.tasks}: {stats['added']} added, {stats['ticked']} newly ticked, "
          f"{stats['duplicates']} already there, {stats['notes']} notes, {stats['sections']} new sections.",
          file=sys.stderr if a.dry_run else sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
