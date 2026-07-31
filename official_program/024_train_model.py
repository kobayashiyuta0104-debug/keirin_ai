"""
===========================================================
競輪AI Ver1.0
024_train_model.py

AIモデル学習

【役割】

training_race_features.csv

↓

学習データ作成

↓

Part2
LightGBM学習

↓

Part3
モデル保存

===========================================================
"""

import json
import shutil

from datetime import datetime
import joblib
import os

import pandas as pd

import lightgbm as lgb

from sklearn.model_selection import train_test_split

from sklearn.metrics import (

    accuracy_score,

    classification_report,

)

from pathlib import Path


# ===========================================================
# GitHub対応
# ===========================================================

if os.name == "nt":

    BASE = Path(r"C:\競輪AI")

else:

    BASE = Path(__file__).resolve().parent.parent


# ===========================================================
# パス
# ===========================================================

CSV_AI = (
    BASE
    / "csv"
    / "ai"
)

MODEL_DIR = (
    BASE
    / "model"
)

BACKUP_DIR = (

    MODEL_DIR

    / "backup"

)

MODEL_FILE = (

    MODEL_DIR

    / "lightgbm_model.pkl"

)

FEATURE_FILE = (

    MODEL_DIR

    / "feature_columns.json"

)

IMPORTANCE_FILE = (

    MODEL_DIR

    / "feature_importance.csv"

)

INPUT_CSV = (
    CSV_AI
    / "training_race_features.csv"
)

MODEL_DIR.mkdir(

    parents=True,

    exist_ok=True,

)


# ===========================================================
# ログ
# ===========================================================

def log(message):

    print(f"[024_train_model] {message}")


# ===========================================================
# CSV読込
# ===========================================================

def load_training_features():

    log("=======================================")
    log("training_race_features.csv 読込")
    log("=======================================")

    if not INPUT_CSV.exists():

        raise FileNotFoundError(INPUT_CSV)

    df = pd.read_csv(

        INPUT_CSV,

        encoding="utf-8-sig",

        low_memory=False,

    )

    log(f"Rows    : {len(df):,}")

    log(f"Columns : {len(df.columns):,}")

    print()

    return df


# ===========================================================
# 学習データ作成
# ===========================================================

def build_train_dataset(df):

    log("=======================================")
    log("学習データ作成")
    log("=======================================")

    TARGET_COLUMN = "payout_class"

    DROP_COLUMNS = [

        "race_key",

        "date",

        TARGET_COLUMN,

    ]

    feature_columns = [

        c

        for c in df.columns

        if c not in DROP_COLUMNS

    ]

    X = df[feature_columns].copy()

    y = df[TARGET_COLUMN].copy()

    log(f"Feature数 : {len(feature_columns)}")

    log(f"Target    : {TARGET_COLUMN}")

    log(f"Rows      : {len(X):,}")

    print()

    return (

        X,

        y,

        feature_columns,

    )

# ===========================================================
# LightGBM学習
# ===========================================================

def train_model(

    X,

    y,

    feature_columns,

):

    log("=======================================")
    log("LightGBM 学習開始")
    log("=======================================")

    # --------------------------------------------------
    # カテゴリ列
    # --------------------------------------------------

    categorical_columns = [

        "jo_name",

        "grade",

        "race_type",

        "session",

        "weekday",

        "bank_type",

        "straight_type",

    ]

    for col in categorical_columns:

        if col in X.columns:

            X[col] = X[col].astype("category")

    # --------------------------------------------------
    # Train / Valid
    # --------------------------------------------------

    X_train, X_valid, y_train, y_valid = train_test_split(

        X,

        y,

        test_size=0.2,

        random_state=42,

        stratify=y,

    )

    log(f"Train : {len(X_train):,}")

    log(f"Valid : {len(X_valid):,}")

    print()

    # --------------------------------------------------
    # モデル
    # --------------------------------------------------

    model = lgb.LGBMClassifier(

        objective="multiclass",

        num_class=len(sorted(y.unique())),

        n_estimators=300,

        learning_rate=0.05,

        random_state=42,

        class_weight="balanced",

    )

    model.fit(

        X_train,

        y_train,

        eval_set=[

            (X_valid, y_valid),

        ],

        categorical_feature=categorical_columns,

    )

    # --------------------------------------------------
    # 評価
    # --------------------------------------------------

    pred = model.predict(X_valid)

    acc = accuracy_score(

        y_valid,

        pred,

    )

    log(f"Accuracy : {acc:.5f}")

    print()

    print("Classification Report")

    print()

    print(

        classification_report(

            y_valid,

            pred,

        )

    )

    print()

    log("=======================================")
    log("Feature Importance")
    log("=======================================")

    importance = (

        pd.DataFrame(

            {

                "feature": feature_columns,

                "importance": model.feature_importances_,

            }

        )

        .sort_values(

            "importance",

            ascending=False,

        )

    )

    print(

        importance.head(30)

    )

    print()

    return (

        model,

        feature_columns,

        importance,

    )
# ===========================================================
# モデル保存
# ===========================================================

def save_model(

    model,

    feature_columns,

    importance,

):

    log("=======================================")
    log("モデル保存")
    log("=======================================")

    MODEL_DIR.mkdir(

        parents=True,

        exist_ok=True,

    )

    BACKUP_DIR.mkdir(

        parents=True,

        exist_ok=True,

    )

    # --------------------------------------------------
    # Backup
    # --------------------------------------------------

    if MODEL_FILE.exists():

        timestamp = datetime.now().strftime(

            "%Y%m%d_%H%M%S"

        )

        shutil.copy2(

            MODEL_FILE,

            BACKUP_DIR
            / f"lightgbm_model_{timestamp}.pkl",

        )

        log("Model Backup 完了")

    if FEATURE_FILE.exists():

        timestamp = datetime.now().strftime(

            "%Y%m%d_%H%M%S"

        )

        shutil.copy2(

            FEATURE_FILE,

            BACKUP_DIR
            / f"feature_columns_{timestamp}.json",

        )

        log("Feature Backup 完了")

    # --------------------------------------------------
    # 保存
    # --------------------------------------------------

    joblib.dump(

        model,

        MODEL_FILE,

    )

    with open(

        FEATURE_FILE,

        "w",

        encoding="utf-8",

    ) as f:

        json.dump(

            feature_columns,

            f,

            ensure_ascii=False,

            indent=4,

        )

    importance.to_csv(

        IMPORTANCE_FILE,

        index=False,

        encoding="utf-8-sig",

    )

    log(f"Importance : {IMPORTANCE_FILE}")

    print()

    log(f"Model   : {MODEL_FILE}")

    log(f"Feature : {FEATURE_FILE}")

    print()

    log("保存完了")

# ===========================================================
# Main
# ===========================================================

def main():

    print()

    log("=======================================")
    log("024 Train Model")
    log("=======================================")

    df = load_training_features()

    X, y, feature_columns = build_train_dataset(df)

    model, feature_columns, importance = train_model(

        X,

        y,

        feature_columns,

    )

    save_model(

        model,

        feature_columns,

        importance,

    )
    log("Part2 Complete")

# ===========================================================
# 実行
# ===========================================================

if __name__ == "__main__":

    main()

