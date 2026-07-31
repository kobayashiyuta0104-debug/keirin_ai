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

TODAY_DIR = BASE / "data_official" / "today"
TODAY_DIR.mkdir(parents=True, exist_ok=True)

# 当日の日付
JST = timezone(timedelta(hours=9))
TARGET_DATE = datetime.now(JST).strftime("%Y%m%d")

import time

print("datetime.now(JST) =", datetime.now(JST))
print("TARGET_DATE =", TARGET_DATE)
print("time.tzname =", time.tzname)

# 保存先
PLAYER_FILE = TODAY_DIR / "today_player.json"


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
# 当日の選手データ収集
# ===========================================================

def collect_today_player():
    collector = load_collector_module()

    print()
    print("=== 当日の選手データ収集開始 ===")
    print("TARGET_DATE:", TARGET_DATE)

    daily_map = collector.build_daily_race_map(TARGET_DATE)

    players = []
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

            jsj006 = raw_race.get("jsj006", {})

            sensyu_list = jsj006.get("sensyuTypeInfo", [])

            player_count = len(sensyu_list)

            if player_count > 0:

                player_found_count += 1

            for sensyu in sensyu_list:

                row = {

                    "race_key": race_key,

                    "date": TARGET_DATE,

                    "jo_code": jsj006.get("bKeirinjyoCd"),

                    "jo_name": venue_name,

                    "race_no": race_item.get("race_no"),

                    "car_no": int(sensyu.get("syaban")),

                    "player_id": sensyu.get("sensyuRegistNo"),

                    "player_name": sensyu.get("sensyuName"),

                    "prefecture": sensyu.get("huKen"),

                    "age": int(sensyu.get("age", 0)),

                    "term": int(sensyu.get("sotugyouki") or 0),

                    "class": sensyu.get("kyuhan"),

                    "previous_class": sensyu.get("prevKyuhan"),

                    "style": sensyu.get("kyakusitu"),

                    "average_score": float(sensyu.get("heikinTokuten") or 0),
                    "win_rate": float(sensyu.get("syouritu") or 0),
                    "quinella_rate": float(sensyu.get("rentairitu2") or 0),
                    "trio_rate": float(sensyu.get("rentairitu3") or 0),
                    "escape_count": int(sensyu.get("nigeCnt", 0)),

                    "makuri_count": int(sensyu.get("makuriCnt", 0)),

                    "sashi_count": int(sensyu.get("sasiCnt", 0)),

                    "mark_count": int(sensyu.get("markCnt", 0)),

                    "back_count": int(sensyu.get("backCnt", 0)),

                    "home_count": int(sensyu.get("homeTori", 0)),

                    "start_count": int(sensyu.get("stTori", 0)),

                }

                players.append(row)

    output = {
        "program": "017_collect_today_player.py",
        "data_type": "PLAYER",
        "target_date": TARGET_DATE,
        "player_count": len(players),
        "player_found_count": player_found_count,
        "players": players,
    }

    save_json(PLAYER_FILE, output)

    print()
    print("================================")
    print("取得選手数 :", len(players))
    print("選手取得成功 :", player_found_count)
    print("保存先       :", PLAYER_FILE)
    print("================================")

    print()
    print("保存:", PLAYER_FILE)
    print("=== 完了 ===")
    return output


# ===========================================================
# main
# ===========================================================

if __name__ == "__main__":
    collect_today_player()

