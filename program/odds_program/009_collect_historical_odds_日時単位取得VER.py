from pathlib import Path
from datetime import datetime, timedelta
import base64
import csv
import itertools
import json
import time
import urllib.parse
import urllib.request
import zlib


# ============================================================
# 008
# pre_race JSONから指定期間の3連単オッズを取得し、
# 「車番順」「人気順」の2種類のCSVを作成する
#
# 【保存先】
# pre_race読込:
#   C:\競輪AI\data_official\historical\pre_race
#
# オッズJSON:
#   C:\競輪AI\data_official\historical\odds
#
# オッズCSV:
#   C:\競輪AI\csv\historical_date\historical_odds
#
# 【race_key】
# 既存のplayer CSV等と同じ
#   YYYYMMDD_開催場_1R
#
# 例:
#   20260819_川崎_1R
#
# race_idはAPI問い合わせ専用。
# CSVや保存JSONの共通識別子はrace_keyを使用する。
# ============================================================


BASE = Path(r"C:\競輪AI")


# ============================================================
# pre_race JSON読込先
# ============================================================

PRE_RACE_DIR = (
    BASE
    / "data_official"
    / "historical"
    / "pre_race"
)


# ============================================================
# オッズJSON保存先
# ============================================================

JSON_OUTPUT_DIR = (
    BASE
    / "data_official"
    / "daily"
    / "odds"
)


# ============================================================
# オッズCSV保存先
# ============================================================

ODDS_CSV_OUTPUT_DIR = (
    BASE
    / "csv"
    / "odds"
)


# ============================================================
# netkeirin API
# ============================================================

API_URL = "https://keirin.netkeiba.com/api/race/"

REQUEST_TIMEOUT = 30
REQUEST_INTERVAL_SECONDS = 0.15

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/142.0.0.0 Safari/537.36"
)


# ============================================================
# CSV固定列
# 9車立ての3連単は 9P3 = 504通り
# ============================================================

MAX_CAR_COUNT = 9

MAX_COMBINATIONS = [
    "-".join(map(str, combo))
    for combo in itertools.permutations(
        range(1, MAX_CAR_COUNT + 1),
        3,
    )
]


# ============================================================
# 日付
# ============================================================

def parse_input_date(text):
    text = text.strip()

    formats = [
        "%Y-%m-%d",
        "%Y.%m.%d",
        "%Y/%m/%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    raise ValueError(
        "日付は 2020-01-01 / 2020.1.1 / 2020/1/1 の形式で入力してください。"
    )


def build_target_dates(start_date, end_date):
    dates = []
    current = start_date

    while current <= end_date:
        dates.append(current.strftime("%Y%m%d"))
        current += timedelta(days=1)

    return dates


# ============================================================
# JSON
# ============================================================

def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_daily_odds_json(kday, daily_races):
    """
    1日分の取得したオッズJSONを、1つのJSONファイルにまとめて保存する。

    保存ファイル名:
        YYYYMMDD_odds.json

    JSON内部:
        {
            "date": "YYYYMMDD",
            "race_count": 取得成功レース数,
            "races": {
                "YYYYMMDD_開催場_1R": {
                    "race_key": ...,
                    "date": ...,
                    "jo_code": ...,
                    "jo_name": ...,
                    "race_no": ...,
                    "race_id": ...,
                    "odds_data": ...
                }
            }
        }
    """

    JSON_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    races_data = {}

    for item in daily_races:
        race = item["race"]
        race_id = item["race_id"]
        decoded = item["decoded"]
        race_key = race["race_key"]

        races_data[race_key] = {
            "race_key": race_key,
            "date": race["date"],
            "jo_code": race["jo_code"],
            "jo_name": race["jo_name"],
            "race_no": race["race_no"],
            "race_id": race_id,
            "odds_data": decoded,
        }

    output_data = {
        "date": kday,
        "race_count": len(races_data),
        "races": races_data,
    }

    output_file = JSON_OUTPUT_DIR / f"{kday}_odds.json"

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(
            output_data,
            f,
            ensure_ascii=False,
            indent=2,
        )

    return output_file


# ============================================================
# pre_raceからレース一覧を作る
# ============================================================

