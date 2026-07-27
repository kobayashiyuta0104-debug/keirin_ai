"""
===========================================================
競輪AI 正式版
010_analyze_risk_ranking.py

目的:
・AI予測確率による荒れレース順位付け能力を検証
・0.05～0.95 閾値総当たり
・上位5% / 10% / 20% / 30% / 40% / 50% 検証
・2万円以上モデル順位内に5万円以上が集まるか確認
・Logistic Regression / Random Forest 比較

重要:
・009と完全同一の時系列分割
・Train: 過去
・Test: 未来
・Testデータのみでランキング評価
===========================================================
"""

import json
import warnings
from pathlib import Path
from collections import Counter

import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
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
    / "010_risk_ranking"
)

RESULT_FILE = (
    OUT_DIR
    / "010_risk_ranking_results.json"
)

PREDICTION_FILE = (
    OUT_DIR
    / "010_test_predictions.csv"
)


TRAIN_RATIO = 0.80
RANDOM_STATE = 42

TARGETS = [
    "is_20000_plus",
    "is_50000_plus",
]

RANKING_PERCENTAGES = [
    0.05,
    0.10,
    0.20,
    0.30,
    0.40,
    0.50,
]

THRESHOLDS = [
    x / 100
    for x in range(5, 96, 5)
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
# 閾値評価
# ===========================================================

def analyze_thresholds(
    y_true,
    probabilities,
):

    results = []

    for threshold in THRESHOLDS:

        predictions = (
            probabilities >= threshold
        ).astype(int)

        cm = confusion_matrix(
            y_true,
            predictions,
            labels=[0, 1],
        )

        tn, fp, fn, tp = cm.ravel()

        results.append({
            "threshold": threshold,
            "precision": float(
                precision_score(
                    y_true,
                    predictions,
                    zero_division=0,
                )
            ),
            "recall": float(
                recall_score(
                    y_true,
                    predictions,
                    zero_division=0,
                )
            ),
            "f1": float(
                f1_score(
                    y_true,
                    predictions,
                    zero_division=0,
                )
            ),
            "predicted_positive_count": int(
                predictions.sum()
            ),
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp),
        })

    return results


# ===========================================================
# Ranking評価
# ===========================================================

def analyze_ranking(
    prediction_df,
    probability_column,
    target_column,
):

    ranked = prediction_df.sort_values(
        probability_column,
        ascending=False,
        kind="stable",
    ).reset_index(drop=True)

    total_count = len(ranked)

    total_positive = int(
        ranked[target_column].sum()
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
            top[target_column].sum()
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
            "positive_rate": positive_rate,
            "capture_rate": capture_rate,
            "lift": lift,
        })

    return {
        "total_count": total_count,
        "total_positive": total_positive,
        "baseline_rate": baseline_rate,
        "ranking_results": results,
    }


# ===========================================================
# 2万円モデル内の5万円分析
# ===========================================================

def analyze_50000_inside_20000_ranking(
    prediction_df,
    probability_column,
):

    ranked = prediction_df.sort_values(
        probability_column,
        ascending=False,
        kind="stable",
    ).reset_index(drop=True)

    total_count = len(ranked)

    total_50000 = int(
        ranked["is_50000_plus"].sum()
    )

    baseline_50000_rate = (
        total_50000 / total_count
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

        count_50000 = int(
            top["is_50000_plus"].sum()
        )

        rate_50000 = (
            count_50000 / top_count
            if top_count
            else 0
        )

        capture_rate = (
            count_50000 / total_50000
            if total_50000
            else 0
        )

        lift = (
            rate_50000 / baseline_50000_rate
            if baseline_50000_rate
            else 0
        )

        results.append({
            "percentage": percentage,
            "top_count": top_count,
            "50000_plus_count": count_50000,
            "50000_plus_rate": rate_50000,
            "capture_rate": capture_rate,
            "lift": lift,
        })

    return {
        "total_50000_plus": total_50000,
        "baseline_50000_plus_rate": baseline_50000_rate,
        "ranking_results": results,
    }


# ===========================================================
# main
# ===========================================================

def main():

    print(
        "=== 010 荒れレース順位付け・"
        "閾値総当たり検証 ==="
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

    print()
    print("=== Dataset ===")
    print("全レース:", len(df))
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

    models = {
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

    prediction_df = test_df[
        [
            "race_key",
            "race_date",
            "venue",
            "race_no",
            "payout_class_4",
            "is_20000_plus",
            "is_50000_plus",
        ]
    ].copy()

    all_results = {
        "dataset": {
            "total_race_count": len(df),
            "train_race_count": len(train_df),
            "test_race_count": len(test_df),
            "train_first_date": train_dates[0],
            "train_last_date": train_dates[-1],
            "test_first_date": test_dates[0],
            "test_last_date": test_dates[-1],
        },
        "targets": {},
    }

    for target in TARGETS:

        print()
        print("=" * 80)
        print("TARGET:", target)
        print("=" * 80)

        y_train = (
            train_df[target]
            .astype(int)
        )

        y_test = (
            test_df[target]
            .astype(int)
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

        target_result = {
            "models": {},
        }

        for model_name, model_factory in models.items():

            print()
            print(
                "--- MODEL:",
                model_name,
                "---",
            )

            pipeline = build_pipeline(
                model_factory(),
                categorical_features,
                numeric_features,
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
                f"{target}__"
                f"{model_name}__probability"
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

            threshold_results = analyze_thresholds(
                y_test,
                probabilities,
            )

            ranking_result = analyze_ranking(
                prediction_df,
                probability_column,
                target,
            )

            model_result = {
                "roc_auc": roc_auc,
                "pr_auc": pr_auc,
                "threshold_results":
                    threshold_results,
                "ranking":
                    ranking_result,
            }

            if target == "is_20000_plus":

                model_result[
                    "50000_plus_inside_20000_ranking"
                ] = (
                    analyze_50000_inside_20000_ranking(
                        prediction_df,
                        probability_column,
                    )
                )

            target_result[
                "models"
            ][
                model_name
            ] = model_result

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

            print()
            print(
                "Ranking:"
            )

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

            if target == "is_20000_plus":

                print()
                print(
                    "2万円モデル順位内 "
                    "5万円以上:"
                )

                inside_result = model_result[
                    "50000_plus_inside_20000_ranking"
                ]

                for result in (
                    inside_result[
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
                        "| 5万円+=",
                        result[
                            "50000_plus_count"
                        ],
                        "| 率=",
                        round(
                            result[
                                "50000_plus_rate"
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
            "targets"
        ][
            target
        ] = target_result

    prediction_df.to_csv(
        PREDICTION_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    save_json(
        RESULT_FILE,
        all_results,
    )

    print()
    print("=" * 80)
    print("=== 010 最終結果 ===")
    print("Testレース数:", len(test_df))

    print()
    print(
        "Test 2万円以上:",
        int(
            test_df[
                "is_20000_plus"
            ].sum()
        ),
    )

    print(
        "Test 5万円以上:",
        int(
            test_df[
                "is_50000_plus"
            ].sum()
        ),
    )

    print()
    print("予測CSV保存:")
    print(PREDICTION_FILE)

    print()
    print("検証結果保存:")
    print(RESULT_FILE)

    print()
    print("=== 010 完了 ===")


if __name__ == "__main__":

    main()