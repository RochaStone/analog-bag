"""Moon phases and seasons against published 2026 values.

Moon phase reference: NASA GSFC, "Phases of the Moon: 2001 to 2100" (Espenak),
https://eclipse.gsfc.nasa.gov/phase/phases2001.html, times in UT.
The full moons of 3 Mar and 28 Aug 2026 are also lunar eclipses, and the new moons
of 17 Feb and 12 Aug 2026 are solar eclipses (NASA eclipse catalogue), which makes
them easy to cross-check in any almanac.
Season reference: the UT table in Wikipedia's "Equinox" and "Solstice" articles
(sourced from USNO data): 20 Mar 14:46, 21 Jun 08:25, 23 Sep 00:06, 21 Dec 20:50.
"""
import unittest
from datetime import datetime, timedelta, timezone

from core.moon import illumination, moon_age, phases_between, seasons

UTC = timezone.utc
NASA_2026_FULL = [
    (1, 3, 10, 3), (2, 1, 22, 9), (3, 3, 11, 38), (4, 2, 2, 12), (5, 1, 17, 23),
    (5, 31, 8, 45), (6, 29, 23, 57), (7, 29, 14, 36), (8, 28, 4, 18), (9, 26, 16, 49),
    (10, 26, 4, 12), (11, 24, 14, 53), (12, 24, 1, 28),
]
NASA_2026_NEW = [(2, 17, 12, 1), (8, 12, 17, 37), (10, 10, 15, 50)]
NASA_2026_QUARTERS = [("first quarter", 3, 25, 19, 18), ("last quarter", 11, 1, 20, 28)]
SEASONS_2026 = [(3, 20, 14, 46), (6, 21, 8, 25), (9, 23, 0, 6), (12, 21, 20, 50)]


def year_phases(name):
    ps = phases_between(datetime(2026, 1, 1, tzinfo=UTC), datetime(2027, 1, 1, tzinfo=UTC))
    return [t for n, t in ps if n == name]


class MoonTests(unittest.TestCase):
    def assert_close(self, got, want, minutes):
        self.assertLessEqual(abs((got - want).total_seconds()) / 60, minutes, f"{got} vs {want}")

    def test_full_moons_2026_within_one_day(self):
        got = year_phases("full moon")
        self.assertEqual(len(got), 13)  # 2026 has a blue moon on 31 May
        for g, (m, d, h, mi) in zip(got, NASA_2026_FULL):
            self.assertLess(abs(g - datetime(2026, m, d, h, mi, tzinfo=UTC)), timedelta(days=1))

    def test_full_moons_2026_within_two_minutes(self):
        for g, (m, d, h, mi) in zip(year_phases("full moon"), NASA_2026_FULL):
            self.assert_close(g, datetime(2026, m, d, h, mi, tzinfo=UTC), 2)

    def test_eclipse_new_moons_and_quarters(self):
        news = year_phases("new moon")
        for m, d, h, mi in NASA_2026_NEW:
            want = datetime(2026, m, d, h, mi, tzinfo=UTC)
            self.assert_close(min(news, key=lambda t: abs(t - want)), want, 2)
        for name, m, d, h, mi in NASA_2026_QUARTERS:
            want = datetime(2026, m, d, h, mi, tzinfo=UTC)
            self.assert_close(min(year_phases(name), key=lambda t: abs(t - want)), want, 2)

    def test_phase_order_and_count(self):
        ps = phases_between(datetime(2026, 1, 1, tzinfo=UTC), datetime(2027, 1, 1, tzinfo=UTC))
        self.assertEqual(len(ps), 50)
        names = [n for n, _ in ps]
        cycle = ["new moon", "first quarter", "full moon", "last quarter"]
        start = cycle.index(names[0])
        for i, n in enumerate(names):
            self.assertEqual(n, cycle[(start + i) % 4])

    def test_seasons_2026(self):
        for (name, feel, got), (m, d, h, mi) in zip(seasons(2026), SEASONS_2026):
            self.assert_close(got, datetime(2026, m, d, h, mi, tzinfo=UTC), 5)
        self.assertEqual(seasons(2026, "south")[0][1], "autumn equinox")

    def test_moon_age(self):
        full = datetime(2026, 10, 26, 4, 12, tzinfo=UTC)
        self.assertAlmostEqual(moon_age(full), 0.5, delta=0.03)
        self.assertGreater(illumination(moon_age(full)), 0.99)
        self.assertLess(moon_age(datetime(2026, 10, 10, 16, 0, tzinfo=UTC)), 0.01)

    def test_other_years_still_sane(self):
        for year in (2025, 2030, 2040):
            ps = phases_between(datetime(year, 1, 1, tzinfo=UTC), datetime(year + 1, 1, 1, tzinfo=UTC))
            gaps = [(b[1] - a[1]).total_seconds() / 86400 for a, b in zip(ps, ps[1:])]
            self.assertTrue(all(6.0 < g < 8.8 for g in gaps), year)


if __name__ == "__main__":
    unittest.main()
