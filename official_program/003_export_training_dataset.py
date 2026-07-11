"""
===========================================================
競輪AI 正式版
003_export_training_dataset.py

Part 1
・基本設定
・学習ターゲット正式定義
・特徴量型定義
・共通関数
・002 Feature Dataset読込
===========================================================
"""

import csv
import json
from pathlib import Path
from collections import Counter


# ===========================================================
# Part 1
# 基本設定・学習データ定義
# ===========================================================


# ===========================================================
# ファイル設定
# ===========================================================

BASE = Path(r"C:\競輪AI")

INPUT_FILE = (
    BASE
    / "data_official"
    / "002_feature_dataset.json"
)

VALIDATION_SOURCE_FILE = (
    BASE
    / "data_official"
    / "002_feature_validation.json"
)

OUTPUT_DIR = (
    BASE
    / "data_official"
    / "training"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_CSV = (
    OUTPUT_DIR
    / "003_training_dataset.csv"
)

FEATURE_SCHEMA_FILE = (
    OUTPUT_DIR
    / "003_feature_schema.json"
)

VALIDATION_FILE = (
    OUTPUT_DIR
    / "003_training_validation.json"
)


# ===========================================================
# 最大車立て
# ===========================================================

MAX_PLAYER_SLOTS = 9


# ===========================================================
# 学習ターゲット正式定義
# ===========================================================

TARGET_COLUMNS = [

    "payout_class_4",

    "is_20000_plus",

    "is_50000_plus",

]


# ===========================================================
# 学習対象外ラベル
# ===========================================================

NON_TRAINING_LABEL_COLUMNS = [

    "trifecta_combination",

    "trifecta_payout",

    "trifecta_popularity",

]


# ===========================================================
# レース識別列
# ===========================================================

ID_COLUMNS = [

    "race_key",

    "race_date",

    "venue",

    "race_no",

]


# ===========================================================
# カテゴリ特徴量正式定義
# ===========================================================

PLAYER_CATEGORICAL_FEATURES = [

    "prefecture",

    "previous_class",

    "class",

    "riding_style",

]


# ===========================================================
# 数値特徴量正式定義
# ===========================================================

PLAYER_NUMERIC_FEATURES = [

    "graduation_term",

    "age",

    "race_score",

    "nige_count",

    "makuri_count",

    "sashi_count",

    "mark_count",

    "back_count",

    "home_count",

    "start_count",

    "win_rate",

    "top2_rate",

    "top3_rate",

    "recent_finish_1",

    "recent_finish_2",

    "recent_finish_3",

]


# ===========================================================
# レース共通特徴量型
# ===========================================================

RACE_NUMERIC_FEATURES = [

    "player_count",

]


# ===========================================================
# 正式カテゴリ特徴量名生成
# ===========================================================

def build_categorical_feature_names():
    """
    p1～p9カテゴリ特徴量名を生成
    """

    names = []

    for player_slot in range(
        1,
        MAX_PLAYER_SLOTS + 1,
    ):

        prefix = f"p{player_slot}_"

        for feature_name in (
            PLAYER_CATEGORICAL_FEATURES
        ):

            names.append(
                prefix + feature_name
            )

    return names


# ===========================================================
# 正式数値特徴量名生成
# ===========================================================

def build_numeric_feature_names():
    """
    p1～p9数値特徴量
    +
    レース共通数値特徴量を生成
    """

    names = []

    for player_slot in range(
        1,
        MAX_PLAYER_SLOTS + 1,
    ):

        prefix = f"p{player_slot}_"

        for feature_name in (
            PLAYER_NUMERIC_FEATURES
        ):

            names.append(
                prefix + feature_name
            )

    names.extend(
        RACE_NUMERIC_FEATURES
    )

    return names


# ===========================================================
# 正式学習特徴量名生成
# ===========================================================

def build_training_feature_names():
    """
    181特徴量を002の正式列順で生成

    選手ごとに
    カテゴリ4列
    +
    数値16列

    p1～p9
    +
    player_count
    """

    names = []

    for player_slot in range(
        1,
        MAX_PLAYER_SLOTS + 1,
    ):

        prefix = f"p{player_slot}_"

        for feature_name in (
            PLAYER_CATEGORICAL_FEATURES
        ):

            names.append(
                prefix + feature_name
            )

        for feature_name in (
            PLAYER_NUMERIC_FEATURES
        ):

            names.append(
                prefix + feature_name
            )

    names.extend(
        RACE_NUMERIC_FEATURES
    )

    return names


# ===========================================================
# JSON読込
# ===========================================================

def load_json(path):
    """
    JSONファイル読込
    """

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


def load_feature_dataset():
    """
    002 Feature Dataset読込
    """

    data = load_json(
        INPUT_FILE
    )

    if not isinstance(
        data,
        list,
    ):

        raise ValueError(
            "002_feature_dataset.json "
            "のTOP構造がlistではありません"
        )

    return data


def load_002_validation():
    """
    002検証レポート読込
    """

    data = load_json(
        VALIDATION_SOURCE_FILE
    )

    if not isinstance(
        data,
        dict,
    ):

        raise ValueError(
            "002_feature_validation.json "
            "のTOP構造がdictではありません"
        )

    return data


# ===========================================================
# 特徴量型判定
# ===========================================================

def build_feature_type_map():
    """
    全181特徴量の正式型定義を生成
    """

    categorical_names = set(
        build_categorical_feature_names()
    )

    numeric_names = set(
        build_numeric_feature_names()
    )

    training_names = (
        build_training_feature_names()
    )

    type_map = {}

    for feature_name in training_names:

        if feature_name in categorical_names:

            type_map[
                feature_name
            ] = "categorical"

        elif feature_name in numeric_names:

            type_map[
                feature_name
            ] = "numeric"

        else:

            type_map[
                feature_name
            ] = "unknown"

    return type_map


# ===========================================================
# 特徴量定義検証
# ===========================================================

def validate_training_feature_definition():
    """
    003特徴量定義そのものを検証
    """

    training_names = (
        build_training_feature_names()
    )

    type_map = (
        build_feature_type_map()
    )

    counter = Counter(
        training_names
    )

    duplicates = {

        name: count

        for name, count
        in counter.items()

        if count > 1

    }

    unknown_features = [

        name

        for name, feature_type
        in type_map.items()

        if feature_type == "unknown"

    ]

    return {

        "training_feature_count":
            len(training_names),

        "duplicate_features":
            duplicates,

        "unknown_features":
            unknown_features,

        "categorical_feature_count":
            sum(
                1
                for value
                in type_map.values()
                if value == "categorical"
            ),

        "numeric_feature_count":
            sum(
                1
                for value
                in type_map.values()
                if value == "numeric"
            ),

    }


# ===========================================================
# End Part 1
# ===========================================================


# ===========================================================
# Part 2
# 学習行生成・平坦化
# ===========================================================


# ===========================================================
# カテゴリ値変換
# ===========================================================

def normalize_categorical_value(value):
    """
    カテゴリ特徴量をCSV保存用に変換

    Noneは空欄として保持する
    """

    if value is None:
        return ""

    return str(value).strip()


# ===========================================================
# 数値値変換
# ===========================================================

def normalize_numeric_value(value):
    """
    数値特徴量をCSV保存用に変換

    Noneは空欄として保持する
    数値は元のint / floatを維持する
    """

    if value in (
        None,
        "",
    ):

        return ""

    if isinstance(
        value,
        bool,
    ):

        return int(value)

    if isinstance(
        value,
        (
            int,
            float,
        ),
    ):

        return value

    text = (
        str(value)
        .replace(",", "")
        .replace("%", "")
        .strip()
    )

    if text == "":
        return ""

    try:

        number = float(text)

        if number.is_integer():

            return int(number)

        return number

    except Exception:

        return ""


# ===========================================================
# 特徴量1件変換
# ===========================================================

def normalize_feature_value(
    feature_name,
    value,
    feature_type_map,
):
    """
    特徴量型定義に従って値を変換
    """

    feature_type = (
        feature_type_map.get(
            feature_name
        )
    )

    if feature_type == "categorical":

        return normalize_categorical_value(
            value
        )

    if feature_type == "numeric":

        return normalize_numeric_value(
            value
        )

    raise ValueError(
        "未定義特徴量型: "
        + str(feature_name)
    )


# ===========================================================
# ID列生成
# ===========================================================

def build_id_values(race):
    """
    レース識別列を生成
    """

    return {

        "race_key":
            race.get(
                "race_key"
            ),

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

    }


# ===========================================================
# ターゲット列生成
# ===========================================================

def build_target_values(race):
    """
    正解ラベルを正式取得
    """

    labels = race.get(
        "labels"
    )

    if not isinstance(
        labels,
        dict,
    ):

        labels = {}

    return {

        "payout_class_4":
            labels.get(
                "payout_class_4"
            ),

        "is_20000_plus":
            normalize_numeric_value(
                labels.get(
                    "is_20000_plus"
                )
            ),

        "is_50000_plus":
            normalize_numeric_value(
                labels.get(
                    "is_50000_plus"
                )
            ),

    }


# ===========================================================
# 学習行1件生成
# ===========================================================

def build_training_row(
    race,
    training_feature_names,
    feature_type_map,
):
    """
    002の1レースを

    ID列
    +
    181特徴量
    +
    正解ターゲット

    の1行へ変換
    """

    features = race.get(
        "features"
    )

    if not isinstance(
        features,
        dict,
    ):

        features = {}

    row = {}

    id_values = build_id_values(
        race
    )

    for column_name in ID_COLUMNS:

        row[
            column_name
        ] = id_values.get(
            column_name
        )

    for feature_name in (
        training_feature_names
    ):

        row[
            feature_name
        ] = normalize_feature_value(

            feature_name,

            features.get(
                feature_name
            ),

            feature_type_map,

        )

    target_values = build_target_values(
        race
    )

    for target_name in TARGET_COLUMNS:

        row[
            target_name
        ] = target_values.get(
            target_name
        )

    return row


# ===========================================================
# 学習CSV正式列順生成
# ===========================================================

def build_training_column_names():
    """
    CSV正式列順を生成

    ID
    ↓
    181特徴量
    ↓
    正解ターゲット
    """

    columns = []

    columns.extend(
        ID_COLUMNS
    )

    columns.extend(
        build_training_feature_names()
    )

    columns.extend(
        TARGET_COLUMNS
    )

    return columns


# ===========================================================
# 学習行一括生成
# ===========================================================

def build_training_rows(
    feature_dataset,
):
    """
    全レースを正式学習行へ変換
    """

    training_feature_names = (
        build_training_feature_names()
    )

    feature_type_map = (
        build_feature_type_map()
    )

    rows = []

    problems = []

    for race in feature_dataset:

        race_key = race.get(
            "race_key"
        )

        try:

            row = build_training_row(

                race,

                training_feature_names,

                feature_type_map,

            )

            rows.append(
                row
            )

        except Exception as e:

            problems.append({

                "race_key":
                    race_key,

                "problem":
                    "TRAINING_ROW_BUILD_ERROR",

                "error":
                    repr(e),

            })

    return (
        rows,
        problems,
    )


# ===========================================================
# 列順検証
# ===========================================================

def validate_training_row_columns(
    rows,
):
    """
    全学習行の列順が正式列順と
    完全一致しているか確認
    """

    official_columns = (
        build_training_column_names()
    )

    exact_count = 0

    problems = []

    for row_no, row in enumerate(
        rows,
        1,
    ):

        actual_columns = list(
            row.keys()
        )

        if actual_columns == official_columns:

            exact_count += 1

        else:

            problems.append({

                "row_no":
                    row_no,

                "race_key":
                    row.get(
                        "race_key"
                    ),

                "problem":
                    "COLUMN_ORDER_MISMATCH",

            })

    return (
        exact_count,
        problems,
    )


# ===========================================================
# 正解ラベル欠損検証
# ===========================================================

def validate_target_values(rows):
    """
    学習ターゲット欠損確認
    """

    problems = []

    target_missing_dist = Counter()

    for row in rows:

        race_key = row.get(
            "race_key"
        )

        for target_name in TARGET_COLUMNS:

            value = row.get(
                target_name
            )

            if value in (
                None,
                "",
            ):

                target_missing_dist[
                    target_name
                ] += 1

                problems.append({

                    "race_key":
                        race_key,

                    "problem":
                        "TARGET_MISSING",

                    "target":
                        target_name,

                })

    return (
        target_missing_dist,
        problems,
    )


# ===========================================================
# ラベル漏洩検証
# ===========================================================

def validate_label_leakage():
    """
    正解・払戻情報が181特徴量へ
    混入していないことを確認
    """

    training_feature_names = set(
        build_training_feature_names()
    )

    leakage_columns = []

    for column_name in (
        TARGET_COLUMNS
        + NON_TRAINING_LABEL_COLUMNS
    ):

        if column_name in training_feature_names:

            leakage_columns.append(
                column_name
            )

    return leakage_columns


# ===========================================================
# End Part 2
# ===========================================================


# ===========================================================
# Part 3
# CSV保存・Feature Schema生成・構造検証
# ===========================================================


# ===========================================================
# 学習CSV保存
# ===========================================================

def save_training_csv(rows):
    """
    正式学習CSVを保存
    """

    columns = (
        build_training_column_names()
    )

    with open(
        OUTPUT_CSV,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=columns,
            extrasaction="raise",
        )

        writer.writeheader()

        writer.writerows(
            rows
        )


# ===========================================================
# Feature Schema生成
# ===========================================================

def build_feature_schema():
    """
    学習・本番予測で共通利用する
    正式Feature Schemaを生成

    この列順と型定義を
    004以降の基準とする
    """

    training_feature_names = (
        build_training_feature_names()
    )

    categorical_feature_names = (
        build_categorical_feature_names()
    )

    numeric_feature_names = (
        build_numeric_feature_names()
    )

    feature_type_map = (
        build_feature_type_map()
    )

    schema = {

        "schema_version":
            "003_v1",

        "max_player_slots":
            MAX_PLAYER_SLOTS,

        "feature_count":
            len(
                training_feature_names
            ),

        "feature_names":
            training_feature_names,

        "categorical_feature_count":
            len(
                categorical_feature_names
            ),

        "categorical_feature_names":
            categorical_feature_names,

        "numeric_feature_count":
            len(
                numeric_feature_names
            ),

        "numeric_feature_names":
            numeric_feature_names,

        "feature_type_map":
            feature_type_map,

        "id_columns":
            ID_COLUMNS,

        "target_columns":
            TARGET_COLUMNS,

        "non_training_label_columns":
            NON_TRAINING_LABEL_COLUMNS,

        "csv_columns":
            build_training_column_names(),

    }

    return schema


# ===========================================================
# Feature Schema保存
# ===========================================================

def save_feature_schema(schema):
    """
    Feature SchemaをJSON保存
    """

    with open(
        FEATURE_SCHEMA_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            schema,
            f,
            ensure_ascii=False,
            indent=2,
        )


# ===========================================================
# 002列順との完全一致検証
# ===========================================================

def validate_against_002_schema(
    validation_002,
):
    """
    002で確定した正式特徴量順と
    003の学習特徴量順を比較する
    """

    feature_names_002 = (
        validation_002.get(
            "official_feature_names"
        )
    )

    if not isinstance(
        feature_names_002,
        list,
    ):

        return {

            "match":
                False,

            "problem":
                "002_FEATURE_NAMES_MISSING",

            "missing_in_003":
                [],

            "extra_in_003":
                [],

        }

    feature_names_003 = (
        build_training_feature_names()
    )

    missing_in_003 = [

        name

        for name in feature_names_002

        if name not in feature_names_003

    ]

    extra_in_003 = [

        name

        for name in feature_names_003

        if name not in feature_names_002

    ]

    exact_match = (
        feature_names_002
        == feature_names_003
    )

    return {

        "match":
            exact_match,

        "problem":
            (
                None
                if exact_match
                else
                "002_003_FEATURE_SCHEMA_MISMATCH"
            ),

        "missing_in_003":
            missing_in_003,

        "extra_in_003":
            extra_in_003,

        "feature_count_002":
            len(
                feature_names_002
            ),

        "feature_count_003":
            len(
                feature_names_003
            ),

    }


# ===========================================================
# 特徴量値型検証
# ===========================================================

def validate_feature_value_types(rows):
    """
    正規化後の特徴量値型を検証

    categorical:
        str または空欄

    numeric:
        int / float または空欄
    """

    type_map = (
        build_feature_type_map()
    )

    problems = []

    categorical_value_count = 0

    numeric_value_count = 0

    missing_value_count = 0

    for row in rows:

        race_key = row.get(
            "race_key"
        )

        for feature_name, feature_type in (
            type_map.items()
        ):

            value = row.get(
                feature_name
            )

            if value in (
                None,
                "",
            ):

                missing_value_count += 1

                continue

            if feature_type == "categorical":

                if isinstance(
                    value,
                    str,
                ):

                    categorical_value_count += 1

                else:

                    problems.append({

                        "race_key":
                            race_key,

                        "feature":
                            feature_name,

                        "problem":
                            "INVALID_CATEGORICAL_TYPE",

                        "value":
                            value,

                        "python_type":
                            type(value).__name__,

                    })

            elif feature_type == "numeric":

                if (
                    isinstance(
                        value,
                        (
                            int,
                            float,
                        ),
                    )
                    and not isinstance(
                        value,
                        bool,
                    )
                ):

                    numeric_value_count += 1

                else:

                    problems.append({

                        "race_key":
                            race_key,

                        "feature":
                            feature_name,

                        "problem":
                            "INVALID_NUMERIC_TYPE",

                        "value":
                            value,

                        "python_type":
                            type(value).__name__,

                    })

    return {

        "categorical_value_count":
            categorical_value_count,

        "numeric_value_count":
            numeric_value_count,

        "missing_value_count":
            missing_value_count,

        "problem_count":
            len(problems),

        "problems":
            problems,

    }


# ===========================================================
# CSV列数検証
# ===========================================================

def validate_csv_column_definition():
    """
    CSV正式列定義の重複と列数を検証
    """

    columns = (
        build_training_column_names()
    )

    counter = Counter(
        columns
    )

    duplicates = {

        name: count

        for name, count
        in counter.items()

        if count > 1

    }

    expected_count = (

        len(ID_COLUMNS)

        + len(
            build_training_feature_names()
        )

        + len(TARGET_COLUMNS)

    )

    return {

        "csv_column_count":
            len(columns),

        "expected_csv_column_count":
            expected_count,

        "duplicate_csv_columns":
            duplicates,

        "count_match":
            (
                len(columns)
                == expected_count
            ),

    }


# ===========================================================
# 学習データ統計生成
# ===========================================================

def build_training_statistics(rows):
    """
    学習行の基本統計を生成
    """

    player_count_dist = Counter()

    payout_class_dist = Counter()

    is_20000_plus_dist = Counter()

    is_50000_plus_dist = Counter()

    race_date_dist = Counter()

    for row in rows:

        player_count_dist[
            row.get(
                "player_count"
            )
        ] += 1

        payout_class_dist[
            row.get(
                "payout_class_4"
            )
        ] += 1

        is_20000_plus_dist[
            row.get(
                "is_20000_plus"
            )
        ] += 1

        is_50000_plus_dist[
            row.get(
                "is_50000_plus"
            )
        ] += 1

        race_date_dist[
            row.get(
                "race_date"
            )
        ] += 1

    return {

        "row_count":
            len(rows),

        "player_count_distribution":
            dict(
                player_count_dist
            ),

        "payout_class_distribution":
            dict(
                payout_class_dist
            ),

        "is_20000_plus_distribution":
            dict(
                is_20000_plus_dist
            ),

        "is_50000_plus_distribution":
            dict(
                is_50000_plus_dist
            ),

        "race_date_distribution":
            dict(
                race_date_dist
            ),

    }


# ===========================================================
# End Part 3
# ===========================================================


# ===========================================================
# Part 4
# 検証レポート・保存・main
# ===========================================================


# ===========================================================
# 検証レポート生成
# ===========================================================

def build_training_validation_report(
    rows,
    definition_validation,
    schema_match,
    type_validation,
    csv_validation,
    training_statistics,
    row_build_problems,
    column_problems,
    target_missing_dist,
    target_problems,
    leakage_columns,
):
    """
    003正式検証レポートを生成
    """

    all_problems = []

    all_problems.extend(
        row_build_problems
    )

    all_problems.extend(
        column_problems
    )

    all_problems.extend(
        target_problems
    )

    all_problems.extend(
        type_validation.get(
            "problems",
            [],
        )
    )

    if definition_validation.get(
        "duplicate_features"
    ):

        all_problems.append({
            "problem":
                "DUPLICATE_FEATURE_DEFINITION",
            "details":
                definition_validation.get(
                    "duplicate_features"
                ),
        })

    if definition_validation.get(
        "unknown_features"
    ):

        all_problems.append({
            "problem":
                "UNKNOWN_FEATURE_TYPE",
            "details":
                definition_validation.get(
                    "unknown_features"
                ),
        })

    if not schema_match.get(
        "match"
    ):

        all_problems.append({
            "problem":
                schema_match.get(
                    "problem"
                ),
            "missing_in_003":
                schema_match.get(
                    "missing_in_003"
                ),
            "extra_in_003":
                schema_match.get(
                    "extra_in_003"
                ),
        })

    if not csv_validation.get(
        "count_match"
    ):

        all_problems.append({
            "problem":
                "CSV_COLUMN_COUNT_MISMATCH",
        })

    if csv_validation.get(
        "duplicate_csv_columns"
    ):

        all_problems.append({
            "problem":
                "DUPLICATE_CSV_COLUMNS",
            "details":
                csv_validation.get(
                    "duplicate_csv_columns"
                ),
        })

    if leakage_columns:

        all_problems.append({
            "problem":
                "LABEL_LEAKAGE",
            "columns":
                leakage_columns,
        })

    report = {

        "input_file":
            str(INPUT_FILE),

        "validation_source_file":
            str(
                VALIDATION_SOURCE_FILE
            ),

        "output_csv":
            str(OUTPUT_CSV),

        "feature_schema_file":
            str(FEATURE_SCHEMA_FILE),

        "row_count":
            len(rows),

        "training_feature_count":
            definition_validation.get(
                "training_feature_count"
            ),

        "categorical_feature_count":
            definition_validation.get(
                "categorical_feature_count"
            ),

        "numeric_feature_count":
            definition_validation.get(
                "numeric_feature_count"
            ),

        "duplicate_features":
            definition_validation.get(
                "duplicate_features"
            ),

        "unknown_features":
            definition_validation.get(
                "unknown_features"
            ),

        "schema_002_003_match":
            schema_match,

        "csv_validation":
            csv_validation,

        "feature_type_validation": {

            "categorical_value_count":
                type_validation.get(
                    "categorical_value_count"
                ),

            "numeric_value_count":
                type_validation.get(
                    "numeric_value_count"
                ),

            "missing_value_count":
                type_validation.get(
                    "missing_value_count"
                ),

            "problem_count":
                type_validation.get(
                    "problem_count"
                ),

        },

        "target_missing_distribution":
            dict(
                target_missing_dist
            ),

        "label_leakage_columns":
            leakage_columns,

        "training_statistics":
            training_statistics,

        "problem_count":
            len(all_problems),

        "problems":
            all_problems,

    }

    return report


# ===========================================================
# 検証レポート保存
# ===========================================================

def save_training_validation_report(
    report,
):
    """
    003検証レポート保存
    """

    with open(
        VALIDATION_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            report,
            f,
            ensure_ascii=False,
            indent=2,
        )


# ===========================================================
# 9車立て学習行サンプル表示
# ===========================================================

def print_nine_player_training_sample(
    rows,
):
    """
    9車立ての学習行を1件表示
    """

    target_row = None

    for row in rows:

        if row.get(
            "player_count"
        ) == 9:

            target_row = row

            break

    if target_row is None:

        print()
        print(
            "9車立て学習行サンプル: なし"
        )

        return

    print()
    print(
        "=== 9車立て学習行サンプル ==="
    )

    print(
        "race_key:",
        target_row.get(
            "race_key"
        ),
    )

    print(
        "player_count:",
        target_row.get(
            "player_count"
        ),
    )

    for slot in range(
        1,
        MAX_PLAYER_SLOTS + 1,
    ):

        print(
            f"p{slot}:",
            "class=",
            target_row.get(
                f"p{slot}_class"
            ),
            "/ race_score=",
            target_row.get(
                f"p{slot}_race_score"
            ),
            "/ recent=",
            [
                target_row.get(
                    f"p{slot}_recent_finish_{n}"
                )
                for n in range(
                    1,
                    4,
                )
            ],
        )

    print(
        "target:",
        {
            target_name:
                target_row.get(
                    target_name
                )
            for target_name
            in TARGET_COLUMNS
        },
    )


# ===========================================================
# main
# ===========================================================

def main():

    print(
        "=== 003 正式学習Dataset "
        "CSV・Schema生成 ==="
    )

    feature_dataset = (
        load_feature_dataset()
    )

    validation_002 = (
        load_002_validation()
    )

    print(
        "002 Feature Datasetレース数:",
        len(feature_dataset),
    )

    definition_validation = (
        validate_training_feature_definition()
    )

    print(
        "003定義特徴量数:",
        definition_validation[
            "training_feature_count"
        ],
    )

    rows, row_build_problems = (
        build_training_rows(
            feature_dataset
        )
    )

    (
        exact_column_order_count,
        column_problems,
    ) = validate_training_row_columns(
        rows
    )

    (
        target_missing_dist,
        target_problems,
    ) = validate_target_values(
        rows
    )

    leakage_columns = (
        validate_label_leakage()
    )

    schema_match = (
        validate_against_002_schema(
            validation_002
        )
    )

    type_validation = (
        validate_feature_value_types(
            rows
        )
    )

    csv_validation = (
        validate_csv_column_definition()
    )

    training_statistics = (
        build_training_statistics(
            rows
        )
    )

    schema = build_feature_schema()

    report = (
        build_training_validation_report(

            rows,

            definition_validation,

            schema_match,

            type_validation,

            csv_validation,

            training_statistics,

            row_build_problems,

            column_problems,

            target_missing_dist,

            target_problems,

            leakage_columns,

        )
    )

    save_training_csv(
        rows
    )

    save_feature_schema(
        schema
    )

    save_training_validation_report(
        report
    )

    print()
    print("=== 003 結果 ===")

    print(
        "学習行数:",
        len(rows),
    )

    print(
        "正式特徴量数:",
        definition_validation[
            "training_feature_count"
        ],
    )

    print(
        "カテゴリ特徴量数:",
        definition_validation[
            "categorical_feature_count"
        ],
    )

    print(
        "数値特徴量数:",
        definition_validation[
            "numeric_feature_count"
        ],
    )

    print(
        "CSV列数:",
        csv_validation[
            "csv_column_count"
        ],
    )

    print(
        "CSV期待列数:",
        csv_validation[
            "expected_csv_column_count"
        ],
    )

    print(
        "列順完全一致行:",
        exact_column_order_count,
    )

    print(
        "002・003特徴量順完全一致:",
        schema_match[
            "match"
        ],
    )

    print(
        "特徴量名重複:",
        definition_validation[
            "duplicate_features"
        ],
    )

    print(
        "未定義特徴量型:",
        definition_validation[
            "unknown_features"
        ],
    )

    print(
        "ラベル漏洩列:",
        leakage_columns,
    )

    print(
        "ターゲット欠損:",
        dict(
            target_missing_dist
        ),
    )

    print(
        "特徴量型問題:",
        type_validation[
            "problem_count"
        ],
    )

    print(
        "欠損特徴量セル数:",
        type_validation[
            "missing_value_count"
        ],
    )

    print(
        "車立て分布:",
        training_statistics[
            "player_count_distribution"
        ],
    )

    print(
        "4分類分布:",
        training_statistics[
            "payout_class_distribution"
        ],
    )

    print(
        "2万円以上分布:",
        training_statistics[
            "is_20000_plus_distribution"
        ],
    )

    print(
        "5万円以上分布:",
        training_statistics[
            "is_50000_plus_distribution"
        ],
    )

    print(
        "問題件数:",
        report[
            "problem_count"
        ],
    )

    print_nine_player_training_sample(
        rows
    )

    if report[
        "problems"
    ]:

        print()
        print(
            "=== 問題一覧 先頭50件 ==="
        )

        for problem in report[
            "problems"
        ][:50]:

            print(
                problem
            )

    print()
    print(
        "学習CSV保存:"
    )
    print(
        OUTPUT_CSV
    )

    print()
    print(
        "Feature Schema保存:"
    )
    print(
        FEATURE_SCHEMA_FILE
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
        "=== 003 完了 ==="
    )


if __name__ == "__main__":

    main()


# ===========================================================
# End Part 4
# ===========================================================