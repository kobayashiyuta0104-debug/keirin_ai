"""
===========================================================
競輪AI 正式版
012_compare_structural_features.py

目的:
・現行181特徴量からレース相対・構造特徴量を生成
・BASE 181特徴量モデル
・181 + STRUCTURE特徴量モデル
・完全同一Train/Test期間で直接比較
・TOP5/10/20/30/40/50%ランキング評価
・構造特徴量名・値を正式保存

重要:
・008 Historical Training Dataset使用
・008 Feature Schema使用
・009 / 010 / 011と同じ時系列分割
・未来Testを学習へ使用しない
・元データは変更しない
===========================================================
"""

import json
import warnings
from pathlib import Path
from collections import Counter

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
)

warnings.filterwarnings("ignore")


# ===========================================================
# 基本設定
# ===========================================================

BASE = Path(r"C:\競輪AI")

TRAINING_DIR = (
    BASE
    / "data_official"
    / "training"
)

SOURCE_CSV = (
    TRAINING_DIR
    / "008_historical_training_dataset.csv"
)

SCHEMA_FILE = (
    TRAINING_DIR
    / "008_historical_feature_schema.json"
)

OUT_DIR = (
    BASE
    / "data_official"
    / "models"
    / "012_structural_features"
)

RESULT_FILE = (
    OUT_DIR
    / "012_structural_feature_comparison.json"
)

STRUCTURE_SCHEMA_FILE = (
    OUT_DIR
    / "012_structural_feature_schema.json"
)

STRUCTURE_DATASET_FILE = (
    OUT_DIR
    / "012_dataset_with_structural_features.csv"
)

TEST_PREDICTION_FILE = (
    OUT_DIR
    / "012_test_predictions.csv"
)


TRAIN_RATIO = 0.80
RANDOM_STATE = 42
TARGET = "is_20000_plus"


RANKING_PERCENTAGES = [
    0.05,
    0.10,
    0.20,
    0.30,
    0.40,
    0.50,
]


# ===========================================================
# 構造特徴量対象
# ===========================================================

