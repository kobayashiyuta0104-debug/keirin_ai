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

# ===========================================================
# 基本設定
# ===========================================================

if os.name == "nt":
    BASE = Path(r"C:\競輪AI")
else:
    BASE = Path(__file__).resolve().parent.parent

TARGET_DATE = "20230101"

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

OUTPUT_FILE = (
    OUTPUT_DIR
    / f"{TARGET_DATE}_schedule.json"
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

def collect_schedule():

    print()
    print("======================================")
    print("Historical Schedule")
    print("TARGET :", TARGET_DATE)
    print("======================================")
    print()

    url = (
        f"https://www.keirin.jp/pc/json?"
        f"kday={TARGET_DATE}"
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
            TARGET_DATE,

        "venue_count":
            len(venues),

        "venues":
            venues,

        "raw_jsj057":
            jsj057,

    }

    with open(
        OUTPUT_FILE,
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
    print(OUTPUT_FILE)
    print("======================================")

# ===========================================================
# main
# ===========================================================

if __name__ == "__main__":

    collect_schedule()