from __future__ import annotations

from collections import Counter


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def calculate_streak(daily_history):
    if not daily_history:
        return 0
    streak = 0
    for item in sorted(daily_history, key=lambda entry: entry.get('date', ''))[::-1]:
        value = safe_int(item.get('developer_commits') or item.get('commits') or 0)
        if value > 0:
            streak += 1
        else:
            break
    return streak


def summarize_language_share(repositories):
    counts = Counter()
    for repo in repositories:
        language = str(repo.get('language') or repo.get('primary_language') or 'Unknown').strip()
        if not language or language.lower() == 'unknown':
            continue
        counts[language] += 1
    total = sum(counts.values()) or 1
    rows = []
    for name, value in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        rows.append({"name": name, "count": value, "share": round((value / total) * 100, 2)})
    return rows


def compute_active_days(history):
    return sum(1 for item in history if safe_int(item.get('developer_commits') or item.get('commits') or 0) > 0)


def compute_core_repo_ratio(repositories):
    if not repositories:
        return 0.0
    total = sum(max(1, safe_int(repo.get('commits') or 0)) for repo in repositories)
    if total <= 0:
        return 0.0
    leader = max(repositories, key=lambda repo: safe_int(repo.get('commits') or 0))
    return round(safe_int(leader.get('commits') or 0) / total, 4)


def build_trend_history(daily_history):
    rows = []
    for item in sorted(daily_history, key=lambda entry: entry.get('date', '')):
        rows.append({
            'date': item.get('date'),
            'developer_commits': safe_int(item.get('developer_commits') or item.get('commits') or 0),
            'repositories_touched': safe_int(item.get('repositories_touched') or 0),
            'pull_requests': safe_int(item.get('pull_requests') or 0),
            'issues': safe_int(item.get('issues') or 0),
            'observed_push_events': safe_int(item.get('observed_push_events') or 0),
        })
    return rows
