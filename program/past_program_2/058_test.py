import json
from pathlib import Path
from datetime import datetime
from collections import Counter


# ============================================================
# 058
#
# AI学習用統合データ 最終監査
#
# 対象:
# 057_merged_training_dataset.json
#
# 確認:
# ・選手車番
# ・選手能力欠損
# ・ライン車番
# ・競り車番
# ・結果車番
# ・3連単組番
# ・各データ間の車番整合性
# ============================================================


BASE = Path(r"C:\競輪AI")


SRC_FILE = (
    BASE
    / "data_ai"
    / "training_dataset"
    / "057_merged_training_dataset"
    / "057_merged_training_dataset.json"
)


OUT_DIR = (
    BASE
    / "data_ai"
    / "training_audit"
    / "058_training_dataset_audit"
)


OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


OUT_FILE = (
    OUT_DIR
    / "058_training_dataset_audit.json"
)


print(
    "=== 058 AI学習用統合データ 最終監査 ==="
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
            .replace("(", "")
            .replace(")", "")
            .strip()
        )

        return int(
            float(text)
        )

    except Exception:

        return None


# ============================================================
# 平坦化
# ============================================================


def flatten_numbers(value):

    numbers = []

    if isinstance(
        value,
        list,
    ):

        for item in value:

            numbers.extend(
                flatten_numbers(
                    item
                )
            )

    elif isinstance(
        value,
        dict,
    ):

        car_numbers = value.get(
            "car_numbers"
        )

        if car_numbers is not None:

            numbers.extend(
                flatten_numbers(
                    car_numbers
                )
            )

        reconstructed_lines = value.get(
            "reconstructed_lines"
        )

        if reconstructed_lines is not None:

            numbers.extend(
                flatten_numbers(
                    reconstructed_lines
                )
            )

    else:

        number = to_int(
            value
        )

        if number is not None:

            numbers.append(
                number
            )

    return numbers


# ============================================================
# 3連単組番
# ============================================================


def parse_trifecta_combination(value):

    if value in (
        None,
        "",
    ):

        return []

    text = str(
        value
    )

    for separator in [
        "－",
        "ー",
        "―",
        "→",
        ">",
        "/",
    ]:

        text = text.replace(
            separator,
            "-",
        )

    parts = text.split(
        "-"
    )

    result = []

    for part in parts:

        number = to_int(
            part
        )

        if number is not None:

            result.append(
                number
            )

    return result


# ============================================================
# 能力項目
# ============================================================


ABILITY_FIELDS = [
    "average_score",
    "win_rate",
    "quinella_rate",
    "trio_rate",
    "nige_count",
    "makuri_count",
    "sashi_count",
    "mark_count",
    "back_count",
    "class",
    "previous_class",
]


# ============================================================
# MAIN
# ============================================================


