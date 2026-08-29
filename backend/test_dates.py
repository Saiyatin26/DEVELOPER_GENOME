import unittest
from datetime import datetime, timezone

from config import get_target_date_for_run


class DateValidationTests(unittest.TestCase):
    def test_target_date_rolls_back_one_day_in_ist(self):
        now_utc = datetime(2026, 8, 29, 8, 0, tzinfo=timezone.utc)
        result = get_target_date_for_run(now_utc=now_utc, timezone_name="Asia/Kolkata")
        self.assertEqual(str(result), "2026-08-28")

    def test_target_date_uses_previous_calendar_day(self):
        now_utc = datetime(2026, 8, 29, 0, 30, tzinfo=timezone.utc)
        result = get_target_date_for_run(now_utc=now_utc, timezone_name="Asia/Kolkata")
        self.assertEqual(str(result), "2026-08-28")


if __name__ == "__main__":
    unittest.main()
