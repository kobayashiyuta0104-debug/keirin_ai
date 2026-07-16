import json
import urllib.request
import urllib.parse
import importlib.util
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ===========================================================
# 基本設定
# ===========================================================

if os.name == "nt":
    BASE = Path(r"C:\競輪AI")
else:
    BASE = Path(__file__).resolve().parent.parent

COLLECTOR_FILE = (
    BASE
    / "official_program"
    / "origin_program"
    / "004_collect_historical_raw.py"
)

MASTER_FILE = (
    BASE
    / "data_official"
    / "master"
    / "bank_master.json"
)

OUTPUT_DIR = (
    BASE
    / "data_official"
    / "daily"
    / "race_data"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

JST = timezone(timedelta(hours=9))

TARGET_DATE = (
    datetime.now(JST)
    - timedelta(days=1)
).strftime("%Y%m%d")

OUTPUT_FILE = (
    OUTPUT_DIR
    / f"{TARGET_DATE}_race_data.json"
)

# ===========================================================
# JSON
# ===========================================================

def save_json(path,data):

    with open(path,"w",encoding="utf-8") as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )


# ===========================================================
# bank master
# ===========================================================

def load_bank_master():

    with open(
        MASTER_FILE,
        "r",
        encoding="utf-8",
    ) as f:

        data=json.load(f)

    return data["banks"]


# ===========================================================
# collector
# ===========================================================

def load_collector():

    spec=importlib.util.spec_from_file_location(
        "collector",
        COLLECTOR_FILE,
    )

    module=importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    return module


# ===========================================================
# 共通JSJ取得
# ===========================================================

def fetch_jsj(encp,jsj):

    query=urllib.parse.urlencode({

        "encp":encp,

        "type":jsj,

    })

    url="https://www.keirin.jp/pc/json?"+query

    request=urllib.request.Request(

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

            raw=response.read().decode(
                "utf-8",
                errors="replace",
            )

            return json.loads(raw)

    except:

        return None


# ===========================================================
# JSJ055
# ===========================================================

def fetch_jsj055(encp):

    return fetch_jsj(
        encp,
        "JSJ055",
    )


# ===========================================================
# JSJ012
# ===========================================================

def fetch_jsj012(encp):

    return fetch_jsj(
        encp,
        "JSJ012",
    )


# ===========================================================
# JSJ055解析
# ===========================================================

def build_jsj055_map(jsj055):

    race_map = {}

    if jsj055 is None:
        return race_map

    venue_list = jsj055.get(
        "printingSimpleSyusouSubData",
        []
    )

    if len(venue_list) == 0:
        return race_map

    race_list = venue_list[0].get(
        "syusouInfoSubData",
        []
    )

    for race in race_list:

        race_no = int(race["raceNo"])

        race_map[race_no] = {

            "レース種別": race.get("syumoku"),

            "距離": race.get("kyori"),

            "周回数": race.get("syukaiCnt"),

            "発走時刻": race.get("startTime"),

            "投票締切": race.get("telVoteEndTime"),

        }

    return race_map

# ===========================================================
# JSJ012解析
# ===========================================================

def build_jsj012_map(jsj012, race_no):

    if jsj012 is None:
        return {}

    return {

        race_no: {

            "天候": jsj012.get("tenki"),

            "風速": jsj012.get("husoku"),

        }

    }

    print(jsj012)
    print(race_map)

    return race_map

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
# 開催処理
# ===========================================================

def collect_race_data():

    collector = load_collector()

    bank_master = load_bank_master()

    print()
    print("=======================================")
    print("Race Data 作成")
    print("TARGET :", TARGET_DATE)
    print("=======================================")
    print()

    daily_map = collector.build_daily_race_map(
        TARGET_DATE
    )

    race_rows = []

    venue_total = len(
        daily_map.get(
            "venues",
            [],
        )
    )

    venue_index = 0

    for venue in daily_map.get(
        "venues",
        [],
    ):

        venue_index += 1

        venue_name = venue.get("venue")

        print(
            f"[{venue_index}/{venue_total}] {venue_name}"
        )

        jsj001 = venue.get("jsj001")

        if jsj001 is None:

            print("  JSJ001なし")

            continue

        c0201 = jsj001["C0201data"]

        bank_code = str(
            c0201.get("selKjyoCd")
        )

        bank = bank_master.get(
            bank_code,
            {}
        )

        races = venue.get(
            "races",
            []
        )

        if len(races) == 0:

            continue

        encp = races[0].get(
            "encParaR"
        )

        print("  JSJ055取得")

        print("encp =", encp)

        jsj055 = fetch_jsj055(
            encp
        )

        print(json.dumps(jsj055, ensure_ascii=False, indent=2)[:5000])

        jsj055_map = build_jsj055_map(
            jsj055
        )

        for race in races:

            race_no = race["race_no"]

            print("JSJ012取得")

            jsj012 = fetch_jsj012(
                race["encParaR"]
            )

            jsj012_map = build_jsj012_map(
                jsj012,
                race_no,
            )

            print(race)

            race_key = build_race_key(

                TARGET_DATE,

                venue_name,

                race_no,

            )

            row = {

                "race_key":
                    race_key,

                "開催日":
                    TARGET_DATE,

                "競輪場コード":
                    bank_code,

                "競輪場名":
                    venue_name,

                "開催名":
                    c0201.get(
                        "raceName"
                    ),

                "グレード":
                    c0201.get(
                        "imgGradeAlt"
                    ),

                "レース番号":
                    race_no,

                "周長(m)":
                    bank.get(
                        "周長(m)"
                    ),

                "みなし直線(m)":
                    bank.get(
                        "みなし直線(m)"
                    ),

                "カント角(度)":
                    bank.get(
                        "カント角(度)"
                    ),

            }

            jsj055_row = jsj055_map.get(
                race_no,
                {}
            )

            row.update(
                jsj055_row
            )

            jsj012_row = jsj012_map[race_no]

            row.update(
                jsj012_row
            )

            race_rows.append(
                row
            )

    # ==========================================
    # ソート
    # ==========================================

    race_rows.sort(

        key=lambda x:(

            x["競輪場コード"],

            x["レース番号"],

        )

    )

    output={

        "program":

            "002_collect_race_data.py",

        "data_type":

            "RACE_DATA",

        "target_date":

            TARGET_DATE,

        "race_count":

            len(race_rows),

        "races":

            race_rows,

    }

    save_json(

        OUTPUT_FILE,

        output,

    )

    print()

    print("=======================================")
    print("保存完了")
    print("=======================================")
    print()

    print("保存先")

    print(
        OUTPUT_FILE
    )

    print()

    print(
        "レース数 :",
        len(race_rows),
    )

    print()

    print("=======================================")

    return output


# ===========================================================
# main
# ===========================================================

if __name__ == "__main__":

    collect_race_data()