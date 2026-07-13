import json
import importlib.util
from datetime import datetime, timedelta
from pathlib import Path

# ===========================================================
# 基本設定
# ===========================================================

BASE = Path(r"C:\競輪AI")

OFFICIAL_PROGRAM_DIR = BASE / "official_program"
ORIGIN_PROGRAM_DIR = BASE / "official_program"/ "origin_program" 

COLLECTOR_FILE = BASE/ "official_program" / "origin_program"  / "004_collect_historical_raw.py"


DAILY_DIR = BASE / "data_official" / "daily"
DAILY_DIR.mkdir(parents=True, exist_ok=True)

# 昨日の日付
YESTERDAY = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

# 保存先
INTEGRATED_FILE = DAILY_DIR / f"{YESTERDAY}_integrated.json"


# ===========================================================
# JSON
# ===========================================================

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ===========================================================
# 004 モジュール読込
# ===========================================================

def load_collector_module():
    if not COLLECTOR_FILE.exists():
        raise FileNotFoundError("004_collect_historical_raw.py がありません")

    spec = importlib.util.spec_from_file_location(
        "official_collector_004",
        COLLECTOR_FILE,
    )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ===========================================================
# 昨日の確定結果収集
# ===========================================================

def collect_yesterday_results():
    collector = load_collector_module()

    print()
    print("=== 昨日の確定結果収集開始 ===")
    print("YESTERDAY:", YESTERDAY)

    daily_map = collector.build_daily_race_map(YESTERDAY)

    connected_rows = []
    race_total = daily_map.get("race_count", 0)
    current_index = 0

    for venue in daily_map.get("venues", []):
        venue_name = venue.get("venue")

        for race_item in venue.get("races", []):
            current_index += 1

            race_key = race_item.get("race_key")

            print(f"[{current_index}/{race_total}] {race_key}")

            # 昨日の結果を取得
            fresh_raw = collector.fetch_race_raw(
                YESTERDAY,
                venue_name,
                race_item,
            )

            result_count = fresh_raw.get("result_count", 0)
            has_trifecta = fresh_raw.get("has_trifecta_result", False)

            connected = {
                "race_key": race_key,
                "race_date": YESTERDAY,
                "venue": venue_name,
                "race_no": race_item.get("race_no"),
                "encParaR": race_item.get("encParaR"),
                "result_count": result_count,
                "has_trifecta_result": has_trifecta,
                "jsj012": fresh_raw.get("jsj012"),
            }

            connected_rows.append(connected)

            print("RESULT:", result_count)
            print("TRIFECTA:", has_trifecta)

    output = {
        "program": "002_collect_yesterday_result.py",
        "data_type": "INTEGRATED",
        "target_date": YESTERDAY,
        "race_count": len(connected_rows),
        "races": connected_rows,
    }

    save_json(INTEGRATED_FILE, output)

    print()
    print("保存:", INTEGRATED_FILE)
    print("=== 完了 ===")

    return output


# ===========================================================
# main
# ===========================================================

if __name__ == "__main__":
    collect_yesterday_results()
