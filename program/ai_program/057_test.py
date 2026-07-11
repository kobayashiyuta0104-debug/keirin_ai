import json
from pathlib import Path
from datetime import datetime
from collections import Counter


# ============================================================
# 057
#
# 選手能力 + ライン + 確定結果
# race_key 統合
#
# 入力:
# 046 JSJ006能力データ
# 043 ラインデータ
# 056 JSJ012確定結果
#
# 出力:
# AI学習用統合JSON
# ============================================================


BASE = Path(r"C:\競輪AI")


ABILITY_FILE = (
    BASE
    / "data_official"
    / "pre_race"
    / "046_jsj006_by_race_key"
    / "046_jsj006_by_race_key.json"
)


LINE_FILE = (
    BASE
    / "data_official"
    / "line_predictions"
    / "043_all_venues_official_lines.json"
)


RESULT_FILE = (
    BASE
    / "data_official"
    / "confirmed_results"
    / "056_jsj012_confirmed_results"
    / "056_jsj012_confirmed_results.json"
)


OUT_DIR = (
    BASE
    / "data_ai"
    / "training_dataset"
    / "057_merged_training_dataset"
)


OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


OUT_FILE = (
    OUT_DIR
    / "057_merged_training_dataset.json"
)


print(
    "=== 057 選手能力 + ライン + 確定結果 "
    "AI学習データ統合 ==="
)


# ============================================================
# JSON
# ============================================================


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


# ============================================================
# 数値変換
# ============================================================


def to_int(value):

    if value in (
        None,
        "",
    ):

        return None

    try:

        text = (
            str(value)
            .replace(",", "")
            .replace("円", "")
            .replace("%", "")
            .replace("(", "")
            .replace(")", "")
            .strip()
        )

        return int(
            float(text)
        )

    except Exception:

        return None


def to_float(value):

    if value in (
        None,
        "",
    ):

        return None

    try:

        text = (
            str(value)
            .replace(",", "")
            .replace("%", "")
            .strip()
        )

        return float(text)

    except Exception:

        return None


# ============================================================
# 再帰探索
# ============================================================


def walk(value):

    yield value

    if isinstance(value, dict):

        for child in value.values():

            yield from walk(child)

    elif isinstance(value, list):

        for child in value:

            yield from walk(child)


# ============================================================
# race_key を持つ辞書を全部探す
# ============================================================


def collect_race_objects(data):

    result = {}

    for obj in walk(data):

        if not isinstance(
            obj,
            dict,
        ):

            continue

        race_key = obj.get(
            "race_key"
        )

        if not race_key:

            continue

        race_key = str(
            race_key
        ).strip()

        if "_20" in race_key:

            continue

        if not race_key.startswith(
            "20260710_"
        ):

            continue

        current = result.get(
            race_key
        )

        if current is None:

            result[
                race_key
            ] = obj

            continue

        # 情報量が多い方を残す

        try:

            current_size = len(
                json.dumps(
                    current,
                    ensure_ascii=False,
                )
            )

            new_size = len(
                json.dumps(
                    obj,
                    ensure_ascii=False,
                )
            )

            if new_size > current_size:

                result[
                    race_key
                ] = obj

        except Exception:

            pass

    return result


# ============================================================
# JSJ006探索
# ============================================================


ABILITY_KEYS = {
    "sensyuName",
    "heikinTokuten",
    "syouritu",
    "rentairitu2",
    "rentairitu3",
    "nigeCnt",
    "makuriCnt",
    "sasiCnt",
    "markCnt",
    "backCnt",
    "kyuhan",
    "prevKyuhan",
}


def ability_score(obj):

    if not isinstance(
        obj,
        dict,
    ):

        return 0

    score = 0

    for value in walk(obj):

        if not isinstance(
            value,
            dict,
        ):

            continue

        keys = set(
            value.keys()
        )

        score += len(
            keys & ABILITY_KEYS
        )

    return score


def find_best_ability_object(race_obj):

    candidates = []

    for obj in walk(race_obj):

        if not isinstance(
            obj,
            dict,
        ):

            continue

        score = ability_score(
            obj
        )

        if score > 0:

            candidates.append(
                (
                    score,
                    obj,
                )
            )

    if not candidates:

        return None

    candidates.sort(
        key=lambda x: x[0],
        reverse=True,
    )

    return candidates[0][1]


# ============================================================
# 選手能力行探索
# ============================================================


