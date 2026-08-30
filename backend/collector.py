from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from config import get_config, get_daily_window
from github_client import GitHubClient

SYSTEM_REPO_NAMES = {"developer-genome", "developer_genome", "developer genome"}
SYSTEM_ACTORS = {"github-actions[bot]", "dependabot[bot]", "renovate[bot]", "web-flow", "github-actions-bot"}


def _in_system_activity(repo_name: str | None, actor: str | None) -> bool:
    repo_key = (repo_name or "").lower()
    actor_key = (actor or "").lower()
    if repo_key in SYSTEM_REPO_NAMES:
        return True
    if actor_key in {name.lower() for name in SYSTEM_ACTORS}:
        return True
    if "bot" in actor_key:
        return True
    return False


def _as_utc(value: str | None):
    if not value:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        try:
            return datetime.strptime(value[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
        except ValueError:
            return datetime.now(timezone.utc)


def _build_commit_record(commit: dict, repo_name: str, username: str):
    commit_info = commit.get("commit") or {}
    author_info = commit.get("author") or {}
    author_login = author_info.get("login") or commit_info.get("author", {}).get("name") or "unknown"
    committer = (commit.get("committer") or {}).get("login") or commit_info.get("committer", {}).get("name") or "unknown"
    timestamp = commit_info.get("author", {}).get("date") or commit_info.get("committer", {}).get("date") or ""
    stat = commit.get("stats") or {}
    return {
        "sha": commit.get("sha") or "",
        "repository": repo_name,
        "message": (commit_info.get("message") or "").strip() or "No commit message",
        "author": author_login,
        "committer": committer,
        "authored_at": timestamp,
        "committed_at": timestamp,
        "html_url": commit.get("html_url") or "",
        "additions": int(stat.get("additions") or 0),
        "deletions": int(stat.get("deletions") or 0),
        "changed_files": int(stat.get("total") or 0),
        "in_system_repo": repo_name.lower() in SYSTEM_REPO_NAMES,
    }


def collect_daily_activity(username: str, target_date, token: str | None = None, analytics_repo: str | None = None):
    config = get_config()
    username = username or config["github_username"]
    if not username:
        raise ValueError("GitHub username is required. Do not use a dummy or sample username.")
    analytics_repo_name = (analytics_repo or config["analytics_repo"] or "developer-genome").lower()
    client = GitHubClient(token=token or config.get("token"))
    start_utc, end_utc = get_daily_window(target_date, config["timezone"])
    start_iso = start_utc.isoformat().replace("+00:00", "Z")
    end_iso = end_utc.isoformat().replace("+00:00", "Z")

    repos = client.list_user_repos(username, per_page=100)
    if not isinstance(repos, list):
        raise RuntimeError(f"GitHub API returned unexpected repository payload for {username}: {repos!r}")

    repo_commit_map = defaultdict(list)
    commit_rows = []
    repository_rows = []

    for repo in repos:
        repo_name = repo.get("name")
        if not repo_name:
            continue
        if repo_name.lower() == analytics_repo_name:
            continue
        try:
            commits = client.list_repo_commits(username, repo_name, since=start_iso, until=end_iso, author=username)
        except RuntimeError:
            commits = []
        filtered = []
        for commit in commits:
            if not isinstance(commit, dict):
                continue
            record = _build_commit_record(commit, repo_name, username)
            actor = record.get("committer") or record.get("author") or ""
            if _in_system_activity(repo_name, actor):
                continue
            if record.get("author", "").lower() != username.lower() and record.get("committer", "").lower() != username.lower():
                continue
            filtered.append(record)
        repo_commit_map[repo_name] = filtered
        commit_rows.extend(filtered)
        if filtered:
            repository_rows.append({
                "name": repo_name,
                "full_name": repo.get("full_name") or f"{username}/{repo_name}",
                "description": repo.get("description") or "Repository activity",
                "html_url": repo.get("html_url") or "",
                "language": repo.get("language") or "Unknown",
                "topics": repo.get("topics") or [],
                "stars": int(repo.get("stargazers_count") or 0),
                "commits": len(filtered),
                "pull_requests": 0,
                "issues": 0,
                "last_activity": max((item["committed_at"] for item in filtered), default=""),
                "commit_records": filtered,
            })

    try:
        public_events = client.list_public_events(username, per_page=100)
        observed_push_events = 0
        for event in public_events or []:
            if event.get("type") != "PushEvent":
                continue
            created_at = event.get("created_at")
            if not created_at:
                continue
            event_dt = _as_utc(created_at)
            if start_utc <= event_dt <= end_utc:
                observed_push_events += 1
    except RuntimeError:
        observed_push_events = None

    try:
        pr_results = client.search_issues(f'author:{username} is:pr created:{target_date.isoformat()}..{target_date.isoformat()}', per_page=100)
        pr_records = pr_results.get("items", []) if isinstance(pr_results, dict) else []
    except RuntimeError:
        pr_records = []

    try:
        issue_results = client.search_issues(f'author:{username} is:issue created:{target_date.isoformat()}..{target_date.isoformat()}', per_page=100)
        issue_records = issue_results.get("items", []) if isinstance(issue_results, dict) else []
    except RuntimeError:
        issue_records = []

    for repo in repository_rows:
        repo_name = repo["name"]
        pr_count = 0
        issue_count = 0
        for item in pr_records:
            if (item.get("repository_url") or "").rstrip("/").split("/")[-1] == repo_name:
                pr_count += 1
        for item in issue_records:
            if (item.get("repository_url") or "").rstrip("/").split("/")[-1] == repo_name:
                issue_count += 1
        repo["pull_requests"] = pr_count
        repo["issues"] = issue_count

    return {
        "date": target_date.isoformat(),
        "timezone": config["timezone"],
        "developer_commits": len(commit_rows),
        "repositories_touched": len(repository_rows),
        "pull_requests": len(pr_records),
        "issues": len(issue_records),
        "observed_push_events": observed_push_events,
        "no_activity": len(commit_rows) == 0,
        "repositories": repository_rows,
        "commits": commit_rows,
        "data_quality": {
            "commit_collection": "live-github-api",
            "push_event_source": "public-events" if observed_push_events is not None else "partial",
            "observed_push_events": observed_push_events,
            "notes": "Commit collection uses GitHub API date filters, author filtering, and pagination. Push-event counts are from public event data and may be partial because of GitHub retention limits.",
            "automation_exclusions": sorted(SYSTEM_ACTORS),
        },
    }
