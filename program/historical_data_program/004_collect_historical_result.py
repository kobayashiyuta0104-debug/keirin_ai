"""
===========================================================
競輪AI
004_collect_historical_result.py

過去レース結果取得
(JSJ012)

Part1
・基本設定
・JSON読込
・JSJ012取得
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

TARGET_START = "20200101"
TARGET_END = "20221231"

OUTPUT_DIR = (
    BASE
    / "data_official"
    / "historical"
    / "result"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# ===========================================================
# JSON
# ===========================================================

def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


def save_json(path,data):

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )

# ===========================================================
# 共通JSJ取得
# ===========================================================

def fetch_jsj(encp,jsj):

    query = urllib.parse.urlencode({

        "encp":encp,

        "type":jsj,

    })

    url = "https://www.keirin.jp/pc/json?" + query

    request = urllib.request.Request(

        url,

        headers={

            "User-Agent":"Mozilla/5.0",

            "Referer":"https://www.keirin.jp/pc/racelive",

            "Accept":"application/json",

            "X-Requested-With":"XMLHttpRequest",

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
# JSJ012
# ===========================================================

def fetch_jsj012(encp):

    return fetch_jsj(

        encp,

        "JSJ012",

    )

# ===========================================================
# レース結果取得
# ===========================================================

def collect_result(target_date):

    if target_date is None:
        target_date = TARGET_DATE

    input_file = (
        BASE
        / "data_official"
        / "historical"
        / "pre_race"
        / f"{target_date}_pre_race.json"
    )

    data = load_json(

        input_file,
    )
    
    venues = data.get(

        "venues",

        [],

    )

    print()

    print("========================================")
    print("Historical Result")
    print("TARGET :", target_date)
    print("========================================")
    print()

    output = {

        "target_date":

            target_date,

        "venue_count":

            len(venues),

        "race_count":

            0,

        "venues":

            [],

    }

    total_race = 0

    venue_total = len(

        venues,

    )

    for venue_index, venue in enumerate(

        venues,

        1,

    ):

        venue_name = venue.get(

            "venue",

            "UNKNOWN",

        )

        bank_code = venue.get(

            "bank_code",

        )

        print(

            f"[{venue_index}/{venue_total}] {venue_name}"

        )

        jsj001 = venue.get(

            "jsj001",

            {},

        )

        c0201 = jsj001.get(

            "C0201data",

            {},

        )

        race_list = c0201.get(

            "C0201race",

            [],

        )

        print(

            "  レース数 :",

            len(race_list),

        )

        venue_result = {

            "venue":

                venue_name,

            "bank_code":

                bank_code,

            "races":

                [],

        }

        for race_no, race in enumerate(

            race_list,

            1,

        ):

            encp = race.get(

                "encParaR",

            )

            race_key = (

                f"{target_date}_{venue_name}_{race_no}R"

            )

            jsj012 = fetch_jsj012(

                encp,

            )

            if jsj012 is None:

                print(

                    f"    {race_no}R NG"

                )

                continue

            venue_result["races"].append({

                "race_key":

                    race_key,

                "race_no":

                    race_no,

                "encParaR":

                    encp,

                "jsj012":

                    jsj012,

            })

            total_race += 1

            print(

                f"    {race_no}R OK"

            )

        output["venues"].append(

            venue_result,

        )

    output["race_count"] = total_race

    return output

# ===========================================================
# 保存
# ===========================================================

def save_result(output, target_date):

    if target_date is None:
        target_date = TARGET_DATE

    output_file = (
        OUTPUT_DIR
        / f"{target_date}_result.json"
    )

    save_json(

        output_file,

        output,

    )

    print()

    print("========================================")
    print("取得完了")
    print("========================================")
    print()

    print(
        "開催数 :",
        output["venue_count"],
    )

    print(
        "レース数 :",
        output["race_count"],
    )

    print()

    print("========================================")
    print("保存完了")
    print("========================================")
    print()

    print("保存先")

    print(
        output_file,
    )

    print()

    print(
        "開催数 :",
        output["venue_count"],
    )

    print(
        "レース数 :",
        output["race_count"],
    )

    print(
        "JSJ012取得 :",
        output["race_count"],
    )

    print()

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
            / f"{target_date}_result.json"
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

            output = collect_result(
                target_date
            )

            save_result(
                output,
                target_date,
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
    print("Historical Result Complete")
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