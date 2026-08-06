"""
===========================================================
競輪AI Ver1.0
004_update_training_prediction.py

予想結果更新

【役割】

training_prediction.csv

＋

historical_result

↓

prediction.csv 更新

===========================================================
"""

import os
from pathlib import Path
from datetime import datetime, timedelta, timezone

import pandas as pd


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

TRAINING_DIR = (
    BASE
    / "csv"
    / "training"
)

RESULT_DIR = (
    BASE
    / "csv"
    / "historical_date"
    / "historical_result"
)

PREDICTION_FILE = (
    TRAINING_DIR
    / "training_prediction.csv"
)

RESULT_FILE = (
    RESULT_DIR
    / "historical_result.csv"
)

# ===========================================================
# ログ
# ===========================================================

def log(message):

    print(f"[004_update_training_prediction] {message}")


# ===========================================================
# Prediction CSV読込
# ===========================================================

def load_prediction():

    log("=======================================")
    log("Prediction CSV 読込")
    log("=======================================")

    if not PREDICTION_FILE.exists():

        raise FileNotFoundError(PREDICTION_FILE)

    df = pd.read_csv(

        PREDICTION_FILE,

        encoding="utf-8-sig",

        low_memory=False,

    )

    log(f"Rows    : {len(df):,}")

    log(f"Columns : {len(df.columns):,}")

    print()

    print(df.columns.tolist())

    return df


# ===========================================================
# Result CSV読込
# ===========================================================

def load_result():

    log("=======================================")
    log("Result CSV 読込")
    log("=======================================")

    if not RESULT_FILE.exists():

        raise FileNotFoundError(RESULT_FILE)

    df = pd.read_csv(

        RESULT_FILE,

        encoding="utf-8-sig",

        low_memory=False,

    )

    log(f"Rows    : {len(df):,}")
    log(f"Columns : {len(df.columns):,}")

    print()

    df = df.set_index("race_key", drop=False)

    return df

# ===========================================================
# 払戻クラス判定
# ===========================================================

def get_result_class(payout):

    if payout <= 9999:

        return "0～9,999円"

    elif payout <= 29999:

        return "10,000～29,999円"

    elif payout <= 49999:

        return "30,000～49,999円"

    elif payout <= 99999:

        return "50,000～99,999円"

    else:

        return "100,000円以上"


# ===========================================================
# Prediction更新
# ===========================================================

def update_prediction(

    prediction_df,

    result_df,

):

    log("=======================================")
    log("Prediction Update")
    log("=======================================")

    prediction_df["三連単\n払戻"] = prediction_df["三連単\n払戻"].astype(object)
    prediction_df["実際\nクラス"] = prediction_df["実際\nクラス"].astype(object)
    prediction_df["的中\n判定"] = prediction_df["的中\n判定"].astype(object)

    prediction_df["１着"] = prediction_df["１着"].astype(object)
    prediction_df["２着"] = prediction_df["２着"].astype(object)
    prediction_df["３着"] = prediction_df["３着"].astype(object)

    update_count = 0

    # --------------------------------------------------
    # レース単位処理
    # --------------------------------------------------

    for race_key in prediction_df["レースキー"].unique():

        try:

            race_result = result_df.loc[[race_key]]

        except KeyError:

            continue

        if race_result.empty:

            continue

        # ------------------------------
        # 払戻
        # ------------------------------

        payout_value = race_result["trifecta_payout"].iloc[0]

        if pd.isna(payout_value):

            continue

        payout = int(

            float(

                str(payout_value).replace(",", "")

            )

        )

        prediction_df.loc[

            prediction_df["レースキー"] == race_key,

            "三連単\n払戻"

        ] = payout

        # ------------------------------
        # 実際クラス
        # ------------------------------

        result_class = get_result_class(

            payout

        )

        prediction_df.loc[

            prediction_df["レースキー"] == race_key,

            "実際\nクラス"

        ] = result_class

        # ------------------------------
        # 的中判定
        # ------------------------------

        ai_class = prediction_df.loc[

            prediction_df["レースキー"] == race_key,

            "AI予想"

        ].iloc[0]

        prediction_df.loc[

            prediction_df["レースキー"] == race_key,

            "的中\n判定"

        ] = (

            "○"

            if ai_class == result_class

            else "×"

        )

        # ------------------------------
        # 着順
        # ------------------------------

        for order in [1, 2, 3]:

            row = race_result[

                race_result["finish_order"] == order

            ]

            if row.empty:

                continue

            car_no = int(

                row["car_no"]

                .iloc[0]

            )

            ORDER_COLUMNS = {

                1: "１着",

                2: "２着",

                3: "３着",

            }

            prediction_df.loc[

                prediction_df["レースキー"] == race_key,

                ORDER_COLUMNS[order]

            ] = car_no

        update_count += 1

    print()

    log(f"更新レース数 : {update_count:,}")

    print()

    return prediction_df


# ===========================================================
# CSV保存
# ===========================================================

def save_prediction(

    prediction_df,

):

    log("=======================================")
    log("Prediction CSV 保存")
    log("=======================================")

    prediction_df.to_csv(

        PREDICTION_FILE,

        index=False,

        encoding="utf-8-sig",

    )

    log(f"Rows    : {len(prediction_df):,}")

    log(f"Columns : {len(prediction_df.columns):,}")

    log(f"保存先 : {PREDICTION_FILE}")

    print()


# ===========================================================
# Main
# ===========================================================

def main():

    print()

    log("=======================================")
    log("004 Update Training Prediction")
    log("=======================================")

    # --------------------------------------------------
    # Prediction
    # --------------------------------------------------

    prediction_df = load_prediction()

    # --------------------------------------------------
    # Result
    # --------------------------------------------------

    result_df = load_result()

    # --------------------------------------------------
    # 更新
    # --------------------------------------------------

    prediction_df = update_prediction(

        prediction_df,

        result_df,

    )

    # --------------------------------------------------
    # 保存
    # --------------------------------------------------

    save_prediction(

        prediction_df,

    )

    log("Complete")

    print()


# ===========================================================
# 実行
# ===========================================================

if __name__ == "__main__":

    main()