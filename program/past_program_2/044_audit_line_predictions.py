from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
import json


# ============================================================
# 044
#
# 043 ラインデータ全件自動監査
#
# サイトアクセスなし
#
# 入力:
# 043_all_venues_official_lines.json
#
# 監査:
# ・LINE_FOUND全件
# ・車番重複
# ・車番欠落候補
# ・7車 / 9車構成
# ・想定外の車番
# ・空ライン
# ・ライン内重複
# ・競り段
# ・競り文字と競り段の不一致
# ・TYPE別復元パターン
# ・ライン数
# ・単騎数
#
# 注意:
# prediction_type とライン数は
# 一致必須とは判定しない
#
# ============================================================


BASE = Path(r"C:\競輪AI")

SRC = (
    BASE
    / "data_official"
    / "line_predictions"
    / "043_all_venues_official_lines.json"
)

OUT_DIR = (
    BASE
    / "data_official"
    / "line_research"
    / "044_line_audit"
)

OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUT_FILE = (
    OUT_DIR
    / "044_line_audit.json"
)


# ============================================================
# JSON読込
# ============================================================


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


# ============================================================
# JSON保存
# ============================================================


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
# 全レース平坦化
# ============================================================


def flatten_races(data):

    races = []

    for venue_data in data.get(
        "venues",
        []
    ):

        for race in venue_data.get(
            "races",
            []
        ):

            races.append(race)

    return races


# ============================================================
# ライン平坦化
# ============================================================


def flatten_main_lines(main_lines):

    riders = []

    for line in main_lines:

        if isinstance(
            line,
            list,
        ):

            riders.extend(line)

    return riders


# ============================================================
# 競り段平坦化
# ============================================================


def flatten_competition_rows(
    competition_rows,
):

    riders = []

    for row in competition_rows:

        if not isinstance(
            row,
            dict,
        ):

            continue

        car_numbers = row.get(
            "car_numbers",
            []
        )

        if isinstance(
            car_numbers,
            list,
        ):

            riders.extend(
                car_numbers
            )

    return riders


# ============================================================
# 1レース監査
# ============================================================