def find_rider_rows(ability_obj):

    candidates = []

    for value in walk(
        ability_obj
    ):

        if not isinstance(
            value,
            list,
        ):

            continue

        dict_rows = [
            row
            for row in value
            if isinstance(
                row,
                dict,
            )
        ]

        if not dict_rows:

            continue

        score = 0

        for row in dict_rows:

            keys = set(
                row.keys()
            )

            score += len(
                keys
                & ABILITY_KEYS
            )

        if score > 0:

            candidates.append(
                (
                    score,
                    dict_rows,
                )
            )

    if not candidates:

        return []

    candidates.sort(
        key=lambda x: x[0],
        reverse=True,
    )

    return candidates[0][1]


# ============================================================
# 車番
# ============================================================


CAR_NUMBER_KEYS = [
    "syaban",
    "carNum",
    "car_no",
    "syabanNo",
]


def get_car_no(row):

    for key in CAR_NUMBER_KEYS:

        value = row.get(key)

        number = to_int(value)

        if number is not None:

            if 1 <= number <= 9:

                return number

    return None


# ============================================================
# 選手ID
# ============================================================


PLAYER_ID_KEYS = [
    "sensyuRegistNo",
    "sensyuTourokuNo",
    "sensyuId",
    "player_id",
]


def get_player_id(row):

    for key in PLAYER_ID_KEYS:

        value = row.get(key)

        if value not in (
            None,
            "",
        ):

            return str(value)

    return None


# ============================================================
# 選手能力整形
# ============================================================


def parse_riders(race_obj):

    ability_obj = (
        find_best_ability_object(
            race_obj
        )
    )

    if ability_obj is None:

        return []

    rows = find_rider_rows(
        ability_obj
    )

    riders = []

    used_car_numbers = set()

    for row in rows:

        car_no = get_car_no(
            row
        )

        if car_no is None:

            continue

        if car_no in used_car_numbers:

            continue

        used_car_numbers.add(
            car_no
        )

        rider = {
            "car_no": car_no,
            "player_id": get_player_id(
                row
            ),
            "name": row.get(
                "sensyuName"
            ),
            "average_score": to_float(
                row.get(
                    "heikinTokuten"
                )
            ),
            "win_rate": to_float(
                row.get(
                    "syouritu"
                )
            ),
            "quinella_rate": to_float(
                row.get(
                    "rentairitu2"
                )
            ),
            "trio_rate": to_float(
                row.get(
                    "rentairitu3"
                )
            ),
            "nige_count": to_int(
                row.get(
                    "nigeCnt"
                )
            ),
            "makuri_count": to_int(
                row.get(
                    "makuriCnt"
                )
            ),
            "sashi_count": to_int(
                row.get(
                    "sasiCnt"
                )
            ),
            "mark_count": to_int(
                row.get(
                    "markCnt"
                )
            ),
            "back_count": to_int(
                row.get(
                    "backCnt"
                )
            ),
            "class": row.get(
                "kyuhan"
            ),
            "previous_class": row.get(
                "prevKyuhan"
            ),
        }

        riders.append(
            rider
        )

    riders.sort(
        key=lambda x: x[
            "car_no"
        ]
    )

    return riders


# ============================================================
# ライン探索
# ============================================================


def find_line_data(race_obj):

    best = None

    best_score = -1

    for obj in walk(
        race_obj
    ):

        if not isinstance(
            obj,
            dict,
        ):

            continue

        score = 0

        if "main_lines" in obj:

            score += 10

        if "prediction_type" in obj:

            score += 3

        if "provider" in obj:

            score += 2

        if "competition_rows" in obj:

            score += 2

        if score > best_score:

            best_score = score
            best = obj

    if best_score < 10:

        return None

    return {
        "prediction_type": best.get(
            "prediction_type"
        ),
        "provider": best.get(
            "provider"
        ),
        "main_lines": best.get(
            "main_lines"
        ) or [],
        "competition_rows": best.get(
            "competition_rows"
        ) or [],
    }


# ============================================================
# 結果整形
#
# tyakujyunItemSubData は着順順
# 056で finish_rank が None でも
# 配列順から 1着・2着・3着を確定
# ============================================================


