"""
===========================================================
競輪AI
067_test.py

004完成済み直接取得導線
JSJ057
↓
JSJ001
↓
encParaR

同一 encParaR から

JSJ006 選手能力
JSJ005 ライン予想
JSJ012 確定結果

を同一 race_key に統合するテスト

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
    / "067_integrated_race_raw_test.json"
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
# 004読込
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
# 063成功方式
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

            "url":
                url,

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

            "url":
                url,

            "raw_length":
                0,

            "data":
                None,

            "error":
                repr(e),

        }


# ===========================================================
# JSJ005 narabiyoso探索
# ===========================================================

def find_narabiyoso(
    obj,
):

    if isinstance(
        obj,
        dict,
    ):

        narabiyoso = obj.get(
            "narabiyoso"
        )

        if isinstance(
            narabiyoso,
            dict,
        ):

            return narabiyoso

        for value in obj.values():

            found = find_narabiyoso(
                value
            )

            if found is not None:

                return found

    elif isinstance(
        obj,
        list,
    ):

        for value in obj:

            found = find_narabiyoso(
                value
            )

            if found is not None:

                return found

    return None


# ===========================================================
# JSJ005ライン復元
# 063成功方式
# ===========================================================

def reconstruct_lines(
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

        key=lambda x: (

            x["ichi"],

            x["shaban"],

        )

    )

    lines = []

    current = []

    previous_ichi = None

    for item in positions:

        ichi = item[
            "ichi"
        ]

        shaban = item[
            "shaban"
        ]

        if previous_ichi is None:

            current = [
                shaban
            ]

        elif (
            ichi
            == previous_ichi + 1
        ):

            current.append(
                shaban
            )

        else:

            if current:

                lines.append(
                    current
                )

            current = [
                shaban
            ]

        previous_ichi = ichi

    if current:

        lines.append(
            current
        )

    return (
        lines,
        positions,
    )


# ===========================================================
# JSJ006選手リスト探索
# ===========================================================

def find_player_list(
    obj,
):

    if isinstance(
        obj,
        dict,
    ):

        players = obj.get(
            "sensyuTypeInfo"
        )

        if isinstance(
            players,
            list,
        ):

            return players

        for value in obj.values():

            found = find_player_list(
                value
            )

            if found is not None:

                return found

    elif isinstance(
        obj,
        list,
    ):

        for value in obj:

            found = find_player_list(
                value
            )

            if found is not None:

                return found

    return []


# ===========================================================
# JSJ012着順リスト探索
# ===========================================================

def find_result_list(
    obj,
):

    if isinstance(
        obj,
        dict,
    ):

        results = obj.get(
            "tyakujyunItemSubData"
        )

        if isinstance(
            results,
            list,
        ):

            return results

        for value in obj.values():

            found = find_result_list(
                value
            )

            if found:

                return found

    elif isinstance(
        obj,
        list,
    ):

        for value in obj:

            found = find_result_list(
                value
            )

            if found:

                return found

    return []


# ===========================================================
# JSJ012払戻探索
# ===========================================================

def find_harai_data(
    obj,
):

    if isinstance(
        obj,
        dict,
    ):

        harai = obj.get(
            "haraiGakuSubData"
        )

        if isinstance(
            harai,
            dict,
        ):

            return harai

        for value in obj.values():

            found = find_harai_data(
                value
            )

            if found is not None:

                return found

    elif isinstance(
        obj,
        list,
    ):

        for value in obj:

            found = find_harai_data(
                value
            )

            if found is not None:

                return found

    return None


# ===========================================================
# 3連単結果確認
# ===========================================================

def has_trifecta_result(
    harai_data,
):

    if not isinstance(
        harai_data,
        dict,
    ):

        return False

    items = harai_data.get(
        "RT3HaraiGakuDispItemSubData"
    )

    if not isinstance(
        items,
        list,
    ):

        return False

    for item in items:

        if not isinstance(
            item,
            dict,
        ):

            continue

        combination = item.get(
            "kumiBan"
        )

        payout = item.get(
            "haraiGaku"
        )

        if combination in (
            None,
            "",
        ):

            continue

        if payout in (
            None,
            "",
            "【未発売】",
        ):

            continue

        return True

    return False


# ===========================================================
# 1レース統合
# ===========================================================

def build_integrated_race(
    collector,
    kday,
    venue_name,
    race_item,
):

    race_key = race_item.get(
        "race_key"
    )

    race_no = race_item.get(
        "race_no"
    )

    encp = race_item.get(
        "encParaR"
    )

    integrated = {

        "race_key":
            race_key,

        "race_date":
            kday,

        "venue":
            venue_name,

        "race_no":
            race_no,

        "encParaR":
            encp,

        "jsj001_race":
            race_item.get(
                "jsj001_race"
            ),

        "jsj006":
            None,

        "jsj005":
            None,

        "jsj012":
            None,

        "line_prediction":
            {

                "prediction_type":
                    None,

                "provider":
                    None,

                "positions":
                    [],

                "main_lines":
                    [],

            },

        "player_count":
            0,

        "line_player_count":
            0,

        "result_count":
            0,

        "has_trifecta_result":
            False,

        "same_race_key_integrated":
            False,

        "status":
            None,

        "problems":
            [],

    }

    if not encp:

        integrated[
            "problems"
        ].append({

            "problem":
                "ENC_PARA_R_MISSING",

        })

        integrated[
            "status"
        ] = "ENC_PARA_R_MISSING"

        return integrated


    # =======================================================
    # JSJ006
    # =======================================================

    jsj006_result = (
        collector.fetch_race_json(

            encp,

            "JSJ006",

        )
    )

    if jsj006_result.get(
        "ok"
    ):

        integrated[
            "jsj006"
        ] = jsj006_result.get(
            "data"
        )

    else:

        integrated[
            "problems"
        ].append({

            "problem":
                "JSJ006_FETCH_ERROR",

            "error":
                jsj006_result.get(
                    "error"
                ),

        })


    # =======================================================
    # JSJ005
    # =======================================================

    jsj005_result = fetch_jsj005(
        encp
    )

    if jsj005_result.get(
        "ok"
    ):

        integrated[
            "jsj005"
        ] = jsj005_result.get(
            "data"
        )

    else:

        integrated[
            "problems"
        ].append({

            "problem":
                "JSJ005_FETCH_ERROR",

            "error":
                jsj005_result.get(
                    "error"
                ),

        })


    # =======================================================
    # JSJ012
    # =======================================================

    jsj012_result = (
        collector.fetch_race_json(

            encp,

            "JSJ012",

        )
    )

    if jsj012_result.get(
        "ok"
    ):

        integrated[
            "jsj012"
        ] = jsj012_result.get(
            "data"
        )

    else:

        integrated[
            "problems"
        ].append({

            "problem":
                "JSJ012_FETCH_ERROR",

            "error":
                jsj012_result.get(
                    "error"
                ),

        })


    # =======================================================
    # JSJ006解析
    # =======================================================

    players = find_player_list(
        integrated[
            "jsj006"
        ]
    )

    integrated[
        "player_count"
    ] = len(
        players
    )

    if not players:

        integrated[
            "problems"
        ].append({

            "problem":
                "JSJ006_PLAYER_EMPTY",

        })


    # =======================================================
    # JSJ005解析
    # =======================================================

    narabiyoso = find_narabiyoso(
        integrated[
            "jsj005"
        ]
    )

    if isinstance(
        narabiyoso,
        dict,
    ):

        lines, positions = (
            reconstruct_lines(
                narabiyoso
            )
        )

        integrated[
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

            "positions":
                positions,

            "main_lines":
                lines,

        }

        integrated[
            "line_player_count"
        ] = sum(

            len(line)

            for line in lines

        )

    else:

        integrated[
            "problems"
        ].append({

            "problem":
                "JSJ005_NARABIYOSO_EMPTY",

        })


    # =======================================================
    # JSJ012解析
    # =======================================================

    results = find_result_list(
        integrated[
            "jsj012"
        ]
    )

    integrated[
        "result_count"
    ] = len(
        results
    )

    harai_data = find_harai_data(
        integrated[
            "jsj012"
        ]
    )

    integrated[
        "has_trifecta_result"
    ] = has_trifecta_result(
        harai_data
    )


    # =======================================================
    # 人数整合性
    # =======================================================

    player_count = integrated[
        "player_count"
    ]

    line_player_count = integrated[
        "line_player_count"
    ]

    result_count = integrated[
        "result_count"
    ]

    if (
        player_count > 0
        and line_player_count > 0
        and player_count
        != line_player_count
    ):

        integrated[
            "problems"
        ].append({

            "problem":
                "PLAYER_LINE_COUNT_MISMATCH",

            "player_count":
                player_count,

            "line_player_count":
                line_player_count,

        })

    if (
        player_count > 0
        and result_count > 0
        and player_count
        != result_count
    ):

        integrated[
            "problems"
        ].append({

            "problem":
                "PLAYER_RESULT_COUNT_MISMATCH",

            "player_count":
                player_count,

            "result_count":
                result_count,

        })


    # =======================================================
    # 統合判定
    # =======================================================

    has_jsj006 = isinstance(

        integrated[
            "jsj006"
        ],

        dict,

    )

    has_jsj005 = isinstance(

        integrated[
            "jsj005"
        ],

        dict,

    )

    has_jsj012 = isinstance(

        integrated[
            "jsj012"
        ],

        dict,

    )

    has_line = (
        line_player_count > 0
    )

    has_result = (
        result_count > 0
    )

    integrated[
        "same_race_key_integrated"
    ] = (

        has_jsj006
        and has_jsj005
        and has_jsj012
        and has_line
        and has_result

    )


    # =======================================================
    # STATUS
    # =======================================================

    if integrated[
        "same_race_key_integrated"
    ]:

        integrated[
            "status"
        ] = "FULL_INTEGRATED"

    elif (
        has_jsj006
        and has_jsj005
        and has_line
        and not has_result
    ):

        integrated[
            "status"
        ] = "PRE_RACE_INTEGRATED"

    elif (
        has_jsj006
        and not has_line
    ):

        integrated[
            "status"
        ] = "ABILITY_ONLY"

    else:

        integrated[
            "status"
        ] = "INCOMPLETE"

    return integrated


# ===========================================================
# main
# ===========================================================

def main():

    print()
    print(
        "=" * 100
    )

    print(
        "067 JSJ006 + JSJ005 + JSJ012 "
        "race_key統合テスト"
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

    print()


    # =======================================================
    # 004読込
    # =======================================================

    print(
        "[1] 004完成済み収集コード読込"
    )

    collector = (
        load_collector_module()
    )

    print(
        "004:",
        COLLECTOR_FILE,
    )


    # =======================================================
    # レース地図
    # =======================================================

    print()
    print(
        "[2] JSJ057 -> JSJ001 -> encParaR"
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
    # 全レース統合
    # =======================================================

    print()
    print(
        "[3] 全レース統合開始"
    )

    integrated_races = []

    status_counter = Counter()

    venue_counter = Counter()

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

            integrated = (
                build_integrated_race(

                    collector,

                    TARGET_DATE,

                    venue_name,

                    race_item,

                )
            )

            integrated_races.append(
                integrated
            )

            status = integrated.get(
                "status"
            )

            status_counter[
                status
            ] += 1

            venue_counter[
                venue_name
            ] += 1

            print(
                "STATUS:",
                status,
            )

            print(
                "PLAYER:",
                integrated.get(
                    "player_count"
                ),
            )

            print(
                "LINE PLAYER:",
                integrated.get(
                    "line_player_count"
                ),
            )

            print(
                "RESULT:",
                integrated.get(
                    "result_count"
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
                "TRIFECTA:",
                integrated.get(
                    "has_trifecta_result"
                ),
            )

            print(
                "INTEGRATED:",
                integrated.get(
                    "same_race_key_integrated"
                ),
            )

            if integrated.get(
                "problems"
            ):

                print(
                    "PROBLEMS:",
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

    full_integrated_count = (
        status_counter[
            "FULL_INTEGRATED"
        ]
    )

    pre_race_integrated_count = (
        status_counter[
            "PRE_RACE_INTEGRATED"
        ]
    )

    ability_only_count = (
        status_counter[
            "ABILITY_ONLY"
        ]
    )

    incomplete_count = (
        status_counter[
            "INCOMPLETE"
        ]
    )

    line_found_count = sum(

        1

        for race in integrated_races

        if race.get(
            "line_player_count",
            0,
        ) > 0

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


    # =======================================================
    # 保存
    # =======================================================

    output = {

        "program":
            "067_test.py",

        "purpose":
            (
                "004完成済み直接取得導線を使用し、"
                "同一encParaRから"
                "JSJ006・JSJ005・JSJ012を取得。"
                "同一race_keyへ統合可能か検証する。"
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

        "full_integrated_count":
            full_integrated_count,

        "pre_race_integrated_count":
            pre_race_integrated_count,

        "ability_only_count":
            ability_only_count,

        "incomplete_count":
            incomplete_count,

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

        "venue_race_summary":
            dict(
                venue_counter
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
        "067 最終結果"
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
        "FULL INTEGRATED:",
        full_integrated_count,
    )

    print(
        "PRE RACE INTEGRATED:",
        pre_race_integrated_count,
    )

    print(
        "ABILITY ONLY:",
        ability_only_count,
    )

    print(
        "INCOMPLETE:",
        incomplete_count,
    )

    print()

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
    # FULL INTEGRATED一覧
    # =======================================================

    print()
    print(
        "★ FULL INTEGRATED一覧 ★"
    )

    full_rows = [

        race

        for race in integrated_races

        if race.get(
            "status"
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
    # 問題一覧
    # =======================================================

    print()
    print(
        "★ PROBLEM一覧 ★"
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
                    "status"
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
        "=== 067 完了 ==="
    )


if __name__ == "__main__":

    main()