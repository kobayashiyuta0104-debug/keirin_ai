"""
===========================================================
競輪AI
068_test.py

完成済み004の処理をそのまま使用

004:
JSJ057
↓
JSJ001
↓
encParaR
↓
fetch_race_raw()
↓
JSJ006
JSJ012
player_count
result_count
has_trifecta_result

ここへ

完成済みJSJ005ライン直接取得

だけを追加する統合確認

Edge:
使用しない

Playwright:
使用しない
===========================================================
"""

import json
import time
import urllib.request
import urllib.parse
import importlib.util

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

OUT_FILE = (
    BASE
    / "068_integrated_race_raw_test.json"
)


# ===========================================================
# 対象日
# ===========================================================

TARGET_DATE = "20260711"


# ===========================================================
# 通信待機
# ===========================================================

REQUEST_INTERVAL_SECONDS = 0.05


# ===========================================================
# JSON保存
# ===========================================================

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
# JSJ005 narabiyoso取得
# ===========================================================

def get_narabiyoso(
    jsj005,
):

    if not isinstance(
        jsj005,
        dict,
    ):

        return None

    narabiyoso = jsj005.get(
        "narabiyoso"
    )

    if isinstance(
        narabiyoso,
        dict,
    ):

        return narabiyoso

    return None


# ===========================================================
# JSJ005ライン復元
# 066完成方式
# ===========================================================

def reconstruct_main_lines(
    narabiyoso,
):

    if not isinstance(
        narabiyoso,
        dict,
    ):

        return (
            [],
            [],
        )

    rows = narabiyoso.get(
        "shaban"
    )

    if not isinstance(
        rows,
        list,
    ):

        return (
            [],
            [],
        )

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

    return (
        main_lines,
        positions,
    )


# ===========================================================
# 004完成RAWへJSJ005だけ追加
# ===========================================================