def parse_result(race_obj):

    if race_obj.get(
        "status"
    ) != "CONFIRMED_RESULT_FOUND":

        return None

    results = race_obj.get(
        "results"
    ) or []

    ordered_cars = []

    for row in results:

        if not isinstance(
            row,
            dict,
        ):

            continue

        car_no = to_int(
            row.get(
                "car_no"
            )
        )

        if car_no is not None:

            ordered_cars.append(
                car_no
            )

    trifecta = race_obj.get(
        "trifecta"
    ) or {}

    combination = trifecta.get(
        "combination"
    )

    payout = to_int(
        trifecta.get(
            "payout"
        )
    )

    popularity = to_int(
        trifecta.get(
            "popularity"
        )
    )

    first = (
        ordered_cars[0]
        if len(ordered_cars) >= 1
        else None
    )

    second = (
        ordered_cars[1]
        if len(ordered_cars) >= 2
        else None
    )

    third = (
        ordered_cars[2]
        if len(ordered_cars) >= 3
        else None
    )

    return {
        "first": first,
        "second": second,
        "third": third,
        "finish_order": ordered_cars,
        "trifecta_combination": combination,
        "trifecta_payout": payout,
        "trifecta_popularity": popularity,
    }


# ============================================================
# ラベル
# ============================================================


def make_label(payout):

    if payout is None:

        return None

    if payout >= 50000:

        payout_class = "50000_PLUS"

    elif payout >= 20000:

        payout_class = "20000_49999"

    elif payout >= 10000:

        payout_class = "10000_19999"

    else:

        payout_class = "UNDER_10000"

    return {
        "payout_20000_plus": (
            1
            if payout >= 20000
            else 0
        ),
        "payout_50000_plus": (
            1
            if payout >= 50000
            else 0
        ),
        "payout_class": payout_class,
    }


# ============================================================
# MAIN
# ============================================================


