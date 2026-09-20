import json
import csv
import urllib.request
import urllib.parse
import time
from itertools import permutations
from pathlib import Path


# ============================================================
# 取得期間
# ============================================================

START_DATE = "20200101"
END_DATE = "20221231"


# ============================================================
# フォルダ
# ============================================================

PRE_RACE_DIR = Path(
    r"C:\競輪AI\data_official\historical\pre_race"
)

ODDS_JSON_DIR = Path(
    r"C:\競輪AI\data_official\historical\odds"
)

CSV_DIR = Path(
    r"C:\競輪AI\csv\historical_date\historical_odds"
)


# ============================================================
# KEIRIN.JP JST011
# ============================================================

KAIKEI = "6"
MODE = "0"
TYPE = "JST011"


# ============================================================
# 既存JSON
# True  = 上書き
# False = 既存ならスキップ
# ============================================================

OVERWRITE_JSON = False


# ============================================================
# CSVヘッダー
# 先頭5列 + 3連単504列
# ============================================================

BASE_HEADERS = [
    "race_key",
    "date",
    "jo_code",
    "jo_name",
    "race_no",
]

TRIFECTA_HEADERS = [
    f"{a}-{b}-{c}"
    for a, b, c in permutations(range(1, 10), 3)
]

HEADERS = BASE_HEADERS + TRIFECTA_HEADERS


# ============================================================
# 日付チェック
# ============================================================

def validate_date(date_text):

    if len(date_text) != 8:
        raise ValueError(
            f"日付はYYYYMMDD形式で指定してください: {date_text}"
        )

    if not date_text.isdigit():
        raise ValueError(
            f"日付は数字8桁で指定してください: {date_text}"
        )


validate_date(START_DATE)
validate_date(END_DATE)

if START_DATE > END_DATE:
    raise ValueError(
        "START_DATEはEND_DATE以前にしてください"
    )


# ============================================================
# JST011取得
# ============================================================

def get_jst011(encp):

    params = {
        "kake": KAIKEI,
        "mode": MODE,
        "encp": encp,
        "type": TYPE,
    }

    query = urllib.parse.urlencode(params)

    url = (
        "https://www.keirin.jp/pc/json?"
        + query
    )

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/142.0.0.0 Safari/537.36"
            ),
            "Referer": "https://www.keirin.jp/pc/racelive",
            "Accept": (
                "application/json, "
                "text/javascript, */*; q=0.01"
            ),
            "X-Requested-With": "XMLHttpRequest",
        },
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=20
        ) as response:

            raw = response.read()

        data = json.loads(
            raw.decode("utf-8")
        )

    except Exception as e:

        return {
            "success": False,
            "odds": {},
            "error": str(e),
        }


    if data.get("resultCd") != 0:

        return {
            "success": False,
            "odds": {},
            "error": (
                f"resultCd={data.get('resultCd')} "
                f"messageCd={data.get('messageCd')}"
            ),
        }


    root_data = data.get(
        "data",
        {}
    )

    odds = root_data.get(
        "ozz3RentanData",
        {}
    )


    return {
        "success": True,
        "odds": odds,
        "error": None,
    }


# ============================================================
# OZZ → 3連単
# ============================================================

def convert_ozz_to_trifecta(odds_data):

    result = {}

    for key, value in odds_data.items():

        if not isinstance(key, str):
            continue

        if not key.startswith("OZZ"):
            continue

        if len(key) != 6:
            continue

        number = key[3:]

        if not number.isdigit():
            continue

        trifecta = (
            f"{number[0]}-"
            f"{number[1]}-"
            f"{number[2]}"
        )

        result[trifecta] = value

    return result


# ============================================================
# OZZ件数から車立数判定
# ============================================================

def get_car_count(trifecta_count):

    if trifecta_count == 504:
        return 9

    if trifecta_count == 336:
        return 8

    if trifecta_count == 210:
        return 7

    if trifecta_count == 120:
        return 6

    if trifecta_count == 60:
        return 5

    return 0


