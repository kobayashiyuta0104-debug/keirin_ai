"""
===========================================================
競輪AI 正式版
008_build_historical_training_dataset.py

007 Historical Feature Dataset
↓
003正式Feature Schemaを基準
↓
2565レース正式学習CSV生成

重要:
・181特徴量
・003 Schema完全準拠
・特徴量順完全一致
・5～9車対応
・ラベル漏洩検証
・型検証
===========================================================
"""

import csv
import json
from pathlib import Path
from collections import Counter


# ===========================================================
# 基本設定
# ===========================================================

BASE = Path(r"C:\競輪AI")

DATA_OFFICIAL_DIR = (
    BASE
    / "data_official"
)

TRAINING_DIR = (
    DATA_OFFICIAL_DIR
    / "training"
)

SOURCE_FILE = (
    DATA_OFFICIAL_DIR
    / "007_historical_feature_dataset.json"
)

REFERENCE_SCHEMA_FILE = (
    TRAINING_DIR
    / "003_feature_schema.json"
)

OUT_CSV_FILE = (
    TRAINING_DIR
    / "008_historical_training_dataset.csv"
)

OUT_SCHEMA_FILE = (
    TRAINING_DIR
    / "008_historical_feature_schema.json"
)

VALIDATION_FILE = (
    TRAINING_DIR
    / "008_historical_training_validation.json"
)


# ===========================================================
# 正式列
# ===========================================================

META_COLUMNS = [
    "race_key",
    "race_date",
    "venue",
    "race_no",
]

TARGET_COLUMNS = [
    "payout_class_4",
    "is_20000_plus",
    "is_50000_plus",
]


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

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

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
# Datasetレース取得
# ===========================================================

def get_races(data):

    if isinstance(
        data,
        list,
    ):

        return data

    if isinstance(
        data,
        dict,
    ):

        for key in (
            "races",
            "dataset",
            "data",
        ):

            value = data.get(
                key
            )

            if isinstance(
                value,
                list,
            ):

                return value

    return []


# ===========================================================
# Schema配列探索
# ===========================================================

def find_list_by_keys(
    obj,
    candidate_keys,
):

    if isinstance(
        obj,
        dict,
    ):

        for key in candidate_keys:

            value = obj.get(
                key
            )

            if (
                isinstance(value, list)
                and
                all(
                    isinstance(x, str)
                    for x in value
                )
            ):

                return value

        for value in obj.values():

            found = find_list_by_keys(
                value,
                candidate_keys,
            )

            if found is not None:

                return found

    elif isinstance(
        obj,
        list,
    ):

        for value in obj:

            found = find_list_by_keys(
                value,
                candidate_keys,
            )

            if found is not None:

                return found

    return None


# ===========================================================
# 003 Schema読込
# ===========================================================

def load_reference_schema():

    schema = load_json(
        REFERENCE_SCHEMA_FILE
    )

    feature_names = find_list_by_keys(
        schema,
        [
            "feature_names",
            "features",
            "official_feature_names",
        ],
    )

    categorical_features = find_list_by_keys(
        schema,
        [
            "categorical_features",
            "categorical_feature_names",
            "categorical_columns",
        ],
    )

    numeric_features = find_list_by_keys(
        schema,
        [
            "numeric_features",
            "numerical_features",
            "numeric_feature_names",
            "numeric_columns",
        ],
    )

    if feature_names is None:

        raise RuntimeError(
            "003 Schemaからfeature_namesを取得できません"
        )

    if categorical_features is None:

        raise RuntimeError(
            "003 Schemaからcategorical featuresを取得できません"
        )

    if numeric_features is None:

        raise RuntimeError(
            "003 Schemaからnumeric featuresを取得できません"
        )

    return (
        schema,
        feature_names,
        categorical_features,
        numeric_features,
    )


# ===========================================================
# 数値判定
# ===========================================================

def is_valid_numeric(value):

    if value in (
        None,
        "",
    ):

        return True

    if isinstance(
        value,
        bool,
    ):

        return True

    if isinstance(
        value,
        (
            int,
            float,
        ),
    ):

        return True

    try:

        float(
            str(value)
            .replace(",", "")
            .strip()
        )

        return True

    except Exception:

        return False


# ===========================================================
# CSV値
# ===========================================================

def csv_value(value):

    if value is None:

        return ""

    return value


