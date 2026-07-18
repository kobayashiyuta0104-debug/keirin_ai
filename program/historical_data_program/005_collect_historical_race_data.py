import json
import urllib.request
import urllib.parse
from pathlib import Path

# ===========================================================
# 基本設定
# ===========================================================

BASE = Path(r"C:\競輪AI")

TARGET_DATE = "20230101"

MASTER_FILE = (
    BASE
    / "data_official"
    / "master"
    / "bank_master.json"
)

OUTPUT_DIR = (
    BASE
    / "data_official"
    / "historical"
    / "race_data"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# ===========================================================
# JSON
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
# pre_race
# ===========================================================

def load_pre_race(pre_race_file):

    with open(
        pre_race_file,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


# ===========================================================
# bank master
# ===========================================================

def load_bank_master():

    with open(
        MASTER_FILE,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)["banks"]


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

            "Referer": "https://www.keirin.jp/",

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
# race_key
# ===========================================================

def build_race_key(

    race_date,
    venue_name,
    race_no,

):

    return f"{race_date}_{venue_name}_{race_no}R"

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

        race_no = int(
            race["raceNo"]
        )

        race_map[race_no] = {

            "レース種別":
                race.get("syumoku"),

            "距離":
                race.get("kyori"),

            "周回数":
                race.get("syukaiCnt"),

            "発走時刻":
                race.get("startTime"),

            "投票締切":
                race.get("telVoteEndTime"),

        }

    return race_map


# ===========================================================
# JSJ012解析
# ===========================================================

def build_jsj012_map(
    jsj012,
    race_no,
):

    if jsj012 is None:

        return {}

    return {

        race_no: {

            "天候":
                jsj012.get("tenki"),

            "風速":
                jsj012.get("husoku"),

        }

    }


# ===========================================================
# race_data出力テンプレート
# ===========================================================

def create_race_row(

    race_key,
    target_date,
    bank_code,
    venue_name,
    race_name,
    grade,
    race_no,
    bank,

):

    return {

        "race_key":
            race_key,

        "開催日":
            target_date,

        "競輪場コード":
            bank_code,

        "競輪場名":
            venue_name,

        "開催名":
            race_name,

        "グレード":
            grade,

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

# ===========================================================
# メイン処理
# ===========================================================

def collect_race_data(target_date=None):

    if target_date is None:
        target_date = TARGET_DATE

    pre_race_file = (
        BASE
        / "data_official"
        / "historical"
        / "pre_race"
        / f"{target_date}_pre_race.json"
    )

    output_file = (
        OUTPUT_DIR
        / f"{target_date}_race_data.json"
    )

    pre_race = load_pre_race(pre_race_file)

    bank_master = load_bank_master()

    output = {

        "target_date": target_date,

        "race_count": 0,

        "races": [],

    }

    print()

    print("========================================")
    print("Historical Race Data")
    print("TARGET :", target_date)
    print("========================================")
    print()

    venues = pre_race.get(
        "venues",
        []
    )

    race_total = 0

    for i, venue in enumerate(
        venues,
        1,
    ):

        venue_name = venue["venue"]

        bank_code = venue["bank_code"]

        jsj001 = venue["jsj001"]

        c0201 = jsj001["C0201data"]

        bank = bank_master.get(
            str(bank_code),
            {},
        )

        races = c0201.get(
            "C0201race",
            [],
        )

        print(
            f"[{i}/{len(venues)}] {venue_name}"
        )

        print(
            "レース数 :",
            len(races),
        )

        if len(races) == 0:

            continue

        # ==============================
        # JSJ055
        # ==============================

        jsj055 = fetch_jsj055(

            races[0]["encParaR"]

        )

        jsj055_map = build_jsj055_map(
            jsj055
        )

        # ==============================
        # 全レース
        # ==============================

        for race_no, race in enumerate(
            races,
            1,
        ):

            jsj012 = fetch_jsj012(

                race["encParaR"]

            )

            jsj012_map = build_jsj012_map(

                jsj012,

                race_no,

            )

            race_key = build_race_key(

                target_date,

                venue_name,

                race_no,

            )

            row = create_race_row(

                race_key,

                target_date,

                bank_code,

                venue_name,

                c0201.get(
                    "raceName"
                ),

                c0201.get(
                    "imgGradeAlt"
                ),

                race_no,

                bank,

            )

            row.update(

                jsj055_map.get(
                    race_no,
                    {},
                )

            )

            row.update(

                jsj012_map.get(
                    race_no,
                    {},
                )

            )

            output["races"].append(
                row
            )

            race_total += 1

            print(
                f"    {race_no}R OK"
            )

    output["race_count"] = race_total

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
        len(venues),
    )

    print(
        "レース数 :",
        race_total,
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

    print(
        "レース数 :",
        race_total,
    )

    print()

    print("========================================")


# ===========================================================
# main
# ===========================================================

def main(target_date=None):

    collect_race_data(target_date)


if __name__ == "__main__":

    main()