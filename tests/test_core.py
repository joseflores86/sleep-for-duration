import unittest

from sleep_for_duration import parse_duration, sleep_for
from sleep_for_duration.core import InvalidDurationError


class TestParseDuration(unittest.TestCase):
    def test_seconds(self):
        self.assertEqual(parse_duration("5s"), 5.0)

    def test_minutes(self):
        self.assertEqual(parse_duration("2m"), 120.0)

    def test_hours(self):
        self.assertEqual(parse_duration("1h"), 3600.0)

    def test_days(self):
        self.assertEqual(parse_duration("3d"), 259200.0)

    def test_milliseconds(self):
        self.assertEqual(parse_duration("100ms"), 0.1)

    def test_fractional_value(self):
        self.assertEqual(parse_duration("1.5h"), 5400.0)

    def test_uppercase_unit(self):
        self.assertEqual(parse_duration("2M"), 120.0)

    def test_whitespace_around_value(self):
        self.assertEqual(parse_duration("  5s  "), 5.0)

    def test_whitespace_between_number_and_unit(self):
        self.assertEqual(parse_duration("5 s"), 5.0)

    def test_no_unit_means_seconds(self):
        self.assertEqual(parse_duration("10"), 10.0)

    def test_empty_string_raises(self):
        with self.assertRaises(InvalidDurationError):
            parse_duration("")

    def test_whitespace_only_raises(self):
        with self.assertRaises(InvalidDurationError):
            parse_duration("   ")

    def test_unknown_unit_raises(self):
        with self.assertRaises(InvalidDurationError):
            parse_duration("5x")

    def test_no_number_raises(self):
        with self.assertRaises(InvalidDurationError):
            parse_duration("s")

    def test_negative_raises(self):
        with self.assertRaises(InvalidDurationError):
            parse_duration("-5s")

    def test_non_string_raises(self):
        with self.assertRaises(InvalidDurationError):
            parse_duration(5)


class TestSleepFor(unittest.TestCase):
    def test_calls_sleeper_with_parsed_seconds(self):
        calls = []

        def fake_sleeper(seconds):
            calls.append(seconds)

        result = sleep_for("5s", sleeper=fake_sleeper)
        self.assertEqual(calls, [5.0])
        self.assertEqual(result, 5.0)

    def test_returns_parsed_seconds_without_sleeping_by_default(self):
        # We pass a fake sleeper so no real sleep happens. We assert only on
        # the value the sleeper received, never on wall-clock time.
        received = []
        sleep_for("250ms", sleeper=lambda s: received.append(s))
        self.assertEqual(received, [0.25])

    def test_invalid_duration_raises_before_sleeping(self):
        called = []
        with self.assertRaises(InvalidDurationError):
            sleep_for("abc", sleeper=lambda s: called.append(s))
        self.assertEqual(called, [])


if __name__ == "__main__":
    unittest.main()
