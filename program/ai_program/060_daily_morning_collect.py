import json
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import requests


print("=== 060 毎朝 競輪AI 学習データ自動収集 正式版 ===")


# ============================================================
# 基本PATH
# ============================================================

BASE = Path(r"C:\競輪AI")
PROGRAM_DIR = BASE / "ai_program"
DAILY_DIR = BASE / "data_daily"

LINE_PROGRAM = (
    PROGRAM_DIR
    / "043_capture_all_venues_official_lines.py"
)

TODAY = datetime.now().strftime("%Y%m%d")

YESTERDAY = (
    datetime.now() - timedelta(days=1)
).strftime("%Y%m%d")

TODAY_DIR = DAILY_DIR / TODAY
YESTERDAY_DIR = DAILY_DIR / YESTERDAY

TODAY_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

YESTERDAY_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# 通信
# ============================================================

session = requests.Session()

session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/142.0.0.0 "
        "Safari/537.36 "
        "Edg/142.0.0.0"
    ),
    "Referer": "https://www.keirin.jp/pc/top",
})


def get_json(url, retry=3):

    last_error = None

    for attempt in range(
        1,
        retry + 1,
    ):

        try:

            response = session.get(
                url,
                timeout=30,
            )

            response.raise_for_status()

            return response.json()

        except Exception as e:

            last_error = repr(e)

            if attempt < retry:

                time.sleep(1)

    raise RuntimeError(last_error)


# ============================================================
# 日付の全レース地図取得
# ============================================================

def collect_race_map(kday):

    print()
    print(
        "=" * 100
    )

    print(
        "レース地図取得:",
        kday,
    )

    print(
        "=" * 100
    )

    url057 = (
        "https://www.keirin.jp/pc/json"
        f"?kday={kday}"
        "&type=JSJ057"
    )

    jsj057 = get_json(
        url057
    )

    venues = (
        jsj057.get("kInfo")
        or []
    )

    print(
        "開催会場数:",
        len(venues),
    )

    race_map = {}

    for venue_index, venue in enumerate(
        venues,
        1,
    ):

        venue_name = venue.get(
            "jyoName"
        )

        venue_code = (
            venue.get("KeirinCd")
            or venue.get("bKeirinCd")
        )

        enc_prm = venue.get(
            "encPrm"
        )

        print()
        print(
            f"[会場 "
            f"{venue_index}/"
            f"{len(venues)}] "
            f"{venue_name}"
        )

        if not enc_prm:

            print(
                "  encPrmなし"
            )

            continue

        url001 = (
            "https://www.keirin.jp/pc/json"
            f"?encp={enc_prm}"
            "&type=JSJ001"
        )

        try:

            jsj001 = get_json(
                url001
            )

        except Exception as e:

            print(
                "  JSJ001取得失敗:",
                repr(e),
            )

            continue

        c0201 = (
            jsj001.get("C0201data")
            or {}
        )

        races = (
            c0201.get("C0201race")
            or []
        )

        print(
            "  レース数:",
            len(races),
        )

        for race_no, race in enumerate(
            races,
            1,
        ):

            enc_para_r = race.get(
                "encParaR"
            )

            if not enc_para_r:

                continue

            race_key = (
                f"{kday}_"
                f"{venue_name}_"
                f"{race_no}R"
            )

            race_map[race_key] = {

                "race_key":
                    race_key,

                "date":
                    kday,

                "venue":
                    venue_name,

                "venue_code":
                    venue_code,

                "race_no":
                    race_no,

                "encParaR":
                    enc_para_r,

                "race_meta":
                    race,

            }

    print()
    print(
        "レース地図総数:",
        len(race_map),
    )

    return race_map


# ============================================================
# JSJ006 能力データ取得
# ============================================================

def collect_pre_race(
    race_map,
):

    print()
    print(
        "=" * 100
    )

    print(
        "当日 JSJ006 "
        "選手能力データ取得"
    )

    print(
        "=" * 100
    )

    output = {}

    success = 0
    failed = 0

    items = list(
        race_map.items()
    )

    for index, (
        race_key,
        race,
    ) in enumerate(
        items,
        1,
    ):

        encp = race[
            "encParaR"
        ]

        url = (
            "https://www.keirin.jp/pc/json"
            f"?encp={encp}"
            "&type=JSJ006"
        )

        try:

            jsj006 = get_json(
                url
            )

            players = (
                jsj006.get(
                    "sensyuTypeInfo"
                )
                or []
            )

            if players:

                status = (
                    "ABILITY_FOUND"
                )

                success += 1

            else:

                status = (
                    "ABILITY_NOT_FOUND"
                )

                failed += 1

            output[race_key] = {

                **race,

                "status":
                    status,

                "jsj006":
                    jsj006,

            }

            print(
                f"[{index}/"
                f"{len(items)}] "
                f"{race_key} "
                f"{status} "
                f"{len(players)}人"
            )

        except Exception as e:

            failed += 1

            output[race_key] = {

                **race,

                "status":
                    "ABILITY_ERROR",

                "error":
                    repr(e),

                "jsj006":
                    None,

            }

            print(
                f"[{index}/"
                f"{len(items)}] "
                f"{race_key} ERROR"
            )

        time.sleep(
            0.05
        )

    return (
        output,
        success,
        failed,
    )


