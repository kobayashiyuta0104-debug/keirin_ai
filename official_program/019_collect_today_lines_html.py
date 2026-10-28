"""Collect today's line HTML from WINTICKET for the daily pipeline."""

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path


if os.name == "nt":
    BASE_DIR = Path(r"C:\競輪AI")
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

from winticket_line_collector import collect_lines_html


SAVE_DIR = BASE_DIR / "data_official" / "today"
FAILED_LOG = SAVE_DIR / "today_lines_failed.txt"
SAVE_DIR.mkdir(parents=True, exist_ok=True)

JST = timezone(timedelta(hours=9))
TARGET_DATE = datetime.now(JST).strftime("%Y%m%d")
OUTPUT_FILE = SAVE_DIR / "today_lines.html"

print("=" * 70)
print("019 Collect Today WINTICKET Lines HTML")
print("SOURCE: WINTICKET RaceCard")
print("TARGET DATE:", TARGET_DATE)
print("=" * 70)

try:
    collect_lines_html(
        TARGET_DATE,
        OUTPUT_FILE,
        generated_by="019_collect_today_lines_html.py",
        allow_empty=False,
        max_races=None,
    )
except Exception as exc:
    with FAILED_LOG.open("a", encoding="utf-8") as log:
        log.write(f"{TARGET_DATE}\t{type(exc).__name__}: {exc}\n")
    raise
