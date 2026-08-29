import os
from datetime import datetime, timedelta, timezone

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - fallback when tzdata is unavailable
    ZoneInfo = None

DEFAULT_TIMEZONE = "Asia/Kolkata"
TIMEZONE_OFFSETS = {
    "Asia/Kolkata": timedelta(hours=5, minutes=30),
}


def get_config():
    return {
        "github_username": os.getenv("GITHUB_USERNAME", "your_github_username"),
        "github_owner": os.getenv("GITHUB_OWNER", os.getenv("GITHUB_USERNAME", "your_github_username")),
        "analytics_repo": os.getenv("GITHUB_ANALYTICS_REPO", "developer-genome"),
        "timezone": os.getenv("TIMEZONE", DEFAULT_TIMEZONE),
        "lookback_days": int(os.getenv("LOOKBACK_DAYS", "30")),
        "system_bot_actor": os.getenv("SYSTEM_BOT_ACTOR", "github-actions[bot]"),
        "token": os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN"),
    }


def get_timezone_offset(timezone_name: str):
    if timezone_name in TIMEZONE_OFFSETS:
        return TIMEZONE_OFFSETS[timezone_name]
    if ZoneInfo is not None:
        try:
            tz = ZoneInfo(timezone_name)
            return datetime.now(timezone.utc).astimezone(tz) - datetime.now(timezone.utc)
        except Exception:
            return timedelta(0)
    return timedelta(0)


def get_target_date_for_run(now_utc: datetime | None = None, timezone_name: str | None = None):
    tz_name = timezone_name or get_config()["timezone"]
    if now_utc is None:
        now_utc = datetime.now(timezone.utc)
    offset = get_timezone_offset(tz_name)
    now_local = now_utc + offset
    return (now_local - timedelta(days=1)).date()


def get_daily_window(target_date, timezone_name: str | None = None):
    tz_name = timezone_name or get_config()["timezone"]
    offset = get_timezone_offset(tz_name)
    start_local = datetime.combine(target_date, datetime.min.time()) + offset
    end_local = datetime.combine(target_date, datetime.max.time().replace(microsecond=0)) + offset
    return start_local.astimezone(timezone.utc), end_local.astimezone(timezone.utc)
