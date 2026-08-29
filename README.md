# Developer Genome

Developer Genome is a real GitHub developer analytics platform that turns public GitHub activity into a daily developer profile, repository health overview, technical DNA, behavioral patterns, and historical insight.

This project is designed to run automatically every day at 8:00 AM IST using the previous calendar date. It is built around real GitHub API data and does not use fake production fallback data.

## Features

- Real GitHub profile and repository collection
- Previous-day IST analytics window
- Daily activity summary by date
- Repository push and commit summaries
- Health signals and repo-level insights
- Technical DNA and behavioral DNA
- Automated daily refresh workflow
- Frontend dashboard for exploring activity and repositories
- Test coverage for pipeline logic

## Architecture

- Backend analytics engine in `backend/analytics_engine.py`
- Frontend Vite app in `frontend/`
- GitHub Actions workflow in `.github/workflows/daily-analytics.yml`
- Generated snapshot output in `backend/data/analytics_snapshot.json`

## Real-data policy

- No fake production values
- No hardcoded repo counts
- No fabricated push counts
- No sample-data fallback in production
- Private repositories require a token to be visible
- The workflow always analyzes the previous day in Asia/Kolkata time (IST)

## Setup

1. Create a virtual environment and install dependencies.
2. Set environment variables in your shell or a `.env` file.
3. Provide a GitHub username and optional token.

Example:

```bash
set GITHUB_USERNAME=YourUsername
set TIMEZONE=Asia/Kolkata
set GH_TOKEN=your_github_token
```

## Local run

```bash
cd backend
python analytics_engine.py --username YOUR_USERNAME
```

## GitHub token setup

Use a personal access token with repository access if you need private repo visibility. Do not commit the token to the repo or expose it in the frontend.

## Workflow behavior

The daily GitHub Actions job runs at 02:30 UTC, which is 08:00 IST. It analyzes the previous calendar day and updates the snapshot if data changed.

## Testing

```bash
cd backend
python -m unittest test_github_pipeline.py
```

## Frontend build

```bash
cd frontend
npm install
npm run build
```

## Data quality and limitations

- Public repository data is available directly from GitHub.
- Historical push-event detail may be partial depending on GitHub API retention.
- Private repository data is only visible with the correct token permissions.
- Automated system commits are not counted as developer activity.

## Deployment

The frontend is static and can be deployed to Vercel, Netlify, or GitHub Pages. It reads the generated data model and does not require direct GitHub authentication.

## Who this is for

This project is intended for developers who want a transparent, real, and daily view of their GitHub activity and repository momentum.
