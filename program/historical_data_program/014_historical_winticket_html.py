"""Collect yesterday's line HTML from WINTICKET for the daily pipeline."""

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path


if os.name == "nt":
    BASE_DIR = Path(r"C:\競輪AI")
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

import sys

sys.path.insert(0, str(BASE_DIR / "official_program"))

from winticket_line_collector import collect_lines_html


SAVE_DIR = BASE_DIR / "data_official" / "daily" / "html"
LOG_DIR = BASE_DIR / "data_official" / "daily" / "log"
FAILED_LOG = LOG_DIR / "failed_daily_html.txt"
SAVE_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

JST = timezone(timedelta(hours=9))
TARGET_DATE = "20261027"
OUTPUT_FILE = SAVE_DIR / f"{TARGET_DATE}.html"

print("=" * 70)
print("011 Collect Yesterday WINTICKET Lines HTML")
print("SOURCE: WINTICKET RaceCard")
print("TARGET DATE:", TARGET_DATE)
print("=" * 70)

try:
    summary = collect_lines_html(
        TARGET_DATE,
        OUTPUT_FILE,
        generated_by="011_collect_daily_winticket_html.py",
        allow_empty=True,
        max_races=None,
    )
except Exception as exc:
    with FAILED_LOG.open("a", encoding="utf-8") as log:
        log.write(f"{TARGET_DATE}\t{type(exc).__name__}: {exc}\n")
    raise

if summary["race_count"] == 0:
    print("対象日の開催がありません。空のHTMLを保存しました。")