def audit_race(race):

    race_key = race.get(
        "race_key"
    )

    prediction_type = race.get(
        "prediction_type"
    )

    provider = race.get(
        "provider"
    )

    main_lines = race.get(
        "main_lines",
        []
    )

    competition_rows = race.get(
        "competition_rows",
        []
    )

    has_competition = (
        race.get(
            "has_competition"
        )
        is True
    )


    issues = []

    warnings = []


    # ========================================================
    # MAIN車番
    # ========================================================


    main_riders = (
        flatten_main_lines(
            main_lines
        )
    )


    competition_riders = (
        flatten_competition_rows(
            competition_rows
        )
    )


    all_riders = (
        main_riders
        +
        competition_riders
    )


    unique_riders = sorted(
        set(
            all_riders
        )
    )


    # ========================================================
    # ライン基本
    # ========================================================


    if not main_lines:

        issues.append(
            "MAIN_LINES_EMPTY"
        )


    empty_line_indexes = [

        index

        for index, line
        in enumerate(main_lines)

        if (
            not isinstance(
                line,
                list,
            )
            or
            len(line) == 0
        )

    ]


    if empty_line_indexes:

        issues.append(
            "EMPTY_MAIN_LINE"
        )


    # ========================================================
    # 車番型
    # ========================================================


    invalid_riders = [

        rider

        for rider in all_riders

        if (
            not isinstance(
                rider,
                int,
            )
            or
            rider < 1
            or
            rider > 9
        )

    ]


    if invalid_riders:

        issues.append(
            "INVALID_RIDER_NUMBER"
        )


    # ========================================================
    # 重複
    # ========================================================


    rider_counter = Counter(
        all_riders
    )


    duplicate_riders = sorted([

        rider

        for rider, count
        in rider_counter.items()

        if count > 1

    ])


    if duplicate_riders:

        issues.append(
            "DUPLICATE_RIDER"
        )


    # ========================================================
    # MAIN内ライン重複
    # ========================================================


    line_internal_duplicates = []


    for line_index, line in enumerate(
        main_lines
    ):

        if not isinstance(
            line,
            list,
        ):

            continue


        counts = Counter(
            line
        )


        duplicates = sorted([

            rider

            for rider, count
            in counts.items()

            if count > 1

        ])


        if duplicates:

            line_internal_duplicates.append({

                "line_index":
                    line_index,

                "duplicate_riders":
                    duplicates,

            })


    if line_internal_duplicates:

        issues.append(
            "LINE_INTERNAL_DUPLICATE"
        )


    # ========================================================
    # 車立て推定
    #
    # 現在の取得対象では
    # 主に7車 / 9車
    #
    # それ以外は即エラーではなくWARNING
    # ========================================================


    rider_count = len(
        unique_riders
    )


    if rider_count in {
        7,
        9,
    }:

        estimated_field_size = (
            rider_count
        )

    else:

        estimated_field_size = None

        warnings.append(
            "UNUSUAL_RIDER_COUNT"
        )


    # ========================================================
    # 1〜N欠落確認
    # ========================================================


    missing_riders = []


    if estimated_field_size:

        expected_riders = set(
            range(
                1,
                estimated_field_size + 1,
            )
        )


        missing_riders = sorted(

            expected_riders
            -
            set(
                unique_riders
            )

        )


        if missing_riders:

            issues.append(
                "MISSING_RIDER"
            )


    # ========================================================
    # 競り構造
    # ========================================================


    competition_row_count = len(
        competition_rows
    )


    if (
        has_competition
        and
        competition_row_count == 0
    ):

        warnings.append(
            "COMPETITION_FLAG_WITHOUT_EXTRA_ROW"
        )


    if (
        not has_competition
        and
        competition_row_count > 0
    ):

        issues.append(
            "EXTRA_ROW_WITHOUT_COMPETITION_FLAG"
        )


    if (
        competition_row_count > 0
        and
        len(
            competition_riders
        )
        == 0
    ):

        issues.append(
            "EMPTY_COMPETITION_ROW"
        )


    # ========================================================
    # ライン数・単騎
    # ========================================================


    line_count = len(
        main_lines
    )


    solo_lines = [

        line

        for line in main_lines

        if (
            isinstance(
                line,
                list,
            )
            and
            len(line) == 1
        )

    ]


    solo_riders = [

        line[0]

        for line in solo_lines

    ]


    line_lengths = [

        len(line)

        if isinstance(
            line,
            list,
        )

        else None

        for line in main_lines

    ]


    # ========================================================
    # TYPEは保存・集計だけ
    #
    # ライン数との一致判定はしない
    # ========================================================


    if prediction_type is None:

        warnings.append(
            "PREDICTION_TYPE_NONE"
        )


    if provider is None:

        warnings.append(
            "PROVIDER_NONE"
        )


    # ========================================================
    # 監査結果
    # ========================================================


    audit_status = (
        "ISSUE"
        if issues
        else
        "WARNING"
        if warnings
        else
        "OK"
    )


    return {

        "race_key":
            race_key,

        "venue":
            race.get(
                "venue"
            ),

        "race_no":
            race.get(
                "race_no"
            ),

        "prediction_type":
            prediction_type,

        "provider":
            provider,

        "audit_status":
            audit_status,

        "issues":
            issues,

        "warnings":
            warnings,

        "main_lines":
            main_lines,

        "has_competition":
            has_competition,

        "competition_rows":
            competition_rows,

        "main_riders":
            main_riders,

        "competition_riders":
            competition_riders,

        "all_riders":
            all_riders,

        "unique_riders":
            unique_riders,

        "rider_count":
            rider_count,

        "estimated_field_size":
            estimated_field_size,

        "missing_riders":
            missing_riders,

        "duplicate_riders":
            duplicate_riders,

        "invalid_riders":
            invalid_riders,

        "empty_line_indexes":
            empty_line_indexes,

        "line_internal_duplicates":
            line_internal_duplicates,

        "line_count":
            line_count,

        "line_lengths":
            line_lengths,

        "solo_count":
            len(
                solo_lines
            ),

        "solo_riders":
            solo_riders,

        "competition_row_count":
            competition_row_count,

    }


