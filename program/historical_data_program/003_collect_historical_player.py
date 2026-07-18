"""
===========================================================
競輪AI
003_collect_historical_player.py

Part1
・基本設定
・入力ファイル
・出力フォルダ
・JSON保存
・JSJ006取得
===========================================================
"""

import json
import urllib.request
import urllib.parse
import os
from pathlib import Path

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
    / "player"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# ===========================================================
# JSON保存
# ===========================================================

def save_json(path, data):

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
# pre_race.json読込
# ===========================================================

def load_pre_race(input_file):

    with open(
        input_file,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


# ===========================================================
# 共通JSJ取得
# ===========================================================

def fetch_jsj(encp, jsj):

    query = urllib.parse.urlencode({

        "encp": encp,

        "type": jsj,

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
# JSJ006取得
# ===========================================================

def fetch_jsj006(encp):

    return fetch_jsj(
        encp,
        "JSJ006",
    )


# ===========================================================
# race_key
# ===========================================================

def build_race_key(

    race_date,
    venue_name,
    race_no,

):

    return f"{race_date}_{venue_name}_{race_no}R"

# ===========================================================
# Player取得
# ===========================================================

def collect_player(target_date=None):

    if target_date is None:
        target_date = TARGET_DATE

    input_file = (
        BASE
        / "data_official"
        / "historical"
        / "pre_race"
        / f"{target_date}_pre_race.json"
    )

    print()
    print("========================================")
    print("Historical Player")
    print("TARGET :", target_date)
    print("========================================")
    print()

    pre_race = load_pre_race(input_file)

    venues = pre_race.get(
        "venues",
        [],
    )

    output = {

        "program":
            "003_collect_historical_player.py",

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

    success = 0

    venue_total = len(venues)

    venue_index = 0

    for venue in venues:

        venue_index += 1

        # -------------------------
        # 開催情報
        # -------------------------

        venue_name = (

            venue.get("venue")

            or venue.get("競輪場名")

            or venue.get("jyoName")

            or "UNKNOWN"

        )

        bank_code = (

            venue.get("bank_code")

            or venue.get("競輪場コード")

            or venue.get("KeirinCd")

        )

        print(
            f"[{venue_index}/{venue_total}] {venue_name}"
        )

        jsj001 = venue.get(
            "jsj001"
        )

        venue_item = {

            "venue":
                venue_name,

            "bank_code":
                bank_code,

            "races":
                [],

        }

        if not isinstance(jsj001, dict):

            print("  JSJ001なし")

            output["venues"].append(
                venue_item
            )

            continue

        c0201 = jsj001.get(
            "C0201data",
            {},
        )

        race_list = c0201.get(
            "C0201race",
            [],
        )

        race_total = len(
            race_list
        )

        print(
            f"  レース数 : {race_total}"
        )

        for race_no, race in enumerate(

            race_list,

            start=1,

        ):

            total_race += 1

            encp = race.get(
                "encParaR"
            )

            race_key = build_race_key(

                target_date,

                venue_name,

                race_no,

            )

            if encp is None:

                print(
                    f"    {race_no}R encParaRなし"
                )

                continue

            jsj006 = fetch_jsj006(
                encp
            )

            if jsj006 is None:

                print(
                    f"    {race_no}R 取得失敗"
                )

                continue

            success += 1

            print(
                f"    {race_no}R OK"
            )

            venue_item["races"].append({

                "race_key":
                    race_key,

                "race_no":
                    race_no,

                "encParaR":
                    encp,

                "jsj006":
                    jsj006,

            })

        output["venues"].append(
            venue_item
        )

    output["race_count"] = total_race

    print()
    print("========================================")
    print("取得完了")
    print("========================================")
    print()

    print("開催数 :", len(venues))
    print("レース数 :", total_race)
    print("JSJ006取得 :", success)

    print()

    return output

# ===========================================================
# 保存
# ===========================================================

def save_player(output, target_date=None):

    if target_date is None:
        target_date = TARGET_DATE

    output_file = (
        OUTPUT_DIR
        / f"{target_date}_player.json"
    )

    save_json(

        output_file,

        output,

    )

    print()

    print("========================================")
    print("保存完了")
    print("========================================")

    print()

    print("保存先")

    print(
        output_file
    )

    print()

    print("開催数 :",
        output["venue_count"],
    )

    print(
        "レース数 :",
        output["race_count"],
    )

    race_success = 0

    for venue in output["venues"]:

        race_success += len(

            venue.get(
                "races",
                [],
            )

        )

    print(
        "JSJ006取得 :",
        race_success,
    )

    print()

    print("========================================")


# ===========================================================
# main
# ===========================================================

def main(target_date=None):

    output = collect_player(target_date)

    save_player(
        output,
        target_date,
    )


# ===========================================================
# 実行
# ===========================================================

if __name__ == "__main__":

    main()