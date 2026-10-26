"""A tiny iCalendar (RFC 5545) writer for all-day events. No dependencies."""
from __future__ import annotations

import hashlib
from datetime import date, datetime, timedelta, timezone


def escape(text: str) -> str:
    return (text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")
            .replace("\r\n", "\\n").replace("\n", "\\n"))


def fold(line: str) -> str:
    """Fold to 75 octets per line, continuation lines start with one space."""
    raw = line.encode("utf-8")
    if len(raw) <= 75:
        return line
    parts, cur = [], b""
    for ch in line:
        b = ch.encode("utf-8")
        limit = 75 if not parts else 74
        if len(cur) + len(b) > limit:
            parts.append(cur.decode("utf-8"))
            cur = b""
        cur += b
    parts.append(cur.decode("utf-8"))
    return "\r\n ".join(parts)


def calendar(name: str, events: list[dict], stamp: datetime | None = None) -> str:
    """events: dicts with day (date), summary, optional description and category."""
    stamp = (stamp or datetime.now(timezone.utc)).strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Rocha Coded//analog-bag//EN",
             "CALSCALE:GREGORIAN", "METHOD:PUBLISH", f"X-WR-CALNAME:{escape(name)}"]
    for ev in events:
        day: date = ev["day"]
        uid_src = f"{name}|{day.isoformat()}|{ev['summary']}"
        uid = hashlib.sha1(uid_src.encode("utf-8")).hexdigest()[:20] + "@analog-bag"
        lines += ["BEGIN:VEVENT", f"UID:{uid}", f"DTSTAMP:{stamp}",
                  f"DTSTART;VALUE=DATE:{day.strftime('%Y%m%d')}",
                  f"DTEND;VALUE=DATE:{(day + timedelta(days=1)).strftime('%Y%m%d')}",
                  f"SUMMARY:{escape(ev['summary'])}", "TRANSP:TRANSPARENT"]
        if ev.get("description"):
            lines.append(f"DESCRIPTION:{escape(ev['description'])}")
        if ev.get("category"):
            lines.append(f"CATEGORIES:{escape(ev['category'])}")
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return "\r\n".join(fold(x) for x in lines) + "\r\n"
