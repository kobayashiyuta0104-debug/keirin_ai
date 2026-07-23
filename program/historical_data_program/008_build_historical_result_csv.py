"""
===========================================================
競輪AI 正式版
008_build_historical_result_csv.py

Part 1
・基本設定
・入力ファイル自動検出
・CSV出力準備
・共通変換
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

HISTORICAL_DIR = BASE / "data_official" / "historical" / "result"
RESULT_CSV_DIR = BASE / "csv" / "historical_result"

RESULT_CSV_DIR.mkdir(parents=True, exist_ok=True)

# ===========================================================
# 最新result.json自動検出
# ===========================================================

def get_historical_json_files():

    files = sorted(HISTORICAL_DIR.glob("*_result.json"))

    if not files:
        raise FileNotFoundError("historical result.json が見つかりません")

    return files

# ===========================================================
# CSVヘッダー（日本語）
# ===========================================================

RESULT_HEADERS = [
    "race_key",
    "date",
    "jo_code",
    "jo_name",
    "race_no",
    "car_no",
    "player_id",
    "finish_order",
    "result_status",
    "result_reason",
    "trifecta",
    "trifecta_payout",
    "popularity",
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


"""
===========================================================
Part 2
・result.json 読込
・JSJ012（着順 + 払戻）抽出
・result行生成
===========================================================
"""

# ===========================================================
# result.json 読込
# ===========================================================

def load_result_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ===========================================================
# JSJ012 → result行生成
# ===========================================================

def build_result_rows_from_race(race):
    """
    1レースの JSJ012 から result行を生成
    """

    jsj012 = race.get("jsj012")
    if not isinstance(jsj012, dict):
        return []

    # 着順データ
    results_raw = jsj012.get("tyakujyunItemSubData")
    if not isinstance(results_raw, list):
        results_raw = []

    # 払戻データ
    harai = jsj012.get("haraiGakuSubData")
    if not isinstance(harai, dict):
        harai = {}

    rt3 = harai.get("RT3HaraiGakuDispItemSubData")
    if not isinstance(rt3, list):
        rt3 = []

    # 3連単の最初の項目を採用（001と同じ仕様）
    trifecta = None
    for item in rt3:
        if isinstance(item, dict) and item.get("kumiBan"):
            trifecta = item
            break

    trifecta_comb = trifecta.get("kumiBan") if trifecta else None
    trifecta_payout = to_int(trifecta.get("haraiGaku")) if trifecta else None
    trifecta_pop = (
        to_int(str(trifecta.get("ninki", "")).replace("(", "").replace(")", ""))
        if trifecta
        else None
    )

    rows = []

    for r in results_raw:
        car_no = to_int(r.get("syaban"))
        player_id = str(r.get("sensyuRegistNo", "")).zfill(6)
        finish_rank = to_int(r.get("tyaku"))

        # ===========================================================
        # 個人状態
        # ===========================================================

        status = "NORMAL"
        note = None

        state_list = r.get("kojinStateItemSubData", [])

        if isinstance(state_list, list) and state_list:

            state = state_list[0]

            status = (state.get("kojinState") or "").strip()

            if status == "":
                status = "NORMAL"

            note = (state.get("tyakuNote") or "").strip()

            if note == "":
                note = None

        else:

            text = (
                str(r.get("kikaku", "")) +
                str(r.get("jyoutai", "")) +
                str(r.get("tyakusa", ""))
            )

            if "落" in text:
                status = "落車"
            elif "失" in text:
                status = "失格"
            elif "棄" in text:
                status = "棄権"
            elif "欠" in text:
                status = "欠場"

        rows.append({
            "race_key": race.get("race_key"),
            "date": race.get("race_date"),
            "jo_code": race.get("jo_code"),
            "jo_name": race.get("venue"),
            "race_no": race.get("race_no"),

            "car_no": car_no,
            "player_id": player_id,
            "finish_order": finish_rank,

            "result_status": status,
            "result_reason": note,

            "trifecta": trifecta_comb,
            "trifecta_payout": trifecta_payout,
            "popularity": trifecta_pop,
        })

    return rows


"""
===========================================================
Part 3
・全レース処理
・result行の一括生成
・CSV保存
===========================================================
"""

# ===========================================================
# 全レース → 全result行生成
# ===========================================================

def build_all_result_rows(result):

    rows = []

    venues = result.get("venues", [])

    for venue in venues:

        venue_name = venue.get("venue")
        target_date = result.get("target_date")

        races = venue.get("races", [])

        for race in races:

            race["venue"] = venue_name
            race["race_date"] = target_date
            race["jo_code"] = venue.get("bank_code")

            result_rows = build_result_rows_from_race(race)

            rows.extend(result_rows)

    return rows

# ===========================================================
# CSV保存
# ===========================================================

def save_result_csv(rows):
    output_path = RESULT_CSV_DIR / "historical_result.csv"

    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=RESULT_HEADERS, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)

    return output_path


"""
===========================================================
Part 4
・main
・最新result.json → result.csv 出力
===========================================================
"""

# ===========================================================
# main
# ===========================================================

def main():
    print("===" * 20)
    print("006 Result CSV Exporter")
    print("===" * 20)

    json_files = get_historical_json_files()

    rows = []
    total_races = 0

    for path in json_files:

        print(f"読込中: {path.name}")

        result = load_result_json(path)

        result_rows = build_all_result_rows(result)

        rows.extend(result_rows)

        for venue in result.get("venues", []):

            total_races += len(venue.get("races", []))

    print()
    print(f"総レース数: {total_races}")
    print(f"結果行数: {len(rows)}")

    output_path = save_result_csv(rows)

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
