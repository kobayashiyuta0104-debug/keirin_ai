"""
===========================================================
競輪AI 正式版
006_build_historical_player_csv.py

Part 1
・基本設定
・入力ファイル自動検出
・CSV出力準備
・共通関数
===========================================================
"""

import json
import csv
import os
from pathlib import Path


# ===========================================================
# 基本設定
# ===========================================================

import os

if os.name == "nt":
    BASE = Path(r"C:\競輪AI")
else:
    BASE = Path(__file__).resolve().parent.parent

HISTORICAL_DIR = BASE / "data_official" / "historical" / "players"
PLAYER_CSV_DIR = BASE / "csv" / "historical_player"

PLAYER_CSV_DIR.mkdir(parents=True, exist_ok=True)


# ===========================================================
# historical JSON 一覧取得
# ===========================================================

def get_historical_json_files():
    files = sorted(HISTORICAL_DIR.glob("*_player.json"))

    if not files:
        raise FileNotFoundError("historical player.json が見つかりません")

    return files

# ===========================================================
# CSVヘッダー（日本語）
# ===========================================================

PLAYER_HEADERS = [
    "race_key",
    "date",
    "jo_code",
    "jo_name",
    "race_no",

    "car_no",
    "player_id",
    "player_name",
    "prefecture",
    "age",
    "term",
    "class",
    "previous_class",
    "style",

    "average_score",
    "win_rate",
    "quinella_rate",
    "trio_rate",

    "escape_count",
    "makuri_count",
    "sashi_count",
    "mark_count",
    "back_count",
    "home_count",
    "start_count",
]


# ===========================================================
# 共通変換
# ===========================================================

def to_int(value):
    if value in ("", None):
        return None
    try:
        return int(float(str(value).replace(",", "").replace("%", "")))
    except Exception:
        return None


def to_float(value):
    if value in ("", None):
        return None
    try:
        return float(str(value).replace(",", "").replace("%", ""))
    except Exception:
        return None


def normalize_space(value):
    if not isinstance(value, str):
        return value
    return " ".join(value.replace("\u3000", " ").split())


# ===========================================================
# Part 1 End
# ===========================================================


"""
===========================================================
Part 2
・integrated.json 読込
・レース単位で選手一覧抽出
・player行生成
===========================================================
"""

# ===========================================================
# integrated.json 読込
# ===========================================================

def load_pre_race_json(path):
    """
    integrated.json を読込む
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ===========================================================
# 選手行生成
# ===========================================================

def build_player_row(race, player, venue_name, jo_code, target_date):
    """
    1選手をCSV行へ変換
    """

    return {
        "race_key": race.get("race_key"),
        "date": target_date,
        "jo_code": jo_code,
        "jo_name": venue_name,
        "race_no": race.get("race_no"),

        "car_no": player.get("car_no"),
        "player_id": player.get("player_id"),
        "player_name": normalize_space(player.get("player_name")),
        "prefecture": normalize_space(player.get("prefecture")),
        "age": to_int(player.get("age")),
        "term": to_int(player.get("graduation_term")),
        "class": player.get("class"),
        "previous_class": player.get("previous_class"),
        "style": player.get("riding_style"),

        "average_score": to_float(player.get("race_score")),
        "win_rate": to_float(player.get("win_rate")),
        "quinella_rate": to_float(player.get("top2_rate")),
        "trio_rate": to_float(player.get("top3_rate")),

        "escape_count": to_int(player.get("nige_count")),
        "makuri_count": to_int(player.get("makuri_count")),
        "sashi_count": to_int(player.get("sashi_count")),
        "mark_count": to_int(player.get("mark_count")),
        "back_count": to_int(player.get("back_count")),
        "home_count": to_int(player.get("home_count")),
        "start_count": to_int(player.get("start_count")),
    }

# ===========================================================
# レース → 選手一覧展開
# ===========================================================

def extract_players_from_race(race):
    """
    integrated.json の race から players を抽出
    """

    jsj006 = race.get("jsj006")
    if not isinstance(jsj006, dict):
        return []

    players_raw = jsj006.get("sensyuTypeInfo")
    if not isinstance(players_raw, list):
        return []

    players = []

    for p in players_raw:
        player = {
            "car_no": to_int(p.get("syaban")),
            "player_id": str(p.get("sensyuRegistNo", "")).zfill(6),
            "player_name": normalize_space(p.get("sensyuName")),
            "prefecture": normalize_space(p.get("huKen")),
            "graduation_term": to_int(p.get("sotugyouki")),
            "age": to_int(p.get("age")),
            "class": p.get("kyuhan"),
            "previous_class": p.get("prevKyuhan"),
            "riding_style": p.get("kyakusitu"),
            "race_score": to_float(p.get("heikinTokuten")),
            "nige_count": to_int(p.get("nigeCnt")),
            "makuri_count": to_int(p.get("makuriCnt")),
            "sashi_count": to_int(p.get("sasiCnt")),
            "mark_count": to_int(p.get("markCnt")),
            "back_count": to_int(p.get("backCnt")),
            "home_count": to_int(p.get("homeTori")),
            "start_count": to_int(p.get("stTori")),
            "win_rate": to_float(p.get("syouritu")),
            "top2_rate": to_float(p.get("rentairitu2")),
            "top3_rate": to_float(p.get("rentairitu3")),
        }

        players.append(player)

    players.sort(key=lambda x: x["car_no"] if x["car_no"] is not None else 99)

    return players



# ===========================================================
# Part 3
# 全レース処理
# player行の一括生成
# CSV保存
# ===========================================================

def build_all_player_rows(integrated):
    """
    historical player.json の全選手をCSV行へ変換
    """

    venues = integrated.get("venues")

    if not isinstance(venues, list):
        return []

    rows = []

    for venue in venues:

        venue_name = venue.get("venue")
        jo_code = str(venue.get("bank_code", "")).zfill(2)
        races = venue.get("races")
        target_date = integrated.get("target_date")

        if not isinstance(races, list):
            continue

        for race in races:

            players = extract_players_from_race(race)

            for player in players:

                rows.append(
                    build_player_row(
                        race,
                        player,
                        venue_name,
                        jo_code,
                        target_date
                    )
                )

    return rows

# ===========================================================
# CSV保存
# ===========================================================

def save_player_csv(rows):
    """
    player CSV を保存する
    """

    output_path = PLAYER_CSV_DIR / "historical_player.csv"

    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=PLAYER_HEADERS, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)

    return output_path


# ===========================================================
# Part 3 End
# ===========================================================

"""
===========================================================
#Part 4
・main
・最新pre_race.json → player.csv 出力
===========================================================
"""

# ===========================================================
# main
# ===========================================================

def main():
    print("===" * 20)
    print("006 Historical Player CSV Builder")
    print("===" * 20)

    # historical JSON一覧取得
    json_files = get_historical_json_files()

    print(f"対象ファイル数: {len(json_files)}")

    rows = []
    total_races = 0

    for path in json_files:

        print(f"読込中: {path.name}")

        pre_race = load_pre_race_json(path)
        for venue in pre_race.get("venues", []):
            total_races += len(venue.get("races", []))

        race_rows = build_all_player_rows(pre_race)

        rows.extend(race_rows)

    print()
    print(f"総レース数: {total_races}")
    print(f"総選手行数: {len(rows)}")

    # CSV保存
    output_path = save_player_csv(rows)

    print()
    print("保存先:")
    print(output_path)

    print()
    print("=== 006 完了 ===")


if __name__ == "__main__":
    main()


# ===========================================================
# End Part 4
# ===========================================================
