"""
===========================================================
競輪AI Ver1.0
025_predict_today.py

当日AI予測

【役割】

today_race_features.csv

↓

学習済みモデル読込

↓

特徴量チェック

↓

AI予測

↓

today_prediction.csv 保存

===========================================================
"""

import os
import json
import joblib
from datetime import datetime
import pandas as pd

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

PREDICTION_DIR = (
    BASE
    / "csv"
    / "prediction"
)

MODEL_DIR = (
    BASE
    / "model"
)

INPUT_CSV = (
    CSV_AI
    / "today_race_features.csv"
)

MODEL_FILE = (
    MODEL_DIR
    / "lightgbm_model.pkl"
)

FEATURE_FILE = (
    MODEL_DIR
    / "feature_columns.json"
)

PREDICTION_DIR.mkdir(

    parents=True,

    exist_ok=True,

)


# ===========================================================
# ログ
# ===========================================================

def log(message):

    print(f"[025_predict_today] {message}")


# ===========================================================
# CSV読込
# ===========================================================

def load_today_features():

    log("=======================================")
    log("today_race_features.csv 読込")
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
# モデル読込
# ===========================================================

def load_model():

    log("=======================================")
    log("Model Load")
    log("=======================================")

    if not MODEL_FILE.exists():

        raise FileNotFoundError(MODEL_FILE)

    if not FEATURE_FILE.exists():

        raise FileNotFoundError(FEATURE_FILE)

    model = joblib.load(

        MODEL_FILE,

    )

    with open(

        FEATURE_FILE,

        "r",

        encoding="utf-8",

    ) as f:

        feature_columns = json.load(f)

    log("Model OK")

    print()

    return (

        model,

        feature_columns,

    )

# ===========================================================
# 予測データ作成
# ===========================================================

def build_prediction_dataset(

    df,

    feature_columns,

):

    log("=======================================")
    log("Feature Check")
    log("=======================================")

    # --------------------------------------------------
    # 不足列
    # --------------------------------------------------

    missing_columns = [

        c

        for c in feature_columns

        if c not in df.columns

    ]

    # --------------------------------------------------
    # 余分列
    # --------------------------------------------------

    extra_columns = [

        c

        for c in df.columns

        if c not in feature_columns

    ]

    print()

    log(f"学習列数 : {len(feature_columns)}")

    log(f"予測列数 : {len(df.columns)}")

    print()

    log(f"不足列 : {len(missing_columns)}")

    log(f"余分列 : {len(extra_columns)}")

    print()

    if missing_columns:

        print("===== Missing Columns =====")

        for col in missing_columns:

            print(col)

        raise ValueError("不足列があります")

    print("Feature Check OK")

    print()

    # --------------------------------------------------
    # 学習時と同じ順番
    # --------------------------------------------------

    X = df[feature_columns].copy()

    # --------------------------------------------------
    # category
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

    return X


# ===========================================================
# AI予測
# ===========================================================

def predict(

    model,

    X,

    df,

):

    log("=======================================")
    log("Prediction")
    log("=======================================")

    # ------------------------------
    # クラス予測
    # ------------------------------

    pred = model.predict(

        X

    )

    # ------------------------------
    # 確率
    # ------------------------------

    prob = model.predict_proba(

        X

    )

    result = df.copy()

    result["predict_class"] = pred

    result["predict_probability"] = prob.max(axis=1)

    CLASS_NAME = {
        0: "0～9,999円",
        1: "10,000～29,999円",
        2: "30,000～49,999円",
        3: "50,000～99,999円",
        4: "100,000円以上",
    }

    result["AI予想"] = (
        result["predict_class"]
        .map(CLASS_NAME)
    )

    result["AI確信度"] = (
        result["predict_probability"] * 100
    ).round(0).astype(int).astype(str) + "%"

    PROB_COLUMNS = [

        "0～\n9,999",

        "10,000～\n29,999",

        "30,000～\n49,999",

        "50,000～\n99,999",

        "100,000\n以上",

    ]

    for i, column in enumerate(PROB_COLUMNS):

        result[column] = (

            prob[:, i] * 100

        ).round(0).astype(int).astype(str) + "%"

    log(f"Rows : {len(result):,}")

    print()

    return result

# ===========================================================
# CSV保存
# ===========================================================

def save_prediction(result):

    log("=======================================")
    log("CSV Save")
    log("=======================================")

    # --------------------------------------------------
    # 出力列
    # --------------------------------------------------

    session_order = {

        "モーニング": 0,

        "デイ": 1,

        "ナイター": 2,

        "ミッドナイト": 3,

    }

    result["session_order"] = (

        result["session"]

        .map(session_order)

    )

    result = result.sort_values(

        [

            "session_order",

            "jo_name",

            "race_no",

        ]

    )

    result = result.drop(

        columns=[

            "session_order",

        ]

    )

    result = result.rename(

        columns={

            "date": "日付",

            "jo_name": "競輪場",

            "race_no": "レース\n番号",

            "race_time": "発走\n時刻",

            "session": "開催区分",

        }

    )

    result["レース\n番号"] = (
        result["レース\n番号"].astype(str) + "R"
    )

    result = result[

        [

            "日付",

            "競輪場",

            "レース\n番号",

            "発走\n時刻",

            "開催区分",

            "AI予想",

            "AI確信度",

            "0～\n9,999",

            "10,000～\n29,999",

            "30,000～\n49,999",

            "50,000～\n99,999",

            "100,000\n以上",

        ]

    ]

    print()

    log(f"Columns : {len(result.columns)}")

    log(f"Rows    : {len(result):,}")

    print()

    today = result["日付"].iloc[0].replace("-", "")

    output_csv = (

        PREDICTION_DIR

        / f"{today}_prediction.csv"

    )

    result.to_csv(

        output_csv,

        index=False,

        encoding="utf-8-sig",

    )

    log(f"Rows : {len(result):,}")

    log(f"Columns : {len(result.columns)}")

    log(f"保存先 : {output_csv}")

    print()


# ===========================================================
# Main
# ===========================================================

def main():

    print()

    log("=======================================")
    log("025 Predict Today")
    log("=======================================")

    # --------------------------------------------------
    # CSV読込
    # --------------------------------------------------

    df = load_today_features()

    # --------------------------------------------------
    # モデル読込
    # --------------------------------------------------

    model, feature_columns = load_model()

    # --------------------------------------------------
    # 学習時特徴量へ変換
    # --------------------------------------------------

    X = build_prediction_dataset(

        df,

        feature_columns,

    )

    # --------------------------------------------------
    # AI予測
    # --------------------------------------------------

    result = predict(

        model,

        X,

        df,

    )

    # --------------------------------------------------
    # CSV保存
    # --------------------------------------------------

    save_prediction(
        
        result,

    )

    print(result.info())

    print()

    print(result.head())

    print()

    print(result.tail())

    print()

    log("Complete")

    print()


# ===========================================================
# 実行
# ===========================================================

if __name__ == "__main__":

    main()