import json
import urllib.request
import urllib.parse
import importlib.util
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ===========================================================
# 基本設定
# ===========================================================

import os

if os.name == "nt":
    BASE = Path(r"C:\競輪AI")
else:
    BASE = Path(__file__).resolve().parent.parent

OFFICIAL_PROGRAM_DIR = BASE / "official_program"
ORIGIN_PROGRAM_DIR = BASE  / "official_program"/ "origin_program"

COLLECTOR_FILE = BASE / "official_program" / "origin_program" / "004_collect_historical_raw.py"

DAILY_DIR = BASE / "data_official" / "daily" / "player"
DAILY_DIR.mkdir(parents=True, exist_ok=True)

# 前日の日付
JST = timezone(timedelta(hours=9))
TARGET_DATE = (datetime.now(JST) - timedelta(days=1)).strftime("%Y%m%d")

import time

print("datetime.now(JST) =", datetime.now(JST))
print("TARGET_DATE =", TARGET_DATE)
print("time.tzname =", time.tzname)

# 保存先
PLAYER_FILE = DAILY_DIR / f"{TARGET_DATE}_player.json"


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
# 前日の選手データ収集
# ===========================================================

def collect_today_player():
    collector = load_collector_module()

    print()
    print("=== 前日の選手データ収集開始 ===")
    print("TARGET_DATE:", TARGET_DATE)

    daily_map = collector.build_daily_race_map(TARGET_DATE)

    races = []
    race_total = daily_map.get("race_count", 0)
    current_index = 0

    player_found_count = 0

    for venue in daily_map.get("venues", []):
        venue_name = venue.get("venue")

        for race_item in venue.get("races", []):
            current_index += 1

            race_key = race_item.get("race_key")
            encp = race_item.get("encParaR")

            print(f"[{current_index}/{race_total}] {race_key}")

            # JSJ006（選手能力）
            raw_race = collector.fetch_race_raw(
                TARGET_DATE,
                venue_name,
                race_item,
            )

            player_count = raw_race.get("player_count", 0)
            if player_count > 0:
                player_found_count += 1

            row = {
                "race_key": race_key,
                "race_date": TARGET_DATE,
                "venue": venue_name,
                "race_no": race_item.get("race_no"),
                "encParaR": encp,
                "player_count": player_count,
                "jsj006": raw_race.get("jsj006"),
            }

            races.append(row)

    output = {
        "program": "001_collect_today_player.py",
        "data_type": "PLAYER",
        "target_date": TARGET_DATE,
        "race_count": len(races),
        "player_found_count": player_found_count,
        "races": races,
    }

    save_json(PLAYER_FILE, output)

    print()
    print("保存:", PLAYER_FILE)
    print("=== 完了 ===")

    return output


# ===========================================================
# main
# ===========================================================

if __name__ == "__main__":
    collect_today_player()
