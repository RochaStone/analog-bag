"""Small date utilities shared by the launch calendar and the pocket week."""
from __future__ import annotations

import re
from datetime import date, datetime, timedelta


def parse_date(text: str) -> date:
    try:
        return date.fromisoformat(text)
    except ValueError as exc:
        raise SystemExit(f"Dates look like 2026-11-02. Got: {text}") from exc


def parse_offset(text: str | None) -> timedelta:
    """'+08:00', '-5', '+5:30', 'utc' or None (this computer's offset)."""
    if not text:
        off = datetime.now().astimezone().utcoffset()
        return off or timedelta(0)
    if text.lower() in ("utc", "z", "0"):
        return timedelta(0)
    m = re.fullmatch(r"([+-])?(\d{1,2})(?::?(\d{2}))?", text.strip())
    if not m:
        raise SystemExit(f"UTC offset looks like +08:00 or -5. Got: {text}")
    sign = -1 if m.group(1) == "-" else 1
    hours, mins = int(m.group(2)), int(m.group(3) or 0)
    if hours > 14 or mins >= 60:
        raise SystemExit(f"UTC offset out of range: {text}")
    return sign * timedelta(hours=hours, minutes=mins)


def offset_label(off: timedelta) -> str:
    total = int(off.total_seconds() // 60)
    sign = "+" if total >= 0 else "-"
    total = abs(total)
    return f"UTC{sign}{total // 60:02d}:{total % 60:02d}"


def nice(d: date) -> str:
    return f"{d.strftime('%a')} {d.day} {d.strftime('%b')}"
