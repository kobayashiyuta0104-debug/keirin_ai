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

    rows = []

    races = data.get("races", [])

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

    rows = []

    total_races = 0

    for path in json_files:

        print(f"読込中: {path.name}")

        race_json = load_race_json(path)

        race_rows = build_race_rows(race_json)

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