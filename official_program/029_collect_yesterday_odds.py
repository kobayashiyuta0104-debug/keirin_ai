from pathlib import Path
from datetime import datetime, timedelta, timezone
import base64
import csv
import itertools
import json
import time
import urllib.parse
import urllib.request
import zlib

# ============================================================
# 029
# 前日の race_data から netkeirin の3連単オッズを取得
#
# 実行日が 2026-09-15 の場合 TARGET_DATE = 20260914
#
# 読込:
#   data_official/daily/race_data/YYYYMMDD_race_data.json
# 保存:
#   data_official/daily/odds/YYYYMMDD_odds.json
#   csv/odds/car_number/YYYYMMDD_odds_car_number.csv
#
# race_key は既存 race_data をそのまま使用。
# race_id は netkeirin API 問い合わせ専用。
# 人気順CSVは作成しない。
# ============================================================


def find_base_dir():
    """ローカルC:\\競輪AI / GitHub Actionsのリポジトリルートを自動判定。"""
    local_base = Path(r"C:\競輪AI")
    if local_base.exists():
        return local_base

    # GitHub Actions:
    # リポジトリ/
    # └── official_program/
    #     └── 029_collect_yesterday_odds.py
    # の構成なので、2つ目の親がリポジトリルート
    current = Path(__file__).resolve()
    return current.parent.parent


BASE = find_base_dir()
JST = timezone(timedelta(hours=9))
TARGET_DATE = (datetime.now(JST) - timedelta(days=1)).strftime("%Y%m%d")

RACE_DATA_DIR = BASE / "data_official" / "daily" / "race_data"
JSON_OUTPUT_DIR = BASE / "data_official" / "daily" / "odds"
CAR_NUMBER_OUTPUT_DIR = BASE / "csv" / "odds"

RACE_DATA_FILE = RACE_DATA_DIR / f"{TARGET_DATE}_race_data.json"
ODDS_JSON_FILE = JSON_OUTPUT_DIR / f"{TARGET_DATE}_odds.json"
CAR_NUMBER_CSV_FILE = CAR_NUMBER_OUTPUT_DIR / f"{TARGET_DATE}_odds.csv"
ERROR_JSON_FILE = JSON_OUTPUT_DIR / f"{TARGET_DATE}_odds_error.json"

API_URL = "https://keirin.netkeiba.com/api/race/"
REQUEST_TIMEOUT = 30
REQUEST_INTERVAL_SECONDS = 0.20
MAX_RETRIES = 3
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/142.0.0.0 Safari/537.36"
)

MAX_COMBINATIONS = [
    "-".join(map(str, combo))
    for combo in itertools.permutations(range(1, 10), 3)
]


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def extract_races(data):
    races = data.get("races", [])
    if isinstance(races, list):
        return races
    if isinstance(races, dict):
        return list(races.values())
    return []


def make_race_id(race):
    date = str(race.get("開催日") or race.get("date") or TARGET_DATE).strip()
    jo_code = str(race.get("競輪場コード") or race.get("jo_code") or "").strip()
    race_no = race.get("レース番号") if race.get("レース番号") is not None else race.get("race_no")

    if not date.isdigit() or len(date) != 8:
        raise ValueError(f"開催日が不正です: {date}")
    if not jo_code.isdigit():
        raise ValueError(f"競輪場コードが不正です: {jo_code}")
    if race_no is None:
        raise ValueError("レース番号がありません")

    return f"{date}{int(jo_code):02d}{int(race_no):02d}"


def fetch_race_odds(race_id):
    params = urllib.parse.urlencode({
        "class": "AplRaceOdds",
        "method": "get",
        "compress": "1",
        "race_id": race_id,
        "input": "UTF-8",
        "output": "json",
    }).encode("utf-8")

    request = urllib.request.Request(
        API_URL,
        data=params,
        method="POST",
        headers={
            "User-Agent": USER_AGENT,
            "Referer": f"https://keirin.netkeiba.com/race/odds_new/?race_id={race_id}",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
        },
    )

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
                raw = response.read().decode("utf-8", errors="replace")

            response_data = json.loads(raw)
            if response_data.get("status") != "OK":
                return None, f"API_STATUS_{response_data.get('status')}"

            compressed_text = response_data.get("data", {}).get(f"nkrace_odds::{race_id}")
            if not compressed_text:
                return None, "ODDS_DATA_MISSING"

            decoded_bytes = zlib.decompress(base64.b64decode(compressed_text))
            decoded = json.loads(decoded_bytes.decode("utf-8", errors="replace"))
            return decoded, None

        except Exception as e:
            last_error = repr(e)
            if attempt < MAX_RETRIES:
                time.sleep(1.0 * attempt)

    return None, f"REQUEST_FAILED: {last_error}"


