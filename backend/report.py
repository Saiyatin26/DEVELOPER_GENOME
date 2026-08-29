from __future__ import annotations


def build_daily_markdown(date_label: str, summary: dict, repositories: list[dict], commits: list[dict] | None = None):
    repo_lines = []
    for repo in repositories:
        repo_name = repo.get("name", "unknown")
        repo_commits = repo.get("commits", 0)
        repo_lines.append(f"### {repo_name}\n{repo_commits} commits\n")

    commit_lines = []
    for commit in commits or []:
        message = commit.get("message", "No message")
        sha = commit.get("sha", "")[:7]
        timestamp = commit.get("timestamp", "unknown")
        repo_name = commit.get("repository", "unknown")
        commit_lines.append(f"- {repo_name}: {message} ({sha}) at {timestamp}\n")

    markdown = f"""# Developer Genome Daily Report
Date: {date_label}
Timezone: Asia/Kolkata

## Summary

Commits: {summary.get('commits', 0)}
Repositories touched: {summary.get('repositories_touched', 0)}
PRs: {summary.get('pull_requests', 0)}
Issues: {summary.get('issues', 0)}

## Repositories

{''.join(repo_lines) if repo_lines else 'No repository activity recorded.'}

## Commits

{''.join(commit_lines) if commit_lines else 'No qualifying developer commits were recorded for this date.'}

## Data Quality

Push event history: Partial, depending on GitHub retention and API availability.
System maintenance commit: Excluded from developer activity.
"""
    return markdown