# ============================================================
# race_key
# ============================================================

def make_race_key(
    date,
    venue,
    race_no
):

    return (
        f"{date}_"
        f"{venue}_"
        f"{int(race_no)}R"
    )


# ============================================================
# 日付をdatetimeに変換
# ============================================================

from datetime import datetime, timedelta


def make_date_range(
    start_date,
    end_date
):

    start = datetime.strptime(
        start_date,
        "%Y%m%d"
    )

    end = datetime.strptime(
        end_date,
        "%Y%m%d"
    )

    current = start

    while current <= end:

        yield current.strftime(
            "%Y%m%d"
        )

        current += timedelta(days=1)


# ============================================================
# 1日分取得
# ============================================================

def collect_one_day(
    target_date
):

    print()
    print("=" * 70)
    print(f"{target_date} 取得開始")
    print("=" * 70)


    pre_race_file = (
        PRE_RACE_DIR
        / f"{target_date}_pre_race.json"
    )

    odds_json_file = (
        ODDS_JSON_DIR
        / f"{target_date}_odds.json"
    )


    # --------------------------------------------------------
    # PRE_RACE確認
    # --------------------------------------------------------

    if not pre_race_file.exists():

        print()
        print(
            f"★ PRE_RACEなし: "
            f"{pre_race_file}"
        )

        return {
            "date": target_date,
            "status": "pre_race_missing",
            "total": 0,
            "success": 0,
            "failed": 0,
            "races": [],
        }


    # --------------------------------------------------------
    # 既存JSON
    # --------------------------------------------------------

    if (
        odds_json_file.exists()
        and not OVERWRITE_JSON
    ):

        print()
        print(
            "★ 既存JSONあり → スキップ"
        )

        print(odds_json_file)

        return {
            "date": target_date,
            "status": "json_exists",
            "total": 0,
            "success": 0,
            "failed": 0,
            "races": [],
        }


    # --------------------------------------------------------
    # PRE_RACE読み込み
    # --------------------------------------------------------

    with open(
        pre_race_file,
        "r",
        encoding="utf-8"
    ) as f:

        pre_race = json.load(f)


    venues = pre_race.get(
        "venues",
        []
    )


    print()
    print(
        f"開催場数: {len(venues)}"
    )


    day_result = {
        "target_date": target_date,
        "source": "KEIRIN.JP",
        "type": TYPE,
        "kake": KAIKEI,
        "mode": MODE,
        "venues": [],
    }


    total_races = 0
    success_races = 0
    failed_races = 0


    # --------------------------------------------------------
    # 開催場
    # --------------------------------------------------------

    for venue_data in venues:

        venue = venue_data.get(
            "venue"
        )

        bank_code = venue_data.get(
            "bank_code"
        )

        jsj001 = venue_data.get(
            "jsj001",
            {}
        )

        c0201data = jsj001.get(
            "C0201data",
            {}
        )

        c0201race = c0201data.get(
            "C0201race",
            []
        )


        print()
        print("-" * 70)
        print(
            f"{venue} "
            f"bank_code={bank_code} "
            f"race_count={len(c0201race)}"
        )
        print("-" * 70)


        venue_result = {
            "venue": venue,
            "bank_code": bank_code,
            "races": [],
        }


        # ----------------------------------------------------
        # レース
        # ----------------------------------------------------

        for index, race in enumerate(
            c0201race
        ):

            race_no = index + 1

            enc_para_r = race.get(
                "encParaR"
            )

            total_races += 1


            race_result = {
                "race_no": race_no,
                "encParaR": enc_para_r,
                "rcvOdds": race.get(
                    "rcvOdds"
                ),
                "success": False,
                "odds_count": 0,
                "trifecta_count": 0,
                "odds": {},
                "error": None,
            }


            print(
                f"{venue} "
                f"{race_no}R : ",
                end="",
                flush=True
            )


            if not enc_para_r:

                failed_races += 1

                race_result["error"] = (
                    "encParaRなし"
                )

                venue_result[
                    "races"
                ].append(
                    race_result
                )

                print(
                    "失敗 / encParaRなし"
                )

                continue


            # ------------------------------------------------
            # JST011
            # ------------------------------------------------

            result = get_jst011(
                enc_para_r
            )


            if not result["success"]:

                failed_races += 1

                race_result["error"] = (
                    result["error"]
                )

                venue_result[
                    "races"
                ].append(
                    race_result
                )

                print(
                    "失敗 / "
                    f"{result['error']}"
                )

                continue


            odds_data = result["odds"]


            # ------------------------------------------------
            # OZZ
            # ------------------------------------------------

            ozz_count = sum(
                1
                for key in odds_data
                if (
                    isinstance(key, str)
                    and key.startswith("OZZ")
                    and len(key) == 6
                    and key[3:].isdigit()
                )
            )


            trifecta_data = (
                convert_ozz_to_trifecta(
                    odds_data
                )
            )


            trifecta_count = len(
                trifecta_data
            )


            race_result[
                "success"
            ] = True

            race_result[
                "odds_count"
            ] = ozz_count

            race_result[
                "trifecta_count"
            ] = trifecta_count

            race_result[
                "odds"
            ] = trifecta_data


            venue_result[
                "races"
            ].append(
                race_result
            )


            success_races += 1


            car_count = get_car_count(
                trifecta_count
            )


            print(
                "成功 / "
                f"OZZ={ozz_count} / "
                f"3連単={trifecta_count} / "
                f"{car_count}車"
            )


        day_result[
            "venues"
        ].append(
            venue_result
        )


    # --------------------------------------------------------
    # JSON保存
    # --------------------------------------------------------

    ODDS_JSON_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    with open(
        odds_json_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            day_result,
            f,
            ensure_ascii=False,
            indent=2
        )


    print()
    print(
        f"JSON保存: "
        f"{odds_json_file}"
    )


    print()
    print(
        f"{target_date} 結果: "
        f"総数={total_races} "
        f"成功={success_races} "
        f"失敗={failed_races}"
    )


    return {
        "target_date": target_date,
        "date": target_date,
        "status": "completed",
        "total": total_races,
        "success": success_races,
        "failed": failed_races,
        "venues": day_result["venues"],
    }


