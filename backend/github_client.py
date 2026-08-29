import json
from urllib import error, request


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
        if params:
            query = "&".join(f"{key}={value}" for key, value in params.items())
            url = f"{url}?{query}"
        req = request.Request(url, headers=self._headers())
        try:
            with request.urlopen(req, timeout=30) as response:
                body = response.read().decode("utf-8")
                return json.loads(body)
        except error.HTTPError as exc:
            payload = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"GitHub API request failed for {url}: {payload}") from exc

    def get_user(self, username: str):
        return self.request(f"https://api.github.com/users/{username}")

    def list_user_repos(self, username: str, per_page: int = 100):
        return self.request(f"https://api.github.com/users/{username}/repos", {"per_page": per_page, "sort": "updated"})

    def list_public_events(self, username: str, per_page: int = 100):
        return self.request(f"https://api.github.com/users/{username}/events/public", {"per_page": per_page})

    def list_repo_commits(self, username: str, repo_name: str, since: str | None = None, until: str | None = None):
        params = {"per_page": 100}
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        return self.request(f"https://api.github.com/repos/{username}/{repo_name}/commits", params)
