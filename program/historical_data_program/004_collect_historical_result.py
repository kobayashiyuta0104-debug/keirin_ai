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

# ===========================================================
# 基本設定
# ===========================================================

BASE = Path(r"C:\競輪AI")

INPUT_FILE = (
    BASE
    / "data_official"
    / "historical"
    / "pre_race"
    / "20230101_pre_race.json"
)

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

OUTPUT_FILE = (
    OUTPUT_DIR
    / "20230101_result.json"
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

def collect_result():

    data = load_json(

        INPUT_FILE,

    )

    target_date = data.get(

        "target_date",

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

def save_result(output):

    save_json(

        OUTPUT_FILE,

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
        OUTPUT_FILE,
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

    output = collect_result()

    save_result(

        output,

    )


# ===========================================================
# 実行
# ===========================================================

if __name__ == "__main__":

    main()