import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DAILY_DIR = DATA_DIR / "daily"
REPORTS_DIR = ROOT.parent / "reports"


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload):
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def write_daily_snapshot(date_label: str, record: dict):
    target = DAILY_DIR / f"{date_label}.json"
    return write_json(target, record)


def write_report(date_label: str, markdown: str):
    ensure_dir(REPORTS_DIR / "daily")
    report_path = REPORTS_DIR / "daily" / f"{date_label}.md"
    report_path.write_text(markdown, encoding="utf-8")
    latest_path = REPORTS_DIR / "latest.md"
    latest_path.write_text(f"# Latest report\n\n- Date: {date_label}\n- Path: reports/daily/{date_label}.md\n", encoding="utf-8")
    return report_path