PLAYER_NUMERIC_METRICS = [
    "race_score",
    "graduation_term",
    "age",
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


PLAYER_NUMBERS = list(
    range(1, 10)
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
# 日付
# ===========================================================

def normalize_race_date(value):

    text = str(value).strip()

    text = text.replace("-", "")
    text = text.replace("/", "")

    return text


# ===========================================================
# 数値
# ===========================================================

def safe_float(value):

    if pd.isna(value):

        return None

    try:

        return float(value)

    except:

        return None


def valid_numeric_values(
    row,
    metric,
):

    values = []

    for player_number in PLAYER_NUMBERS:

        column = (
            f"p{player_number}_{metric}"
        )

        if column not in row.index:

            continue

        value = safe_float(
            row[column]
        )

        if value is not None:

            values.append(value)

    return values


# ===========================================================
# 数値構造特徴量
# ===========================================================

def calculate_numeric_structure(
    row,
    metric,
):

    values = valid_numeric_values(
        row,
        metric,
    )

    prefix = f"struct_{metric}"

    result = {
        f"{prefix}_valid_count": len(values),
        f"{prefix}_missing_count":
            int(row["player_count"]) - len(values),
        f"{prefix}_max": np.nan,
        f"{prefix}_min": np.nan,
        f"{prefix}_mean": np.nan,
        f"{prefix}_std": np.nan,
        f"{prefix}_range": np.nan,
        f"{prefix}_top1_top2_gap": np.nan,
        f"{prefix}_top1_mean_gap": np.nan,
        f"{prefix}_top3_mean": np.nan,
        f"{prefix}_bottom3_mean": np.nan,
    }

    if not values:

        return result

    array = np.array(
        values,
        dtype=float,
    )

    sorted_desc = sorted(
        values,
        reverse=True,
    )

    sorted_asc = sorted(
        values,
    )

    max_value = float(
        np.max(array)
    )

    min_value = float(
        np.min(array)
    )

    mean_value = float(
        np.mean(array)
    )

    std_value = float(
        np.std(array)
    )

    result[
        f"{prefix}_max"
    ] = max_value

    result[
        f"{prefix}_min"
    ] = min_value

    result[
        f"{prefix}_mean"
    ] = mean_value

    result[
        f"{prefix}_std"
    ] = std_value

    result[
        f"{prefix}_range"
    ] = max_value - min_value

    if len(sorted_desc) >= 2:

        result[
            f"{prefix}_top1_top2_gap"
        ] = (
            sorted_desc[0]
            - sorted_desc[1]
        )

    result[
        f"{prefix}_top1_mean_gap"
    ] = (
        max_value
        - mean_value
    )

    result[
        f"{prefix}_top3_mean"
    ] = float(
        np.mean(
            sorted_desc[:3]
        )
    )

    result[
        f"{prefix}_bottom3_mean"
    ] = float(
        np.mean(
            sorted_asc[:3]
        )
    )

    return result


# ===========================================================
# カテゴリ人数
# ===========================================================

def count_player_category(
    row,
    suffix,
    target_value,
):

    count = 0

    for player_number in PLAYER_NUMBERS:

        column = (
            f"p{player_number}_{suffix}"
        )

        if column not in row.index:

            continue

        value = row[column]

        if pd.isna(value):

            continue

        if str(value).strip() == target_value:

            count += 1

    return count


# ===========================================================
# 直近着順集約
# ===========================================================

def calculate_recent_summary(row):

    finishes = []

    player_recent_means = []

    recent_first_count = 0
    recent_top3_count = 0
    recent_valid_player_count = 0

    for player_number in PLAYER_NUMBERS:

        player_finishes = []

        for recent_number in range(1, 4):

            column = (
                f"p{player_number}"
                f"_recent_finish_"
                f"{recent_number}"
            )

            if column not in row.index:

                continue

            value = safe_float(
                row[column]
            )

            if value is None:

                continue

            finishes.append(value)
            player_finishes.append(value)

            if value == 1:

                recent_first_count += 1

            if value <= 3:

                recent_top3_count += 1

        if player_finishes:

            recent_valid_player_count += 1

            player_recent_means.append(
                float(
                    np.mean(
                        player_finishes
                    )
                )
            )

    result = {
        "struct_recent_total_valid_count":
            len(finishes),
        "struct_recent_valid_player_count":
            recent_valid_player_count,
        "struct_recent_first_count":
            recent_first_count,
        "struct_recent_top3_count":
            recent_top3_count,
        "struct_recent_finish_mean":
            np.nan,
        "struct_recent_finish_std":
            np.nan,
        "struct_recent_player_mean_best":
            np.nan,
        "struct_recent_player_mean_worst":
            np.nan,
        "struct_recent_player_mean_range":
            np.nan,
    }

    if finishes:

        result[
            "struct_recent_finish_mean"
        ] = float(
            np.mean(finishes)
        )

        result[
            "struct_recent_finish_std"
        ] = float(
            np.std(finishes)
        )

    if player_recent_means:

        best = min(
            player_recent_means
        )

        worst = max(
            player_recent_means
        )

        result[
            "struct_recent_player_mean_best"
        ] = float(best)

        result[
            "struct_recent_player_mean_worst"
        ] = float(worst)

        result[
            "struct_recent_player_mean_range"
        ] = float(
            worst - best
        )

    return result


# ===========================================================
# レース構造特徴量生成
# ===========================================================

def build_structural_features(row):

    features = {}

    for metric in PLAYER_NUMERIC_METRICS:

        features.update(
            calculate_numeric_structure(
                row,
                metric,
            )
        )

    # 脚質人数
    for style in [
        "逃",
        "捲",
        "追",
        "両",
    ]:

        features[
            f"struct_riding_style_{style}_count"
        ] = count_player_category(
            row,
            "riding_style",
            style,
        )

    # 現在級班人数
    for class_name in [
        "SS",
        "S1",
        "S2",
        "A1",
        "A2",
        "A3",
        "L1",
    ]:

        features[
            f"struct_class_{class_name}_count"
        ] = count_player_category(
            row,
            "class",
            class_name,
        )

    # 前期級班人数
    for class_name in [
        "SS",
        "S1",
        "S2",
        "A1",
        "A2",
        "A3",
        "L1",
    ]:

        features[
            f"struct_previous_class_"
            f"{class_name}_count"
        ] = count_player_category(
            row,
            "previous_class",
            class_name,
        )

    # 直近成績集約
    features.update(
        calculate_recent_summary(
            row
        )
    )

    # 車立て
    player_count = int(
        row["player_count"]
    )

    features[
        "struct_player_count"
    ] = player_count

    features[
        "struct_is_5_car"
    ] = int(player_count == 5)

    features[
        "struct_is_6_car"
    ] = int(player_count == 6)

    features[
        "struct_is_7_car"
    ] = int(player_count == 7)

    features[
        "struct_is_8_car"
    ] = int(player_count == 8)

    features[
        "struct_is_9_car"
    ] = int(player_count == 9)

    return features

# ===========================================================
# Pipeline
# ===========================================================

def build_pipeline(
    model,
    categorical_features,
    numeric_features,
):

    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="constant",
                    fill_value="__MISSING__",
                ),
            ),
            (
                "onehot",
                OneHotEncoder(
                    handle_unknown="ignore",
                ),
            ),
        ]
    )

    numeric_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="median",
                ),
            ),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                categorical_pipeline,
                categorical_features,
            ),
            (
                "numeric",
                numeric_pipeline,
                numeric_features,
            ),
        ],
        remainder="drop",
    )

    return Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor,
            ),
            (
                "model",
                model,
            ),
        ]
    )


