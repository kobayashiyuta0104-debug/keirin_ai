"""
===========================================================
競輪AI
002_collect_historical_pre_race.py

001で取得した schedule.json を読み込み、
各開催の JSJ001 を取得して保存する

保存先
data_official/historical/pre_race/

===========================================================
"""

import json
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime, timedelta

# ===========================================================
# 基本設定
# ===========================================================

BASE = Path(r"C:\競輪AI")

TARGET_START = "20260716"
TARGET_END = "20260804"

OUTPUT_DIR = (
    BASE
    / "data_official"
    / "historical"
    / "pre_race"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# ===========================================================
# JSJ取得
# ===========================================================

def fetch_jsj001(encp):

    query = urllib.parse.urlencode({

        "encp": encp,

        "type": "JSJ001",

    })

    url = "https://www.keirin.jp/pc/json?" + query

    request = urllib.request.Request(

        url,

        headers={

            "User-Agent": "Mozilla/5.0",

            "Referer": "https://www.keirin.jp/pc/racelive",

            "Accept": "application/json",

            "X-Requested-With": "XMLHttpRequest",

        },

    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=20,
        ) as response:

            raw = response.read().decode(
                "utf-8",
                errors="replace",
            )

            return json.loads(raw)

    except Exception:

        return None


# ===========================================================
# main
# ===========================================================

def collect_pre_race(target_date):

    if target_date is None:
        target_date = TARGET_DATE

    schedule_file = (
        BASE
        / "data_official"
        / "historical"
        / "schedule"
        / f"{target_date}_schedule.json"
    )

    output_file = (
        OUTPUT_DIR
        / f"{target_date}_pre_race.json"
    )
    
    print()
    print("========================================")
    print("Historical Pre Race")
    print("TARGET :", target_date)
    print("========================================")
    print()

    with open(
        schedule_file,
        "r",
        encoding="utf-8",
    ) as f:

        schedule = json.load(f)

    venues = schedule.get(
        "venues",
        []
    )

    output = {

        "target_date":  target_date,

        "venue_count": len(venues),

        "venues": [],

    }

    for i, venue in enumerate(venues, 1):

        venue_name = venue.get("venue")
        bank_code = venue.get("bank_code")
        encp = venue.get("encPrm")

        print(f"[{i}/{len(venues)}] {venue_name}")

        jsj001 = fetch_jsj001(encp)

        race_count = 0

        if jsj001:

            try:
                race_count = len(
                    jsj001["C0201data"]["C0201race"]
                )
            except Exception:
                pass

        print("レース数 :", race_count)

        output["venues"].append({

            "venue":
                jsj001["C0201data"]["joName"].replace("競輪場", ""),

            "bank_code":
                jsj001["C0201data"]["selKjyoCd"],

            "encPrm":
                encp,

            "jsj001":
                jsj001,

        })

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
    print("========================================")
    print("保存完了")
    print(output_file,)
    print("========================================")

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
            / f"{target_date}_pre_race.json"
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

            collect_pre_race(
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
    print("Historical Pre Race Complete")
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