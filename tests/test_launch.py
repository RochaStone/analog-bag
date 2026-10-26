"""Launch arc and the .ics it writes, checked with a tiny independent parser."""
import re
import tempfile
import contextlib
import io
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import launch as L


def unfold(text):
    return re.sub(r"\r\n[ \t]", "", text)


def parse_ics(text):
    """Minimal RFC 5545 reader: checks CRLF, line length, BEGIN/END nesting and
    returns a list of VEVENT property dicts."""
    assert "\r\n" in text, "lines must end in CRLF"
    for raw in text.split("\r\n"):
        assert len(raw.encode("utf-8")) <= 75, f"line longer than 75 octets: {raw!r}"
    stack, events, cur = [], [], None
    for line in unfold(text).split("\r\n"):
        if not line:
            continue
        name, _, value = line.partition(":")
        key = name.split(";")[0]
        if key == "BEGIN":
            stack.append(value)
            if value == "VEVENT":
                cur = {}
        elif key == "END":
            assert stack and stack[-1] == value, f"END:{value} without BEGIN"
            stack.pop()
            if value == "VEVENT":
                events.append(cur)
                cur = None
        elif cur is not None:
            cur[key] = (name, value)
    assert not stack, f"unclosed: {stack}"
    return events


def quiet(fn, args):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(args)


class LaunchTests(unittest.TestCase):
    def setUp(self):
        self.p = L.plan("Spring Breath Retreat", date(2026, 11, 2), 6, timedelta(0))

    def test_six_stages_in_order_inside_window(self):
        st = self.p["stages"]
        self.assertEqual([s["key"] for s in st], ["seed", "build", "open", "peak", "close", "integrate"])
        for a, b in zip(st, st[1:]):
            self.assertLess(a["start"], b["start"])
            self.assertEqual(a["end"] + timedelta(days=1), b["start"])
        self.assertEqual(st[0]["start"], date(2026, 11, 2))
        self.assertEqual(st[-1]["end"], date(2026, 12, 13))
        for s in st:
            self.assertIn(len(s["beats"]), (2, 3))
            for b in s["beats"]:
                self.assertTrue(s["start"] <= b["day"] <= s["end"])

    def test_stages_snap_to_real_phases(self):
        by = {s["key"]: s for s in self.p["stages"]}
        self.assertEqual(by["peak"]["anchor"], "full moon")
        self.assertEqual(by["peak"]["start"], date(2026, 11, 24))  # NASA: full moon 24 Nov 14:53 UT
        self.assertEqual(by["build"]["start"], date(2026, 11, 9))   # NASA: new moon 9 Nov 07:02 UT

    def test_offset_moves_dates(self):
        east = L.plan("X", date(2026, 11, 2), 6, timedelta(hours=10))
        full = [p for p in east["phases"] if p["name"] == "full moon"][0]
        self.assertEqual(full["day"], date(2026, 11, 25))  # 14:53 UT is past midnight at UTC+10

    def test_seasons_flag_in_window(self):
        p = L.plan("X", date(2026, 12, 1), 6, timedelta(0))
        inside = [s for s in p["seasons"] if s["in_window"]]
        self.assertEqual([s["name"] for s in inside], ["December solstice"])

    def test_weeks_bounds(self):
        for w in (4, 8, 12):
            p = L.plan("X", date(2026, 3, 1), w, timedelta(0))
            self.assertEqual(p["stages"][-1]["end"], date(2026, 3, 1) + timedelta(days=w * 7 - 1))
        with self.assertRaises(SystemExit):
            L.plan("X", date(2026, 3, 1), 2, timedelta(0))

    def test_ics_parses_and_counts(self):
        text = L.to_ics(self.p, datetime(2026, 10, 26, tzinfo=timezone.utc))
        self.assertTrue(text.startswith("BEGIN:VCALENDAR\r\nVERSION:2.0"))
        events = parse_ics(text)
        beats = sum(len(s["beats"]) for s in self.p["stages"])
        self.assertEqual(len(events), beats + len(self.p["phases"]))
        uids = set()
        for ev in events:
            for k in ("UID", "DTSTAMP", "DTSTART", "DTEND", "SUMMARY"):
                self.assertIn(k, ev)
            self.assertEqual(ev["DTSTART"][0], "DTSTART;VALUE=DATE")
            self.assertRegex(ev["DTSTART"][1], r"^\d{8}$")
            uids.add(ev["UID"][1])
        self.assertEqual(len(uids), len(events))
        self.assertTrue(any(ev["SUMMARY"][1] == "Full moon" for ev in events))

    def test_ics_escaping(self):
        p = L.plan("Moon; Money, and Magic", date(2026, 11, 2), 6, timedelta(0))
        events = parse_ics(L.to_ics(p))
        self.assertIn(r"Moon\; Money\, and Magic", events[0]["SUMMARY"][1])

    def test_outputs_written(self):
        with tempfile.TemporaryDirectory() as d:
            quiet(L.main, ["--offer", "Retreat", "--date", "2026-11-02", "--out", d,
                    "--utc-offset", "+08:00", "--html-only"])
            for f in ("launch.ics", "launch.html", "launch.md"):
                self.assertTrue((Path(d) / f).stat().st_size > 500, f)
            md = (Path(d) / "launch.md").read_text()
            self.assertIn("- [ ] open the doors {due:", md)


if __name__ == "__main__":
    unittest.main()
