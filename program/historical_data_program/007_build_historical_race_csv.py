"""
===========================================================
競輪AI 正式版
007_build_historical_race_csv.py

Part 1
・基本設定
・入力ファイル自動検出
・CSV出力準備
===========================================================
"""

import json
import csv
import os
from pathlib import Path

# ===========================================================
# 基本設定
# ===========================================================

if os.name == "nt":
    BASE = Path(r"C:\競輪AI")
else:
    BASE = Path(__file__).resolve().parent.parent
RACE_DATA_DIR = BASE / "data_official" / "historical" / "race_data"
RACE_CSV_DIR = BASE / "csv" / "historical_race"

SESSION_MASTER_FILE = (
    BASE
    / "data_official"
    / "master"
    / "session_master.json"
)

RACE_CSV_DIR.mkdir(parents=True, exist_ok=True)
# ===========================================================
# 最新 race_data.json 自動検出
# ===========================================================

def get_historical_json_files():

    files = sorted(RACE_DATA_DIR.glob("*_race_data.json"))

    if not files:
        raise FileNotFoundError("historical race_data.json が見つかりません")

    return files

# ===========================================================
# CSVヘッダー
# ===========================================================

RACE_HEADERS = [

    "race_key",
    "date",
    "jo_code",
    "jo_name",
    "event_name",
    "grade",
    "race_no",
    "track_length",
    "straight_length",
    "bank_angle",
    "race_type",
    "session",
    "weather",
    "wind_speed",

]

"""
===========================================================
Part2
・race_data.json読込
===========================================================
"""

def load_race_json(path):

    with open(path, "r", encoding="utf-8") as f:

        return json.load(f)
    
def load_session_master():

    with open(
        SESSION_MASTER_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def time_to_minutes(time_str):

    if not time_str:
        return None

    hour, minute = map(int, time_str.split(":"))

    return hour * 60 + minute

def detect_session(

    first_start,
    last_start,
    session_master,

):

    first = time_to_minutes(first_start)
    last = time_to_minutes(last_start)

    if first is None or last is None:

        return "不明"

    for rule in session_master:

        if (

            rule["first_min"] <= first <= rule["first_max"]

            and

            rule["last_min"] <= last <= rule["last_max"]

        ):

            return rule["display_name"]

    return "不明"

"""
===========================================================
Part3
・CSV行生成
===========================================================
"""

def build_race_rows(
    data,
    session_master,
):

    rows = []

    races = data.get("races", [])

    session_map = {}

    venue_times = {}

    for race in races:

        venue_key = (
            race.get("開催日"),
            race.get("競輪場コード"),
        )

        venue_times.setdefault(venue_key, [])

        start = race.get("発走時刻")

        if start:

            venue_times[venue_key].append(start)

    for venue_key, times in venue_times.items():

        if times:

            session_map[venue_key] = detect_session(

                min(times),
               max(times),
                session_master,

            )

        else:

            session_map[venue_key] = "不明"

    for race in races:

        rows.append({

            "race_key": race.get("race_key"),
            "date": race.get("開催日"),
            "jo_code": race.get("競輪場コード"),
            "jo_name": race.get("競輪場名"),
            "event_name": race.get("開催名"),
            "grade": race.get("グレード"),
            "race_no": race.get("レース番号"),
            "track_length": race.get("周長(m)"),
            "straight_length": race.get("みなし直線(m)"),
            "bank_angle": race.get("カント角(度)"),
            "race_type": race.get("レース種別"),
            "session": session_map.get(

                (
                    race.get("開催日"),
                    race.get("競輪場コード"),
                ),

                "不明",

            ),
            "weather": race.get("天候"),
            "wind_speed": race.get("風速"),

        })

    return rows

# ===========================================================
# CSV保存
# ===========================================================

def save_race_csv(rows):

    output_path = RACE_CSV_DIR / "historical_race.csv"

    with open(
        output_path,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=RACE_HEADERS,
            extrasaction="raise"
        )

        writer.writeheader()

        writer.writerows(rows)

    return output_path

"""
===========================================================
Part4
・main
===========================================================
"""

def main():

    print("===" * 20)
    print("007 Historical Race CSV Builder")
    print("===" * 20)

    json_files = get_historical_json_files()

    print(f"対象ファイル数: {len(json_files)}")

    session_master = load_session_master()

    rows = []

    total_races = 0

    for path in json_files:

        print(f"読込中: {path.name}")

        race_json = load_race_json(path)

        race_rows = build_race_rows(

            race_json,

            session_master,

        )

        rows.extend(race_rows)

        total_races += len(race_rows)

    print()
    print(f"総レース数: {total_races}")

    output_path = save_race_csv(rows)

    print()
    print("保存先")
    print(output_path)

    print()
    print("=== 007 完了 ===")


if __name__ == "__main__":

    main()

# ===========================================================
# End
# ===========================================================