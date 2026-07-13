"""
===========================================================
競輪AI 正式版
keirin_daily_collector.py

目的:

当日レース前データ
    ・JSJ006 選手能力
    ・JSJ005 ライン予想

を直接取得・保存

↓

同じrace_keyについて
JSJ012確定結果を取得

↓

能力
ライン
確定結果
3連単結果

を同一race_keyへ統合

Edge:
使用しない

Playwright:
使用しない

完成済み004:
JSJ057
JSJ001
JSJ006
JSJ012
の処理をそのまま使用

JSJ005:
066完成方式を使用
===========================================================
"""

import json
import urllib.request
import urllib.parse
import importlib.util

from datetime import datetime
from pathlib import Path
from collections import Counter


# ===========================================================
# 基本設定
# ===========================================================

BASE = Path(r"C:\競輪AI")

AI_PROGRAM_DIR = (
    BASE
    / "ai_program"
)

COLLECTOR_FILE = (
    AI_PROGRAM_DIR
    / "004_collect_historical_raw.py"
)

DAILY_DIR = (
    BASE
    / "data_official"
    / "daily"
)

DAILY_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ===========================================================
# 対象日
# 現在日を自動使用
# ===========================================================

TARGET_DATE = datetime.now().strftime(
    "%Y%m%d"
)


# ===========================================================
# 保存先
# ===========================================================

PRE_RACE_FILE = (
    DAILY_DIR
    / f"{TARGET_DATE}_pre_race.json"
)

INTEGRATED_FILE = (
    DAILY_DIR
    / f"{TARGET_DATE}_integrated.json"
)


# ===========================================================
# JSON
# ===========================================================

def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


def save_json(
    path,
    data,
):

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )


# ===========================================================
# 004完成済みコード読込
# ===========================================================

def load_collector_module():

    if not COLLECTOR_FILE.exists():

        raise FileNotFoundError(
            "004_collect_historical_raw.py がありません: "
            + str(COLLECTOR_FILE)
        )

    spec = (
        importlib.util.spec_from_file_location(
            "official_collector_004",
            COLLECTOR_FILE,
        )
    )

    if (
        spec is None
        or spec.loader is None
    ):

        raise RuntimeError(
            "004_collect_historical_raw.py "
            "を読込できません"
        )

    module = (
        importlib.util.module_from_spec(
            spec
        )
    )

    spec.loader.exec_module(
        module
    )

    return module


# ===========================================================
# JSJ005直接取得
# 066完成方式
# ===========================================================

def fetch_jsj005(
    encp,
):

    query = urllib.parse.urlencode({

        "encp":
            encp,

        "type":
            "JSJ005",

    })

    url = (
        "https://www.keirin.jp/pc/json?"
        + query
    )

    request = urllib.request.Request(

        url,

        headers={

            "User-Agent":
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/142.0.0.0 Safari/537.36",

            "Referer":
                "https://www.keirin.jp/pc/racelive",

            "Accept":
                "application/json, "
                "text/javascript, "
                "*/*; q=0.01",

            "X-Requested-With":
                "XMLHttpRequest",

        },

    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=20,
        ) as response:

            raw = response.read().decode(
                "utf-8",
                errors="replace",
            )

            status = response.status

        try:

            data = json.loads(
                raw
            )

        except Exception:

            data = None

        return {

            "ok":
                True,

            "status":
                status,

            "raw_length":
                len(raw),

            "data":
                data,

            "error":
                None,

        }

    except Exception as e:

        return {

            "ok":
                False,

            "status":
                None,

            "raw_length":
                0,

            "data":
                None,

            "error":
                repr(e),

        }


# ===========================================================
# JSJ005ライン復元
# 066完成方式
# ===========================================================

def reconstruct_main_lines(
    jsj005,
):

    if not isinstance(
        jsj005,
        dict,
    ):

        return {

            "line_found":
                False,

            "prediction_type":
                None,

            "provider":
                None,

            "main_lines":
                [],

            "positions":
                [],

        }

    narabiyoso = jsj005.get(
        "narabiyoso"
    )

    if not isinstance(
        narabiyoso,
        dict,
    ):

        return {

            "line_found":
                False,

            "prediction_type":
                None,

            "provider":
                None,

            "main_lines":
                [],

            "positions":
                [],

        }

    rows = narabiyoso.get(
        "shaban"
    )

    if not isinstance(
        rows,
        list,
    ):

        rows = []

    positions = []

    for row in rows:

        if not isinstance(
            row,
            dict,
        ):

            continue

        try:

            ichi = int(
                row.get(
                    "ichi"
                )
            )

            shaban = int(
                row.get(
                    "shaban"
                )
            )

        except Exception:

            continue

        if ichi < 1:

            continue

        if not (
            1
            <= shaban
            <= 9
        ):

            continue

        positions.append({

            "ichi":
                ichi,

            "shaban":
                shaban,

        })

    positions.sort(

        key=lambda item: (

            item["ichi"],

            item["shaban"],

        )

    )

    main_lines = []

    current_line = []

    previous_ichi = None

    for item in positions:

        ichi = item[
            "ichi"
        ]

        shaban = item[
            "shaban"
        ]

        if previous_ichi is None:

            current_line = [
                shaban
            ]

        elif (
            ichi
            == previous_ichi + 1
        ):

            current_line.append(
                shaban
            )

        else:

            if current_line:

                main_lines.append(
                    current_line
                )

            current_line = [
                shaban
            ]

        previous_ichi = ichi

    if current_line:

        main_lines.append(
            current_line
        )

    return {

        "line_found":
            len(
                positions
            ) > 0,

        "prediction_type":
            narabiyoso.get(
                "lineKeitai"
            ),

        "provider":
            narabiyoso.get(
                "teikyo"
            ),

        "main_lines":
            main_lines,

        "positions":
            positions,

    }


