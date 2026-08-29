import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from analytics_engine import build_daily_activity, build_monthly_history


class GithubPipelineTests(unittest.TestCase):
    def test_build_daily_activity_groups_events_by_day(self):
        events = [
            {"created_at": "2026-08-10T10:00:00Z", "type": "PushEvent", "payload": {"commits": [{}, {}]}},
            {"created_at": "2026-08-10T15:00:00Z", "type": "PullRequestEvent"},
            {"created_at": "2026-08-11T08:00:00Z", "type": "PushEvent", "payload": {"commits": [{}]}},
            {"created_at": "2026-08-11T09:00:00Z", "type": "IssuesEvent", "payload": {"action": "closed"}},
        ]

        result = build_daily_activity(events, days=30)
        self.assertEqual(result[0]["date"], "2026-08-10")
        self.assertEqual(result[0]["commits"], 2)
        self.assertEqual(result[0]["pull_requests"], 1)
        self.assertEqual(result[0]["issues_closed"], 0)

    def test_build_monthly_history_uses_last_six_months(self):
        events = [
            {"created_at": "2026-08-12T10:00:00Z", "type": "PushEvent", "payload": {"commits": [{}, {}]}},
            {"created_at": "2026-07-15T10:00:00Z", "type": "PushEvent", "payload": {"commits": [{}]}},
            {"created_at": "2026-04-10T10:00:00Z", "type": "PullRequestEvent"},
        ]

        result = build_monthly_history(events)
        self.assertTrue(any(item["period"] == "Aug" for item in result))
        self.assertTrue(any(item["period"] == "Jul" for item in result))
        self.assertTrue(all(item["commits"] >= 0 for item in result))


if __name__ == "__main__":
    unittest.main()