def add_line_prediction(
    raw_race,
):

    result = dict(
        raw_race
    )

    result[
        "jsj005"
    ] = None

    result[
        "line_prediction"
    ] = {

        "prediction_type":
            None,

        "provider":
            None,

        "main_lines":
            [],

        "positions":
            [],

    }

    result[
        "line_found"
    ] = False

    encp = result.get(
        "encParaR"
    )

    if not encp:

        result[
            "problems"
        ].append({

            "problem":
                "JSJ005_ENCP_MISSING",

        })

        return result

    jsj005_result = fetch_jsj005(
        encp
    )

    if not jsj005_result[
        "ok"
    ]:

        result[
            "problems"
        ].append({

            "problem":
                "JSJ005_FETCH_ERROR",

            "error":
                jsj005_result[
                    "error"
                ],

        })

        return result

    jsj005 = jsj005_result[
        "data"
    ]

    result[
        "jsj005"
    ] = jsj005

    narabiyoso = get_narabiyoso(
        jsj005
    )

    if not isinstance(
        narabiyoso,
        dict,
    ):

        return result

    main_lines, positions = (
        reconstruct_main_lines(
            narabiyoso
        )
    )

    result[
        "line_prediction"
    ] = {

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

    result[
        "line_found"
    ] = (
        len(
            positions
        )
        > 0
    )

    return result


# ===========================================================
# 統合状態判定
# ===========================================================

def classify_integrated_status(
    race,
):

    player_count = race.get(
        "player_count",
        0,
    )

    result_count = race.get(
        "result_count",
        0,
    )

    has_trifecta = race.get(
        "has_trifecta_result",
        False,
    )

    line_found = race.get(
        "line_found",
        False,
    )

    if (
        player_count > 0
        and line_found
        and result_count > 0
        and has_trifecta
    ):

        return "FULL_INTEGRATED"

    if (
        player_count > 0
        and line_found
        and result_count == 0
    ):

        return "PRE_RACE_INTEGRATED"

    if (
        player_count > 0
        and not line_found
        and result_count > 0
        and has_trifecta
    ):

        return "ABILITY_RESULT"

    if (
        player_count > 0
        and not line_found
        and result_count == 0
    ):

        return "ABILITY_ONLY"

    return "INCOMPLETE"


# ===========================================================
# main
# ===========================================================

def main():

    print()
    print(
        "=" * 100
    )

    print(
        "068 完成済み004 + JSJ005 "
        "race_key統合確認"
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


    # =======================================================
    # 004読込
    # =======================================================

    print()
    print(
        "[1] 004完成済みコード読込"
    )

    collector = (
        load_collector_module()
    )

    print(
        "004:",
        COLLECTOR_FILE,
    )


    # =======================================================
    # 004完成済みレース地図
    # =======================================================

    print()
    print(
        "[2] 004 build_daily_race_map実行"
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


    # =======================================================
    # 全レース
    # =======================================================

    print()
    print(
        "[3] 004 fetch_race_raw "
        "+ JSJ005開始"
    )

    integrated_races = []

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
                "-" * 100
            )

            print(

                f"[{current_index}/"
                f"{race_total}] "
                f"{race_key}"

            )


            # =================================================
            # 004完成済み
            # JSJ006 + JSJ012
            # =================================================

            raw_race = (
                collector.fetch_race_raw(

                    TARGET_DATE,

                    venue_name,

                    race_item,

                )
            )


            # =================================================
            # JSJ005だけ追加
            # =================================================

            integrated = (
                add_line_prediction(
                    raw_race
                )
            )


            # =================================================
            # 統合STATUS
            # =================================================

            integrated_status = (
                classify_integrated_status(
                    integrated
                )
            )

            integrated[
                "integrated_status"
            ] = integrated_status

            status_counter[
                integrated_status
            ] += 1

            integrated_races.append(
                integrated
            )


            # =================================================
            # 表示
            # =================================================

            print(
                "STATUS:",
                integrated_status,
            )

            print(
                "PLAYER:",
                integrated.get(
                    "player_count"
                ),
            )

            print(
                "LINE FOUND:",
                integrated.get(
                    "line_found"
                ),
            )

            print(
                "TYPE:",
                integrated[
                    "line_prediction"
                ].get(
                    "prediction_type"
                ),
            )

            print(
                "PROVIDER:",
                integrated[
                    "line_prediction"
                ].get(
                    "provider"
                ),
            )

            print(
                "LINES:",
                integrated[
                    "line_prediction"
                ].get(
                    "main_lines"
                ),
            )

            print(
                "RESULT:",
                integrated.get(
                    "result_count"
                ),
            )

            print(
                "TRIFECTA:",
                integrated.get(
                    "has_trifecta_result"
                ),
            )

            print(
                "004 COMPLETE:",
                integrated.get(
                    "complete"
                ),
            )

            if integrated.get(
                "problems"
            ):

                print(
                    "004 PROBLEMS:",
                    integrated.get(
                        "problems"
                    ),
                )

            time.sleep(
                REQUEST_INTERVAL_SECONDS
            )


    # =======================================================
    # 集計
    # =======================================================

    line_found_count = sum(

        1

        for race in integrated_races

        if race.get(
            "line_found"
        )

    )

    result_found_count = sum(

        1

        for race in integrated_races

        if race.get(
            "result_count",
            0,
        ) > 0

    )

    trifecta_found_count = sum(

        1

        for race in integrated_races

        if race.get(
            "has_trifecta_result"
        )

    )

    player_found_count = sum(

        1

        for race in integrated_races

        if race.get(
            "player_count",
            0,
        ) > 0

    )


    # =======================================================
    # 保存
    # =======================================================

    output = {

        "program":
            "068_test.py",

        "purpose":
            (
                "完成済み004のfetch_race_rawを"
                "そのまま使用して"
                "JSJ006・JSJ012を取得・解析し、"
                "完成済みJSJ005ライン直接取得だけを追加。"
                "同一race_key統合を確認する。"
            ),

        "target_date":
            TARGET_DATE,

        "collector_source":
            str(
                COLLECTOR_FILE
            ),

        "venue_count":
            daily_map.get(
                "venue_count"
            ),

        "race_count":
            len(
                integrated_races
            ),

        "player_found_count":
            player_found_count,

        "line_found_count":
            line_found_count,

        "result_found_count":
            result_found_count,

        "trifecta_found_count":
            trifecta_found_count,

        "status_summary":
            dict(
                status_counter
            ),

        "races":
            integrated_races,

    }

    save_json(
        OUT_FILE,
        output,
    )


    # =======================================================
    # 最終結果
    # =======================================================

    print()
    print(
        "=" * 100
    )

    print(
        "068 最終結果"
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
        "VENUE COUNT:",
        daily_map.get(
            "venue_count"
        ),
    )

    print(
        "RACE COUNT:",
        len(
            integrated_races
        ),
    )

    print()

    print(
        "PLAYER FOUND:",
        player_found_count,
    )

    print(
        "LINE FOUND:",
        line_found_count,
    )

    print(
        "RESULT FOUND:",
        result_found_count,
    )

    print(
        "TRIFECTA FOUND:",
        trifecta_found_count,
    )

    print()

    print(
        "★ STATUS SUMMARY ★"
    )

    for (
        status,
        count,
    ) in status_counter.most_common():

        print(
            status,
            ":",
            count,
        )


    # =======================================================
    # FULL一覧
    # =======================================================

    print()
    print(
        "★ FULL INTEGRATED一覧 ★"
    )

    full_rows = [

        race

        for race in integrated_races

        if race.get(
            "integrated_status"
        ) == "FULL_INTEGRATED"

    ]

    if not full_rows:

        print(
            "なし"
        )

    else:

        for race in full_rows:

            print()
            print(
                race.get(
                    "race_key"
                )
            )

            print(
                "PLAYER:",
                race.get(
                    "player_count"
                ),
            )

            print(
                "TYPE:",
                race[
                    "line_prediction"
                ].get(
                    "prediction_type"
                ),
            )

            print(
                "PROVIDER:",
                race[
                    "line_prediction"
                ].get(
                    "provider"
                ),
            )

            print(
                "LINES:",
                race[
                    "line_prediction"
                ].get(
                    "main_lines"
                ),
            )

            print(
                "RESULT:",
                race.get(
                    "result_count"
                ),
            )

            print(
                "TRIFECTA:",
                race.get(
                    "has_trifecta_result"
                ),
            )


    # =======================================================
    # 004問題一覧
    # =======================================================

    print()
    print(
        "★ 004 PROBLEM一覧 ★"
    )

    problem_rows = [

        race

        for race in integrated_races

        if race.get(
            "problems"
        )

    ]

    if not problem_rows:

        print(
            "なし"
        )

    else:

        for race in problem_rows:

            print()
            print(
                race.get(
                    "race_key"
                )
            )

            print(
                "STATUS:",
                race.get(
                    "integrated_status"
                ),
            )

            print(
                "PROBLEMS:",
                race.get(
                    "problems"
                ),
            )


    print()
    print(
        "保存先:"
    )

    print(
        OUT_FILE
    )

    print()
    print(
        "=== 068 完了 ==="
    )


if __name__ == "__main__":

    main()