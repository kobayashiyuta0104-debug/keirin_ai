"""
===========================================================
競輪AI 正式版
010_export_result_csv_by_date.py

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
from datetime import datetime, timedelta

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
BANK_MASTER_FILE = BASE / "data_official" / "master" / "bank_master.json"

RESULT_CSV_DIR.mkdir(parents=True, exist_ok=True)

# ===========================================================
# 対象期間
# ===========================================================

START_DATE = "20260716"
END_DATE = "20260721"

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
def get_result_json_path(date_text):
    path = DAILY_DIR / f"{date_text}_result.json"

    if not path.exists():
        print(f"[SKIP] {date_text} result.json がありません")
        return None

    return path

def generate_target_dates(start_date, end_date):
    dates = []

    current = datetime.strptime(start_date, "%Y%m%d")
    end = datetime.strptime(end_date, "%Y%m%d")

    while current <= end:
        dates.append(current.strftime("%Y%m%d"))
        current += timedelta(days=1)

    return dates

def load_result_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_bank_master():
    with open(BANK_MASTER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_jo_code(bank_master, jo_name):
    banks = bank_master.get("banks", {})

    for bank in banks.values():
        if bank.get("競輪場名") == jo_name:
            return bank.get("競輪場コード")

    return None

# ===========================================================
# JSJ012 → result行生成
# ===========================================================

def build_result_rows_from_race(race, bank_master):
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
    jo_code = get_jo_code(bank_master, race.get("venue"))

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
            "race_key": race.get("race_key"),
            "date": race.get("race_date"),
            "jo_code": jo_code,
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

def build_all_result_rows(result, bank_master):
    races = result.get("races")
    if not isinstance(races, list):
        return []

    rows = []

    for race in races:
        result_rows = build_result_rows_from_race(race, bank_master)
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
    print("010 Result CSV Exporter By Date")
    print("===" * 20)

    bank_master = load_bank_master()

    total_races = 0
    total_rows = 0

    target_dates = generate_target_dates(START_DATE, END_DATE)

    for date_text in target_dates:

        result_path = get_result_json_path(date_text)

        if result_path is None:
            continue

        print()
        print("=" * 60)
        print(f"対象日付: {date_text}")

        result = load_result_json(result_path)

        rows = build_all_result_rows(result, bank_master)

        output_path = save_result_csv(rows, date_text)

        race_count = len(result.get("races", []))
        row_count = len(rows)

        total_races += race_count
        total_rows += row_count

        print(f"レース数: {race_count}")
        print(f"結果行数: {row_count}")
        print(f"保存: {output_path}")

    print()
    print("=" * 60)
    print("全期間 完了")
    print(f"対象日数: {len(target_dates)}")
    print(f"総レース数: {total_races}")
    print(f"総結果行数: {total_rows}")


# ===========================================================
# End Part 4
# ===========================================================

if __name__ == "__main__":
    main()