# ===========================================================
# レース前データ作成
# ===========================================================

def collect_pre_race(
    collector,
):

    print()
    print(
        "[1] 当日レース地図取得"
    )

    daily_map = (
        collector.build_daily_race_map(
            TARGET_DATE
        )
    )

    print(
        "VENUE COUNT:",
        daily_map.get(
            "venue_count"
        ),
    )

    print(
        "RACE COUNT:",
        daily_map.get(
            "race_count"
        ),
    )

    races = []

    line_found_count = 0

    player_found_count = 0

    race_total = daily_map.get(
        "race_count",
        0,
    )

    current_index = 0

    for venue in daily_map.get(
        "venues",
        [],
    ):

        venue_name = venue.get(
            "venue"
        )

        for race_item in venue.get(
            "races",
            [],
        ):

            current_index += 1

            race_key = race_item.get(
                "race_key"
            )

            encp = race_item.get(
                "encParaR"
            )

            print()
            print(
                f"[{current_index}/"
                f"{race_total}] "
                f"{race_key}"
            )

            raw_race = (
                collector.fetch_race_raw(
                    TARGET_DATE,
                    venue_name,
                    race_item,
                )
            )

            jsj005_result = fetch_jsj005(
                encp
            )

            jsj005 = jsj005_result.get(
                "data"
            )

            line_prediction = (
                reconstruct_main_lines(
                    jsj005
                )
            )

            player_count = raw_race.get(
                "player_count",
                0,
            )

            if player_count > 0:

                player_found_count += 1

            if line_prediction[
                "line_found"
            ]:

                line_found_count += 1

            row = {

                "race_key":
                    race_key,

                "race_date":
                    TARGET_DATE,

                "venue":
                    venue_name,

                "race_no":
                    race_item.get(
                        "race_no"
                    ),

                "encParaR":
                    encp,

                "player_count":
                    player_count,

                "line_found":
                    line_prediction[
                        "line_found"
                    ],

                "line_prediction":
                    line_prediction,

                "jsj006":
                    raw_race.get(
                        "jsj006"
                    ),

                "jsj005":
                    jsj005,

            }

            races.append(
                row
            )

            print(
                "PLAYER:",
                player_count,
            )

            print(
                "LINE:",
                line_prediction[
                    "line_found"
                ],
            )

            print(
                "TYPE:",
                line_prediction[
                    "prediction_type"
                ],
            )

            print(
                "LINES:",
                line_prediction[
                    "main_lines"
                ],
            )

    output = {

        "program":
            "keirin_daily_collector.py",

        "data_type":
            "PRE_RACE",

        "target_date":
            TARGET_DATE,

        "race_count":
            len(
                races
            ),

        "player_found_count":
            player_found_count,

        "line_found_count":
            line_found_count,

        "races":
            races,

    }

    save_json(
        PRE_RACE_FILE,
        output,
    )

    return output


# ===========================================================
# 保存済みレース前データ読込
# ===========================================================

def load_or_collect_pre_race(
    collector,
):

    if PRE_RACE_FILE.exists():

        print()
        print(
            "[1] 保存済みレース前データ使用"
        )

        print(
            PRE_RACE_FILE
        )

        return load_json(
            PRE_RACE_FILE
        )

    return collect_pre_race(
        collector
    )


# ===========================================================
# race_key MAP
# ===========================================================

def build_race_map(
    rows,
):

    result = {}

    for row in rows:

        if not isinstance(
            row,
            dict,
        ):

            continue

        race_key = row.get(
            "race_key"
        )

        if not race_key:

            continue

        if race_key in result:

            raise RuntimeError(
                "DUPLICATE_RACE_KEY: "
                + race_key
            )

        result[
            race_key
        ] = row

    return result


# ===========================================================
# 現在結果を接続
# ===========================================================