# ============================================================
# JSJ012 確定結果取得
# ============================================================

def collect_confirmed_result(
    race_map,
):

    print()
    print(
        "=" * 100
    )

    print(
        "前日 JSJ012 "
        "確定結果取得"
    )

    print(
        "=" * 100
    )

    output = {}

    confirmed = 0
    pending = 0
    error = 0

    items = list(
        race_map.items()
    )

    for index, (
        race_key,
        race,
    ) in enumerate(
        items,
        1,
    ):

        encp = race[
            "encParaR"
        ]

        url = (
            "https://www.keirin.jp/pc/json"
            f"?encp={encp}"
            "&type=JSJ012"
        )

        try:

            jsj012 = get_json(
                url
            )

            finish_rows = (
                jsj012.get(
                    "tyakujyunItemSubData"
                )
                or []
            )

            payout = (
                jsj012.get(
                    "haraiGakuSubData"
                )
            )

            if (
                finish_rows
                and isinstance(
                    payout,
                    dict,
                )
            ):

                status = (
                    "CONFIRMED_RESULT_FOUND"
                )

                confirmed += 1

            else:

                status = (
                    "RESULT_NOT_CONFIRMED"
                )

                pending += 1

            output[race_key] = {

                **race,

                "status":
                    status,

                "jsj012":
                    jsj012,

            }

            print(
                f"[{index}/"
                f"{len(items)}] "
                f"{race_key} "
                f"{status}"
            )

        except Exception as e:

            error += 1

            output[race_key] = {

                **race,

                "status":
                    "RESULT_ERROR",

                "error":
                    repr(e),

                "jsj012":
                    None,

            }

            print(
                f"[{index}/"
                f"{len(items)}] "
                f"{race_key} ERROR"
            )

        time.sleep(
            0.05
        )

    return (
        output,
        confirmed,
        pending,
        error,
    )


# ============================================================
# JSON保存
# ============================================================

def save_json(
    path,
    data,
):

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )


# ============================================================
# 043 ライン取得実行
# ============================================================

def run_line_program():

    print()
    print(
        "=" * 100
    )

    print(
        "043 ライン予想 "
        "自動取得開始"
    )

    print(
        "=" * 100
    )

    if not LINE_PROGRAM.exists():

        print(
            "043 PROGRAM NOT FOUND"
        )

        print(
            LINE_PROGRAM
        )

        return False

    result = subprocess.run(
        [
            sys.executable,
            str(
                LINE_PROGRAM
            ),
        ],
        cwd=str(BASE),
    )

    if result.returncode != 0:

        print(
            "043 実行失敗"
        )

        return False

    print(
        "043 実行成功"
    )

    return True


# ============================================================
# 昨日分 学習候補合体
# ============================================================

def merge_yesterday(
    pre_race,
    confirmed_result,
):

    line_file = (
        YESTERDAY_DIR
        / "line_prediction.json"
    )

    if not line_file.exists():

        print()
        print(
            "昨日ラインデータなし"
        )

        return {}

    with line_file.open(
        "r",
        encoding="utf-8",
    ) as f:

        line_data = json.load(
            f
        )

    if isinstance(
        line_data,
        dict,
    ):

        if isinstance(
            line_data.get("races"),
            dict,
        ):

            line_map = (
                line_data["races"]
            )

        else:

            line_map = line_data

    else:

        line_map = {}

    merged = {}

    all_keys = sorted(
        set(pre_race)
        | set(line_map)
        | set(confirmed_result)
    )

    for race_key in all_keys:

        ability = pre_race.get(
            race_key
        )

        line = line_map.get(
            race_key
        )

        result = confirmed_result.get(
            race_key
        )

        ready = (
            isinstance(
                ability,
                dict,
            )
            and ability.get(
                "status"
            )
            == "ABILITY_FOUND"
            and isinstance(
                line,
                dict,
            )
            and bool(
                line.get(
                    "main_lines"
                )
            )
            and isinstance(
                result,
                dict,
            )
            and result.get(
                "status"
            )
            == "CONFIRMED_RESULT_FOUND"
        )

        merged[race_key] = {

            "race_key":
                race_key,

            "merge_status":
                (
                    "READY_FOR_AI"
                    if ready
                    else "EXCLUDED"
                ),

            "ability":
                ability,

            "line_prediction":
                line,

            "confirmed_result":
                result,

        }

    return merged


