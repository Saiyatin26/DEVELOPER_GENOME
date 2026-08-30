from __future__ import annotations


def build_daily_markdown(date_label: str, summary: dict, repositories: list[dict], commits: list[dict] | None = None, timezone_name: str = "Asia/Kolkata"):
    repo_lines = []
    for repo in repositories:
        repo_name = repo.get("name", "unknown")
        repo_commits = repo.get("commits", 0)
        repo_lines.append(f"### {repo_name}\n{repo_commits} commits\n")

    commit_lines = []
    for commit in commits or []:
        message = commit.get("message", "No message")
        sha = (commit.get("sha") or "")[:7]
        timestamp = commit.get("committed_at") or commit.get("authored_at") or "unknown"
        repo_name = commit.get("repository", "unknown")
        commit_lines.append(f"- {repo_name}: {message} ({sha}) at {timestamp}\n")

    summary_text = (
        f"Commits: {summary.get('developer_commits', summary.get('commits', 0))}\n"
        f"Repositories touched: {summary.get('repositories_touched', 0)}\n"
        f"PRs: {summary.get('pull_requests', 0)}\n"
        f"Issues: {summary.get('issues', 0)}\n"
        f"Observed push events: {summary.get('observed_push_events', 'Unavailable')}\n"
    )

    if summary.get("developer_commits", 0) == 0:
        summary_text += "NO COMMITS ON THIS DATE\n"

    markdown = f"""# Developer Genome Daily Report
Date: {date_label}
Timezone: {timezone_name}

## Summary

{summary_text}

## Repositories

{''.join(repo_lines) if repo_lines else 'NO COMMITS ON THIS DATE - no qualifying developer commits were recorded.'}

## Commits

{''.join(commit_lines) if commit_lines else 'NO COMMITS ON THIS DATE. The system maintenance commit is excluded from personal activity and is shown separately as automation activity if present.'}

## Data Quality

- Commit collection: live GitHub API with since/until filtering and author filtering.
- Push-event count: public events only when available; partial if GitHub retention limits access.
- System automation: excluded from personal activity by repository and bot actor checks.
- No silent sample-data fallback is used in production.
"""
    return markdown
