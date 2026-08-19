"""
===========================================================
競輪AI
001_collect_historical_schedule.py

役割
・指定日の開催一覧取得
・JSJ057取得
・schedule.json保存
===========================================================
"""

import json
import urllib.request
from pathlib import Path
import os
from datetime import datetime, timedelta

# ===========================================================
# 基本設定
# ===========================================================

if os.name == "nt":
    BASE = Path(r"C:\競輪AI")
else:
    BASE = Path(__file__).resolve().parent.parent

TARGET_START = "20260716"
TARGET_END = "20260804"

OUTPUT_DIR = (
    BASE
    / "data_official"
    / "historical"
    / "schedule"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# ===========================================================
# JSON取得
# ===========================================================

def fetch_json(url):

    request = urllib.request.Request(

        url,

        headers={

            "User-Agent":"Mozilla/5.0",

            "Referer":"https://www.keirin.jp/pc/top",

            "Accept":"application/json",

            "X-Requested-With":"XMLHttpRequest",

        }

    )

    with urllib.request.urlopen(
        request,
        timeout=30,
    ) as response:

        return json.loads(
            response.read().decode("utf-8")
        )

# ===========================================================
# schedule取得
# ===========================================================

def collect_schedule(target_date):

    if target_date is None:
        target_date = TARGET_DATE

    output_file = (
        OUTPUT_DIR
        / f"{target_date}_schedule.json"
    )
    
    print()
    print("======================================")
    print("Historical Schedule")
    print("TARGET :", target_date)
    print("======================================")
    print()

    url = (
        f"https://www.keirin.jp/pc/json?"
        f"kday={target_date}"
        f"&type=JSJ057"
    )

    jsj057 = fetch_json(url)

    kinfo = jsj057.get(
        "kInfo",
        [],
    )

    venues = []

    print("開催数 :", len(kinfo))
    print()

    for venue in kinfo:

        row = {

            "競輪場コード":
                venue.get("KeirinCd"),

            "競輪場名":
                venue.get("jyoName"),

            "encPrm":
                venue.get("encPrm"),

        }

        venues.append(row)

        print(
            row["競輪場コード"],
            row["競輪場名"],
        )

    output = {

        "program":
            "001_collect_historical_schedule.py",

        "target_date":
            target_date,

        "venue_count":
            len(venues),

        "venues":
            venues,

        "raw_jsj057":
            jsj057,

    }

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            output,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print("======================================")
    print("保存完了")
    print(output_file)
    print("======================================")

# ===========================================================
# main
# ===========================================================

def main():

    start_date = datetime.strptime(
        TARGET_START,
        "%Y%m%d"
    )

    end_date = datetime.strptime(
        TARGET_END,
        "%Y%m%d"
    )

    current_date = start_date

    total_days = 0
    saved_days = 0
    skipped_days = 0
    error_days = 0

    while current_date <= end_date:

        target_date = current_date.strftime("%Y%m%d")

        total_days += 1

        output_file = (
            OUTPUT_DIR
            / f"{target_date}_schedule.json"
        )

        print()
        print("=" * 60)
        print(
            f"[{total_days}] {target_date}"
        )
        print("=" * 60)

        # --------------------------------------------
        # 既に取得済みならスキップ
        # --------------------------------------------

        if output_file.exists():

            skipped_days += 1

            print(
                f"SKIP : {output_file.name}"
            )

            current_date += timedelta(days=1)

            continue

        try:

            collect_schedule(
                target_date
            )

            saved_days += 1

        except Exception as e:

            error_days += 1

            print()
            print("ERROR")
            print(type(e).__name__)
            print(e)

        current_date += timedelta(days=1)

    print()
    print("=" * 60)
    print("Historical Schedule Complete")
    print("=" * 60)

    print(
        f"対象期間 : "
        f"{TARGET_START} ～ {TARGET_END}"
    )

    print(
        f"対象日数 : {total_days}"
    )

    print(
        f"SAVED    : {saved_days}"
    )

    print(
        f"SKIP     : {skipped_days}"
    )

    print(
        f"ERROR    : {error_days}"
    )

    print(
        f"OUTPUT   : {OUTPUT_DIR}"
    )

    print()
    print("Finished.")

# ===========================================================
# 実行
# ===========================================================

if __name__ == "__main__":

    main()