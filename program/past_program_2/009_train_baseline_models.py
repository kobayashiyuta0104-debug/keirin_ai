"""
===========================================================
競輪AI 正式版
009_train_baseline_models.py

008 Historical Training Dataset
↓
日付順 Train / Test 分割
↓
前処理
・カテゴリ: 欠損補完 + OneHot
・数値: 中央値補完
↓
Baseline Model比較
・Logistic Regression
・Random Forest

Target:
・is_20000_plus
・is_50000_plus

評価:
・Accuracy
・Precision
・Recall
・F1
・ROC-AUC
・PR-AUC
・Confusion Matrix

重要:
・ランダム分割禁止
・過去 -> 未来の時系列評価
・Meta列、Target列は特徴量に使用しない
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
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
)

warnings.filterwarnings(
    "ignore"
)


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
    / "009_baseline"
)

RESULT_FILE = (
    OUT_DIR
    / "009_baseline_results.json"
)


# ===========================================================
# 設定
# ===========================================================

TRAIN_RATIO = 0.80

RANDOM_STATE = 42

TARGETS = [
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
# 日付正規化
# ===========================================================

def normalize_race_date(value):

    text = str(
        value
    ).strip()

    text = text.replace(
        "-",
        "",
    )

    text = text.replace(
        "/",
        "",
    )

    return text


# ===========================================================
# 評価
# ===========================================================

def evaluate_model(
    y_true,
    y_pred,
    y_probability,
):

    cm = confusion_matrix(
        y_true,
        y_pred,
        labels=[
            0,
            1,
        ],
    )

    tn, fp, fn, tp = (
        cm.ravel()
    )

    return {

        "accuracy":
            float(
                accuracy_score(
                    y_true,
                    y_pred,
                )
            ),

        "precision":
            float(
                precision_score(
                    y_true,
                    y_pred,
                    zero_division=0,
                )
            ),

        "recall":
            float(
                recall_score(
                    y_true,
                    y_pred,
                    zero_division=0,
                )
            ),

        "f1":
            float(
                f1_score(
                    y_true,
                    y_pred,
                    zero_division=0,
                )
            ),

        "roc_auc":
            float(
                roc_auc_score(
                    y_true,
                    y_probability,
                )
            ),

        "pr_auc":
            float(
                average_precision_score(
                    y_true,
                    y_probability,
                )
            ),

        "confusion_matrix": {

            "tn":
                int(tn),

            "fp":
                int(fp),

            "fn":
                int(fn),

            "tp":
                int(tp),

        },

        "predicted_positive_count":
            int(
                sum(
                    y_pred
                )
            ),

        "actual_positive_count":
            int(
                sum(
                    y_true
                )
            ),

    }


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
# main
# ===========================================================

def main():

    print(
        "=== 009 初回Baseline AI "
        "時系列学習・評価 ==="
    )

    OUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # -------------------------------------------------------
    # Dataset
    # -------------------------------------------------------

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

    print(
        "Dataset行数:",
        len(df),
    )

    print(
        "特徴量数:",
        len(feature_names),
    )

    print(
        "カテゴリ特徴量:",
        len(categorical_features),
    )

    print(
        "数値特徴量:",
        len(numeric_features),
    )

    # -------------------------------------------------------
    # race_date
    # -------------------------------------------------------

    df[
        "race_date"
    ] = (
        df[
            "race_date"
        ]
        .apply(
            normalize_race_date
        )
    )

    # -------------------------------------------------------
    # 時系列Sort
    # -------------------------------------------------------

    df = df.sort_values(
        by=[
            "race_date",
            "race_key",
        ],
        kind="stable",
    ).reset_index(
        drop=True
    )

    unique_dates = sorted(
        df[
            "race_date"
        ].unique()
    )

    print(
        "対象日数:",
        len(unique_dates),
    )

    print(
        "最古日:",
        unique_dates[0],
    )

    print(
        "最新日:",
        unique_dates[-1],
    )

    # -------------------------------------------------------
    # 日付単位80/20 split
    # -------------------------------------------------------

    split_date_index = int(
        len(unique_dates)
        * TRAIN_RATIO
    )

    if split_date_index <= 0:

        raise RuntimeError(
            "Train日付数が0"
        )

    if split_date_index >= len(
        unique_dates
    ):

        split_date_index = (
            len(unique_dates)
            - 1
        )

    train_dates = unique_dates[
        :split_date_index
    ]

    test_dates = unique_dates[
        split_date_index:
    ]

    train_df = df[
        df[
            "race_date"
        ].isin(
            train_dates
        )
    ].copy()

    test_df = df[
        df[
            "race_date"
        ].isin(
            test_dates
        )
    ].copy()

    print()
    print(
        "=== 時系列分割 ==="
    )

    print(
        "Train日数:",
        len(train_dates),
    )

    print(
        "Test日数:",
        len(test_dates),
    )

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
        "Trainレース数:",
        len(train_df),
    )

    print(
        "Testレース数:",
        len(test_df),
    )

    # -------------------------------------------------------
    # X
    # -------------------------------------------------------

    X_train = train_df[
        feature_names
    ].copy()

    X_test = test_df[
        feature_names
    ].copy()

    # -------------------------------------------------------
    # モデル定義
    # -------------------------------------------------------

    model_definitions = {

        "logistic_regression":

            LogisticRegression(

                max_iter=3000,

                class_weight="balanced",

                random_state=RANDOM_STATE,

            ),

        "random_forest":

            RandomForestClassifier(

                n_estimators=500,

                max_depth=None,

                min_samples_leaf=2,

                class_weight="balanced",

                random_state=RANDOM_STATE,

                n_jobs=-1,

            ),

    }

    # -------------------------------------------------------
    # 結果
    # -------------------------------------------------------

    all_results = {

        "dataset": {

            "source_csv":
                str(
                    SOURCE_CSV
                ),

            "row_count":
                len(df),

            "feature_count":
                len(feature_names),

            "categorical_feature_count":
                len(
                    categorical_features
                ),

            "numeric_feature_count":
                len(
                    numeric_features
                ),

            "date_count":
                len(unique_dates),

            "first_date":
                unique_dates[0],

            "last_date":
                unique_dates[-1],

        },

        "split": {

            "method":
                "date_order_80_20",

            "train_date_count":
                len(train_dates),

            "test_date_count":
                len(test_dates),

            "train_first_date":
                train_dates[0],

            "train_last_date":
                train_dates[-1],

            "test_first_date":
                test_dates[0],

            "test_last_date":
                test_dates[-1],

            "train_race_count":
                len(train_df),

            "test_race_count":
                len(test_df),

        },

        "targets": {},

    }

    # -------------------------------------------------------
    # Target Loop
    # -------------------------------------------------------

    for target in TARGETS:

        print()
        print(
            "=" * 70
        )

        print(
            "TARGET:",
            target,
        )

        print(
            "=" * 70
        )

        y_train = (
            train_df[
                target
            ]
            .astype(int)
        )

        y_test = (
            test_df[
                target
            ]
            .astype(int)
        )

        train_distribution = Counter(
            y_train.tolist()
        )

        test_distribution = Counter(
            y_test.tolist()
        )

        print(
            "Train分布:",
            dict(
                train_distribution
            ),
        )

        print(
            "Test分布:",
            dict(
                test_distribution
            ),
        )

        target_result = {

            "train_distribution":
                {
                    str(k): int(v)
                    for k, v
                    in train_distribution.items()
                },

            "test_distribution":
                {
                    str(k): int(v)
                    for k, v
                    in test_distribution.items()
                },

            "models": {},

        }

        # ---------------------------------------------------
        # Model Loop
        # ---------------------------------------------------

        for (
            model_name,
            model,
        ) in model_definitions.items():

            print()
            print(
                "--- MODEL:",
                model_name,
                "---"
            )

            pipeline = build_pipeline(

                model,

                categorical_features,

                numeric_features,

            )

            pipeline.fit(
                X_train,
                y_train,
            )

            y_probability = (
                pipeline.predict_proba(
                    X_test
                )[:, 1]
            )

            y_pred = (
                y_probability
                >= 0.5
            ).astype(
                int
            )

            metrics = evaluate_model(

                y_test,

                y_pred,

                y_probability,

            )

            target_result[
                "models"
            ][
                model_name
            ] = metrics

            print(
                "Accuracy:",
                round(
                    metrics[
                        "accuracy"
                    ],
                    4,
                ),
            )

            print(
                "Precision:",
                round(
                    metrics[
                        "precision"
                    ],
                    4,
                ),
            )

            print(
                "Recall:",
                round(
                    metrics[
                        "recall"
                    ],
                    4,
                ),
            )

            print(
                "F1:",
                round(
                    metrics[
                        "f1"
                    ],
                    4,
                ),
            )

            print(
                "ROC-AUC:",
                round(
                    metrics[
                        "roc_auc"
                    ],
                    4,
                ),
            )

            print(
                "PR-AUC:",
                round(
                    metrics[
                        "pr_auc"
                    ],
                    4,
                ),
            )

            print(
                "Confusion Matrix:",
                metrics[
                    "confusion_matrix"
                ],
            )

            print(
                "予測Positive:",
                metrics[
                    "predicted_positive_count"
                ],
            )

            print(
                "実Positive:",
                metrics[
                    "actual_positive_count"
                ],
            )

        all_results[
            "targets"
        ][
            target
        ] = target_result

    # -------------------------------------------------------
    # 保存
    # -------------------------------------------------------

    save_json(
        RESULT_FILE,
        all_results,
    )

    print()
    print(
        "=" * 70
    )

    print(
        "=== 009 最終結果 ==="
    )

    print(
        "Dataset行数:",
        len(df),
    )

    print(
        "Train:",
        len(train_df),
    )

    print(
        "Test:",
        len(test_df),
    )

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

    for target in TARGETS:

        print()
        print(
            "TARGET:",
            target,
        )

        target_result = (
            all_results[
                "targets"
            ][
                target
            ]
        )

        for (
            model_name,
            metrics,
        ) in target_result[
            "models"
        ].items():

            print()

            print(
                model_name
            )

            print(
                "  Precision:",
                round(
                    metrics[
                        "precision"
                    ],
                    4,
                ),
            )

            print(
                "  Recall:",
                round(
                    metrics[
                        "recall"
                    ],
                    4,
                ),
            )

            print(
                "  F1:",
                round(
                    metrics[
                        "f1"
                    ],
                    4,
                ),
            )

            print(
                "  ROC-AUC:",
                round(
                    metrics[
                        "roc_auc"
                    ],
                    4,
                ),
            )

            print(
                "  PR-AUC:",
                round(
                    metrics[
                        "pr_auc"
                    ],
                    4,
                ),
            )

            print(
                "  CM:",
                metrics[
                    "confusion_matrix"
                ],
            )

    print()
    print(
        "結果保存:"
    )

    print(
        RESULT_FILE
    )

    print()
    print(
        "=== 009 完了 ==="
    )


if __name__ == "__main__":

    main()