# ===========================================================
# Ranking評価
# ===========================================================

def analyze_ranking(
    prediction_df,
    probability_column,
):

    ranked = prediction_df.sort_values(
        probability_column,
        ascending=False,
        kind="stable",
    ).reset_index(drop=True)

    total_count = len(ranked)

    total_positive = int(
        ranked[TARGET].sum()
    )

    baseline_rate = (
        total_positive / total_count
        if total_count
        else 0
    )

    results = []

    for percentage in RANKING_PERCENTAGES:

        top_count = max(
            1,
            int(
                total_count * percentage
            ),
        )

        top = ranked.head(
            top_count
        )

        positive_count = int(
            top[TARGET].sum()
        )

        positive_rate = (
            positive_count / top_count
            if top_count
            else 0
        )

        capture_rate = (
            positive_count / total_positive
            if total_positive
            else 0
        )

        lift = (
            positive_rate / baseline_rate
            if baseline_rate
            else 0
        )

        results.append({
            "percentage": percentage,
            "top_count": top_count,
            "positive_count": positive_count,
            "positive_rate": float(
                positive_rate
            ),
            "capture_rate": float(
                capture_rate
            ),
            "lift": float(lift),
        })

    return {
        "total_count": total_count,
        "total_positive": total_positive,
        "baseline_rate": float(
            baseline_rate
        ),
        "ranking_results": results,
    }


# ===========================================================
# モデル生成
# ===========================================================

def model_factories():

    return {
        "logistic_regression":
            lambda: LogisticRegression(
                max_iter=3000,
                class_weight="balanced",
                random_state=RANDOM_STATE,
            ),

        "random_forest":
            lambda: RandomForestClassifier(
                n_estimators=500,
                max_depth=None,
                min_samples_leaf=2,
                class_weight="balanced",
                random_state=RANDOM_STATE,
                n_jobs=-1,
            ),
    }


# ===========================================================
# main
# ===========================================================

