"""
===========================================================
競輪AI
069_test.py

目的:

068で保存済みの
20260711 レース前データ
    ・JSJ006 選手能力
    ・JSJ005 ライン予想

を読み込む

↓

完成済み004の
fetch_race_raw()
をそのまま使用

↓

現在の20260711 JSJ012確定結果を再取得

↓

race_keyで接続

↓

確定済みレースについて

能力
ライン
確定結果
3連単結果

が同一race_keyへ接続できるか確認

JSJ006解析:
作り直さない

JSJ012解析:
作り直さない

JSJ005:
再取得しない

Edge:
使用しない

Playwright:
使用しない
===========================================================
"""

import json
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

PRE_RACE_FILE = (
    BASE
    / "068_integrated_race_raw_test.json"
)

OUT_FILE = (
    BASE
    / "069_result_race_key_connection_test.json"
)


# ===========================================================
# 対象日
# ===========================================================

TARGET_DATE = "20260711"


# ===========================================================
# JSON
# ===========================================================

def load_json(
    path,
):

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
# 068レース取得
# ===========================================================

def get_pre_race_rows(
    root,
):

    if not isinstance(
        root,
        dict,
    ):

        return []

    rows = root.get(
        "races"
    )

    if not isinstance(
        rows,
        list,
    ):

        return []

    return [
        row
        for row in rows
        if isinstance(
            row,
            dict,
        )
    ]


# ===========================================================
# 068 race_key MAP
# ===========================================================

def build_pre_race_map(
    rows,
):

    result = {}

    duplicates = []

    for row in rows:

        race_key = row.get(
            "race_key"
        )

        if not race_key:

            continue

        if race_key in result:

            duplicates.append(
                race_key
            )

            continue

        result[
            race_key
        ] = row

    return (
        result,
        duplicates,
    )


# ===========================================================
# 接続状態判定
# ===========================================================

