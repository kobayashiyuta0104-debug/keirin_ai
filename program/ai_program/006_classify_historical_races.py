"""
===========================================================
競輪AI 正式版
006_classify_historical_races.py

004で収集した全日別RAWを正式状態分類

分類:
・NORMAL
・ALL_REFUND
・FETCH_ERROR
・INVALID_RAW

NORMALのみ学習対象
===========================================================
"""

import json
from pathlib import Path
from collections import Counter


# ===========================================================
# 基本設定
# ===========================================================

BASE = Path(r"C:\競輪AI")

HISTORICAL_DIR = (
    BASE
    / "data_official"
    / "historical_raw"
)

DAILY_RAW_DIR = (
    HISTORICAL_DIR
    / "daily"
)

COLLECTION_VALIDATION_FILE = (
    HISTORICAL_DIR
    / "004_collection_validation.json"
)

OUT_FILE = (
    HISTORICAL_DIR
    / "006_classified_historical_races.json"
)

VALIDATION_FILE = (
    HISTORICAL_DIR
    / "006_classification_validation.json"
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


def save_json(path, data):

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
# 再帰探索
# ===========================================================

def find_value_by_key(
    obj,
    target_key,
):

    if isinstance(obj, dict):

        if target_key in obj:

            return obj[
                target_key
            ]

        for value in obj.values():

            found = find_value_by_key(
                value,
                target_key,
            )

            if found is not None:

                return found

    elif isinstance(obj, list):

        for value in obj:

            found = find_value_by_key(
                value,
                target_key,
            )

            if found is not None:

                return found

    return None


# ===========================================================
# JSJ006選手
# ===========================================================

def get_players(jsj006):

    players = find_value_by_key(
        jsj006,
        "sensyuTypeInfo",
    )

    if not isinstance(
        players,
        list,
    ):

        return []

    return players


# ===========================================================
# JSJ012着順
# ===========================================================

def get_results(jsj012):

    results = find_value_by_key(
        jsj012,
        "tyakujyunItemSubData",
    )

    if not isinstance(
        results,
        list,
    ):

        return []

    return results


# ===========================================================
# 払戻構造
# ===========================================================

def get_harai_data(jsj012):

    harai = find_value_by_key(
        jsj012,
        "haraiGakuSubData",
    )

    if not isinstance(
        harai,
        dict,
    ):

        return None

    return harai


# ===========================================================
# 全返還判定
# ===========================================================

def is_all_refund(
    harai_data,
):

    if not isinstance(
        harai_data,
        dict,
    ):

        return False

    refund_count = 0

    payout_item_count = 0

    for value in harai_data.values():

        if not isinstance(
            value,
            list,
        ):

            continue

        for item in value:

            if not isinstance(
                item,
                dict,
            ):

                continue

            if "haraiGaku" not in item:

                continue

            payout_item_count += 1

            payout = str(
                item.get(
                    "haraiGaku",
                    ""
                )
            ).strip()

            if payout == "【全返還】":

                refund_count += 1

    return (
        payout_item_count > 0
        and refund_count > 0
    )


# ===========================================================
# 3連単取得
# ===========================================================

def get_trifecta(
    harai_data,
):

    if not isinstance(
        harai_data,
        dict,
    ):

        return None

    rt3 = harai_data.get(
        "RT3HaraiGakuDispItemSubData"
    )

    if not isinstance(
        rt3,
        list,
    ):

        return None

    for item in rt3:

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
            "【全返還】",
        ):

            continue

        return {

            "combination":
                combination,

            "payout":
                payout,

            "popularity":
                item.get(
                    "ninki"
                ),

        }

    return None


# ===========================================================
# 通信取得失敗判定
# ===========================================================

def has_fetch_error(race):

    problems = race.get(
        "problems",
        [],
    )

    fetch_error_types = {

        "JSJ006_FETCH_ERROR",

        "JSJ012_FETCH_ERROR",

    }

    for problem in problems:

        if problem.get(
            "problem"
        ) in fetch_error_types:

            return True

    return False


