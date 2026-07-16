"""
===========================================================
競輪AI 正式版
007_export_race_csv.py

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

RACE_CSV_DIR.mkdir(parents=True, exist_ok=True)

# ===========================================================
# 最新 race_data.json 自動検出
# ===========================================================

def find_latest_race_json():

    candidates = []

    for path in RACE_DATA_DIR.glob("*_race_data.json"):

        try:
            date_text = path.name.split("_")[0]
            int(date_text)
            candidates.append((date_text, path))
        except:
            pass

    if len(candidates) == 0:
        raise FileNotFoundError("race_data.json が見つかりません")

    candidates.sort(key=lambda x: x[0], reverse=True)

    return candidates[0][1]

# ===========================================================
# CSVヘッダー
# ===========================================================

RACE_HEADERS = [

    "レースキー",
    "開催日",
    "競輪場コード",
    "競輪場名",
    "開催名",
    "グレード",
    "レース番号",
    "周長(m)",
    "みなし直線(m)",
    "カント角(度)",
    "レース種別",
    "距離",
    "周回数",
    "発走時刻",
    "投票締切",
    "天候",
    "風速",

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

"""
===========================================================
Part3
・CSV行生成
===========================================================
"""

def build_race_rows(data):

    races = data.get("races", [])

    rows = []

    for race in races:

        rows.append({

            "レースキー": race.get("race_key"),
            "開催日": race.get("開催日"),
            "競輪場コード": race.get("競輪場コード"),
            "競輪場名": race.get("競輪場名"),
            "開催名": race.get("開催名"),
            "グレード": race.get("グレード"),
            "レース番号": race.get("レース番号"),
            "周長(m)": race.get("周長(m)"),
            "みなし直線(m)": race.get("みなし直線(m)"),
            "カント角(度)": race.get("カント角(度)"),
            "レース種別": race.get("レース種別"),
            "距離": race.get("距離"),
            "周回数": race.get("周回数"),
            "発走時刻": race.get("発走時刻"),
            "投票締切": race.get("投票締切"),
            "天候": race.get("天候"),
            "風速": race.get("風速"),

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

    race_json_path = find_latest_race_json()

    date_text = race_json_path.name.split("_")[0]

    print(f"検出された最新race_data: {race_json_path}")
    print(f"対象日付: {date_text}")

    race_json = load_race_json(race_json_path)

    rows = build_race_rows(race_json)

    print(f"レース数: {len(rows)}")

    output_path = save_race_csv(
        rows,
        date_text
    )

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