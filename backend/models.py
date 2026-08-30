from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CommitRecord:
    sha: str
    repository: str
    message: str
    author: str
    committer: str
    authored_at: str
    committed_at: str
    html_url: str
    additions: int = 0
    deletions: int = 0
    changed_files: int | None = None
    in_system_repo: bool = False


@dataclass
class RepositoryRecord:
    name: str
    full_name: str
    description: str
    html_url: str
    private: bool
    archived: bool
    default_branch: str | None
    language: str | None
    languages: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    last_activity: str | None = None
    health_score: float = 0.0
    health_reasons: list[str] = field(default_factory=list)
    commits: int = 0
    pull_requests: int = 0
    issues: int = 0
    push_events_observed: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DailySummary:
    date: str
    timezone: str
    developer_commits: int = 0
    repositories_touched: int = 0
    pull_requests: int = 0
    issues: int = 0
    observed_push_events: int | None = None
    no_activity: bool = False
    repositories: list[dict[str, Any]] = field(default_factory=list)
    commits: list[dict[str, Any]] = field(default_factory=list)
    data_quality: dict[str, Any] = field(default_factory=dict)