def extract_races_from_pre_race(kday, data):
    """
    pre_race JSONの構造:

    {
        "target_date": "YYYYMMDD",
        "venue_count": ...,
        "venues": [
            {
                "venue": "前橋",
                "bank_code": "22",
                "jsj001": {
                    "C0201data": {
                        "selKaisai": "YYYYMMDD",
                        "selKjyoCd": "22",
                        "C0201race": [
                            {...},
                            {...},
                            ...
                        ]
                    }
                }
            }
        ]
    }

    C0201raceは1R, 2R, 3R...の順番で並んでいるため、
    配列位置からrace_noを作る。
    """

    races = []

    venues = data.get("venues", [])

    if not isinstance(venues, list):
        return races

    for venue in venues:
        if not isinstance(venue, dict):
            continue

        venue_name = (
            venue.get("venue")
            or venue.get("jyoName")
            or ""
        )

        bank_code = (
            venue.get("bank_code")
            or venue.get("KeirinCd")
            or venue.get("bKeirinCd")
            or ""
        )

        jsj001 = venue.get("jsj001")

        c0201data = {}
        if isinstance(jsj001, dict):
            c0201data = jsj001.get("C0201data", {})

            if not isinstance(c0201data, dict):
                c0201data = {}

        # bank_codeが空の場合はC0201dataから取得
        if bank_code in (None, ""):
            bank_code = (
                c0201data.get("selKjyoCd")
                or c0201data.get("KeirinCd")
                or c0201data.get("bKeirinCd")
                or ""
            )

        bank_code = str(bank_code).strip()

        if bank_code.isdigit():
            bank_code = bank_code.zfill(2)

        if not bank_code.isdigit():
            print(
                f"  開催場コード取得失敗: {venue_name}"
            )
            continue

        venue_races = c0201data.get("C0201race", [])

        if not isinstance(venue_races, list):
            continue

        # C0201raceの配列順 = 1R, 2R, 3R...
        for index, race_data in enumerate(
            venue_races,
            start=1,
        ):
            if not isinstance(race_data, dict):
                continue

            # encParaRがないものはレース情報として扱わない
            enc_para_r = race_data.get("encParaR")

            if not enc_para_r:
                continue

            race_no = index

            race_key = (
                f"{kday}_{venue_name}_{race_no}R"
            )

            races.append(
                {
                    "race_key": race_key,
                    "date": kday,
                    "jo_code": bank_code,
                    "jo_name": venue_name,
                    "race_no": race_no,
                    "encParaR": enc_para_r,
                }
            )

    return races


# ============================================================
# race_id
# API問い合わせ専用
# ============================================================

def make_race_id(race):
    date = str(race["date"]).zfill(8)
    jo_code = str(race["jo_code"]).zfill(2)
    race_no = int(race["race_no"])

    return f"{date}{jo_code}{race_no:02d}"


# ============================================================
# オッズAPI
# ============================================================

