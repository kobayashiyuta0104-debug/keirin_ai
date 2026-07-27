"""
===========================================================
競輪AI 正式版
011_analyze_feature_importance.py

目的:
・2万円以上モデルの特徴量重要度解析
・Logistic Regression 係数解析
・Random Forest Feature Importance解析
・One-Hot展開後特徴量名を正式追跡
・TOP50 / LOW50 保存
・元181特徴量単位でも重要度集約
・012 相対特徴量設計の基礎資料生成

重要:
・008 Historical Training Dataset使用
・009 / 010と同じ時系列分割
・未来Testを学習に使用しない
===========================================================
"""

import json
import warnings
from pathlib import Path
from collections import defaultdict

import pandas as pd
import numpy as np

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, average_precision_score


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
    / "011_feature_importance"
)

RESULT_FILE = (
    OUT_DIR
    / "011_feature_importance_results.json"
)

LOGISTIC_CSV = (
    OUT_DIR
    / "011_logistic_coefficients.csv"
)

RF_CSV = (
    OUT_DIR
    / "011_random_forest_importance.csv"
)

AGGREGATED_CSV = (
    OUT_DIR
    / "011_original_feature_aggregated_importance.csv"
)


TRAIN_RATIO = 0.80
RANDOM_STATE = 42
TARGET = "is_20000_plus"
TOP_N = 50


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

    pipeline = Pipeline(
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

    return pipeline


# ===========================================================
# 展開後特徴量名
# ===========================================================

def get_transformed_feature_names(
    fitted_pipeline,
    categorical_features,
    numeric_features,
):

    preprocessor = fitted_pipeline.named_steps[
        "preprocessor"
    ]

    categorical_transformer = (
        preprocessor.named_transformers_[
            "categorical"
        ]
    )

    onehot = categorical_transformer.named_steps[
        "onehot"
    ]

    categorical_names = list(
        onehot.get_feature_names_out(
            categorical_features
        )
    )

    transformed_names = (
        categorical_names
        + list(numeric_features)
    )

    return transformed_names


# ===========================================================
# 元特徴量判定
# ===========================================================

def find_original_feature(
    transformed_name,
    categorical_features,
    numeric_features,
):

    if transformed_name in numeric_features:

        return transformed_name

    candidates = []

    for feature in categorical_features:

        prefix = feature + "_"

        if transformed_name.startswith(prefix):

            candidates.append(feature)

    if candidates:

        candidates.sort(
            key=len,
            reverse=True,
        )

        return candidates[0]

    return transformed_name


# ===========================================================
# Logistic解析
# ===========================================================

def analyze_logistic(
    pipeline,
    transformed_names,
    categorical_features,
    numeric_features,
):

    model = pipeline.named_steps[
        "model"
    ]

    coefficients = model.coef_[0]

    rows = []

    for name, coefficient in zip(
        transformed_names,
        coefficients,
    ):

        original_feature = find_original_feature(
            name,
            categorical_features,
            numeric_features,
        )

        rows.append({
            "transformed_feature": name,
            "original_feature": original_feature,
            "coefficient": float(coefficient),
            "absolute_coefficient": float(
                abs(coefficient)
            ),
            "direction": (
                "HIGH_RISK"
                if coefficient > 0
                else "LOW_RISK"
                if coefficient < 0
                else "NEUTRAL"
            ),
        })

    rows.sort(
        key=lambda x: x[
            "absolute_coefficient"
        ],
        reverse=True,
    )

    return rows


# ===========================================================
# Random Forest解析
# ===========================================================

def analyze_random_forest(
    pipeline,
    transformed_names,
    categorical_features,
    numeric_features,
):

    model = pipeline.named_steps[
        "model"
    ]

    importances = model.feature_importances_

    rows = []

    for name, importance in zip(
        transformed_names,
        importances,
    ):

        original_feature = find_original_feature(
            name,
            categorical_features,
            numeric_features,
        )

        rows.append({
            "transformed_feature": name,
            "original_feature": original_feature,
            "importance": float(importance),
        })

    rows.sort(
        key=lambda x: x["importance"],
        reverse=True,
    )

    return rows


# ===========================================================
# 元特徴量単位集約
# ===========================================================

def aggregate_original_features(
    logistic_rows,
    rf_rows,
    feature_names,
):

    logistic_map = defaultdict(float)
    logistic_signed_map = defaultdict(float)
    logistic_count_map = defaultdict(int)

    rf_map = defaultdict(float)
    rf_count_map = defaultdict(int)

    for row in logistic_rows:

        feature = row["original_feature"]

        logistic_map[feature] += row[
            "absolute_coefficient"
        ]

        logistic_signed_map[feature] += row[
            "coefficient"
        ]

        logistic_count_map[feature] += 1

    for row in rf_rows:

        feature = row["original_feature"]

        rf_map[feature] += row[
            "importance"
        ]

        rf_count_map[feature] += 1

    rows = []

    for feature in feature_names:

        rows.append({
            "original_feature": feature,
            "logistic_abs_coefficient_sum":
                float(logistic_map[feature]),
            "logistic_signed_coefficient_sum":
                float(logistic_signed_map[feature]),
            "logistic_expanded_feature_count":
                int(logistic_count_map[feature]),
            "random_forest_importance_sum":
                float(rf_map[feature]),
            "random_forest_expanded_feature_count":
                int(rf_count_map[feature]),
        })

    logistic_max = max(
        (
            row[
                "logistic_abs_coefficient_sum"
            ]
            for row in rows
        ),
        default=0,
    )

    rf_max = max(
        (
            row[
                "random_forest_importance_sum"
            ]
            for row in rows
        ),
        default=0,
    )

    for row in rows:

        logistic_norm = (
            row[
                "logistic_abs_coefficient_sum"
            ] / logistic_max
            if logistic_max
            else 0
        )

        rf_norm = (
            row[
                "random_forest_importance_sum"
            ] / rf_max
            if rf_max
            else 0
        )

        row["logistic_normalized"] = float(
            logistic_norm
        )

        row["random_forest_normalized"] = float(
            rf_norm
        )

        row["combined_score"] = float(
            (
                logistic_norm
                + rf_norm
            ) / 2
        )

    rows.sort(
        key=lambda x: x["combined_score"],
        reverse=True,
    )

    for index, row in enumerate(
        rows,
        start=1,
    ):

        row["combined_rank"] = index

    return rows


# ===========================================================
# 表示
# ===========================================================

def print_logistic_top(rows):

    print()
    print(
        "=== Logistic 高リスク方向 TOP",
        TOP_N,
        "===",
    )

    high_risk = sorted(
        [
            row
            for row in rows
            if row["coefficient"] > 0
        ],
        key=lambda x: x["coefficient"],
        reverse=True,
    )

    for rank, row in enumerate(
        high_risk[:TOP_N],
        start=1,
    ):

        print(
            f"{rank:02d}",
            row["transformed_feature"],
            "| coef=",
            round(
                row["coefficient"],
                6,
            ),
        )


def print_logistic_low(rows):

    print()
    print(
        "=== Logistic 低リスク方向 TOP",
        TOP_N,
        "===",
    )

    low_risk = sorted(
        [
            row
            for row in rows
            if row["coefficient"] < 0
        ],
        key=lambda x: x["coefficient"],
    )

    for rank, row in enumerate(
        low_risk[:TOP_N],
        start=1,
    ):

        print(
            f"{rank:02d}",
            row["transformed_feature"],
            "| coef=",
            round(
                row["coefficient"],
                6,
            ),
        )


def print_rf_top(rows):

    print()
    print(
        "=== Random Forest Importance TOP",
        TOP_N,
        "===",
    )

    for rank, row in enumerate(
        rows[:TOP_N],
        start=1,
    ):

        print(
            f"{rank:02d}",
            row["transformed_feature"],
            "| importance=",
            round(
                row["importance"],
                6,
            ),
        )


def print_aggregated_top(rows):

    print()
    print(
        "=== 元181特徴量 統合重要度 TOP",
        TOP_N,
        "===",
    )

    for row in rows[:TOP_N]:

        print(
            f"{row['combined_rank']:02d}",
            row["original_feature"],
            "| Logistic=",
            round(
                row["logistic_normalized"],
                4,
            ),
            "| RF=",
            round(
                row["random_forest_normalized"],
                4,
            ),
            "| Combined=",
            round(
                row["combined_score"],
                4,
            ),
        )


# ===========================================================
# main
# ===========================================================

def main():

    print(
        "=== 011 特徴量重要度・係数解析 ==="
    )

    OUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df = pd.read_csv(
        SOURCE_CSV,
        encoding="utf-8-sig",
    )

    schema = load_json(
        SCHEMA_FILE
    )

    feature_names = schema[
        "feature_names"
    ]

    categorical_features = schema[
        "categorical_features"
    ]

    numeric_features = schema[
        "numeric_features"
    ]

    df["race_date"] = (
        df["race_date"]
        .apply(normalize_race_date)
    )

    df = df.sort_values(
        [
            "race_date",
            "race_key",
        ],
        kind="stable",
    ).reset_index(drop=True)

    unique_dates = sorted(
        df["race_date"].unique()
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

    train_df = df[
        df["race_date"].isin(
            train_dates
        )
    ].copy()

    test_df = df[
        df["race_date"].isin(
            test_dates
        )
    ].copy()

    X_train = train_df[
        feature_names
    ].copy()

    X_test = test_df[
        feature_names
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
    print("Dataset行数:", len(df))
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
        "正式特徴量数:",
        len(feature_names),
    )

    # =======================================================
    # Logistic Regression
    # =======================================================

    logistic_pipeline = build_pipeline(
        LogisticRegression(
            max_iter=3000,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        categorical_features,
        numeric_features,
    )

    logistic_pipeline.fit(
        X_train,
        y_train,
    )

    logistic_probabilities = (
        logistic_pipeline.predict_proba(
            X_test
        )[:, 1]
    )

    logistic_roc_auc = float(
        roc_auc_score(
            y_test,
            logistic_probabilities,
        )
    )

    logistic_pr_auc = float(
        average_precision_score(
            y_test,
            logistic_probabilities,
        )
    )

    logistic_names = (
        get_transformed_feature_names(
            logistic_pipeline,
            categorical_features,
            numeric_features,
        )
    )

    logistic_rows = analyze_logistic(
        logistic_pipeline,
        logistic_names,
        categorical_features,
        numeric_features,
    )

    # =======================================================
    # Random Forest
    # =======================================================

    rf_pipeline = build_pipeline(
        RandomForestClassifier(
            n_estimators=500,
            max_depth=None,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        categorical_features,
        numeric_features,
    )

    rf_pipeline.fit(
        X_train,
        y_train,
    )

    rf_probabilities = (
        rf_pipeline.predict_proba(
            X_test
        )[:, 1]
    )

    rf_roc_auc = float(
        roc_auc_score(
            y_test,
            rf_probabilities,
        )
    )

    rf_pr_auc = float(
        average_precision_score(
            y_test,
            rf_probabilities,
        )
    )

    rf_names = (
        get_transformed_feature_names(
            rf_pipeline,
            categorical_features,
            numeric_features,
        )
    )

    rf_rows = analyze_random_forest(
        rf_pipeline,
        rf_names,
        categorical_features,
        numeric_features,
    )

    # =======================================================
    # 構造検証
    # =======================================================

    problems = []

    if len(logistic_names) != len(
        logistic_pipeline.named_steps[
            "model"
        ].coef_[0]
    ):

        problems.append(
            "LOGISTIC_FEATURE_LENGTH_MISMATCH"
        )

    if len(rf_names) != len(
        rf_pipeline.named_steps[
            "model"
        ].feature_importances_
    ):

        problems.append(
            "RF_FEATURE_LENGTH_MISMATCH"
        )

    # =======================================================
    # 元特徴量集約
    # =======================================================

    aggregated_rows = (
        aggregate_original_features(
            logistic_rows,
            rf_rows,
            feature_names,
        )
    )

    # =======================================================
    # CSV保存
    # =======================================================

    pd.DataFrame(
        logistic_rows
    ).to_csv(
        LOGISTIC_CSV,
        index=False,
        encoding="utf-8-sig",
    )

    pd.DataFrame(
        rf_rows
    ).to_csv(
        RF_CSV,
        index=False,
        encoding="utf-8-sig",
    )

    pd.DataFrame(
        aggregated_rows
    ).to_csv(
        AGGREGATED_CSV,
        index=False,
        encoding="utf-8-sig",
    )

    # =======================================================
    # JSON保存
    # =======================================================

    high_risk_logistic = sorted(
        [
            row
            for row in logistic_rows
            if row["coefficient"] > 0
        ],
        key=lambda x: x["coefficient"],
        reverse=True,
    )

    low_risk_logistic = sorted(
        [
            row
            for row in logistic_rows
            if row["coefficient"] < 0
        ],
        key=lambda x: x["coefficient"],
    )

    result = {
        "dataset": {
            "total_race_count": len(df),
            "train_race_count": len(train_df),
            "test_race_count": len(test_df),
            "train_first_date": train_dates[0],
            "train_last_date": train_dates[-1],
            "test_first_date": test_dates[0],
            "test_last_date": test_dates[-1],
            "original_feature_count":
                len(feature_names),
        },
        "logistic_regression": {
            "roc_auc": logistic_roc_auc,
            "pr_auc": logistic_pr_auc,
            "transformed_feature_count":
                len(logistic_names),
            "high_risk_top50":
                high_risk_logistic[:TOP_N],
            "low_risk_top50":
                low_risk_logistic[:TOP_N],
        },
        "random_forest": {
            "roc_auc": rf_roc_auc,
            "pr_auc": rf_pr_auc,
            "transformed_feature_count":
                len(rf_names),
            "importance_top50":
                rf_rows[:TOP_N],
        },
        "original_feature_aggregation": {
            "top50":
                aggregated_rows[:TOP_N],
            "bottom50":
                aggregated_rows[-TOP_N:],
        },
        "problem_count": len(problems),
        "problems": problems,
    }

    save_json(
        RESULT_FILE,
        result,
    )

    # =======================================================
    # 表示
    # =======================================================

    print()
    print("=== 011 モデル結果 ===")

    print()
    print("Logistic Regression")
    print(
        "ROC-AUC:",
        round(
            logistic_roc_auc,
            4,
        ),
    )
    print(
        "PR-AUC:",
        round(
            logistic_pr_auc,
            4,
        ),
    )
    print(
        "展開後特徴量数:",
        len(logistic_names),
    )

    print()
    print("Random Forest")
    print(
        "ROC-AUC:",
        round(
            rf_roc_auc,
            4,
        ),
    )
    print(
        "PR-AUC:",
        round(
            rf_pr_auc,
            4,
        ),
    )
    print(
        "展開後特徴量数:",
        len(rf_names),
    )

    print_logistic_top(
        logistic_rows
    )

    print_logistic_low(
        logistic_rows
    )

    print_rf_top(
        rf_rows
    )

    print_aggregated_top(
        aggregated_rows
    )

    print()
    print("=== 011 最終結果 ===")
    print(
        "元特徴量数:",
        len(feature_names),
    )
    print(
        "Logistic展開後特徴量数:",
        len(logistic_names),
    )
    print(
        "RF展開後特徴量数:",
        len(rf_names),
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
    print("Logistic CSV保存:")
    print(LOGISTIC_CSV)

    print()
    print("Random Forest CSV保存:")
    print(RF_CSV)

    print()
    print("元特徴量統合CSV保存:")
    print(AGGREGATED_CSV)

    print()
    print("解析JSON保存:")
    print(RESULT_FILE)

    print()
    print("=== 011 完了 ===")


if __name__ == "__main__":

    main()