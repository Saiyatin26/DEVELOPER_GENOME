from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from analyzer import build_trend_history, calculate_streak, compute_active_days, compute_core_repo_ratio, summarize_language_share
from collector import collect_daily_activity
from config import get_config, get_target_date_for_run
from genome import build_behavioral_genome, build_technical_genome
from insights import build_milestones, detect_evolution
from report import build_daily_markdown
from storage import write_daily_snapshot, write_json, write_report

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / 'data'
DASHBOARD_PATH = ROOT.parent / 'dashboard' / 'data.json'
CURRENT_SNAPSHOT_PATH = DATA_DIR / 'analytics_snapshot.json'


def _safe_iso(value: datetime | None) -> str:
    if value is None:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def _load_history():
    history_dir = DATA_DIR / 'daily'
    if not history_dir.exists():
        return []
    rows = []
    for item in sorted(history_dir.glob('*.json')):
        try:
            payload = json.loads(item.read_text(encoding='utf-8'))
            rows.append(payload)
        except Exception:
            continue
    return rows


def build_dashboard_payload(profile, current_genome, behavioral_genome, daily_activity, repositories, technology_history, milestones, insights, data_quality, analyzed_date):
    payload = {
        'schema_version': 1,
        'generated_at': _safe_iso(datetime.now(timezone.utc)),
        'timezone': 'Asia/Kolkata',
        'last_successful_analysis': _safe_iso(datetime.now(timezone.utc)),
        'analyzed_date': analyzed_date,
        'profile': profile,
        'current_genome': current_genome,
        'behavioral_genome': behavioral_genome,
        'daily_activity': daily_activity,
        'repositories': repositories,
        'technology_history': technology_history,
        'milestones': milestones,
        'insights': insights,
        'data_quality': data_quality,
        'status': 'ok' if data_quality.get('commit_collection') else 'partial',
    }
    return payload


def run_pipeline(username: str | None = None, target_date=None, token: str | None = None):
    config = get_config()
    username = username or config['github_username'] or None
    if not username or username in {'your_github_username', ''}:
        raise ValueError('Set GITHUB_USERNAME before running Developer Genome. Do not use fake values.')
    target_date = target_date or get_target_date_for_run(timezone_name=config['timezone'])
    daily_summary = collect_daily_activity(username, target_date, token=token, analytics_repo=config['analytics_repo'])

    history = _load_history()
    history.append(daily_summary)
    trend_history = build_trend_history(history)
    active_days = compute_active_days(history)
    streak = calculate_streak(history)
    repo_summary = [
        {
            'name': repo.get('name') or 'unknown',
            'language': repo.get('language') or 'Unknown',
            'commits': repo.get('commits') or 0,
            'pull_requests': repo.get('pull_requests') or 0,
            'issues': repo.get('issues') or 0,
            'stars': repo.get('stars') or 0,
            'last_activity': repo.get('last_activity'),
            'html_url': repo.get('html_url') or '',
            'topics': repo.get('topics') or [],
        }
        for repo in daily_summary.get('repositories', [])
    ]
    current_genome = build_technical_genome(repo_summary)
    behavioral_genome = build_behavioral_genome({
        'active_days': active_days,
        'streak_days': streak,
        'repositories_touched': len(repo_summary),
        'core_repo_ratio': compute_core_repo_ratio(repo_summary),
    })
    technology_history = [{
        'date': daily_summary.get('date'),
        'languages': summarize_language_share(repo_summary)
    }]
    milestone_rows = build_milestones(history)
    insight_rows = detect_evolution(history[:-1][-1] if len(history) > 1 else None, {
        'current_genome': current_genome,
        'daily_activity': trend_history,
    })

    payload = {
        'schema_version': 1,
        'generated_at': _safe_iso(datetime.now(timezone.utc)),
        'timezone': config['timezone'],
        'last_successful_analysis': _safe_iso(datetime.now(timezone.utc)),
        'analyzed_date': daily_summary.get('date'),
        'profile': {
            'name': username,
            'handle': f'@{username}',
            'location': 'Remote',
            'headline': 'Developer activity profile generated from real GitHub data.',
        },
        'current_genome': current_genome,
        'behavioral_genome': behavioral_genome,
        'daily_activity': trend_history,
        'repositories': repo_summary,
        'technology_history': technology_history,
        'milestones': milestone_rows,
        'insights': insight_rows,
        'data_quality': daily_summary.get('data_quality', {}),
        'summary': {
            'developer_commits': daily_summary.get('developer_commits'),
            'repositories_touched': daily_summary.get('repositories_touched'),
            'pull_requests': daily_summary.get('pull_requests'),
            'issues': daily_summary.get('issues'),
            'active_days': active_days,
            'streak_days': streak,
            'observed_push_events': daily_summary.get('observed_push_events'),
        },
    }

    write_daily_snapshot(daily_summary.get('date'), payload)
    CURRENT_SNAPSHOT_PATH.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    dashboard_payload = build_dashboard_payload(payload['profile'], payload['current_genome'], payload['behavioral_genome'], payload['daily_activity'], payload['repositories'], payload['technology_history'], payload['milestones'], payload['insights'], payload['data_quality'], payload['analyzed_date'])
    DASHBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_json(DASHBOARD_PATH, dashboard_payload)
    markdown = build_daily_markdown(payload['analyzed_date'], payload['summary'], payload['repositories'], daily_summary.get('commits', []), timezone_name=config['timezone'])
    write_report(payload['analyzed_date'], markdown)
    return payload


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate a real Developer Genome snapshot for the prior IST day.')
    parser.add_argument('--username', default=None, help='GitHub username to analyze')
    parser.add_argument('--date', default=None, help='Override target date in YYYY-MM-DD format')
    parser.add_argument('--token', default=None, help='Optional GitHub token')
    args = parser.parse_args()
    run_pipeline(username=args.username, target_date=None if not args.date else __import__('datetime').datetime.strptime(args.date, '%Y-%m-%d').date(), token=args.token)