def main():

    print(
        "=== 012 レース相対・構造特徴量 "
        "正式生成＋181特徴量直接比較 ==="
    )

    OUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # =======================================================
    # 読込
    # =======================================================

    df = pd.read_csv(
        SOURCE_CSV,
        encoding="utf-8-sig",
    )

    schema = load_json(
        SCHEMA_FILE
    )

    base_feature_names = schema[
        "feature_names"
    ]

    base_categorical_features = schema[
        "categorical_features"
    ]

    base_numeric_features = schema[
        "numeric_features"
    ]

    print()
    print("008 Dataset行数:", len(df))
    print(
        "BASE正式特徴量数:",
        len(base_feature_names),
    )

    # =======================================================
    # 構造特徴量生成
    # =======================================================

    print()
    print(
        "=== 構造特徴量生成開始 ==="
    )

    structural_rows = []

    for index, row in df.iterrows():

        structural_features = (
            build_structural_features(
                row
            )
        )

        structural_rows.append(
            structural_features
        )

        current = index + 1

        if (
            current % 500 == 0
            or current == len(df)
        ):

            print(
                "生成:",
                current,
                "/",
                len(df),
            )

    structural_df = pd.DataFrame(
        structural_rows
    )

    structural_feature_names = list(
        structural_df.columns
    )

    structural_numeric_features = list(
        structural_feature_names
    )

    print()
    print(
        "生成構造特徴量数:",
        len(
            structural_feature_names
        ),
    )

    # =======================================================
    # Dataset結合
    # =======================================================

    full_df = pd.concat(
        [
            df.reset_index(drop=True),
            structural_df.reset_index(
                drop=True
            ),
        ],
        axis=1,
    )

    full_feature_names = (
        list(base_feature_names)
        + structural_feature_names
    )

    full_categorical_features = list(
        base_categorical_features
    )

    full_numeric_features = (
        list(base_numeric_features)
        + structural_numeric_features
    )

    # =======================================================
    # 構造検証
    # =======================================================

    problems = []

    duplicate_structural_names = [
        name
        for name, count in Counter(
            structural_feature_names
        ).items()
        if count > 1
    ]

    duplicate_full_feature_names = [
        name
        for name, count in Counter(
            full_feature_names
        ).items()
        if count > 1
    ]

    base_structural_overlap = sorted(
        set(base_feature_names)
        & set(structural_feature_names)
    )

    if duplicate_structural_names:

        problems.append({
            "problem":
                "DUPLICATE_STRUCTURAL_FEATURE_NAMES",
            "names":
                duplicate_structural_names,
        })

    if duplicate_full_feature_names:

        problems.append({
            "problem":
                "DUPLICATE_FULL_FEATURE_NAMES",
            "names":
                duplicate_full_feature_names,
        })

    if base_structural_overlap:

        problems.append({
            "problem":
                "BASE_STRUCTURAL_FEATURE_OVERLAP",
            "names":
                base_structural_overlap,
        })

    if len(full_df) != len(df):

        problems.append({
            "problem":
                "DATASET_ROW_COUNT_MISMATCH",
        })

    # =======================================================
    # 日付・時系列分割
    # =======================================================

    full_df["race_date"] = (
        full_df["race_date"]
        .apply(normalize_race_date)
    )

    full_df = full_df.sort_values(
        [
            "race_date",
            "race_key",
        ],
        kind="stable",
    ).reset_index(drop=True)

    unique_dates = sorted(
        full_df["race_date"].unique()
    )

    split_date_index = int(
        len(unique_dates)
        * TRAIN_RATIO
    )

    if split_date_index >= len(unique_dates):

        split_date_index = (
            len(unique_dates) - 1
        )

    train_dates = unique_dates[
        :split_date_index
    ]

    test_dates = unique_dates[
        split_date_index:
    ]

    train_df = full_df[
        full_df["race_date"].isin(
            train_dates
        )
    ].copy()

    test_df = full_df[
        full_df["race_date"].isin(
            test_dates
        )
    ].copy()

    y_train = (
        train_df[TARGET]
        .astype(int)
    )

    y_test = (
        test_df[TARGET]
        .astype(int)
    )

    print()
    print("=== Dataset分割 ===")
    print("全レース:", len(full_df))
    print("Train:", len(train_df))
    print("Test:", len(test_df))
    print(
        "Train期間:",
        train_dates[0],
        "->",
        train_dates[-1],
    )
    print(
        "Test期間:",
        test_dates[0],
        "->",
        test_dates[-1],
    )
    print(
        "Train分布:",
        dict(
            Counter(
                y_train.tolist()
            )
        ),
    )
    print(
        "Test分布:",
        dict(
            Counter(
                y_test.tolist()
            )
        ),
    )

    # =======================================================
    # 比較設定
    # =======================================================

    feature_sets = {
        "base_181": {
            "feature_names":
                list(base_feature_names),
            "categorical_features":
                list(
                    base_categorical_features
                ),
            "numeric_features":
                list(
                    base_numeric_features
                ),
        },
        "base_181_plus_structure": {
            "feature_names":
                list(full_feature_names),
            "categorical_features":
                list(
                    full_categorical_features
                ),
            "numeric_features":
                list(
                    full_numeric_features
                ),
        },
    }

    prediction_df = test_df[
        [
            "race_key",
            "race_date",
            "venue",
            "race_no",
            "player_count",
            "payout_class_4",
            "is_20000_plus",
            "is_50000_plus",
        ]
    ].copy()

    all_results = {
        "dataset": {
            "total_race_count":
                len(full_df),
            "train_race_count":
                len(train_df),
            "test_race_count":
                len(test_df),
            "train_first_date":
                train_dates[0],
            "train_last_date":
                train_dates[-1],
            "test_first_date":
                test_dates[0],
            "test_last_date":
                test_dates[-1],
            "target":
                TARGET,
        },
        "features": {
            "base_feature_count":
                len(base_feature_names),
            "structural_feature_count":
                len(
                    structural_feature_names
                ),
            "full_feature_count":
                len(full_feature_names),
            "structural_feature_names":
                structural_feature_names,
        },
        "feature_sets": {},
        "problem_count":
            len(problems),
        "problems":
            problems,
    }

    # =======================================================
    # 学習・比較
    # =======================================================

    for (
        feature_set_name,
        feature_config
    ) in feature_sets.items():

        print()
        print("=" * 80)
        print(
            "FEATURE SET:",
            feature_set_name,
        )
        print(
            "特徴量数:",
            len(
                feature_config[
                    "feature_names"
                ]
            ),
        )
        print("=" * 80)

        X_train = train_df[
            feature_config[
                "feature_names"
            ]
        ].copy()

        X_test = test_df[
            feature_config[
                "feature_names"
            ]
        ].copy()

        feature_set_result = {
            "feature_count":
                len(
                    feature_config[
                        "feature_names"
                    ]
                ),
            "models": {},
        }

        for (
            model_name,
            factory
        ) in model_factories().items():

            print()
            print(
                "--- MODEL:",
                model_name,
                "---",
            )

            pipeline = build_pipeline(
                factory(),
                feature_config[
                    "categorical_features"
                ],
                feature_config[
                    "numeric_features"
                ],
            )

            pipeline.fit(
                X_train,
                y_train,
            )

            probabilities = (
                pipeline.predict_proba(
                    X_test
                )[:, 1]
            )

            probability_column = (
                feature_set_name
                + "__"
                + model_name
                + "__probability"
            )

            prediction_df[
                probability_column
            ] = probabilities

            roc_auc = float(
                roc_auc_score(
                    y_test,
                    probabilities,
                )
            )

            pr_auc = float(
                average_precision_score(
                    y_test,
                    probabilities,
                )
            )

            ranking_result = (
                analyze_ranking(
                    prediction_df,
                    probability_column,
                )
            )

            feature_set_result[
                "models"
            ][
                model_name
            ] = {
                "roc_auc":
                    roc_auc,
                "pr_auc":
                    pr_auc,
                "ranking":
                    ranking_result,
            }

            print(
                "ROC-AUC:",
                round(
                    roc_auc,
                    4,
                ),
            )

            print(
                "PR-AUC:",
                round(
                    pr_auc,
                    4,
                ),
            )

            print("Ranking:")

            for result in (
                ranking_result[
                    "ranking_results"
                ]
            ):

                print(
                    " TOP",
                    int(
                        result[
                            "percentage"
                        ] * 100
                    ),
                    "% |",
                    "件数=",
                    result[
                        "top_count"
                    ],
                    "| Positive=",
                    result[
                        "positive_count"
                    ],
                    "| Positive率=",
                    round(
                        result[
                            "positive_rate"
                        ],
                        4,
                    ),
                    "| Capture=",
                    round(
                        result[
                            "capture_rate"
                        ],
                        4,
                    ),
                    "| Lift=",
                    round(
                        result[
                            "lift"
                        ],
                        3,
                    ),
                )

        all_results[
            "feature_sets"
        ][
            feature_set_name
        ] = feature_set_result

    # =======================================================
    # 保存
    # =======================================================

    full_df.to_csv(
        STRUCTURE_DATASET_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    prediction_df.to_csv(
        TEST_PREDICTION_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    structure_schema = {
        "base_feature_count":
            len(base_feature_names),
        "structural_feature_count":
            len(
                structural_feature_names
            ),
        "full_feature_count":
            len(full_feature_names),
        "structural_feature_names":
            structural_feature_names,
        "structural_numeric_features":
            structural_numeric_features,
        "full_feature_names":
            full_feature_names,
        "full_categorical_features":
            full_categorical_features,
        "full_numeric_features":
            full_numeric_features,
    }

    save_json(
        STRUCTURE_SCHEMA_FILE,
        structure_schema,
    )

    save_json(
        RESULT_FILE,
        all_results,
    )

    # =======================================================
    # 最終表示
    # =======================================================

    print()
    print("=" * 80)
    print("=== 012 最終結果 ===")
    print(
        "BASE特徴量数:",
        len(base_feature_names),
    )
    print(
        "構造特徴量数:",
        len(
            structural_feature_names
        ),
    )
    print(
        "FULL特徴量数:",
        len(full_feature_names),
    )
    print(
        "問題件数:",
        len(problems),
    )

    if problems:

        print()
        print("=== 問題一覧 ===")

        for problem in problems:

            print(problem)

    print()
    print("構造特徴量Dataset保存:")
    print(
        STRUCTURE_DATASET_FILE
    )

    print()
    print("構造特徴量Schema保存:")
    print(
        STRUCTURE_SCHEMA_FILE
    )

    print()
    print("Test予測保存:")
    print(
        TEST_PREDICTION_FILE
    )

    print()
    print("比較結果保存:")
    print(
        RESULT_FILE
    )

    print()
    print("=== 012 完了 ===")


if __name__ == "__main__":

    main()