# ===========================================================
# 1レース分類
# ===========================================================

def classify_race(race):

    jsj006 = race.get(
        "jsj006"
    )

    jsj012 = race.get(
        "jsj012"
    )

    players = get_players(
        jsj006
    )

    results = get_results(
        jsj012
    )

    harai_data = get_harai_data(
        jsj012
    )

    trifecta = get_trifecta(
        harai_data
    )

    all_refund = is_all_refund(
        harai_data
    )

    fetch_error = has_fetch_error(
        race
    )

    reasons = []

    # -------------------------------------------------------
    # FETCH_ERROR
    # -------------------------------------------------------

    if fetch_error:

        status = "FETCH_ERROR"

        reasons.append(
            "RAW_FETCH_ERROR"
        )

    # -------------------------------------------------------
    # ALL_REFUND
    # -------------------------------------------------------

    elif all_refund:

        status = "ALL_REFUND"

        reasons.append(
            "HARAI_ALL_REFUND"
        )

    # -------------------------------------------------------
    # NORMAL
    # -------------------------------------------------------

    elif (
        isinstance(
            jsj006,
            dict,
        )
        and isinstance(
            jsj012,
            dict,
        )
        and len(players) > 0
        and len(results) > 0
        and len(players)
        == len(results)
        and trifecta is not None
    ):

        status = "NORMAL"

        reasons.append(
            "NORMAL_COMPLETE"
        )

    # -------------------------------------------------------
    # INVALID_RAW
    # -------------------------------------------------------

    else:

        status = "INVALID_RAW"

        if not isinstance(
            jsj006,
            dict,
        ):

            reasons.append(
                "JSJ006_MISSING"
            )

        if not isinstance(
            jsj012,
            dict,
        ):

            reasons.append(
                "JSJ012_MISSING"
            )

        if len(players) == 0:

            reasons.append(
                "PLAYER_STRUCTURE_MISSING"
            )

        if len(results) == 0:

            reasons.append(
                "RESULT_STRUCTURE_MISSING"
            )

        if (
            len(players) > 0
            and len(results) > 0
            and len(players)
            != len(results)
        ):

            reasons.append(
                "PLAYER_RESULT_COUNT_MISMATCH"
            )

        if trifecta is None:

            reasons.append(
                "TRIFECTA_MISSING"
            )

    return {

        "status":
            status,

        "reasons":
            reasons,

        "player_count":
            len(
                players
            ),

        "result_count":
            len(
                results
            ),

        "has_trifecta":
            trifecta is not None,

        "all_refund":
            all_refund,

        "trifecta":
            trifecta,

    }


# ===========================================================
# main
# ===========================================================

