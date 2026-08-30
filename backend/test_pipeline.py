import json
from datetime import datetime, timezone

from analyzer import calculate_streak, summarize_language_share
from config import get_target_date_for_run
from genome import build_technical_genome, build_behavioral_genome
from main import build_dashboard_payload


def test_get_target_date_for_run_targets_previous_day():
    now_utc = datetime(2026, 8, 30, 8, 0, tzinfo=timezone.utc)
    assert get_target_date_for_run(now_utc=now_utc, timezone_name='Asia/Kolkata') == datetime(2026, 8, 29, 0, 0).date()


def test_calculate_streak_counts_only_real_activity_dates():
    history = [
        {'date': '2026-08-27', 'developer_commits': 2},
        {'date': '2026-08-28', 'developer_commits': 0},
        {'date': '2026-08-29', 'developer_commits': 3},
        {'date': '2026-08-30', 'developer_commits': 4},
    ]
    assert calculate_streak(history) == 2


def test_zero_activity_day_is_explicit():
    summary = {'developer_commits': 0, 'repositories_touched': 0, 'pull_requests': 0, 'issues': 0}
    assert summary['developer_commits'] == 0
    assert summary['repositories_touched'] == 0


def test_language_share_is_normalized():
    repos = [
        {'language': 'Python', 'size': 100},
        {'language': 'JavaScript', 'size': 50},
        {'language': 'Python', 'size': 50},
    ]
    shares = summarize_language_share(repos)
    values = [entry['share'] for entry in shares]
    assert round(sum(values), 2) == 100.0


def test_genome_scores_are_bounded_and_documented():
    tech = build_technical_genome([
        {'language': 'Python'},
        {'language': 'React'},
        {'language': 'Dockerfile'},
        {'language': 'SQL'},
    ])
    behavioral = build_behavioral_genome({'active_days': 20, 'streak_days': 8, 'repositories_touched': 4, 'core_repo_ratio': 0.45})
    assert all(0 <= value <= 100 for value in tech.values())
    assert all(0 <= value <= 100 for value in behavioral.values())


def test_dashboard_schema_includes_generated_data_fields():
    payload = build_dashboard_payload(
        profile={'name': 'Demo Dev', 'handle': '@demo'},
        current_genome={'Backend': 80, 'Frontend': 70, 'Data': 60, 'Algorithms': 50, 'DevOps': 65},
        behavioral_genome={'Consistency': 70, 'Exploration': 65, 'Focus': 75, 'Persistence': 60},
        daily_activity=[{'date': '2026-08-29', 'developer_commits': 3, 'repositories_touched': 1}],
        repositories=[{'name': 'demo-repo', 'health_score': 85, 'commits': 3}],
        technology_history=[],
        milestones=[],
        insights=[],
        data_quality={'commit_collection': 'live-api'},
        analyzed_date='2026-08-29',
    )
    required = {'schema_version', 'generated_at', 'timezone', 'last_successful_analysis', 'analyzed_date', 'profile', 'current_genome', 'behavioral_genome', 'daily_activity', 'repositories', 'technology_history', 'milestones', 'insights', 'data_quality'}
    assert required.issubset(payload.keys())
    assert payload['analyzed_date'] == '2026-08-29'
    assert payload['daily_activity'][0]['developer_commits'] == 3
