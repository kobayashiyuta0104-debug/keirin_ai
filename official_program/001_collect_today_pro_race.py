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

DAILY_DIR = BASE / "data_official" / "daily"
DAILY_DIR.mkdir(parents=True, exist_ok=True)

# 今日の日付
JST = timezone(timedelta(hours=9))
TARGET_DATE = datetime.now(JST).strftime("%Y%m%d")

import time

JST = timezone(timedelta(hours=9))

print("datetime.now(JST) =", datetime.now(JST))
print("TARGET_DATE =", TARGET_DATE)
print("time.tzname =", time.tzname)

# 保存先
PRE_RACE_FILE = DAILY_DIR / f"{TARGET_DATE}_pre_race.json"


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
# JSJ005 直接取得
# ===========================================================

def fetch_jsj005(encp):
    query = urllib.parse.urlencode({
        "encp": encp,
        "type": "JSJ005",
    })

    url = "https://www.keirin.jp/pc/json?" + query

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.keirin.jp/pc/racelive",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read().decode("utf-8", errors="replace")
            return json.loads(raw)
    except Exception:
        return None


# ===========================================================
# ライン復元（本番 collector と完全同じ）
# ===========================================================

def reconstruct_lines(jsj005):

    if not isinstance(jsj005, dict):
        return {
            "line_found": False,
            "prediction_type": None,
            "provider": None,
            "main_lines": [],
            "positions": [],
        }

    narabiyoso = jsj005.get("narabiyoso")

    if not isinstance(narabiyoso, dict):
        return {
            "line_found": False,
            "prediction_type": None,
            "provider": None,
            "main_lines": [],
            "positions": [],
        }

    rows = narabiyoso.get("shaban")
    if not isinstance(rows, list):
        rows = []

    positions = []

    for row in rows:
        if not isinstance(row, dict):
            continue

        try:
            ichi = int(row.get("ichi"))
            shaban = int(row.get("shaban"))
        except:
            continue

        if ichi < 1:
            continue

        if not (1 <= shaban <= 9):
            continue

        positions.append({
            "ichi": ichi,
            "shaban": shaban,
        })

    positions.sort(key=lambda item: (item["ichi"], item["shaban"]))

    main_lines = []
    current_line = []
    previous_ichi = None

    for item in positions:
        ichi = item["ichi"]
        shaban = item["shaban"]

        if previous_ichi is None:
            current_line = [shaban]
        elif ichi == previous_ichi + 1:
            current_line.append(shaban)
        else:
            if current_line:
                main_lines.append(current_line)
            current_line = [shaban]

        previous_ichi = ichi

    if current_line:
        main_lines.append(current_line)

    return {
        "line_found": len(positions) > 0,
        "prediction_type": narabiyoso.get("lineKeitai"),
        "provider": narabiyoso.get("teikyo"),
        "main_lines": main_lines,
        "positions": positions,
    }


# ===========================================================
# 今日のレース前データ収集（本番仕様）
# ===========================================================

def collect_today_pre_race():
    collector = load_collector_module()

    print()
    print("=== 今日のレース前データ収集開始 ===")
    print("TARGET_DATE:", TARGET_DATE)

    daily_map = collector.build_daily_race_map(TARGET_DATE)

    races = []
    race_total = daily_map.get("race_count", 0)
    current_index = 0

    player_found_count = 0
    line_found_count = 0

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

            # JSJ005（ライン予想）
            jsj005 = fetch_jsj005(encp)
            line_info = reconstruct_lines(jsj005)

            player_count = raw_race.get("player_count", 0)
            if player_count > 0:
                player_found_count += 1

            if line_info["line_found"]:
                line_found_count += 1

            row = {
                "race_key": race_key,
                "race_date": TARGET_DATE,
                "venue": venue_name,
                "race_no": race_item.get("race_no"),
                "encParaR": encp,
                "player_count": player_count,
                "line_found": line_info["line_found"],
                "line_prediction": line_info,
                "jsj006": raw_race.get("jsj006"),
                "jsj005": jsj005,
            }

            races.append(row)

    output = {
        "program": "001_collect_today_pro_race.py",
        "data_type": "PRE_RACE",
        "target_date": TARGET_DATE,
        "race_count": len(races),
        "player_found_count": player_found_count,
        "line_found_count": line_found_count,
        "races": races,
    }

    save_json(PRE_RACE_FILE, output)

    print()
    print("保存:", PRE_RACE_FILE)
    print("=== 完了 ===")

    return output


# ===========================================================
# main
# ===========================================================

if __name__ == "__main__":
    collect_today_pre_race()