def main():

    print()

    print(
        "ABILITY FILE:"
    )

    print(
        ABILITY_FILE
    )

    print()

    print(
        "LINE FILE:"
    )

    print(
        LINE_FILE
    )

    print()

    print(
        "RESULT FILE:"
    )

    print(
        RESULT_FILE
    )

    print()


    ability_raw = load_json(
        ABILITY_FILE
    )

    line_raw = load_json(
        LINE_FILE
    )

    result_raw = load_json(
        RESULT_FILE
    )


    ability_map = collect_race_objects(
        ability_raw
    )

    line_map = collect_race_objects(
        line_raw
    )

    result_map = collect_race_objects(
        result_raw
    )


    print(
        "ABILITY RACE KEYS:",
        len(ability_map)
    )

    print(
        "LINE RACE KEYS:",
        len(line_map)
    )

    print(
        "RESULT RACE KEYS:",
        len(result_map)
    )


    all_race_keys = sorted(
        set(ability_map)
        | set(line_map)
        | set(result_map)
    )


    status_counter = Counter()

    label_counter = Counter()

    training_races = []

    audit_races = []


    for race_key in all_race_keys:

        ability_obj = ability_map.get(
            race_key
        )

        line_obj = line_map.get(
            race_key
        )

        result_obj = result_map.get(
            race_key
        )


        riders = (
            parse_riders(
                ability_obj
            )
            if ability_obj
            else []
        )


        line_data = (
            find_line_data(
                line_obj
            )
            if line_obj
            else None
        )


        result_data = (
            parse_result(
                result_obj
            )
            if result_obj
            else None
        )


        reasons = []


        if not riders:

            reasons.append(
                "ABILITY_NOT_FOUND"
            )


        if line_data is None:

            reasons.append(
                "LINE_NOT_FOUND"
            )

        else:

            main_lines = line_data.get(
                "main_lines"
            ) or []

            prediction_type = (
                line_data.get(
                    "prediction_type"
                )
            )

            if not main_lines:

                reasons.append(
                    "MAIN_LINES_EMPTY"
                )

            # ガールズ等
            if (
                prediction_type is None
                and len(main_lines) >= 6
            ):

                reasons.append(
                    "NON_LINE_RACE_EXCLUDED"
                )


        if result_data is None:

            reasons.append(
                "RESULT_NOT_CONFIRMED"
            )


        payout = (
            result_data.get(
                "trifecta_payout"
            )
            if result_data
            else None
        )


        if result_data and payout is None:

            reasons.append(
                "TRIFECTA_PAYOUT_NOT_FOUND"
            )


        label = make_label(
            payout
        )


        if reasons:

            merge_status = "EXCLUDED"

        else:

            merge_status = "READY_FOR_AI"


        status_counter[
            merge_status
        ] += 1


        audit_item = {
            "race_key": race_key,
            "merge_status": merge_status,
            "reasons": reasons,
            "rider_count": len(
                riders
            ),
            "line_found": (
                line_data is not None
            ),
            "result_found": (
                result_data is not None
            ),
            "payout": payout,
        }


        audit_races.append(
            audit_item
        )


        if merge_status != "READY_FOR_AI":

            continue


        race_parts = race_key.rsplit(
            "_",
            2,
        )


        race_date = race_parts[0]

        venue = race_parts[1]

        race_no_text = race_parts[2]

        race_no = to_int(
            race_no_text.replace(
                "R",
                "",
            )
        )


        training_item = {
            "race_key": race_key,
            "race_date": race_date,
            "venue": venue,
            "race_no": race_no,

            "pre_race": {
                "riders": riders,
                "line": line_data,
            },

            "result": result_data,

            "label": label,
        }


        training_races.append(
            training_item
        )


        label_counter[
            label["payout_class"]
        ] += 1


    # ========================================================
    # SAVE
    # ========================================================


    output = {
        "program": "057_test.py",
        "created_at": datetime.now().isoformat(),
        "purpose": (
            "ABILITY_LINE_CONFIRMED_RESULT_"
            "RACE_KEY_MERGE"
        ),
        "input_files": {
            "ability": str(
                ABILITY_FILE
            ),
            "line": str(
                LINE_FILE
            ),
            "result": str(
                RESULT_FILE
            ),
        },
        "ability_race_key_count": len(
            ability_map
        ),
        "line_race_key_count": len(
            line_map
        ),
        "result_race_key_count": len(
            result_map
        ),
        "all_race_key_count": len(
            all_race_keys
        ),
        "ready_for_ai_count": len(
            training_races
        ),
        "status_summary": dict(
            status_counter
        ),
        "label_summary": dict(
            label_counter
        ),
        "races": training_races,
        "audit": audit_races,
    }


    save_json(
        OUT_FILE,
        output,
    )


    # ========================================================
    # FINAL
    # ========================================================


    print()

    print(
        "#"
        * 100
    )

    print(
        "057 最終結果"
    )

    print(
        "#"
        * 100
    )

    print()

    print(
        "ABILITY RACE KEYS:",
        len(ability_map)
    )

    print(
        "LINE RACE KEYS:",
        len(line_map)
    )

    print(
        "RESULT RACE KEYS:",
        len(result_map)
    )

    print(
        "ALL RACE KEYS:",
        len(all_race_keys)
    )

    print(
        "READY FOR AI:",
        len(training_races)
    )


    print()

    print(
        "★ MERGE STATUS ★"
    )


    for key, count in (
        status_counter.most_common()
    ):

        print(
            key,
            ":",
            count,
        )


    print()

    print(
        "★ LABEL SUMMARY ★"
    )


    for key, count in (
        label_counter.most_common()
    ):

        print(
            key,
            ":",
            count,
        )


    print()

    print(
        "★ READY FOR AI SAMPLE TOP20 ★"
    )


    for race in training_races[:20]:

        print()

        print(
            "-"
            * 100
        )

        print(
            "RACE:",
            race["race_key"]
        )

        print(
            "RIDERS:",
            len(
                race[
                    "pre_race"
                ][
                    "riders"
                ]
            )
        )

        print(
            "TYPE:",
            race[
                "pre_race"
            ][
                "line"
            ][
                "prediction_type"
            ]
        )

        print(
            "LINES:",
            race[
                "pre_race"
            ][
                "line"
            ][
                "main_lines"
            ]
        )

        print(
            "RESULT:",
            (
                race["result"]["first"],
                race["result"]["second"],
                race["result"]["third"],
            )
        )

        print(
            "3連単:",
            race[
                "result"
            ][
                "trifecta_combination"
            ]
        )

        print(
            "払戻:",
            race[
                "result"
            ][
                "trifecta_payout"
            ]
        )

        print(
            "LABEL:",
            race[
                "label"
            ][
                "payout_class"
            ]
        )


    print()

    print(
        "★ EXCLUDED REASON SUMMARY ★"
    )


    reason_counter = Counter()

    for item in audit_races:

        for reason in item[
            "reasons"
        ]:

            reason_counter[
                reason
            ] += 1


    if not reason_counter:

        print(
            "なし"
        )


    for key, count in (
        reason_counter.most_common()
    ):

        print(
            key,
            ":",
            count,
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
        "=== 057 完了 ==="
    )


if __name__ == "__main__":

    main()