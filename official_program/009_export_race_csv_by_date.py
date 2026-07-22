"""
===========================================================
競輪AI 正式版
009_export_race_csv_by_date.py

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

RACE_DATA_DIR = BASE / "data_official" / "daily" / "race_data"
RACE_CSV_DIR = BASE / "csv" / "race"

SESSION_MASTER_FILE = (
    BASE
    / "data_official"
    / "master"
    / "session_master.json"
)

RACE_CSV_DIR.mkdir(parents=True, exist_ok=True)

# ===========================================================
# 対象期間
# ===========================================================

START_DATE = "20260716"
END_DATE = "20260721"

# ===========================================================
# 最新 race_data.json 自動検出
# ===========================================================

def find_target_race_jsons():

    targets = []

    for path in sorted(RACE_DATA_DIR.glob("*_race_data.json")):

        date_text = path.name.split("_")[0]

        if START_DATE <= date_text <= END_DATE:

            targets.append((date_text, path))

    if not targets:

        raise FileNotFoundError("対象期間のrace_data.jsonが見つかりません")

    return targets

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

    races = data.get("races", [])

    rows = []

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

            session_map[venue_key] = "unknown"

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

                "unknown",

            ),
            "weather": race.get("天候"),
            "wind_speed": race.get("風速"),

        })

    return rows

# ===========================================================
# CSV保存
# ===========================================================

def save_race_csv(rows, date_text):

    output_path = RACE_CSV_DIR / f"{date_text}_race.csv"

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
    print("007 Race CSV Exporter")
    print("===" * 20)

    session_master = load_session_master()

    targets = find_target_race_jsons()

    for date_text, race_json_path in targets:

        print()
        print("=" * 60)
        print(date_text)

        race_json = load_race_json(race_json_path)

        rows = build_race_rows(

            race_json,

            session_master,

        )

        print(f"レース数: {len(rows)}")

        output_path = save_race_csv(

            rows,

            date_text,

        )

    print(f"保存完了: {output_path}")
    print()
    print("=== 009 完了 ===")


if __name__ == "__main__":

    main()

# ===========================================================
# End
# ===========================================================