def build_car_number_map(decoded):
    """list_9の組合せ→オッズだけを保存。人気順位はキーにしない。"""
    list_9 = decoded.get("list_9")
    if not isinstance(list_9, list):
        return None, "LIST_9_MISSING"

    odds_map = {}
    for item in list_9:
        if not isinstance(item, list) or len(item) < 2:
            continue

        combo_raw = str(item[0]).strip()
        odds_raw = str(item[1]).strip()
        if len(combo_raw) != 6 or not combo_raw.isdigit():
            continue

        first = int(combo_raw[0:2])
        second = int(combo_raw[2:4])
        third = int(combo_raw[4:6])
        if len({first, second, third}) != 3:
            continue
        if not (1 <= first <= 9 and 1 <= second <= 9 and 1 <= third <= 9):
            continue

        try:
            odds = float(odds_raw)
        except ValueError:
            continue

        combo = f"{first}-{second}-{third}"
        odds_map[combo] = odds

    if not odds_map:
        return None, "NO_TRIFECTA_DATA"

    return odds_map, None


def build_car_number_header():
    return ["race_key", "date", "jo_code", "jo_name", "race_no"] + MAX_COMBINATIONS


def build_car_number_row(race, odds_map):
    date = str(race.get("開催日") or race.get("date") or TARGET_DATE)
    jo_code = str(race.get("競輪場コード") or race.get("jo_code") or "")
    jo_name = str(race.get("競輪場名") or race.get("jo_name") or "")
    race_no = race.get("レース番号") if race.get("レース番号") is not None else race.get("race_no")

    row = [race.get("race_key", ""), date, jo_code, jo_name, race_no]
    for combo in MAX_COMBINATIONS:
        row.append(odds_map.get(combo, ""))
    return row


def main():
    print()
    print("=" * 70)
    print("029 前日3連単オッズ取得")
    print("=" * 70)
    print()
    print("BASE       :", BASE)
    print("実行日時   :", datetime.now(JST))
    print("TARGET_DATE:", TARGET_DATE)
    print()

    JSON_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CAR_NUMBER_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Race Data:")
    print(RACE_DATA_FILE)
    print()

    if not RACE_DATA_FILE.exists():
        print("前日のrace_dataがありません。")
        print("必要ファイル:", RACE_DATA_FILE)
        raise FileNotFoundError(RACE_DATA_FILE)

    race_data = load_json(RACE_DATA_FILE)
    races = extract_races(race_data)
    print("race_data レース数 :", len(races))
    print()

    if not races:
        raise RuntimeError("race_dataからレースを取得できませんでした。")

    success_count = 0
    failed_count = 0
    total_odds_combinations = 0
    problems = []
    daily_races = {}

    with CAR_NUMBER_CSV_FILE.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(build_car_number_header())

        for index, race in enumerate(races, start=1):
            race_key = race.get("race_key", "")
            print(f"[{index}/{len(races)}] {race_key}", end="")

            try:
                race_id = make_race_id(race)
            except Exception as e:
                failed_count += 1
                problems.append({"race_key": race_key, "problem": "RACE_ID_CREATE_ERROR", "error": repr(e)})
                print(" → NG:", repr(e))
                continue

            print(f" race_id={race_id}", end="")
            decoded, error = fetch_race_odds(race_id)

            if error:
                failed_count += 1
                problems.append({"race_key": race_key, "race_id": race_id, "problem": error})
                print(" → NG:", error)
                time.sleep(REQUEST_INTERVAL_SECONDS)
                continue

            odds_map, error = build_car_number_map(decoded)
            if error:
                failed_count += 1
                problems.append({"race_key": race_key, "race_id": race_id, "problem": error})
                print(" → 3連単NG:", error)
                time.sleep(REQUEST_INTERVAL_SECONDS)
                continue

            writer.writerow(build_car_number_row(race, odds_map))

            daily_races[race_key] = {
                "race_key": race_key,
                "date": str(race.get("開催日") or race.get("date") or TARGET_DATE),
                "jo_code": str(race.get("競輪場コード") or race.get("jo_code") or ""),
                "jo_name": str(race.get("競輪場名") or race.get("jo_name") or ""),
                "race_no": race.get("レース番号") if race.get("レース番号") is not None else race.get("race_no"),
                "race_id": race_id,
                "odds_data": decoded,
            }

            success_count += 1
            total_odds_combinations += len(odds_map)
            print(f" → OK ({len(odds_map)}通り)")
            time.sleep(REQUEST_INTERVAL_SECONDS)

    save_json(ODDS_JSON_FILE, {
        "program": "029_collect_yesterday_odds.py",
        "data_type": "DAILY_TRIFECTA_ODDS",
        "date": TARGET_DATE,
        "race_count": len(daily_races),
        "races": daily_races,
    })

    if problems:
        save_json(ERROR_JSON_FILE, {
            "program": "029_collect_yesterday_odds.py",
            "date": TARGET_DATE,
            "problem_count": len(problems),
            "problems": problems,
        })
    elif ERROR_JSON_FILE.exists():
        ERROR_JSON_FILE.unlink()

    print()
    print("=" * 70)
    print("029 完了")
    print("=" * 70)
    print()
    print("対象日       :", TARGET_DATE)
    print("race_data数  :", len(races))
    print("取得成功     :", success_count)
    print("取得失敗     :", failed_count)
    print("3連単総組合せ:", total_odds_combinations)
    print()
    print("オッズJSON:")
    print(ODDS_JSON_FILE)
    print()
    print("車番順CSV:")
    print(CAR_NUMBER_CSV_FILE)
    if problems:
        print()
        print("エラーログ:")
        print(ERROR_JSON_FILE)
    print()


if __name__ == "__main__":
    main()