# ============================================================
# JSON → CSV行
# ============================================================

def make_csv_rows(
    day_result
):

    rows = []


    for venue_data in day_result.get(
        "venues",
        []
    ):

        venue = venue_data.get(
            "venue"
        )

        bank_code = venue_data.get(
            "bank_code"
        )


        for race in venue_data.get(
            "races",
            []
        ):

            if not race.get(
                "success",
                False
            ):
                continue


            race_no = race.get(
                "race_no"
            )

            odds = race.get(
                "odds",
                {}
            )


            row = {
                header: ""
                for header in HEADERS
            }


            row["race_key"] = (
                make_race_key(
                    day_result[
                        "target_date"
                    ],
                    venue,
                    race_no
                )
            )

            row["date"] = (
                day_result[
                    "target_date"
                ]
            )

            row["jo_code"] = bank_code

            row["jo_name"] = venue

            row["race_no"] = race_no


            # ----------------------------------------------
            # 3連単
            # ----------------------------------------------

            for trifecta, value in odds.items():

                if trifecta in row:

                    row[trifecta] = value


            rows.append(row)


    return rows


# ============================================================
# メイン
# ============================================================

print()
print("=" * 70)
print("KEIRIN.JP JST011 過去オッズ本番取得")
print("=" * 70)

print()
print(
    f"取得期間: "
    f"{START_DATE} ～ {END_DATE}"
)

print()
print(
    f"JSON保存先:\n"
    f"{ODDS_JSON_DIR}"
)

print()
print(
    f"CSV保存先:\n"
    f"{CSV_DIR}"
)