def fetch_race_odds(race_id):
    params = urllib.parse.urlencode(
        {
            "class": "AplRaceOdds",
            "method": "get",
            "compress": "1",
            "race_id": race_id,
            "input": "UTF-8",
            "output": "json",
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        API_URL,
        data=params,
        method="POST",
        headers={
            "User-Agent": USER_AGENT,
            "Referer": (
                "https://keirin.netkeiba.com/"
                f"race/odds_new/?race_id={race_id}"
            ),
            "Accept": "application/json, text/plain, */*",
            "Content-Type": (
                "application/x-www-form-urlencoded; "
                "charset=UTF-8"
            ),
            "X-Requested-With": "XMLHttpRequest",
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=REQUEST_TIMEOUT,
        ) as response:

            raw = response.read().decode(
                "utf-8",
                errors="replace",
            )

        response_data = json.loads(raw)

        if response_data.get("status") != "OK":
            return (
                None,
                f"API_STATUS_{response_data.get('status')}",
            )

        compressed_text = (
            response_data
            .get("data", {})
            .get(f"nkrace_odds::{race_id}")
        )

        if not compressed_text:
            return None, "ODDS_DATA_MISSING"

        compressed = base64.b64decode(
            compressed_text
        )

        decoded_bytes = zlib.decompress(
            compressed
        )

        decoded_text = decoded_bytes.decode(
            "utf-8",
            errors="replace",
        )

        decoded = json.loads(decoded_text)

        return decoded, None

    except Exception as e:
        return None, repr(e)


# ============================================================
# 3連単 list_9
# ============================================================

def build_odds_maps(decoded):
    """
    list_9:

        [組み合わせ, オッズ, field_2, 人気順位]

    [0] = 組み合わせ
    [1] = オッズ
    [3] = 人気順位

    例:
        ["010203", "482.7", "0", "89"]
    """

    list_9 = decoded.get("list_9")

    if not isinstance(list_9, list):
        return None, None, "LIST_9_MISSING"

    car_number_map = {}
    popularity_map = {}

    for item in list_9:

        if not isinstance(item, list):
            continue

        if len(item) < 4:
            continue

        combo_raw = str(item[0])
        odds_raw = str(item[1])
        popularity_raw = str(item[3])

        # 3連単は6桁
        if len(combo_raw) != 6:
            continue

        if not combo_raw.isdigit():
            continue

        first = int(combo_raw[0:2])
        second = int(combo_raw[2:4])
        third = int(combo_raw[4:6])

        # 同じ車番が入っているものは除外
        if len({first, second, third}) != 3:
            continue

        # 1～9以外は除外
        if not (
            1 <= first <= 9
            and 1 <= second <= 9
            and 1 <= third <= 9
        ):
            continue

        combo = (
            f"{first}-{second}-{third}"
        )

        try:
            odds = float(odds_raw)
        except ValueError:
            continue

        car_number_map[combo] = odds

        try:
            popularity = int(
                float(popularity_raw)
            )
        except ValueError:
            continue

        if popularity >= 1:
            popularity_map[popularity] = (
                combo,
                odds,
            )

    if not car_number_map:
        return (
            None,
            None,
            "NO_TRIFECTA_DATA",
        )

    return (
        car_number_map,
        popularity_map,
        None,
    )


# ============================================================
# CSVヘッダー
# ============================================================

def build_car_number_header():
    return [
        "race_key",
        "date",
        "jo_code",
        "jo_name",
        "race_no",
    ] + MAX_COMBINATIONS

# ============================================================
# CSV行
# ============================================================

def build_car_number_row(
    race,
    odds_map,
):
    row = [
        race["race_key"],
        race["date"],
        race["jo_code"],
        race["jo_name"],
        race["race_no"],
    ]

    # 常に504列
    # 存在しない車番組み合わせは空欄
    for combo in MAX_COMBINATIONS:
        value = odds_map.get(
            combo,
            "",
        )
        row.append(value)

    return row

# ============================================================
# main
# ============================================================

def main():

    print("=" * 70)
    print("009 pre_race → 3連単オッズ収集（日単位JSON・CSV）")
    print("=" * 70)
    print()

    start_text = input(
        "開始日を入力してください（例：2020-01-01）："
    )

    end_text = input(
        "終了日を入力してください（例：2022-12-31）："
    )

    try:
        start_date = parse_input_date(
            start_text
        )

        end_date = parse_input_date(
            end_text
        )

    except ValueError as e:

        print()
        print("ERROR:", e)

        return

    if start_date > end_date:

        print(
            "ERROR: 開始日が終了日より後になっています。"
        )

        return

    start_str = (
        f"{start_date.year}."
        f"{start_date.month}."
        f"{start_date.day}"
    )

    end_str = (
        f"{end_date.year}."
        f"{end_date.month}."
        f"{end_date.day}"
    )

    # ========================================================
    # 保存先作成
    # ========================================================

    JSON_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    ODDS_CSV_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ========================================================
    # 表示
    # ========================================================

    print()
    print(
        "対象期間:",
        start_date,
        "～",
        end_date,
    )

    print(
        "pre_race読込先:",
        PRE_RACE_DIR,
    )

    print(
        "オッズJSON保存先:",
        JSON_OUTPUT_DIR,
    )

    print()

    # ========================================================
    # 対象日
    # ========================================================

    target_dates = build_target_dates(
        start_date,
        end_date,
    )

    # ========================================================
    # 固定ヘッダー
    # ========================================================

    car_number_header = (
        build_car_number_header()
    )

    # ========================================================
    # カウンター
    # ========================================================

    success_count = 0
    failed_count = 0
    skipped_count = 0
    total_races = 0
    total_odds_races = 0

    problems = []

    # ========================================================
    # 日付ループ
    # ========================================================

    for date_index, kday in enumerate(
        target_dates,
        start=1,
    ):

        # ----------------------------------------------------
        # 1日単位のCSVファイル
        # ----------------------------------------------------

        odds_csv_file = (
            ODDS_CSV_OUTPUT_DIR
            / f"{kday}_odds.csv"
        )

        with odds_csv_file.open(
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as odds_f:

            odds_writer = csv.writer(odds_f)

            odds_writer.writerow(car_number_header)

            pre_race_file = (
                PRE_RACE_DIR
                / f"{kday}_pre_race.json"
            )

            print(
                f"[{date_index}/{len(target_dates)}] "
                f"{kday}"
            )

            print(
                "  オッズCSV:",
                odds_csv_file,
            )

            # ----------------------------------------------
            # pre_raceがない
            # ----------------------------------------------

            if not pre_race_file.exists():

                skipped_count += 1

                problems.append(
                    {
                        "date": kday,
                        "problem": "PRE_RACE_FILE_MISSING",
                        "file": str(pre_race_file),
                    }
                )

                print(
                    "  pre_raceなし → スキップ"
                )

                continue

            # ----------------------------------------------
            # JSON読込
            # ----------------------------------------------

            try:

                daily_data = load_json(
                    pre_race_file
                )

            except Exception as e:

                failed_count += 1

                problems.append(
                    {
                        "date": kday,
                        "problem": "PRE_RACE_JSON_ERROR",
                        "error": repr(e),
                    }
                )

                print(
                    "  pre_race読込エラー:",
                    repr(e),
                )

                continue

            # ----------------------------------------------
            # レース一覧
            # ----------------------------------------------

            races = (
                extract_races_from_pre_race(
                    kday,
                    daily_data,
                )
            )

            print(
                "  レース数:",
                len(races),
            )

            total_races += len(races)

            # ----------------------------------------------
            # その日のオッズ取得成功レースを一時保存
            # ----------------------------------------------

            daily_odds_results = []

            # ----------------------------------------------
            # レースループ
            # ----------------------------------------------

            for race_index, race in enumerate(
                races,
                start=1,
            ):

                race_id = make_race_id(
                    race
                )

                print(
                    f"    [{race_index}/{len(races)}] "
                    f"{race['race_key']} "
                    f"race_id={race_id}",
                    end="",
                )

                # ------------------------------------------
                # オッズAPI
                # ------------------------------------------

                decoded, error = (
                    fetch_race_odds(
                        race_id
                    )
                )

                if error:

                    failed_count += 1

                    problems.append(
                        {
                            "date": kday,
                            "race_key": race[
                                "race_key"
                            ],
                            "race_id": race_id,
                            "problem": error,
                        }
                    )

                    print(
                        " → NG:",
                        error,
                    )

                    time.sleep(
                        REQUEST_INTERVAL_SECONDS
                    )

                    continue

                # ------------------------------------------
                # list_9から3連単抽出
                # ------------------------------------------

                (
                    odds_map,
                    popularity_map,
                    error,
                ) = build_odds_maps(
                    decoded
                )

                if error:

                    failed_count += 1

                    problems.append(
                        {
                            "date": kday,
                            "race_key": race[
                                "race_key"
                            ],
                            "race_id": race_id,
                            "problem": error,
                        }
                    )

                    print(
                        " → 3連単データNG:",
                        error,
                    )

                    time.sleep(
                        REQUEST_INTERVAL_SECONDS
                    )

                    continue

                # ------------------------------------------
                # 取得した生JSONを、その日のJSONへまとめる
                # ------------------------------------------

                daily_odds_results.append(
                    {
                        "race": race,
                        "race_id": race_id,
                        "decoded": decoded,
                    }
                )

                # ------------------------------------------
                # 車番順CSV
                # ------------------------------------------

                odds_writer.writerow(
                    build_car_number_row(
                        race,
                        odds_map,
                    )
                )

            # ----------------------------------------------
            # 1日分のオッズJSONを保存
            # ----------------------------------------------

            if daily_odds_results:
                try:

                    daily_json_file = save_daily_odds_json(
                        kday,
                        daily_odds_results,
                    )

                    print(
                        "  日次オッズJSON保存:",
                        daily_json_file,
                        f"({len(daily_odds_results)}レース)",
                    )

                except Exception as e:

                    problems.append(
                        {
                            "date": kday,
                            "problem": "DAILY_JSON_SAVE_ERROR",
                            "error": repr(e),
                        }
                    )

                    print(
                        "  日次オッズJSON保存NG:",
                        repr(e),
                    )

    # ========================================================
    # エラーログJSON
    # ========================================================

    if problems:

        problem_file = (
            JSON_OUTPUT_DIR
            / (
                "historical_odds_error_"
                f"{start_str}~{end_str}.json"
            )
        )

        with problem_file.open(
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                problems,
                f,
                ensure_ascii=False,
                indent=2,
            )

    else:

        problem_file = None

    # ========================================================
    # 完了
    # ========================================================

    print()
    print("=" * 70)
    print("009 完了")
    print("=" * 70)

    print(
        "対象日数       :",
        len(target_dates),
    )

    print(
        "総レース数     :",
        total_races,
    )

    print(
        "オッズ取得成功 :",
        success_count,
    )

    print(
        "オッズ取得失敗 :",
        failed_count,
    )

    print(
        "pre_raceなし等  :",
        skipped_count,
    )

    print()

    print(
        "オッズJSON保存先:"
    )

    print(
        JSON_OUTPUT_DIR
    )

    print()

    print(
    "オッズCSV保存先:"
    )

    print(
        ODDS_CSV_OUTPUT_DIR
    )

    if problem_file:

        print()

        print(
            "問題ログ:"
        )

        print(
            problem_file
        )


if __name__ == "__main__":
    main()
