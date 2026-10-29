"""Collect yesterday's line HTML from WINTICKET for the daily pipeline."""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path


if os.name == "nt":
    BASE_DIR = Path(r"C:\競輪AI")
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

from winticket_line_collector import collect_lines_html


SAVE_DIR = BASE_DIR / "data_official" / "daily" / "html"
LOG_DIR = BASE_DIR / "data_official" / "daily" / "log"
FAILED_LOG = LOG_DIR / "failed_daily_html.txt"
SAVE_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

JST = timezone(timedelta(hours=9))
TARGET_DATE = (datetime.now(JST) - timedelta(days=1)).strftime("%Y%m%d")
OUTPUT_FILE = SAVE_DIR / f"{TARGET_DATE}.html"
RACE_FILE = (
    BASE_DIR
    / "data_official"
    / "daily"
    / "race_data"
    / f"{TARGET_DATE}_race_data.json"
)

print("=" * 70)
print("011 Collect Yesterday WINTICKET Lines HTML")
print("SOURCE: WINTICKET RaceCard")
print("TARGET DATE:", TARGET_DATE)
print("=" * 70)

try:
    with RACE_FILE.open("r", encoding="utf-8") as race_file:
        race_data = json.load(race_file)
    if race_data.get("target_date") != TARGET_DATE:
        raise ValueError(
            f"daily race data target_date mismatch: {race_data.get('target_date')}"
        )

    summary = collect_lines_html(
        TARGET_DATE,
        OUTPUT_FILE,
        generated_by="011_collect_daily_winticket_html.py",
        allow_empty=True,
        max_races=None,
        expected_races=race_data.get("races", []),
    )
except Exception as exc:
    with FAILED_LOG.open("a", encoding="utf-8") as log:
        log.write(f"{TARGET_DATE}\t{type(exc).__name__}: {exc}\n")
    raise

if summary["race_count"] == 0:
    print("対象日の開催がありません。空のHTMLを保存しました。")