# ============================================================
# MAIN
# ============================================================


def main():

    print()

    print(
        "="
        * 100
    )

    print(
        "044 043ラインデータ 全件自動監査"
    )

    print(
        "="
        * 100
    )

    print()


    # ========================================================
    # 入力確認
    # ========================================================


    print(
        "INPUT:"
    )

    print(
        SRC
    )

    print()


    if not SRC.exists():

        print(
            "ERROR: 043 JSONがありません"
        )

        return


    # ========================================================
    # 読込
    # ========================================================


    data = load_json(
        SRC
    )


    all_races = (
        flatten_races(
            data
        )
    )


    line_found_races = [

        race

        for race in all_races

        if (
            race.get(
                "status"
            )
            ==
            "LINE_FOUND"
        )

    ]


    print(
        "043 RACE COUNT:",
        len(
            all_races
        )
    )

    print(
        "AUDIT TARGET:",
        len(
            line_found_races
        )
    )


    # ========================================================
    # 全件監査
    # ========================================================


    audit_results = []


    for index, race in enumerate(
        line_found_races,
        start=1,
    ):

        result = audit_race(
            race
        )


        audit_results.append(
            result
        )


        print(
            f"[{index:03d}/"
            f"{len(line_found_races):03d}]",
            result[
                "audit_status"
            ],
            result[
                "race_key"
            ],
        )


    # ========================================================
    # 分類
    # ========================================================


    ok_races = [

        item

        for item in audit_results

        if (
            item.get(
                "audit_status"
            )
            ==
            "OK"
        )

    ]


    warning_races = [

        item

        for item in audit_results

        if (
            item.get(
                "audit_status"
            )
            ==
            "WARNING"
        )

    ]


    issue_races = [

        item

        for item in audit_results

        if (
            item.get(
                "audit_status"
            )
            ==
            "ISSUE"
        )

    ]


    competition_races = [

        item

        for item in audit_results

        if (
            item.get(
                "has_competition"
            )
            is True
        )

    ]


    # ========================================================
    # TYPE集計
    # ========================================================


    type_counter = Counter(

        item.get(
            "prediction_type"
        )

        for item in audit_results

    )


    # ========================================================
    # PROVIDER集計
    # ========================================================


    provider_counter = Counter(

        item.get(
            "provider"
        )

        for item in audit_results

    )


    # ========================================================
    # ライン数集計
    # ========================================================


    line_count_counter = Counter(

        item.get(
            "line_count"
        )

        for item in audit_results

    )


    # ========================================================
    # ライン長パターン
    #
    # 例:
    # [2,2,2,1]
    # [3,1,2]
    # ========================================================


    line_pattern_counter = Counter(

        tuple(
            item.get(
                "line_lengths",
                []
            )
        )

        for item in audit_results

    )


    # ========================================================
    # TYPE × ライン数
    # ========================================================


    type_line_count = defaultdict(
        Counter
    )


    for item in audit_results:

        prediction_type = (
            item.get(
                "prediction_type"
            )
        )


        line_count = (
            item.get(
                "line_count"
            )
        )


        type_line_count[
            str(
                prediction_type
            )
        ][
            str(
                line_count
            )
        ] += 1


    # ========================================================
    # 出力
    # ========================================================


    output = {

        "program":
            "044_audit_line_predictions.py",

        "audited_at":
            datetime.now().isoformat(),

        "source_file":
            str(
                SRC
            ),

        "source_race_date":
            data.get(
                "race_date"
            ),

        "source_race_count":
            len(
                all_races
            ),

        "audit_target_count":
            len(
                line_found_races
            ),

        "ok_count":
            len(
                ok_races
            ),

        "warning_count":
            len(
                warning_races
            ),

        "issue_count":
            len(
                issue_races
            ),

        "competition_count":
            len(
                competition_races
            ),

        "summary": {

            "prediction_types":
                dict(
                    type_counter
                ),

            "providers":
                dict(
                    provider_counter
                ),

            "line_counts":
                {

                    str(key):
                        value

                    for key, value
                    in sorted(
                        line_count_counter.items()
                    )

                },

            "line_length_patterns":
                {

                    str(
                        list(key)
                    ):
                        value

                    for key, value
                    in line_pattern_counter.most_common()

                },

            "type_by_line_count":
                {

                    key:
                        dict(
                            value
                        )

                    for key, value
                    in type_line_count.items()

                },

        },

        "issue_races":
            issue_races,

        "warning_races":
            warning_races,

        "competition_races":
            competition_races,

        "all_audit_results":
            audit_results,

    }


    save_json(
        OUT_FILE,
        output,
    )


    # ========================================================
    # 最終表示
    # ========================================================


    print()

    print(
        "#"
        * 100
    )

    print(
        "044 最終結果"
    )

    print(
        "#"
        * 100
    )

    print()

    print(
        "SOURCE DATE:",
        output[
            "source_race_date"
        ]
    )

    print(
        "SOURCE RACES:",
        output[
            "source_race_count"
        ]
    )

    print(
        "AUDIT TARGET:",
        output[
            "audit_target_count"
        ]
    )

    print(
        "OK:",
        output[
            "ok_count"
        ]
    )

    print(
        "WARNING:",
        output[
            "warning_count"
        ]
    )

    print(
        "ISSUE:",
        output[
            "issue_count"
        ]
    )

    print(
        "COMPETITION:",
        output[
            "competition_count"
        ]
    )


    print()

    print(
        "★ TYPE集計 ★"
    )


    for key, value in (
        type_counter.most_common()
    ):

        print(
            key,
            ":",
            value
        )


    print()

    print(
        "★ 情報提供元集計 ★"
    )


    for key, value in (
        provider_counter.most_common()
    ):

        print(
            key,
            ":",
            value
        )


    print()

    print(
        "★ ライン数集計 ★"
    )


    for key, value in sorted(
        line_count_counter.items()
    ):

        print(
            key,
            "ライン:",
            value
        )


    print()

    print(
        "★ ライン長パターン TOP20 ★"
    )


    for pattern, count in (
        line_pattern_counter.most_common(
            20
        )
    ):

        print(
            list(
                pattern
            ),
            ":",
            count
        )


    print()

    print(
        "★ TYPE × 復元ライン数 ★"
    )


    for type_name, counter in (
        type_line_count.items()
    ):

        print()

        print(
            "TYPE:",
            type_name
        )


        for line_count, count in sorted(
            counter.items()
        ):

            print(
                " ",
                line_count,
                "ライン:",
                count
            )


    print()

    print(
        "★ ISSUEレース ★"
    )


    if not issue_races:

        print(
            "なし"
        )


    for item in issue_races:

        print()

        print(
            item[
                "race_key"
            ]
        )

        print(
            "ISSUES:",
            item[
                "issues"
            ]
        )

        print(
            "TYPE:",
            item[
                "prediction_type"
            ]
        )

        print(
            "MAIN:",
            item[
                "main_lines"
            ]
        )

        print(
            "COMPETITION:",
            item[
                "competition_riders"
            ]
        )

        print(
            "RIDERS:",
            item[
                "unique_riders"
            ]
        )


    print()

    print(
        "★ WARNINGレース ★"
    )


    if not warning_races:

        print(
            "なし"
        )


    for item in warning_races:

        print()

        print(
            item[
                "race_key"
            ]
        )

        print(
            "WARNINGS:",
            item[
                "warnings"
            ]
        )

        print(
            "TYPE:",
            item[
                "prediction_type"
            ]
        )

        print(
            "MAIN:",
            item[
                "main_lines"
            ]
        )

        print(
            "RIDERS:",
            item[
                "unique_riders"
            ]
        )


    print()

    print(
        "★ 競りありレース ★"
    )


    if not competition_races:

        print(
            "なし"
        )


    for item in competition_races:

        print()

        print(
            item[
                "race_key"
            ]
        )

        print(
            "TYPE:",
            item[
                "prediction_type"
            ]
        )

        print(
            "MAIN:",
            item[
                "main_lines"
            ]
        )

        print(
            "COMPETITION:",
            item[
                "competition_riders"
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
        "=== 044 完了 ==="
    )


if __name__ == "__main__":

    main()