def connect_results(
    collector,
    pre_root,
):

    print()
    print(
        "[2] 現在JSJ012結果取得"
    )

    pre_rows = pre_root.get(
        "races",
        [],
    )

    pre_map = build_race_map(
        pre_rows
    )

    daily_map = (
        collector.build_daily_race_map(
            TARGET_DATE
        )
    )

    connected_rows = []

    status_counter = Counter()

    race_total = daily_map.get(
        "race_count",
        0,
    )

    current_index = 0

    for venue in daily_map.get(
        "venues",
        [],
    ):

        venue_name = venue.get(
            "venue"
        )

        for race_item in venue.get(
            "races",
            [],
        ):

            current_index += 1

            race_key = race_item.get(
                "race_key"
            )

            print()
            print(
                f"[{current_index}/"
                f"{race_total}] "
                f"{race_key}"
            )

            pre_race = pre_map.get(
                race_key
            )

            if pre_race is None:

                status = (
                    "PRE_RACE_MISSING"
                )

                status_counter[
                    status
                ] += 1

                connected_rows.append({

                    "race_key":
                        race_key,

                    "status":
                        status,

                })

                print(
                    "STATUS:",
                    status,
                )

                continue

            fresh_raw = (
                collector.fetch_race_raw(
                    TARGET_DATE,
                    venue_name,
                    race_item,
                )
            )

            result_count = fresh_raw.get(
                "result_count",
                0,
            )

            has_trifecta = fresh_raw.get(
                "has_trifecta_result",
                False,
            )

            player_count = pre_race.get(
                "player_count",
                0,
            )

            line_found = pre_race.get(
                "line_found",
                False,
            )

            if (
                player_count > 0
                and line_found
                and result_count > 0
                and has_trifecta
            ):

                status = (
                    "FULL_CONNECTED"
                )

            elif (
                player_count > 0
                and not line_found
                and result_count > 0
                and has_trifecta
            ):

                status = (
                    "ABILITY_RESULT_CONNECTED"
                )

            elif (
                player_count > 0
                and result_count == 0
            ):

                status = (
                    "RESULT_NOT_CONFIRMED"
                )

            else:

                status = (
                    "INCOMPLETE"
                )

            status_counter[
                status
            ] += 1

            connected = {

                "race_key":
                    race_key,

                "race_date":
                    TARGET_DATE,

                "venue":
                    venue_name,

                "race_no":
                    race_item.get(
                        "race_no"
                    ),

                "encParaR":
                    race_item.get(
                        "encParaR"
                    ),

                "status":
                    status,

                "player_count":
                    player_count,

                "line_found":
                    line_found,

                "result_count":
                    result_count,

                "has_trifecta_result":
                    has_trifecta,

                "line_prediction":
                    pre_race.get(
                        "line_prediction"
                    ),

                "jsj006":
                    pre_race.get(
                        "jsj006"
                    ),

                "jsj005":
                    pre_race.get(
                        "jsj005"
                    ),

                "jsj012":
                    fresh_raw.get(
                        "jsj012"
                    ),

            }

            connected_rows.append(
                connected
            )

            print(
                "STATUS:",
                status,
            )

            print(
                "PLAYER:",
                player_count,
            )

            print(
                "LINE:",
                line_found,
            )

            print(
                "RESULT:",
                result_count,
            )

            print(
                "TRIFECTA:",
                has_trifecta,
            )

    output = {

        "program":
            "keirin_daily_collector.py",

        "data_type":
            "INTEGRATED",

        "target_date":
            TARGET_DATE,

        "race_count":
            len(
                connected_rows
            ),

        "status_summary":
            dict(
                status_counter
            ),

        "races":
            connected_rows,

    }

    save_json(
        INTEGRATED_FILE,
        output,
    )

    return output


# ===========================================================
# main
# ===========================================================

def main():

    print()
    print(
        "=" * 100
    )

    print(
        "競輪AI 正式日次収集"
    )

    print(
        "=" * 100
    )

    print()

    print(
        "TARGET DATE:",
        TARGET_DATE,
    )

    print(
        "Edge:",
        "使用しません",
    )

    print(
        "Playwright:",
        "使用しません",
    )

    collector = (
        load_collector_module()
    )

    pre_root = (
        load_or_collect_pre_race(
            collector
        )
    )

    integrated = (
        connect_results(
            collector,
            pre_root,
        )
    )

    status_summary = integrated.get(
        "status_summary",
        {},
    )

    print()
    print(
        "=" * 100
    )

    print(
        "正式日次収集 最終結果"
    )

    print(
        "=" * 100
    )

    print()

    print(
        "TARGET DATE:",
        TARGET_DATE,
    )

    print(
        "RACE COUNT:",
        integrated.get(
            "race_count"
        ),
    )

    print()

    print(
        "FULL CONNECTED:",
        status_summary.get(
            "FULL_CONNECTED",
            0,
        ),
    )

    print(
        "ABILITY + RESULT CONNECTED:",
        status_summary.get(
            "ABILITY_RESULT_CONNECTED",
            0,
        ),
    )

    print(
        "RESULT NOT CONFIRMED:",
        status_summary.get(
            "RESULT_NOT_CONFIRMED",
            0,
        ),
    )

    print(
        "PRE RACE MISSING:",
        status_summary.get(
            "PRE_RACE_MISSING",
            0,
        ),
    )

    print(
        "INCOMPLETE:",
        status_summary.get(
            "INCOMPLETE",
            0,
        ),
    )

    print()

    print(
        "レース前保存:"
    )

    print(
        PRE_RACE_FILE
    )

    print()

    print(
        "統合保存:"
    )

    print(
        INTEGRATED_FILE
    )

    print()

    print(
        "=== 完了 ==="
    )


if __name__ == "__main__":

    main()