print()
print(
    f"CSV列数: {len(HEADERS)}"
)

print(
    f"3連単列数: "
    f"{len(TRIFECTA_HEADERS)}"
)


# ============================================================
# 全日付処理
# ============================================================

all_csv_rows = []

day_results = []

start_time = time.time()


for target_date in make_date_range(
    START_DATE,
    END_DATE
):

    day_result = collect_one_day(
        target_date
    )

    day_results.append(
        day_result
    )


    # --------------------------------------------------------
    # 完了済みJSONからCSV行作成
    # --------------------------------------------------------

    if day_result["status"] == "completed":

        rows = make_csv_rows(
            day_result
        )

        all_csv_rows.extend(
            rows
        )


# ============================================================
# CSV保存
# ============================================================

CSV_DIR.mkdir(
    parents=True,
    exist_ok=True
)


start_dt = datetime.strptime(
    START_DATE,
    "%Y%m%d"
)

end_dt = datetime.strptime(
    END_DATE,
    "%Y%m%d"
)


csv_filename = (
    "historical_odds_"
    f"{start_dt.year}."
    f"{start_dt.month}."
    f"{start_dt.day}"
    "~"
    f"{end_dt.year}."
    f"{end_dt.month}."
    f"{end_dt.day}"
    ".csv"
)


csv_path = (
    CSV_DIR
    / csv_filename
)


with open(
    csv_path,
    "w",
    newline="",
    encoding="utf-8-sig"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=HEADERS
    )

    writer.writeheader()

    writer.writerows(
        all_csv_rows
    )


# ============================================================
# 最終結果
# ============================================================

elapsed = time.time() - start_time


print()
print()
print("=" * 70)
print("最終結果")
print("=" * 70)


completed_days = sum(
    1
    for result in day_results
    if result["status"] == "completed"
)


missing_days = sum(
    1
    for result in day_results
    if result["status"]
    == "pre_race_missing"
)


skipped_days = sum(
    1
    for result in day_results
    if result["status"]
    == "json_exists"
)


total_races = sum(
    result["total"]
    for result in day_results
)


success_races = sum(
    result["success"]
    for result in day_results
)


failed_races = sum(
    result["failed"]
    for result in day_results
)


print(
    f"対象日数         : "
    f"{len(day_results)}"
)

print(
    f"取得完了日数     : "
    f"{completed_days}"
)

print(
    f"PRE_RACEなし     : "
    f"{missing_days}"
)

print(
    f"既存JSONスキップ : "
    f"{skipped_days}"
)

print()

print(
    f"総レース数       : "
    f"{total_races}"
)

print(
    f"取得成功         : "
    f"{success_races}"
)

print(
    f"取得失敗         : "
    f"{failed_races}"
)

if total_races:

    print(
        f"成功率           : "
        f"{success_races / total_races * 100:.2f}%"
    )


print()

print(
    f"CSV行数          : "
    f"{len(all_csv_rows)}"
)

print(
    f"CSV列数          : "
    f"{len(HEADERS)}"
)

print()

print(
    f"CSV保存先:\n"
    f"{csv_path}"
)

print()

print(
    f"処理時間         : "
    f"{elapsed:.2f} 秒"
)


# ============================================================
# 問題のある日
# ============================================================

print()
print("-" * 70)
print("確認が必要な日")
print("-" * 70)


problem_found = False


for result in day_results:

    if result["status"] != "completed":

        problem_found = True

        print(
            result["date"],
            ":",
            result["status"]
        )

    elif result["failed"] > 0:

        problem_found = True

        print(
            result["date"],
            ":",
            f"レース失敗={result['failed']}"
        )


if not problem_found:

    print("なし")


print()
print("=" * 70)

if (
    failed_races == 0
    and missing_days == 0
    and len(HEADERS) == 509
):

    print(
        "★ 全対象日の取得・JSON保存・CSV作成成功"
    )

else:

    print(
        "★ 一部に確認が必要です"
    )

print("=" * 70)