"""
===========================================================
競輪AI 正式版
005_export_player_csv.py

Part 1
・基本設定
・入力ファイル自動検出
・CSV出力準備
・共通関数
===========================================================
"""

import json
import csv
from pathlib import Path


# ===========================================================
# 基本設定
# ===========================================================

BASE = Path(r"C:\競輪AI")

DAILY_DIR = BASE / "data_official" / "daily"
PLAYER_CSV_DIR = BASE / "csv" / "player"

PLAYER_CSV_DIR.mkdir(parents=True, exist_ok=True)


# ===========================================================
# 最新integrated.json自動検出
# ===========================================================

def find_latest_pre_race_json():
    """
    data_official/daily 内の *_pre_race.json を自動検出
    最も新しい日付のファイルを返す
    """
def find_previous_pre_race_json():
    candidates = []

    for path in DAILY_DIR.glob("*_pre_race.json"):
        name = path.name
        try:
            date_text = name.split("_")[0]
            int(date_text)
            candidates.append((date_text, path))
        except Exception:
            continue

    if len(candidates) < 2:
        raise FileNotFoundError("前日の integrated.json が見つかりません")

    # 日付で降順ソート（最新が先頭）
    candidates.sort(key=lambda x: x[0], reverse=True)

    # 最新 → 当日
    # 2番目 → 前日
    return candidates[1][1]

    candidates = []

    for path in DAILY_DIR.glob("*_pre_race.json"):
        name = path.name
        try:
            date_text = name.split("_")[0]
            int(date_text)  # YYYYMMDD が整数として解釈できるか
            candidates.append((date_text, path))
        except Exception:
            continue

    if not candidates:
        raise FileNotFoundError("integrated.json が見つかりません")

    candidates.sort(key=lambda x: x[0], reverse=True)

    return candidates[0][1]


# ===========================================================
# CSVヘッダー（日本語）
# ===========================================================

PLAYER_HEADERS = [
    "レースキー",
    "開催日",
    "競輪場",
    "レース番号",
    "車番",
    "登録番号",
    "選手名",
    "府県",
    "年齢",
    "期別",
    "級班",
    "前級班",
    "脚質",
    "ギヤ倍率",
    "平均競走得点",
    "勝率",
    "２連対率",
    "３連対率",
    "逃げ",
    "捲り",
    "差し",
    "マーク",
    "バック",
    "ホーム",
    "スタート",
    "誘導選手",
    "status",
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

def build_player_row(race, player):
    """
    1選手をCSV行へ変換
    """
    return {
        "レースキー": race.get("race_key"),
        "開催日": race.get("race_date"),
        "競輪場": race.get("venue"),
        "レース番号": race.get("race_no"),

        "車番": player.get("car_no"),
        "登録番号": player.get("player_id"),
        "選手名": normalize_space(player.get("player_name")),
        "府県": normalize_space(player.get("prefecture")),
        "年齢": to_int(player.get("age")),
        "期別": to_int(player.get("graduation_term")),
        "級班": player.get("class"),
        "前級班": player.get("previous_class"),
        "脚質": player.get("riding_style"),

        "ギヤ倍率": player.get("giyaritu") or None,

        "平均競走得点": to_float(player.get("race_score")),
        "勝率": to_float(player.get("win_rate")),
        "２連対率": to_float(player.get("top2_rate")),
        "３連対率": to_float(player.get("top3_rate")),

        "逃げ": to_int(player.get("nige_count")),
        "捲り": to_int(player.get("makuri_count")),
        "差し": to_int(player.get("sashi_count")),
        "マーク": to_int(player.get("mark_count")),
        "バック": to_int(player.get("back_count")),
        "ホーム": to_int(player.get("home_count")),
        "スタート": to_int(player.get("start_count")),

        "誘導選手": player.get("yudoSensyu") or None,

        "status": race.get("status"),
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
            "giyaritu": p.get("giyaritu"),
            "yudoSensyu": p.get("yudoSensyu"),
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
    integrated.json の races[] を走査し、全選手のCSV行を生成する
    """

    races = integrated.get("races")
    if not isinstance(races, list):
        return []

    rows = []

    for race in races:
        players = extract_players_from_race(race)

        for player in players:
            row = build_player_row(race, player)
            rows.append(row)

    return rows



# ===========================================================
# CSV保存
# ===========================================================

def save_player_csv(rows, date_text):
    """
    player CSV を保存する
    """

    output_path = PLAYER_CSV_DIR / f"{date_text}_player.csv"

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
    print("005 Player CSV Exporter")
    print("===" * 20)

    # 前日 pre_race.json 自動検出
    pre_race_path = find_previous_pre_race_json()
    date_text = pre_race_path.name.split("_")[0]

    print(f"検出された最新ipre_race: {pre_race_path}")
    print(f"対象日付: {date_text}")

    # 読込
    pre_race = load_pre_race_json(pre_race_path)

    # 全選手行生成
    rows = build_all_player_rows(pre_race)

    print(f"レース数: {len(pre_race.get('races', []))}")
    print(f"選手行数: {len(rows)}")

    # CSV保存
    output_path = save_player_csv(rows, date_text)

    print()
    print("保存先:")
    print(output_path)

    print()
    print("=== 005 完了 ===")


if __name__ == "__main__":
    main()


# ===========================================================
# End Part 4
# ===========================================================
