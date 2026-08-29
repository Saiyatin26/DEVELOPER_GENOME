from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib import error, request

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
INPUT_PATH = DATA_DIR / "sample_activity.json"
OUTPUT_PATH = DATA_DIR / "analytics_snapshot.json"
DEFAULT_USERNAME = "Saiyatin26"


def safe_float(value, default=0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_iso8601(value):
    if not value:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        try:
            return datetime.strptime(value[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
        except ValueError:
            return datetime.now(timezone.utc)


def github_request(url, token: str | None = None):
    headers = {"User-Agent": "DeveloperGenome/1.0", "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = request.Request(url, headers=headers)
    with request.urlopen(req, timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))


def get_github_token():
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or None


def fetch_repo_commit_count(username: str, repo_name: str):
    try:
        commits = github_request(f"https://api.github.com/repos/{username}/{repo_name}/commits?per_page=100", token=get_github_token())
        if isinstance(commits, list):
            return len(commits)
    except Exception:
        return 0
    return 0


def fetch_live_github_profile(username: str):
    try:
        token = get_github_token()
        user = github_request(f"https://api.github.com/users/{username}", token=token)
        repos = github_request(f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated", token=token)
        events = github_request(f"https://api.github.com/users/{username}/events/public?per_page=100", token=token)

        normalized_repos = []
        repo_push_map = defaultdict(int)
        for event in events or []:
            if event.get("type") == "PushEvent":
                repo_name = (event.get("repo", {}) or {}).get("name")
                if repo_name:
                    repo_push_map[repo_name] += len((event.get("payload", {}) or {}).get("commits") or [])

        for repo in repos:
            if repo.get("fork"):
                continue
            repo_name = repo.get("name")
            lang_name = (repo.get("language") or "").lower()
            languages = []
            if lang_name:
                languages.append(lang_name)
            if "javascript" in lang_name:
                languages.append("javascript")
            if "typescript" in lang_name:
                languages.append("typescript")
            visibility = "Private" if repo.get("private") else "Public"
            commit_count = fetch_repo_commit_count(username, repo_name) if repo_name else 0
            if repo_name and repo_name.lower().startswith(f"{username.lower()}/"):
                repo_key = repo_name
            else:
                repo_key = f"{username}/{repo_name}" if repo_name else None
            actual_push_count = repo_push_map.get(repo_key, repo_push_map.get(repo_name, 0)) if repo_key else 0
            if actual_push_count > 0:
                commit_count = actual_push_count
            normalized = {
                "name": repo_name,
                "description": repo.get("description") or ("Private repository" if repo.get("private") else "Public repository"),
                "primary_language": repo.get("language") or "Markdown",
                "languages": list(dict.fromkeys(languages)),
                "commits": commit_count or max(1, repo.get("open_issues_count", 0)),
                "pull_requests": max(0, repo.get("watchers_count", 0) // 8),
                "issues": max(0, repo.get("open_issues_count", 0) // 3),
                "stars": repo.get("stargazers_count", 0),
                "days_since_last_activity": max(0, (datetime.now(timezone.utc) - parse_iso8601(repo.get("pushed_at")).astimezone(timezone.utc)).days),
                "last_commit": repo.get("pushed_at", "")[:10],
                "weight": 1.2 if repo.get("stargazers_count", 0) > 10 else 0.8,
                "technologies": [repo.get("language") or "GitHub", "Code", "Automation"],
                "html_url": repo.get("html_url"),
                "private": bool(repo.get("private", False)),
                "visibility": visibility,
                "commit_count": commit_count,
                "push_count": actual_push_count,
                "access_note": "Private repo data requires a GitHub token" if repo.get("private") else "Public repo data is live from GitHub",
            }
            normalized_repos.append(normalized)

        return {
            "developer": {
                "name": user.get("name") or user.get("login"),
                "handle": f"@{user.get('login', username)}",
                "location": user.get("location") or "Remote",
                "headline": "Developer building software, automation, and product-focused engineering systems.",
            },
            "contributions": {
                "active_repositories": len(normalized_repos),
                "total_commits": sum(int(r.get("commit_count", r.get("commits", 0))) for r in normalized_repos),
                "pull_requests": sum(int(r.get("pull_requests", 0)) for r in normalized_repos),
                "issues_closed": sum(int(r.get("issues", 0)) for r in normalized_repos),
                "streak_days": min(90, max(7, len(normalized_repos) * 3)),
                "active_days": 120,
                "core_repo_ratio": 0.52,
            },
            "repositories": normalized_repos,
            "events": events,
        }
    except (error.URLError, ValueError, KeyError):
        return None


def compute_repo_health(repo):
    commits = int(repo.get("commit_count") or repo.get("commits", 0) or 0)
    prs = int(repo.get("pull_requests", 0) or 0)
    issues = int(repo.get("issues", 0) or 0)
    stars = int(repo.get("stars", 0) or 0)
    last_activity_days = int(repo.get("days_since_last_activity", 0) or 0)
    is_private = bool(repo.get("private", False))

    health = 42 + (commits * 0.9) + (prs * 5) + (issues * 3) + min(stars, 25) * 1.2
    if is_private:
        health += 8
    health -= max(0, last_activity_days - 7) * 0.8

    health = round(min(max(health, 25), 100), 1)
    return health


def calculate_technical_dna(repos):
    backend = 0
    frontend = 0
    data = 0
    algorithms = 0
    devops = 0

    for repo in repos:
        score = repo.get("weight", 1)
        langs = [str(lang).lower() for lang in repo.get("languages", [])]
        backend += score * (2 if any(term in langs for term in ["python", "go", "java", "node"]) else 0)
        frontend += score * (2 if any(term in langs for term in ["javascript", "typescript", "react", "vue"]) else 0)
        data += score * (2 if any(term in langs for term in ["sql", "python", "rust", "pandas"]) else 0)
        algorithms += score * (2 if any(term in langs for term in ["c++", "rust", "python", "java"]) else 0)
        devops += score * (2 if any(term in langs for term in ["docker", "yaml", "bash", "shell"]) else 0)

    total = max(1, backend + frontend + data + algorithms + devops)
    return {
        "Backend": round(min(100, (backend / total) * 100 + 35), 1),
        "Frontend": round(min(100, (frontend / total) * 100 + 28), 1),
        "Data": round(min(100, (data / total) * 100 + 31), 1),
        "Algorithms": round(min(100, (algorithms / total) * 100 + 22), 1),
        "DevOps": round(min(100, (devops / total) * 100 + 24), 1),
    }


def calculate_behavioral_dna(repos, contributions):
    active_days = contributions.get("active_days", 90)
    streak = contributions.get("streak_days", 18)
    repos_count = len(repos)
    focus = min(100, 25 + (contributions.get("core_repo_ratio", 0.45) * 75))
    persistence = min(100, 10 + (streak / 30) * 50 + (active_days / 180) * 30)
    consistency = min(100, 20 + (active_days / 120) * 60)
    exploration = min(100, 15 + (repos_count / 8) * 70)
    return {
        "Consistency": round(consistency, 1),
        "Exploration": round(exploration, 1),
        "Focus": round(focus, 1),
        "Persistence": round(persistence, 1),
    }


def build_daily_activity(events, days=30):
    daily = defaultdict(lambda: {"date": "", "commits": 0, "pull_requests": 0, "issues_closed": 0, "pushes": 0})
    valid_events = [event for event in (events or []) if event.get("created_at")]

    if valid_events:
        event_times = [parse_iso8601(event["created_at"]) for event in valid_events]
        start_date = min(event_times).date()
        end_date = max(event_times).date()
        if (end_date - start_date).days + 1 > days:
            start_date = end_date - timedelta(days=days - 1)
    else:
        end_date = datetime.now(timezone.utc).date()
        start_date = end_date - timedelta(days=days - 1)

    for event in valid_events:
        event_time = parse_iso8601(event.get("created_at"))
        if event_time.date() < start_date or event_time.date() > end_date:
            continue
        day_key = event_time.strftime("%Y-%m-%d")
        bucket = daily[day_key]
        bucket["date"] = day_key
        event_type = event.get("type")
        payload = event.get("payload", {})

        if event_type == "PushEvent":
            bucket["commits"] += len(payload.get("commits") or [])
            bucket["pushes"] += 1
        elif event_type == "PullRequestEvent":
            bucket["pull_requests"] += 1
        elif event_type == "IssuesEvent":
            if payload.get("action") in {"closed", "resolved"}:
                bucket["issues_closed"] += 1

    result = []
    current_day = start_date
    while current_day <= end_date:
        key = current_day.strftime("%Y-%m-%d")
        item = daily.get(key, {"date": key, "commits": 0, "pull_requests": 0, "issues_closed": 0, "pushes": 0})
        result.append({
            "date": item["date"],
            "commits": item["commits"],
            "pull_requests": item["pull_requests"],
            "issues_closed": item["issues_closed"],
            "pushes": item["pushes"],
        })
        current_day += timedelta(days=1)
    return result


def build_repo_activity_for_day(events, target_date=None):
    target_date = target_date or datetime.now(timezone.utc).date()
    repo_activity = defaultdict(lambda: {"repo": "", "commits": 0, "pull_requests": 0, "issues_closed": 0, "pushes": 0})

    for event in events or []:
        created_at = event.get("created_at")
        if not created_at:
            continue
        event_time = parse_iso8601(created_at)
        if event_time.date() != target_date:
            continue
        repo_name = (event.get("repo", {}) or {}).get("name") or "unknown"
        bucket = repo_activity[repo_name]
        bucket["repo"] = repo_name
        event_type = event.get("type")
        payload = event.get("payload", {})
        if event_type == "PushEvent":
            bucket["commits"] += len(payload.get("commits") or [])
            bucket["pushes"] += 1
        elif event_type == "PullRequestEvent":
            bucket["pull_requests"] += 1
        elif event_type == "IssuesEvent":
            if payload.get("action") in {"closed", "resolved"}:
                bucket["issues_closed"] += 1

    return [
        {
            "repo": summary["repo"],
            "commits": summary["commits"],
            "pull_requests": summary["pull_requests"],
            "issues_closed": summary["issues_closed"],
            "pushes": summary["pushes"],
        }
        for summary in sorted(repo_activity.values(), key=lambda item: (-item["commits"], -item["pull_requests"], item["repo"]))
    ]


def build_repo_push_summary(events):
    summary = defaultdict(lambda: {"repo": "", "commits": 0, "pushes": 0, "last_event": ""})
    for event in events or []:
        if event.get("type") != "PushEvent":
            continue
        repo_name = (event.get("repo", {}) or {}).get("name") or "unknown"
        bucket = summary[repo_name]
        bucket["repo"] = repo_name
        bucket["commits"] += len((event.get("payload", {}) or {}).get("commits") or [])
        bucket["pushes"] += 1
        bucket["last_event"] = event.get("created_at") or bucket["last_event"]
    return [
        {
            "repo": entry["repo"],
            "commits": entry["commits"],
            "pushes": entry["pushes"],
            "last_event": entry["last_event"],
        }
        for entry in sorted(summary.values(), key=lambda item: (-item["commits"], item["repo"]))
    ]


def add_months(base_date, months_delta):
    month = base_date.month - 1 + months_delta
    year = base_date.year + month // 12
    month = month % 12 + 1
    return base_date.replace(year=year, month=month)


def build_monthly_history(events, months=6):
    monthly = defaultdict(lambda: {"month": "", "commits": 0, "pull_requests": 0, "issues_closed": 0, "repo_count": set()})
    now = datetime.now(timezone.utc)
    start_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    for offset in range(months):
        target = add_months(start_month, -offset)
        key = target.strftime("%Y-%m")
        monthly[key].update({"month": key})

    for event in events or []:
        created_at = event.get("created_at")
        if not created_at:
            continue
        event_time = parse_iso8601(created_at)
        month_key = event_time.strftime("%Y-%m")
        if month_key not in monthly:
            continue
        bucket = monthly[month_key]
        event_type = event.get("type")
        payload = event.get("payload", {})
        repo_name = event.get("repo", {}).get("name")
        if repo_name:
            bucket["repo_count"].add(repo_name)
        if event_type == "PushEvent":
            bucket["commits"] += len(payload.get("commits") or [])
        elif event_type == "PullRequestEvent":
            bucket["pull_requests"] += 1
        elif event_type == "IssuesEvent":
            if payload.get("action") in {"closed", "resolved"}:
                bucket["issues_closed"] += 1

    ordered_keys = list(monthly.keys())
    result = []
    for key in sorted(ordered_keys):
        month_bucket = monthly[key]
        score = min(99, 55 + (month_bucket["commits"] * 0.6) + (month_bucket["pull_requests"] * 2) + (month_bucket["issues_closed"] * 1.8))
        result.append({
            "period": datetime.strptime(key + "-01", "%Y-%m-%d").strftime("%b"),
            "score": round(score, 1),
            "commits": month_bucket["commits"],
            "pr_count": month_bucket["pull_requests"],
            "repo_count": len(month_bucket["repo_count"]),
        })
    return result


def build_history(repos, events=None):
    events = events or []
    monthly = build_monthly_history(events, months=6)
    if monthly:
        return monthly
    base = [
        {"period": "Jan", "score": 64, "commits": 32, "pr_count": 7, "repo_count": 6},
        {"period": "Feb", "score": 68, "commits": 41, "pr_count": 9, "repo_count": 7},
        {"period": "Mar", "score": 72, "commits": 47, "pr_count": 10, "repo_count": 7},
        {"period": "Apr", "score": 76, "commits": 52, "pr_count": 11, "repo_count": 8},
        {"period": "May", "score": 81, "commits": 58, "pr_count": 13, "repo_count": 9},
        {"period": "Jun", "score": 86, "commits": 64, "pr_count": 14, "repo_count": 10},
    ]
    for idx, item in enumerate(base):
        repo_bonus = sum(min(2, repo.get("weight", 1)) for repo in repos[: max(1, idx + 1)])
        item["score"] = min(99, round(item["score"] + (repo_bonus * 1.5), 1))
        item["commits"] += repo_bonus * 5
    return base


def build_snapshot(username: str | None = None, use_live_data: bool = True):
    username = username or DEFAULT_USERNAME
    raw_data = None
    events = []

    if use_live_data:
        live_data = fetch_live_github_profile(username)
        if live_data:
            raw_data = live_data
            events = live_data.get("events", [])

    if raw_data is None:
        raw_data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
        events = []

    repos = raw_data.get("repositories", [])
    contributions = raw_data.get("contributions", {})
    repo_cards = []

    for repo in repos:
        repo_cards.append(
            {
                "name": repo.get("name"),
                "description": repo.get("description"),
                "language": repo.get("primary_language") or repo.get("language") or "Markdown",
                "stars": repo.get("stars", 0),
                "health": compute_repo_health(repo),
                "days_since_last_activity": repo.get("days_since_last_activity", 7),
                "last_commit": repo.get("last_commit"),
                "technologies": repo.get("technologies", []),
                "html_url": repo.get("html_url"),
            }
        )

    technical = calculate_technical_dna(repos)
    behavioral = calculate_behavioral_dna(repos, contributions)
    overall_score = round((sum(technical.values()) / len(technical) + sum(behavioral.values()) / len(behavioral)) / 2, 1)
    daily_activity = build_daily_activity(events, days=30)
    monthly_history = build_monthly_history(events, months=6)
    today_activity = build_repo_activity_for_day(events, datetime.now(timezone.utc).date())
    repo_push_summary = build_repo_push_summary(events)

    snapshot = {
        "developer": {
            "name": raw_data.get("developer", {}).get("name", "Alex Morgan"),
            "handle": raw_data.get("developer", {}).get("handle", f"@{username}"),
            "location": raw_data.get("developer", {}).get("location", "Remote"),
            "headline": raw_data.get("developer", {}).get("headline", "Developer building software and product experiences."),
        },
        "summary": {
            "active_repositories": contributions.get("active_repositories", len(repos)),
            "total_commits": contributions.get("total_commits", sum(max(1, r.get("commits", 1)) for r in repos)),
            "pull_requests": contributions.get("pull_requests", sum(int(r.get("pull_requests", 0)) for r in repos)),
            "issues_closed": contributions.get("issues_closed", sum(int(r.get("issues", 0)) for r in repos)),
            "current_streak": contributions.get("streak_days", 18),
            "overall_score": overall_score,
        },
        "technical_dna": technical,
        "behavioral_dna": behavioral,
        "history": build_history(repos, events),
        "monthly_history": monthly_history,
        "daily_activity": daily_activity,
        "today_activity": today_activity,
        "repo_push_summary": repo_push_summary,
        "repositories": repo_cards,
        "technology_mix": [
            {"name": "Python", "value": 32},
            {"name": "TypeScript", "value": 24},
            {"name": "Go", "value": 18},
            {"name": "SQL", "value": 15},
            {"name": "Docker", "value": 11},
        ],
        "milestones": [
            {"title": "Profile sync", "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "detail": f"GitHub sync collected live data for {username}."},
            {"title": "Monthly trend review", "date": (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d"), "detail": "Tracked the recent engineering velocity and pull request activity."},
            {"title": "Daily commit health", "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "detail": "Monitored live push activity and repository momentum."},
        ],
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    OUTPUT_PATH.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    return snapshot


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Developer Genome analytics from a GitHub profile.")
    parser.add_argument("--username", default=DEFAULT_USERNAME, help="GitHub username to fetch from")
    parser.add_argument("--offline", action="store_true", help="Use the sample data instead of the live GitHub API")
    args = parser.parse_args()

    snapshot = build_snapshot(username=args.username, use_live_data=not args.offline)
    print(f"Generated snapshot for {args.username} with overall score {snapshot['summary']['overall_score']}")
    print(f"Output: {OUTPUT_PATH}")
