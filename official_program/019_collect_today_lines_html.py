"""Collect today's line HTML from the official KEIRIN JSJ005 source."""

import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

from keirin_line_source import collect_lines_html


if os.name == "nt":
    BASE_DIR = Path(r"C:\競輪AI")
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

SAVE_DIR = BASE_DIR / "data_official" / "today"
FAILED_LOG = SAVE_DIR / "today_lines_failed.txt"
SAVE_DIR.mkdir(parents=True, exist_ok=True)

if FAILED_LOG.exists():
    FAILED_LOG.unlink()

JST = timezone(timedelta(hours=9))
TARGET_DATE = datetime.now(JST).strftime("%Y%m%d")
OUTPUT_FILE = SAVE_DIR / "today_lines.html"

print("=" * 70)
print("019 Collect Today Keirin Lines HTML")
print("SOURCE: KEIRIN.JP JSJ005")
print("TARGET DATE:", TARGET_DATE)
print("=" * 70)

try:
    collect_lines_html(
        TARGET_DATE,
        OUTPUT_FILE,
        generated_by="019_collect_today_lines_html.py",
        allow_empty=False,
    )
except Exception as exc:
    with FAILED_LOG.open("a", encoding="utf-8") as log:
        log.write(f"{TARGET_DATE}\t{type(exc).__name__}: {exc}\n")
    raise