def main():

    print(
        "=== 006 全過去RAW 正式状態分類 ==="
    )

    collection_validation = load_json(
        COLLECTION_VALIDATION_FILE
    )

    target_dates = (
        collection_validation.get(
            "completed_dates",
            []
        )
        +
        collection_validation.get(
            "failed_dates",
            []
        )
    )

    target_dates = sorted(
        set(
            target_dates
        )
    )

    print(
        "対象日数:",
        len(
            target_dates
        ),
    )

    classified_races = []

    status_counter = Counter()

    reason_counter = Counter()

    race_key_counter = Counter()

    player_count_counter = Counter()

    invalid_races = []

    fetch_error_races = []

    learning_target_count = 0

    for date_index, kday in enumerate(
        target_dates,
        1,
    ):

        print(

            f"[日付 "
            f"{date_index}/"
            f"{len(target_dates)}] "
            f"{kday}"

        )

        daily_path = (

            DAILY_RAW_DIR
            / f"{kday}_raw.json"

        )

        daily_data = load_json(
            daily_path
        )

        for race in daily_data.get(
            "races",
            [],
        ):

            race_key = race.get(
                "race_key"
            )

            classification = (
                classify_race(
                    race
                )
            )

            status = classification[
                "status"
            ]

            item = {

                "race_key":
                    race_key,

                "race_date":
                    race.get(
                        "race_date"
                    ),

                "venue":
                    race.get(
                        "venue"
                    ),

                "race_no":
                    race.get(
                        "race_no"
                    ),

                **classification,

            }

            classified_races.append(
                item
            )

            status_counter[
                status
            ] += 1

            race_key_counter[
                race_key
            ] += 1

            player_count_counter[
                classification[
                    "player_count"
                ]
            ] += 1

            for reason in classification[
                "reasons"
            ]:

                reason_counter[
                    reason
                ] += 1

            if status == "NORMAL":

                learning_target_count += 1

            elif status == "INVALID_RAW":

                invalid_races.append(
                    item
                )

            elif status == "FETCH_ERROR":

                fetch_error_races.append(
                    item
                )

    duplicate_race_keys = {

        race_key: count

        for race_key, count
        in race_key_counter.items()

        if count > 1

    }

    output = {

        "race_count":
            len(
                classified_races
            ),

        "learning_target_count":
            learning_target_count,

        "status_distribution":
            dict(
                status_counter
            ),

        "reason_distribution":
            dict(
                reason_counter
            ),

        "races":
            classified_races,

    }

    validation = {

        "target_date_count":
            len(
                target_dates
            ),

        "race_count":
            len(
                classified_races
            ),

        "unique_race_key_count":
            len(
                race_key_counter
            ),

        "duplicate_race_keys":
            duplicate_race_keys,

        "status_distribution":
            dict(
                status_counter
            ),

        "reason_distribution":
            dict(
                reason_counter
            ),

        "player_count_distribution":
            dict(
                player_count_counter
            ),

        "learning_target_count":
            learning_target_count,

        "invalid_race_count":
            len(
                invalid_races
            ),

        "fetch_error_race_count":
            len(
                fetch_error_races
            ),

        "invalid_races":
            invalid_races,

        "fetch_error_races":
            fetch_error_races,

    }

    save_json(
        OUT_FILE,
        output,
    )

    save_json(
        VALIDATION_FILE,
        validation,
    )

    print()
    print(
        "=== 006 結果 ==="
    )

    print(
        "対象日数:",
        len(
            target_dates
        ),
    )

    print(
        "総レース数:",
        len(
            classified_races
        ),
    )

    print(
        "一意race_key数:",
        len(
            race_key_counter
        ),
    )

    print(
        "race_key重複:",
        duplicate_race_keys,
    )

    print(
        "状態分布:",
        dict(
            status_counter
        ),
    )

    print(
        "理由分布:",
        dict(
            reason_counter
        ),
    )

    print(
        "車立て分布:",
        dict(
            player_count_counter
        ),
    )

    print(
        "学習対象NORMAL:",
        learning_target_count,
    )

    print(
        "INVALID_RAW:",
        len(
            invalid_races
        ),
    )

    print(
        "FETCH_ERROR:",
        len(
            fetch_error_races
        ),
    )

    if invalid_races:

        print()
        print(
            "=== INVALID_RAW一覧 ==="
        )

        for race in invalid_races[
            :100
        ]:

            print(
                race[
                    "race_key"
                ],
                race[
                    "reasons"
                ],
            )

    if fetch_error_races:

        print()
        print(
            "=== FETCH_ERROR一覧 ==="
        )

        for race in fetch_error_races[
            :100
        ]:

            print(
                race[
                    "race_key"
                ],
                race[
                    "reasons"
                ],
            )

    print()
    print(
        "分類Dataset保存:"
    )

    print(
        OUT_FILE
    )

    print()
    print(
        "検証レポート保存:"
    )

    print(
        VALIDATION_FILE
    )

    print()
    print(
        "=== 006 完了 ==="
    )


if __name__ == "__main__":

    main()