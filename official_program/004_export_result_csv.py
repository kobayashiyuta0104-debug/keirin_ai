"""
===========================================================
競輪AI 正式版
006_export_result_csv.py

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

DAILY_DIR = BASE / "data_official" / "daily" / "result"
RESULT_CSV_DIR = BASE / "csv" / "result"

RESULT_CSV_DIR.mkdir(parents=True, exist_ok=True)

# ===========================================================
# 最新result.json自動検出
# ===========================================================

def find_latest_result_json():
    candidates = []

    for path in DAILY_DIR.glob("*_result.json"):
        name = path.name
        try:
            date_text = name.split("_")[0]
            int(date_text)
            candidates.append((date_text, path))
        except Exception:
            continue

    if not candidates:
        raise FileNotFoundError("result.json が見つかりません")

    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]

# ===========================================================
# CSVヘッダー（日本語）
# ===========================================================

RESULT_HEADERS = [
    "レースキー",
    "開催日",
    "競輪場",
    "レース番号",
    "車番",
    "登録番号",
    "着順",
    "結果ステータス",
    "結果理由",
    "3連単組番",
    "3連単払戻",
    "人気",
    "払戻分類",
    "is_20000_plus",
    "is_50000_plus",
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
    trifecta_pop = trifecta.get("ninki") if trifecta else None

    # 払戻分類（001と同じロジック）
    if trifecta_payout is None:
        payout_class = None
    elif trifecta_payout < 10000:
        payout_class = "UNDER_10000"
    elif trifecta_payout < 20000:
        payout_class = "10000_TO_19999"
    elif trifecta_payout < 50000:
        payout_class = "20000_TO_49999"
    else:
        payout_class = "50000_PLUS"

    rows = []

    for r in results_raw:
        car_no = to_int(r.get("syaban"))
        player_id = str(r.get("sensyuRegistNo", "")).zfill(6)
        finish_rank = to_int(r.get("tyaku"))

        # 個人状態
        status = "NORMAL"
        note = None

        state_list = r.get("kojinStateItemSubData", [])

        if isinstance(state_list, list) and state_list:

            state = state_list[0]

            status = state.get("kojinState")
            if not status:
                status = "NORMAL"

            reason = state.get("tyakuNote")
            if not note:
                note = None
            note = state.get("tyakuNote")

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
            "レースキー": race.get("race_key"),
            "開催日": race.get("race_date"),
            "競輪場": race.get("venue"),
            "レース番号": race.get("race_no"),

            "車番": car_no,
            "登録番号": player_id,
            "着順": finish_rank,

            "結果ステータス": status,
            "結果理由": note,

            "3連単組番": trifecta_comb,
            "3連単払戻": trifecta_payout,
            "人気": trifecta_pop,

            "払戻分類": payout_class,
            "is_20000_plus": int(trifecta_payout >= 20000) if trifecta_payout else None,
            "is_50000_plus": int(trifecta_payout >= 50000) if trifecta_payout else None,
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
    races = result.get("races")
    if not isinstance(races, list):
        return []

    rows = []

    for race in races:
        result_rows = build_result_rows_from_race(race)
        rows.extend(result_rows)

    return rows

# ===========================================================
# CSV保存
# ===========================================================

def save_result_csv(rows, date_text):
    output_path = RESULT_CSV_DIR / f"{date_text}_result.csv"

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

    result_path = find_latest_result_json()
    date_text = result_path.name.split("_")[0]

    print(f"検出された最新result: {result_path}")
    print(f"対象日付: {date_text}")

    result = load_result_json(result_path)

    rows = build_all_result_rows(result)

    print(f"レース数: {len(result.get('races', []))}")
    print(f"結果行数: {len(rows)}")

    output_path = save_result_csv(rows, date_text)

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
