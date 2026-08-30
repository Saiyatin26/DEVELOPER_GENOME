from __future__ import annotations


def detect_evolution(previous_snapshot: dict | None, latest_snapshot: dict) -> list[dict]:
    events = []
    if not previous_snapshot:
        return [{'title': 'Baseline established', 'detail': 'A first valid GitHub activity snapshot was created.', 'severity': 'info'}]
    prev_genome = previous_snapshot.get('current_genome', {})
    curr_genome = latest_snapshot.get('current_genome', {})
    for category in sorted(curr_genome.keys()):
        before = prev_genome.get(category, 0)
        after = curr_genome.get(category, 0)
        delta = after - before
        if abs(delta) >= 5:
            direction = 'increased' if delta > 0 else 'decreased'
            events.append({'title': f'{category} signal {direction}', 'detail': f'{category} moved from {before} to {after}.', 'severity': 'trend'})
    prev_days = previous_snapshot.get('daily_activity', [])
    curr_days = latest_snapshot.get('daily_activity', [])
    prev_commits = sum(int(day.get('developer_commits') or 0) for day in prev_days)
    curr_commits = sum(int(day.get('developer_commits') or 0) for day in curr_days)
    if curr_commits > prev_commits:
        events.append({'title': 'Activity acceleration', 'detail': f'Current commit volume increased from {prev_commits} to {curr_commits}.', 'severity': 'positive'})
    return events or [{'title': 'Stable activity', 'detail': 'No major changes were detected against the prior snapshot.', 'severity': 'neutral'}]


def build_milestones(history):
    items = []
    total_commits = sum(int(day.get('developer_commits') or 0) for day in history)
    active_days = sum(1 for day in history if int(day.get('developer_commits') or 0) > 0)
    if total_commits >= 100:
        items.append({'title': '100+ commits', 'detail': 'Developer activity has crossed 100 qualifying commits.', 'date': history[-1].get('date') if history else 'n/a'})
    if active_days >= 30:
        items.append({'title': '30 active days', 'detail': 'The developer has achieved at least 30 active days.', 'date': history[-1].get('date') if history else 'n/a'})
    if not items:
        items.append({'title': 'Data collection started', 'detail': 'The analytics pipeline is recording real GitHub activity.', 'date': history[-1].get('date') if history else 'n/a'})
    return items