def main():

    print()

    print(
        "SOURCE:"
    )

    print(
        SRC_FILE
    )

    print()


    raw = load_json(
        SRC_FILE
    )


    races = raw.get(
        "races"
    ) or []


    audit_results = []

    status_counter = Counter()

    issue_counter = Counter()

    warning_counter = Counter()

    missing_field_counter = Counter()


    for race in races:

        race_key = race.get(
            "race_key"
        )


        pre_race = race.get(
            "pre_race"
        ) or {}


        riders = pre_race.get(
            "riders"
        ) or []


        line = pre_race.get(
            "line"
        ) or {}


        result = race.get(
            "result"
        ) or {}


        label = race.get(
            "label"
        ) or {}


        issues = []

        warnings = []


        # ====================================================
        # 選手
        # ====================================================


        rider_car_numbers = []


        for rider in riders:

            car_no = to_int(
                rider.get(
                    "car_no"
                )
            )

            if car_no is not None:

                rider_car_numbers.append(
                    car_no
                )


        rider_car_set = set(
            rider_car_numbers
        )


        if len(
            rider_car_numbers
        ) != len(
            rider_car_set
        ):

            issues.append(
                "DUPLICATE_RIDER_CAR_NUMBER"
            )


        if len(
            rider_car_numbers
        ) not in (
            5,
            6,
            7,
            8,
            9,
        ):

            issues.append(
                "UNEXPECTED_RIDER_COUNT"
            )


        expected_car_set = set(
            range(
                1,
                len(rider_car_numbers) + 1,
            )
        )


        if rider_car_set != expected_car_set:

            issues.append(
                "RIDER_CAR_SEQUENCE_MISMATCH"
            )


        # ====================================================
        # 能力欠損
        # ====================================================


        rider_missing = {}


        for rider in riders:

            car_no = rider.get(
                "car_no"
            )

            missing = []


            for field in ABILITY_FIELDS:

                value = rider.get(
                    field
                )

                if value in (
                    None,
                    "",
                ):

                    missing.append(
                        field
                    )

                    missing_field_counter[
                        field
                    ] += 1


            if missing:

                rider_missing[
                    str(car_no)
                ] = missing


        if rider_missing:

            warnings.append(
                "ABILITY_FIELD_MISSING"
            )


        # ====================================================
        # ライン
        # ====================================================


        main_lines = line.get(
            "main_lines"
        ) or []


        main_line_cars = flatten_numbers(
            main_lines
        )


        main_line_counter = Counter(
            main_line_cars
        )


        main_line_duplicate_cars = sorted(
            [
                car_no
                for car_no, count
                in main_line_counter.items()
                if count > 1
            ]
        )


        if main_line_duplicate_cars:

            issues.append(
                "DUPLICATE_MAIN_LINE_CAR"
            )


        main_line_car_set = set(
            main_line_cars
        )


        competition_rows = line.get(
            "competition_rows"
        ) or []


        competition_cars = []


        for row in competition_rows:

            if isinstance(
                row,
                dict,
            ):

                row_cars = row.get(
                    "car_numbers"
                )

                if row_cars is not None:

                    competition_cars.extend(
                        flatten_numbers(
                            row_cars
                        )
                    )

                else:

                    competition_cars.extend(
                        flatten_numbers(
                            row
                        )
                    )

            else:

                competition_cars.extend(
                    flatten_numbers(
                        row
                    )
                )


        competition_car_set = set(
            competition_cars
        )


        all_line_car_set = (
            main_line_car_set
            | competition_car_set
        )


        unknown_main_line_cars = sorted(
            main_line_car_set
            - rider_car_set
        )


        if unknown_main_line_cars:

            issues.append(
                "MAIN_LINE_UNKNOWN_CAR"
            )


        unknown_competition_cars = sorted(
            competition_car_set
            - rider_car_set
        )


        if unknown_competition_cars:

            issues.append(
                "COMPETITION_UNKNOWN_CAR"
            )


        missing_from_line = sorted(
            rider_car_set
            - all_line_car_set
        )


        if missing_from_line:

            issues.append(
                "RIDER_MISSING_FROM_LINE"
            )


        # ====================================================
        # 結果
        # ====================================================


        first = to_int(
            result.get(
                "first"
            )
        )


        second = to_int(
            result.get(
                "second"
            )
        )


        third = to_int(
            result.get(
                "third"
            )
        )


        top3 = [
            first,
            second,
            third,
        ]


        if any(
            car_no is None
            for car_no in top3
        ):

            issues.append(
                "TOP3_NOT_COMPLETE"
            )


        valid_top3 = [
            car_no
            for car_no in top3
            if car_no is not None
        ]


        if len(
            valid_top3
        ) != len(
            set(valid_top3)
        ):

            issues.append(
                "TOP3_DUPLICATE_CAR"
            )


        result_unknown_cars = sorted(
            set(valid_top3)
            - rider_car_set
        )


        if result_unknown_cars:

            issues.append(
                "RESULT_UNKNOWN_CAR"
            )


        # ====================================================
        # 3連単
        # ====================================================


        trifecta_combination = result.get(
            "trifecta_combination"
        )


        trifecta_numbers = (
            parse_trifecta_combination(
                trifecta_combination
            )
        )


        if len(
            trifecta_numbers
        ) != 3:

            issues.append(
                "TRIFECTA_COMBINATION_PARSE_ERROR"
            )


        elif trifecta_numbers != top3:

            issues.append(
                "TRIFECTA_TOP3_MISMATCH"
            )


        payout = to_int(
            result.get(
                "trifecta_payout"
            )
        )


        if payout is None:

            issues.append(
                "TRIFECTA_PAYOUT_MISSING"
            )


        elif payout <= 0:

            issues.append(
                "TRIFECTA_PAYOUT_INVALID"
            )


        # ====================================================
        # ラベル再計算
        # ====================================================


        stored_label = label.get(
            "payout_class"
        )


        recalculated_label = None


        if payout is not None:

            if payout >= 50000:

                recalculated_label = (
                    "50000_PLUS"
                )

            elif payout >= 20000:

                recalculated_label = (
                    "20000_49999"
                )

            elif payout >= 10000:

                recalculated_label = (
                    "10000_19999"
                )

            else:

                recalculated_label = (
                    "UNDER_10000"
                )


        if (
            stored_label
            != recalculated_label
        ):

            issues.append(
                "LABEL_MISMATCH"
            )


        # ====================================================
        # STATUS
        # ====================================================


        issues = list(
            dict.fromkeys(
                issues
            )
        )


        warnings = list(
            dict.fromkeys(
                warnings
            )
        )


        if issues:

            status = "ISSUE"

        elif warnings:

            status = "WARNING"

        else:

            status = "OK"


        status_counter[
            status
        ] += 1


        for issue in issues:

            issue_counter[
                issue
            ] += 1


        for warning in warnings:

            warning_counter[
                warning
            ] += 1


        audit_item = {
            "race_key": race_key,
            "status": status,
            "issues": issues,
            "warnings": warnings,

            "rider_count": len(
                riders
            ),

            "rider_car_numbers": sorted(
                rider_car_numbers
            ),

            "rider_missing_fields": (
                rider_missing
            ),

            "prediction_type": line.get(
                "prediction_type"
            ),

            "provider": line.get(
                "provider"
            ),

            "main_lines": main_lines,

            "main_line_cars": sorted(
                main_line_car_set
            ),

            "main_line_duplicate_cars": (
                main_line_duplicate_cars
            ),

            "competition_cars": sorted(
                competition_car_set
            ),

            "missing_from_line": (
                missing_from_line
            ),

            "unknown_main_line_cars": (
                unknown_main_line_cars
            ),

            "unknown_competition_cars": (
                unknown_competition_cars
            ),

            "top3": top3,

            "trifecta_combination": (
                trifecta_combination
            ),

            "trifecta_numbers": (
                trifecta_numbers
            ),

            "payout": payout,

            "stored_label": stored_label,

            "recalculated_label": (
                recalculated_label
            ),
        }


        audit_results.append(
            audit_item
        )


    # ========================================================
    # SAVE
    # ========================================================


    output = {
        "program": "058_test.py",
        "created_at": datetime.now().isoformat(),
        "source_file": str(
            SRC_FILE
        ),
        "race_count": len(
            races
        ),
        "status_summary": dict(
            status_counter
        ),
        "issue_summary": dict(
            issue_counter
        ),
        "warning_summary": dict(
            warning_counter
        ),
        "missing_ability_field_summary": dict(
            missing_field_counter
        ),
        "races": audit_results,
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
        "058 最終結果"
    )

    print(
        "#"
        * 100
    )

    print()

    print(
        "RACE COUNT:",
        len(races)
    )

    print(
        "OK:",
        status_counter[
            "OK"
        ]
    )

    print(
        "WARNING:",
        status_counter[
            "WARNING"
        ]
    )

    print(
        "ISSUE:",
        status_counter[
            "ISSUE"
        ]
    )


    print()

    print(
        "★ ISSUE SUMMARY ★"
    )


    if not issue_counter:

        print(
            "なし"
        )

    else:

        for key, count in (
            issue_counter.most_common()
        ):

            print(
                key,
                ":",
                count,
            )


    print()

    print(
        "★ WARNING SUMMARY ★"
    )


    if not warning_counter:

        print(
            "なし"
        )

    else:

        for key, count in (
            warning_counter.most_common()
        ):

            print(
                key,
                ":",
                count,
            )


    print()

    print(
        "★ 能力データ欠損項目 ★"
    )


    if not missing_field_counter:

        print(
            "なし"
        )

    else:

        for key, count in (
            missing_field_counter.most_common()
        ):

            print(
                key,
                ":",
                count,
            )


    print()

    print(
        "★ ISSUE RACE ★"
    )


    issue_races = [
        race
        for race in audit_results
        if race[
            "status"
        ] == "ISSUE"
    ]


    if not issue_races:

        print(
            "なし"
        )


    for race in issue_races:

        print()

        print(
            "-"
            * 100
        )

        print(
            "RACE:",
            race[
                "race_key"
            ]
        )

        print(
            "ISSUES:",
            race[
                "issues"
            ]
        )

        print(
            "RIDERS:",
            race[
                "rider_car_numbers"
            ]
        )

        print(
            "MAIN LINES:",
            race[
                "main_lines"
            ]
        )

        print(
            "COMPETITION:",
            race[
                "competition_cars"
            ]
        )

        print(
            "MISSING FROM LINE:",
            race[
                "missing_from_line"
            ]
        )

        print(
            "TOP3:",
            race[
                "top3"
            ]
        )

        print(
            "3連単:",
            race[
                "trifecta_numbers"
            ]
        )


    print()

    print(
        "★ WARNING RACE ★"
    )


    warning_races = [
        race
        for race in audit_results
        if race[
            "status"
        ] == "WARNING"
    ]


    if not warning_races:

        print(
            "なし"
        )


    for race in warning_races[:50]:

        print()

        print(
            "-"
            * 100
        )

        print(
            "RACE:",
            race[
                "race_key"
            ]
        )

        print(
            "WARNINGS:",
            race[
                "warnings"
            ]
        )

        print(
            "MISSING FIELDS:",
            race[
                "rider_missing_fields"
            ]
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
        "=== 058 完了 ==="
    )


if __name__ == "__main__":

    main()