# ===========================================================
# main
# ===========================================================

def main():

    print(
        "=== 008 Historical正式学習Dataset "
        "CSV・Schema生成 ==="
    )

    TRAINING_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # -------------------------------------------------------
    # 007
    # -------------------------------------------------------

    source_data = load_json(
        SOURCE_FILE
    )

    races = get_races(
        source_data
    )

    print(
        "007 Historical Featureレース数:",
        len(races),
    )

    # -------------------------------------------------------
    # 003 Schema
    # -------------------------------------------------------

    (
        reference_schema,
        feature_names,
        categorical_features,
        numeric_features,
    ) = load_reference_schema()

    print(
        "003正式特徴量数:",
        len(feature_names),
    )

    print(
        "003カテゴリ特徴量数:",
        len(categorical_features),
    )

    print(
        "003数値特徴量数:",
        len(numeric_features),
    )

    csv_columns = (
        META_COLUMNS
        +
        feature_names
        +
        TARGET_COLUMNS
    )

    expected_csv_column_count = (
        len(META_COLUMNS)
        +
        len(feature_names)
        +
        len(TARGET_COLUMNS)
    )

    # -------------------------------------------------------
    # 検証準備
    # -------------------------------------------------------

    problems = []

    race_key_counter = Counter()

    player_count_counter = Counter()

    payout_class_counter = Counter()

    binary_20000_counter = Counter()

    binary_50000_counter = Counter()

    feature_count_counter = Counter()

    exact_feature_order_count = 0

    missing_feature_cell_count = 0

    feature_type_problem_count = 0

    target_missing_counter = Counter()

    # -------------------------------------------------------
    # CSV行生成
    # -------------------------------------------------------

    csv_rows = []

    for race in races:

        race_key = race.get(
            "race_key"
        )

        race_key_counter[
            race_key
        ] += 1

        player_count = race.get(
            "player_count"
        )

        player_count_counter[
            player_count
        ] += 1

        features = race.get(
            "features"
        )

        labels = race.get(
            "labels"
        )

        if not isinstance(
            features,
            dict,
        ):

            problems.append({

                "race_key":
                    race_key,

                "problem":
                    "FEATURES_MISSING",

            })

            continue

        if not isinstance(
            labels,
            dict,
        ):

            problems.append({

                "race_key":
                    race_key,

                "problem":
                    "LABELS_MISSING",

            })

            continue

        current_feature_names = list(
            features.keys()
        )

        feature_count_counter[
            len(current_feature_names)
        ] += 1

        if current_feature_names == feature_names:

            exact_feature_order_count += 1

        else:

            problems.append({

                "race_key":
                    race_key,

                "problem":
                    "FEATURE_ORDER_MISMATCH",

            })

        missing_names = [

            name

            for name in feature_names

            if name not in features

        ]

        extra_names = [

            name

            for name in current_feature_names

            if name not in feature_names

        ]

        if missing_names:

            problems.append({

                "race_key":
                    race_key,

                "problem":
                    "MISSING_FEATURE_NAMES",

                "names":
                    missing_names,

            })

        if extra_names:

            problems.append({

                "race_key":
                    race_key,

                "problem":
                    "EXTRA_FEATURE_NAMES",

                "names":
                    extra_names,

            })

        # ---------------------------------------------------
        # 数値型
        # ---------------------------------------------------

        for feature_name in numeric_features:

            value = features.get(
                feature_name
            )

            if not is_valid_numeric(
                value
            ):

                feature_type_problem_count += 1

                problems.append({

                    "race_key":
                        race_key,

                    "problem":
                        "NUMERIC_FEATURE_TYPE_ERROR",

                    "feature":
                        feature_name,

                    "value":
                        value,

                })

        # ---------------------------------------------------
        # 欠損セル
        # ---------------------------------------------------

        for feature_name in feature_names:

            value = features.get(
                feature_name
            )

            if value in (
                None,
                "",
            ):

                missing_feature_cell_count += 1

        # ---------------------------------------------------
        # Target
        # ---------------------------------------------------

        payout_class = labels.get(
            "payout_class_4"
        )

        is_20000_plus = labels.get(
            "is_20000_plus"
        )

        is_50000_plus = labels.get(
            "is_50000_plus"
        )

        targets = {

            "payout_class_4":
                payout_class,

            "is_20000_plus":
                is_20000_plus,

            "is_50000_plus":
                is_50000_plus,

        }

        for target_name, value in (
            targets.items()
        ):

            if value in (
                None,
                "",
            ):

                target_missing_counter[
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

        payout_class_counter[
            payout_class
        ] += 1

        binary_20000_counter[
            is_20000_plus
        ] += 1

        binary_50000_counter[
            is_50000_plus
        ] += 1

        # ---------------------------------------------------
        # CSV row
        # ---------------------------------------------------

        row = {

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

        }

        for feature_name in feature_names:

            row[
                feature_name
            ] = csv_value(
                features.get(
                    feature_name
                )
            )

        row[
            "payout_class_4"
        ] = payout_class

        row[
            "is_20000_plus"
        ] = is_20000_plus

        row[
            "is_50000_plus"
        ] = is_50000_plus

        csv_rows.append(
            row
        )

    # -------------------------------------------------------
    # race_key重複
    # -------------------------------------------------------

    duplicate_race_keys = {

        race_key: count

        for race_key, count
        in race_key_counter.items()

        if count > 1

    }

    if duplicate_race_keys:

        for race_key, count in (
            duplicate_race_keys.items()
        ):

            problems.append({

                "race_key":
                    race_key,

                "problem":
                    "DUPLICATE_RACE_KEY",

                "count":
                    count,

            })

    # -------------------------------------------------------
    # ラベル漏洩検証
    # -------------------------------------------------------

    leakage_keywords = [

        "trifecta",
        "payout",
        "harai",
        "kumi",
        "combination",
        "popularity",
        "ninki",
        "target",
        "label",
        "is_20000",
        "is_50000",

    ]

    leakage_features = [

        name

        for name in feature_names

        if any(
            keyword in name.lower()
            for keyword in leakage_keywords
        )

    ]

    if leakage_features:

        problems.append({

            "problem":
                "LABEL_LEAKAGE_FEATURES",

            "features":
                leakage_features,

        })

    # -------------------------------------------------------
    # Schema整合性
    # -------------------------------------------------------

    feature_type_defined_names = set(
        categorical_features
        +
        numeric_features
    )

    undefined_feature_types = [

        name

        for name in feature_names

        if name not in feature_type_defined_names

    ]

    duplicate_feature_type_names = {

        name

        for name in categorical_features

        if name in set(
            numeric_features
        )

    }

    if undefined_feature_types:

        problems.append({

            "problem":
                "UNDEFINED_FEATURE_TYPES",

            "features":
                undefined_feature_types,

        })

    if duplicate_feature_type_names:

        problems.append({

            "problem":
                "DUPLICATE_FEATURE_TYPES",

            "features":
                sorted(
                    duplicate_feature_type_names
                ),

        })

    # -------------------------------------------------------
    # CSV保存
    # -------------------------------------------------------

    with open(
        OUT_CSV_FILE,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=csv_columns,
            extrasaction="raise",
        )

        writer.writeheader()

        writer.writerows(
            csv_rows
        )

    # -------------------------------------------------------
    # 008 Schema保存
    # -------------------------------------------------------

    output_schema = {

        "schema_name":
            "official_historical_training_schema",

        "reference_schema":
            str(
                REFERENCE_SCHEMA_FILE
            ),

        "feature_count":
            len(feature_names),

        "categorical_feature_count":
            len(categorical_features),

        "numeric_feature_count":
            len(numeric_features),

        "meta_columns":
            META_COLUMNS,

        "feature_names":
            feature_names,

        "categorical_features":
            categorical_features,

        "numeric_features":
            numeric_features,

        "target_columns":
            TARGET_COLUMNS,

        "csv_columns":
            csv_columns,

        "csv_column_count":
            len(csv_columns),

    }

    save_json(
        OUT_SCHEMA_FILE,
        output_schema,
    )

    # -------------------------------------------------------
    # 検証保存
    # -------------------------------------------------------

    validation = {

        "source_race_count":
            len(races),

        "training_row_count":
            len(csv_rows),

        "official_feature_count":
            len(feature_names),

        "categorical_feature_count":
            len(categorical_features),

        "numeric_feature_count":
            len(numeric_features),

        "csv_column_count":
            len(csv_columns),

        "expected_csv_column_count":
            expected_csv_column_count,

        "feature_count_distribution":
            dict(
                feature_count_counter
            ),

        "exact_feature_order_count":
            exact_feature_order_count,

        "duplicate_race_keys":
            duplicate_race_keys,

        "player_count_distribution":
            dict(
                player_count_counter
            ),

        "payout_class_distribution":
            dict(
                payout_class_counter
            ),

        "is_20000_plus_distribution":
            dict(
                binary_20000_counter
            ),

        "is_50000_plus_distribution":
            dict(
                binary_50000_counter
            ),

        "missing_feature_cell_count":
            missing_feature_cell_count,

        "feature_type_problem_count":
            feature_type_problem_count,

        "target_missing":
            dict(
                target_missing_counter
            ),

        "label_leakage_features":
            leakage_features,

        "undefined_feature_types":
            undefined_feature_types,

        "duplicate_feature_type_names":
            sorted(
                duplicate_feature_type_names
            ),

        "problem_count":
            len(problems),

        "problems":
            problems,

    }

    save_json(
        VALIDATION_FILE,
        validation,
    )

    # -------------------------------------------------------
    # 結果
    # -------------------------------------------------------

    print()
    print(
        "=== 008 結果 ==="
    )

    print(
        "学習行数:",
        len(csv_rows),
    )

    print(
        "正式特徴量数:",
        len(feature_names),
    )

    print(
        "カテゴリ特徴量数:",
        len(categorical_features),
    )

    print(
        "数値特徴量数:",
        len(numeric_features),
    )

    print(
        "CSV列数:",
        len(csv_columns),
    )

    print(
        "CSV期待列数:",
        expected_csv_column_count,
    )

    print(
        "特徴量数分布:",
        dict(
            feature_count_counter
        ),
    )

    print(
        "特徴量順完全一致:",
        exact_feature_order_count,
    )

    print(
        "race_key重複:",
        duplicate_race_keys,
    )

    print(
        "車立て分布:",
        dict(
            player_count_counter
        ),
    )

    print(
        "4分類分布:",
        dict(
            payout_class_counter
        ),
    )

    print(
        "2万円以上分布:",
        dict(
            binary_20000_counter
        ),
    )

    print(
        "5万円以上分布:",
        dict(
            binary_50000_counter
        ),
    )

    print(
        "欠損特徴量セル数:",
        missing_feature_cell_count,
    )

    print(
        "特徴量型問題:",
        feature_type_problem_count,
    )

    print(
        "ターゲット欠損:",
        dict(
            target_missing_counter
        ),
    )

    print(
        "ラベル漏洩列:",
        leakage_features,
    )

    print(
        "未定義特徴量型:",
        undefined_feature_types,
    )

    print(
        "特徴量型重複定義:",
        sorted(
            duplicate_feature_type_names
        ),
    )

    print(
        "問題件数:",
        len(problems),
    )

    # -------------------------------------------------------
    # 9車立てサンプル
    # -------------------------------------------------------

    nine_player_rows = [

        row

        for race, row
        in zip(
            races,
            csv_rows,
        )

        if race.get(
            "player_count"
        ) == 9

    ]

    print(
        "9車立て学習行数:",
        len(
            nine_player_rows
        ),
    )

    if nine_player_rows:

        sample = nine_player_rows[0]

        print()
        print(
            "=== 9車立て学習行サンプル ==="
        )

        print(
            "race_key:",
            sample.get(
                "race_key"
            ),
        )

        for slot in range(
            1,
            10,
        ):

            print(
                f"p{slot}:",
                "class=",
                sample.get(
                    f"p{slot}_class"
                ),
                "/ race_score=",
                sample.get(
                    f"p{slot}_race_score"
                ),
                "/ recent=",
                [
                    sample.get(
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

                target:
                    sample.get(
                        target
                    )

                for target
                in TARGET_COLUMNS

            },
        )

    if problems:

        print()
        print(
            "=== 問題一覧 先頭100件 ==="
        )

        for problem in problems[:100]:

            print(
                problem
            )

    print()
    print(
        "学習CSV保存:"
    )

    print(
        OUT_CSV_FILE
    )

    print()
    print(
        "Feature Schema保存:"
    )

    print(
        OUT_SCHEMA_FILE
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
        "=== 008 完了 ==="
    )


if __name__ == "__main__":

    main()