def classify_connection(
    pre_race,
    fresh_raw,
):

    if not isinstance(
        pre_race,
        dict,
    ):

        return "PRE_RACE_MISSING"

    if not isinstance(
        fresh_raw,
        dict,
    ):

        return "FRESH_RAW_MISSING"

    player_count = pre_race.get(
        "player_count",
        0,
    )

    line_found = pre_race.get(
        "line_found",
        False,
    )

    result_count = fresh_raw.get(
        "result_count",
        0,
    )

    has_trifecta = fresh_raw.get(
        "has_trifecta_result",
        False,
    )

    if (
        player_count > 0
        and line_found
        and result_count > 0
        and has_trifecta
    ):

        return "FULL_CONNECTED"

    if (
        player_count > 0
        and not line_found
        and result_count > 0
        and has_trifecta
    ):

        return "ABILITY_RESULT_CONNECTED"

    if (
        player_count > 0
        and result_count == 0
    ):

        return "RESULT_NOT_CONFIRMED"

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
        "069 7月11日確定結果 "
        "race_key接続確認"
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
    # 068読込
    # =======================================================

    print()
    print(
        "[1] 068保存済みレース前データ読込"
    )

    if not PRE_RACE_FILE.exists():

        print(
            "ERROR: 068保存JSONがありません"
        )

        print(
            PRE_RACE_FILE
        )

        return

    pre_root = load_json(
        PRE_RACE_FILE
    )

    pre_rows = get_pre_race_rows(
        pre_root
    )

    (
        pre_race_map,
        duplicate_keys,
    ) = build_pre_race_map(
        pre_rows
    )

    print(
        "068 RACE COUNT:",
        len(
            pre_rows
        ),
    )

    print(
        "068 RACE KEY COUNT:",
        len(
            pre_race_map
        ),
    )

    print(
        "DUPLICATE RACE KEY:",
        len(
            duplicate_keys
        ),
    )

    if duplicate_keys:

        print(
            "ERROR: race_key重複があります"
        )

        for race_key in duplicate_keys:

            print(
                race_key
            )

        return


    # =======================================================
    # 004読込
    # =======================================================

    print()
    print(
        "[2] 004完成済みコード読込"
    )

    collector = (
        load_collector_module()
    )

    print(
        "004:",
        COLLECTOR_FILE,
    )


    # =======================================================
    # 現在のレース地図
    # =======================================================

    print()
    print(
        "[3] 004 build_daily_race_map実行"
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
    # JSJ012再取得 + race_key接続
    # =======================================================

    print()
    print(
        "[4] 完成済み004で現在結果取得 "
        "+ race_key接続"
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
                "-" * 100
            )

            print(
                f"[{current_index}/"
                f"{race_total}] "
                f"{race_key}"
            )


            # =================================================
            # 068保存済みレース前データ
            # =================================================

            pre_race = pre_race_map.get(
                race_key
            )


            # =================================================
            # 完成済み004
            # JSJ006 + JSJ012取得・解析
            # =================================================

            fresh_raw = (
                collector.fetch_race_raw(
                    TARGET_DATE,
                    venue_name,
                    race_item,
                )
            )


            # =================================================
            # 接続状態
            # =================================================

            connection_status = (
                classify_connection(
                    pre_race,
                    fresh_raw,
                )
            )

            status_counter[
                connection_status
            ] += 1


            # =================================================
            # 保存データ
            # =================================================

            if isinstance(
                pre_race,
                dict,
            ):

                player_count = (
                    pre_race.get(
                        "player_count",
                        0,
                    )
                )

                line_found = (
                    pre_race.get(
                        "line_found",
                        False,
                    )
                )

                line_prediction = (
                    pre_race.get(
                        "line_prediction"
                    )
                )

                jsj006 = (
                    pre_race.get(
                        "jsj006"
                    )
                )

                jsj005 = (
                    pre_race.get(
                        "jsj005"
                    )
                )

            else:

                player_count = 0

                line_found = False

                line_prediction = None

                jsj006 = None

                jsj005 = None


            result_count = fresh_raw.get(
                "result_count",
                0,
            )

            has_trifecta = fresh_raw.get(
                "has_trifecta_result",
                False,
            )

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

                "connection_status":
                    connection_status,

                "player_count":
                    player_count,

                "line_found":
                    line_found,

                "result_count":
                    result_count,

                "has_trifecta_result":
                    has_trifecta,

                "line_prediction":
                    line_prediction,

                "jsj006":
                    jsj006,

                "jsj005":
                    jsj005,

                "jsj012":
                    fresh_raw.get(
                        "jsj012"
                    ),

                "fresh_004_complete":
                    fresh_raw.get(
                        "complete"
                    ),

                "fresh_004_problems":
                    fresh_raw.get(
                        "problems",
                        [],
                    ),

            }

            connected_rows.append(
                connected
            )


            # =================================================
            # 表示
            # =================================================

            print(
                "STATUS:",
                connection_status,
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

            if isinstance(
                line_prediction,
                dict,
            ):

                print(
                    "TYPE:",
                    line_prediction.get(
                        "prediction_type"
                    ),
                )

                print(
                    "LINES:",
                    line_prediction.get(
                        "main_lines"
                    ),
                )

            if fresh_raw.get(
                "problems"
            ):

                print(
                    "004 PROBLEMS:",
                    fresh_raw.get(
                        "problems"
                    ),
                )


    # =======================================================
    # 集計
    # =======================================================

    confirmed_rows = [

        row

        for row in connected_rows

        if row.get(
            "result_count",
            0,
        ) > 0

    ]

    trifecta_rows = [

        row

        for row in connected_rows

        if row.get(
            "has_trifecta_result"
        )

    ]

    full_connected_rows = [

        row

        for row in connected_rows

        if row.get(
            "connection_status"
        ) == "FULL_CONNECTED"

    ]

    ability_result_rows = [

        row

        for row in connected_rows

        if row.get(
            "connection_status"
        ) == "ABILITY_RESULT_CONNECTED"

    ]

    not_confirmed_rows = [

        row

        for row in connected_rows

        if row.get(
            "connection_status"
        ) == "RESULT_NOT_CONFIRMED"

    ]

    incomplete_rows = [

        row

        for row in connected_rows

        if row.get(
            "connection_status"
        ) in (
            "PRE_RACE_MISSING",
            "FRESH_RAW_MISSING",
            "INCOMPLETE",
        )

    ]


    # =======================================================
    # 保存
    # =======================================================

    output = {

        "program":
            "069_test.py",

        "purpose":
            (
                "068保存済み20260711レース前データへ、"
                "完成済み004 fetch_race_rawで"
                "現在のJSJ012確定結果を再取得し、"
                "race_keyで能力・ライン・結果を"
                "接続できるか確認する。"
            ),

        "target_date":
            TARGET_DATE,

        "pre_race_source":
            str(
                PRE_RACE_FILE
            ),

        "collector_source":
            str(
                COLLECTOR_FILE
            ),

        "race_count":
            len(
                connected_rows
            ),

        "confirmed_result_count":
            len(
                confirmed_rows
            ),

        "trifecta_found_count":
            len(
                trifecta_rows
            ),

        "full_connected_count":
            len(
                full_connected_rows
            ),

        "ability_result_connected_count":
            len(
                ability_result_rows
            ),

        "result_not_confirmed_count":
            len(
                not_confirmed_rows
            ),

        "incomplete_count":
            len(
                incomplete_rows
            ),

        "status_summary":
            dict(
                status_counter
            ),

        "races":
            connected_rows,

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
        "069 最終結果"
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
        len(
            connected_rows
        ),
    )

    print()

    print(
        "CONFIRMED RESULT FOUND:",
        len(
            confirmed_rows
        ),
    )

    print(
        "TRIFECTA FOUND:",
        len(
            trifecta_rows
        ),
    )

    print()

    print(
        "FULL CONNECTED:",
        len(
            full_connected_rows
        ),
    )

    print(
        "ABILITY + RESULT CONNECTED:",
        len(
            ability_result_rows
        ),
    )

    print(
        "RESULT NOT CONFIRMED:",
        len(
            not_confirmed_rows
        ),
    )

    print(
        "INCOMPLETE:",
        len(
            incomplete_rows
        ),
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
    # 確定結果接続一覧
    # =======================================================

    print()
    print(
        "★ CONFIRMED RESULT CONNECTED一覧 ★"
    )

    if not confirmed_rows:

        print(
            "なし"
        )

    else:

        for row in confirmed_rows:

            print()
            print(
                row.get(
                    "race_key"
                )
            )

            print(
                "STATUS:",
                row.get(
                    "connection_status"
                ),
            )

            print(
                "PLAYER:",
                row.get(
                    "player_count"
                ),
            )

            print(
                "LINE:",
                row.get(
                    "line_found"
                ),
            )

            print(
                "RESULT:",
                row.get(
                    "result_count"
                ),
            )

            print(
                "TRIFECTA:",
                row.get(
                    "has_trifecta_result"
                ),
            )

            line_prediction = row.get(
                "line_prediction"
            )

            if isinstance(
                line_prediction,
                dict,
            ):

                print(
                    "TYPE:",
                    line_prediction.get(
                        "prediction_type"
                    ),
                )

                print(
                    "PROVIDER:",
                    line_prediction.get(
                        "provider"
                    ),
                )

                print(
                    "LINES:",
                    line_prediction.get(
                        "main_lines"
                    ),
                )


    # =======================================================
    # INCOMPLETE一覧
    # =======================================================

    print()
    print(
        "★ INCOMPLETE一覧 ★"
    )

    if not incomplete_rows:

        print(
            "なし"
        )

    else:

        for row in incomplete_rows:

            print()
            print(
                row.get(
                    "race_key"
                )
            )

            print(
                "STATUS:",
                row.get(
                    "connection_status"
                ),
            )

            print(
                "004 PROBLEMS:",
                row.get(
                    "fresh_004_problems"
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
        "=== 069 完了 ==="
    )


if __name__ == "__main__":

    main()