import json
from urllib import error, request
from urllib.parse import urlencode


class GitHubClient:
    def __init__(self, token: str | None = None, user_agent: str = "DeveloperGenome/1.0"):
        self.token = token
        self.user_agent = user_agent

    def _headers(self):
        headers = {"User-Agent": self.user_agent, "Accept": "application/vnd.github+json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def request(self, url: str, params: dict | None = None):
        full_url = url
        if params:
            full_url = f"{url}?{urlencode(params)}"
        req = request.Request(full_url, headers=self._headers())
        try:
            with request.urlopen(req, timeout=30) as response:
                payload = response.read().decode("utf-8")
                return json.loads(payload)
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"GitHub API request failed for {full_url}: {body}") from exc
        except error.URLError as exc:
            raise RuntimeError(f"GitHub API network failure for {full_url}: {exc}") from exc

    def get_user(self, username: str):
        return self.request(f"https://api.github.com/users/{username}")

    def list_user_repos(self, username: str, per_page: int = 100):
        return self.request(f"https://api.github.com/users/{username}/repos", {"per_page": per_page, "sort": "updated"})

    def list_public_events(self, username: str, per_page: int = 100):
        return self.request(f"https://api.github.com/users/{username}/events/public", {"per_page": per_page})

    def list_repo_commits(self, username: str, repo_name: str, since: str | None = None, until: str | None = None, author: str | None = None):
        params = {"per_page": 100}
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        if author:
            params["author"] = author
        return self.request(f"https://api.github.com/repos/{username}/{repo_name}/commits", params)

    def get_repo_languages(self, username: str, repo_name: str):
        return self.request(f"https://api.github.com/repos/{username}/{repo_name}/languages")

    def search_issues(self, query: str, per_page: int = 100):
        return self.request("https://api.github.com/search/issues", {"q": query, "per_page": per_page})
