import re
import time
import requests

from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone

# ==========================================================
# 011_collect_daily_oddspark_html.py
#
# OddsPark 前日ライン情報HTML取得
#
# 入力:
#   OddsPark RaceList
#
# 出力:
#   data_official/
#       daily/
#           html/
#               YYYYMMDD.html
#
# GitHub Actions対応（JST）
# ==========================================================

import os

if os.name == "nt":
    BASE_DIR = Path(r"C:\競輪AI")
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

SAVE_DIR = (
    BASE_DIR
    / "data_official"
    / "daily"
    / "html"
)

SAVE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

LOG_DIR = (
    BASE_DIR
    / "data_official"
    / "daily"
    / "log"
)

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True
)

FAILED_LOG = LOG_DIR / "failed_daily_html.txt"

HEADERS = {

    "User-Agent":

        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "

        "AppleWebKit/537.36 "

        "(KHTML, like Gecko) "

        "Chrome/138.0 Safari/537.36"

}

# ==========================================================
# Session
# ==========================================================

session = requests.Session()

session.headers.update(HEADERS)

# ==========================================================
# Download
# ==========================================================

def download(url):

    for retry in range(3):

        try:

            r = session.get(
                url,
                timeout=30
            )

            r.raise_for_status()

            r.encoding = "utf-8"

            return r.text

        except Exception:

            if retry == 2:
                raise

            time.sleep(3)
# ==========================================================
# Calendar取得
# ==========================================================

print("=" * 70)
print("011 Collect Daily OddsPark HTML")
print("=" * 70)
print()

JST = timezone(timedelta(hours=9))

TARGET_DATE = (
    datetime.now(JST) - timedelta(days=1)
).strftime("%Y%m%d")

pattern = re.compile(
    r'AllRaceList\.do\?kaisaiBi=(\d{8})&amp;joCode=(\d+)'
)

day_map = {}

print(f"TARGET DATE : {TARGET_DATE}")

calendar_url = (
    "https://www.oddspark.com/keirin/"
    f"KaisaiCalendar.do?target={TARGET_DATE[:6]}"
)

calendar_html = download(calendar_url)

for date, jo in pattern.findall(calendar_html):

    if date == TARGET_DATE:

        day_map.setdefault(date, []).append(jo)

if not day_map:

    print("対象日の開催がありません。")

    exit()

print("対象日数 :", len(day_map))
print()

saved_day = 0
error_day = 0
race_total = 0

# ==========================================================
# 日単位処理開始
# ==========================================================

total_days = len(day_map)

for index, date in enumerate(sorted(day_map.keys()), start=1):

    outfile = SAVE_DIR / f"{date}.html"

    print()
    print("=" * 70)
    print(f"[{index}/{total_days}] {date}")
    print("=" * 70)

    race_urls = set()

    # ------------------------------------------------------
    # AllRaceList取得
    # ------------------------------------------------------

    for jo in sorted(day_map[date]):

        allrace_url = (

            "https://www.oddspark.com/keirin/"

            f"AllRaceList.do?"

            f"kaisaiBi={date}"

            f"&joCode={jo}"

        )

        try:

            html = download(allrace_url)

        except Exception as e:

            print(e)

            with open(
                FAILED_LOG,
                "a",
                encoding="utf-8"
            ) as log:
                log.write(date + "\n")

            continue

        races = re.findall(

            r'RaceList\.do\?joCode=(\d+)'
            r'&amp;kaisaiBi=(\d{8})'
            r'&amp;raceNo=(\d+)',

            html

        )

        for jo_code, race_date, race_no in races:

            race_urls.add(

                (

                    f"{race_date}_{jo_code}_{race_no.zfill(2)}",

                    "https://www.oddspark.com/keirin/"

                    f"RaceList.do?"

                    f"joCode={jo_code}"

                    f"&kaisaiBi={race_date}"

                    f"&raceNo={race_no}"

                )

            )

    race_urls = sorted(race_urls)

    print(f"Race数 : {len(race_urls)}")

    # ------------------------------------------------------
    # Race取得（並列）
    # ------------------------------------------------------

    def fetch_race(item):

        race_key, race_url = item

        try:

            with requests.Session() as s:

                s.headers.update(HEADERS)

                r = s.get(
                    race_url,
                    timeout=30
                 )

                r.raise_for_status()

                r.encoding = "utf-8"

                return (
                    race_key,
                    r.text,
                    None
                )

        except Exception as e:

            return (
                race_key,
                None,
                e
            )

    race_results = []

    with ThreadPoolExecutor(max_workers=8) as executor:

        futures = [

            executor.submit(

                fetch_race,

                item

            )

            for item in race_urls

        ]

        for future in as_completed(futures):

            race_key, html, err = future.result()

            if err is not None:

                error_day += 1

                print(f"ERROR {race_key}")

                print(err)

                continue

            race_results.append(

                (

                    race_key,

                    html

                )

            )

            race_total += 1

    # ------------------------------------------------------
    # race_key順に並べる
    # ------------------------------------------------------

    race_results.sort(

        key=lambda x: x[0]

    )

    # ------------------------------------------------------
    # 保存
    # ------------------------------------------------------
    if len(race_results) != len(race_urls):

        print(
            f"Race取得不足 {len(race_results)}/{len(race_urls)}"
        )

        with open(
            FAILED_LOG,
            "a",
            encoding="utf-8"
        ) as log:
            log.write(date + "\n")

        continue

    html_size = sum(len(html) for _, html in race_results)

    if html_size < 50000:

        print("HTMLサイズ異常")

        with open(
            FAILED_LOG,
            "a",
            encoding="utf-8"
        ) as log:
            log.write(date + "\n")

        continue

    with open(

        outfile,

        "w",

        encoding="utf-8"

    ) as f:

        f.write(
            "<!-- =============================================== -->\n"
        )

        f.write(
            f"<!-- DATE={date} -->\n"
        )

        f.write(
            "<!-- GENERATED BY 011_collect_daily_oddspark_html.py -->\n"
        )

        f.write(
            "<!-- =============================================== -->\n\n"
        )

        for race_key, html in race_results:

            f.write(

                f"<!-- RACE_KEY={race_key} -->\n"

            )

            f.write(

                html

            )

            f.write(

                "\n<!-- END_RACE -->\n\n"

            )

    saved_day += 1

    print(

        f"SAVE {outfile.name}"

    )

    print()

    # メモリ解放

    del race_results

    del race_urls

    time.sleep(0.2)

# ==========================================================
# 完了
# ==========================================================

print()
print("=" * 70)
print("収集完了")
print("=" * 70)

print(f"保存日数        : {saved_day}")
print(f"取得エラー日数  : {error_day}")
print(f"Race取得数      : {race_total}")
print(f"保存先          : {SAVE_DIR}")
print(f"TARGET DATE     : {TARGET_DATE}")

print()
print("Finished.")

print("SAVE_DIR exists :", SAVE_DIR.exists())
print("HTML files :", list(SAVE_DIR.glob("*.html")))