# ============================================================
# main
# ============================================================

def main():

    print()
    print(
        "TODAY:",
        TODAY,
    )

    print(
        "YESTERDAY:",
        YESTERDAY,
    )

    # --------------------------------------------------------
    # 1. 前日レース地図
    # --------------------------------------------------------

    yesterday_map = collect_race_map(
        YESTERDAY
    )

    # --------------------------------------------------------
    # 2. 前日の能力データ読込
    # --------------------------------------------------------

    yesterday_pre_file = (
        YESTERDAY_DIR
        / "pre_race.json"
    )

    if yesterday_pre_file.exists():

        with yesterday_pre_file.open(
            "r",
            encoding="utf-8",
        ) as f:

            yesterday_pre = json.load(
                f
            )

    else:

        print()
        print(
            "昨日のpre_race.jsonなし"
        )

        print(
            "前日能力データを補完取得します"
        )

        (
            yesterday_pre,
            _,
            _,
        ) = collect_pre_race(
            yesterday_map
        )

        save_json(
            yesterday_pre_file,
            yesterday_pre,
        )

    # --------------------------------------------------------
    # 3. 前日確定結果取得
    # --------------------------------------------------------

    (
        yesterday_result,
        result_confirmed,
        result_pending,
        result_error,
    ) = collect_confirmed_result(
        yesterday_map
    )

    save_json(
        YESTERDAY_DIR
        / "confirmed_result.json",
        yesterday_result,
    )

    # --------------------------------------------------------
    # 4. 前日学習候補合体
    # --------------------------------------------------------

    merged = merge_yesterday(
        yesterday_pre,
        yesterday_result,
    )

    save_json(
        YESTERDAY_DIR
        / "merged_training.json",
        merged,
    )

    ready_count = sum(
        1
        for race in merged.values()
        if race.get(
            "merge_status"
        )
        == "READY_FOR_AI"
    )

    # --------------------------------------------------------
    # 5. 今日レース地図
    # --------------------------------------------------------

    today_map = collect_race_map(
        TODAY
    )

    # --------------------------------------------------------
    # 6. 今日能力データ取得
    # --------------------------------------------------------

    (
        today_pre,
        ability_success,
        ability_failed,
    ) = collect_pre_race(
        today_map
    )

    save_json(
        TODAY_DIR
        / "pre_race.json",
        today_pre,
    )

    # --------------------------------------------------------
    # 7. 今日ライン取得
    # --------------------------------------------------------

    line_success = run_line_program()

    # --------------------------------------------------------
    # 8. Manifest
    # --------------------------------------------------------

    manifest = {

        "system_version":
            "060_OFFICIAL_DAILY_V1",

        "run_datetime":
            datetime.now().isoformat(),

        "today":
            TODAY,

        "yesterday":
            YESTERDAY,

        "today_race_count":
            len(today_map),

        "today_ability_found":
            ability_success,

        "today_ability_failed":
            ability_failed,

        "line_program_success":
            line_success,

        "yesterday_race_count":
            len(yesterday_map),

        "yesterday_result_confirmed":
            result_confirmed,

        "yesterday_result_pending":
            result_pending,

        "yesterday_result_error":
            result_error,

        "yesterday_ready_for_ai":
            ready_count,

    }

    save_json(
        TODAY_DIR
        / "daily_manifest.json",
        manifest,
    )

    # --------------------------------------------------------
    # 最終結果
    # --------------------------------------------------------

    print()
    print(
        "#" * 100
    )

    print(
        "060 最終結果"
    )

    print(
        "#" * 100
    )

    print()
    print(
        "TODAY:",
        TODAY,
    )

    print(
        "TODAY RACES:",
        len(today_map),
    )

    print(
        "ABILITY FOUND:",
        ability_success,
    )

    print(
        "ABILITY FAILED:",
        ability_failed,
    )

    print(
        "LINE PROGRAM SUCCESS:",
        line_success,
    )

    print()
    print(
        "YESTERDAY:",
        YESTERDAY,
    )

    print(
        "YESTERDAY RACES:",
        len(yesterday_map),
    )

    print(
        "RESULT CONFIRMED:",
        result_confirmed,
    )

    print(
        "RESULT PENDING:",
        result_pending,
    )

    print(
        "RESULT ERROR:",
        result_error,
    )

    print(
        "READY FOR AI:",
        ready_count,
    )

    print()
    print(
        "今日保存先:"
    )

    print(
        TODAY_DIR
    )

    print()
    print(
        "昨日学習データ:"
    )

    print(
        YESTERDAY_DIR
        / "merged_training.json"
    )

    print()
    print(
        "=== 060 完了 ==="
    )


if __name__ == "__main__":

    main()