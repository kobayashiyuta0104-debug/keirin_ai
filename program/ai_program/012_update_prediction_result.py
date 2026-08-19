# ===========================================================
# 競輪AI Ver1.0
# 012_update_historical_prediction_result.py
#
# 過去AI予測結果更新
#
# 【役割】
#
# training_prediction(2026.1.1~2026.8.18).csv
#
# ＋
#
# historical_result.csv
#
# ↓
#
# training_prediction_result(2020.1.1~2022.12.31).csv
#
# 追加する内容
#
# ・三連単払戻
# ・実際クラス
# ・的中判定
# ・1着
# ・2着
# ・3着
#
# ===========================================================

import os

from pathlib import Path

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
    / "result"
)


# ===========================================================
# 入力
# ===========================================================

PREDICTION_FILE = (
    TRAINING_DIR
    / "training_prediction(2026.1.1~2026.8.18).csv"
)


RESULT_FILE = (
    RESULT_DIR
    / "training_result(2026.1.1~2026.8.18).csv"
)


# ===========================================================
# 出力
# ===========================================================

OUTPUT_FILE = (
    TRAINING_DIR
    / "training_prediction_result(2026.1.1~2026.8.18).csv"
)

# ===========================================================
# 出力フォルダ作成
# ===========================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)


# ===========================================================
# ログ
# ===========================================================

def log(message):

    print(
        f"[012_update_historical_prediction_result] {message}"
    )


# ===========================================================
# Prediction CSV読込
# ===========================================================

def load_prediction():

    log(
        "======================================="
    )

    log(
        "2026 Prediction CSV 読込"
    )

    log(
        "======================================="
    )

    if not PREDICTION_FILE.exists():

        raise FileNotFoundError(
            PREDICTION_FILE
        )

    df = pd.read_csv(

        PREDICTION_FILE,

        encoding="utf-8-sig",

        low_memory=False,

    )

    log(
        f"Rows    : {len(df):,}"
    )

    log(
        f"Columns : {len(df.columns):,}"
    )

    print()

    return df


# ===========================================================
# Result CSV読込
# ===========================================================

def load_result():

    log(
        "======================================="
    )

    log(
        "2026 Result CSV 読込"
    )

    log(
        "======================================="
    )

    if not RESULT_FILE.exists():

        raise FileNotFoundError(
            RESULT_FILE
        )

    df = pd.read_csv(

        RESULT_FILE,

        encoding="utf-8-sig",

        low_memory=False,

    )

    log(
        f"Rows    : {len(df):,}"
    )

    log(
        f"Columns : {len(df.columns):,}"
    )

    print()

    return df


# ===========================================================
# 払戻クラス判定
# ===========================================================

def get_result_class(payout):

    if pd.isna(payout):
        return None

    payout = int(payout)

    if payout <= 1999:
        return "0～1,999円"

    elif payout <= 4999:
        return "2,000～4,999円"

    elif payout <= 9999:
        return "5,000～9,999円"

    elif payout <= 19999:
        return "10,000～19,999円"

    elif payout <= 29999:
        return "20,000～29,999円"

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

    log(
        "======================================="
    )

    log(
        "2026 Prediction Update"
    )

    log(
        "======================================="
    )

    # =======================================================
    # 必要列確認
    # =======================================================

    prediction_required = [

        "レースキー",

        "AI予想",

    ]

    result_required = [

        "race_key",

        "trifecta_payout",

        "finish_order",

        "car_no",

    ]


    for column in prediction_required:

        if column not in prediction_df.columns:

            raise ValueError(
                f"Prediction CSVに必要な列がありません: {column}"
            )


    for column in result_required:

        if column not in result_df.columns:

            raise ValueError(
                f"Result CSVに必要な列がありません: {column}"
            )


    # =======================================================
    # 更新対象列
    # =======================================================

    update_columns = [

        "三連単\n払戻",

        "実際\nクラス",

        "的中\n判定",

        "１着",

        "２着",

        "３着",

    ]


    for column in update_columns:

        if column not in prediction_df.columns:

            prediction_df[column] = ""


        prediction_df[column] = (
            prediction_df[column].astype(object)
        )


    # =======================================================
    # 結果データをrace_key単位で処理
    # =======================================================

    result_race_keys = set(

        result_df["race_key"]

        .dropna()

        .astype(str)

    )


    prediction_df["レースキー"] = (

        prediction_df["レースキー"]

        .astype(str)

    )


    update_count = 0

    no_result_count = 0


    # =======================================================
    # レース単位処理
    # =======================================================

    for race_key in prediction_df["レースキー"].unique():

        race_result = result_df[

            result_df["race_key"].astype(str)

            == race_key

        ]


        # ---------------------------------------------------
        # 結果なし
        # ---------------------------------------------------

        if race_result.empty:

            no_result_count += 1

            continue


        # ===================================================
        # 三連単払戻
        # ===================================================

        payout_series = race_result[
            "trifecta_payout"
        ].dropna()


        if payout_series.empty:

            no_result_count += 1

            continue


        payout = int(
            float(
                str(
                    payout_series.iloc[0]
                ).replace(",", "")
            )
        )


        prediction_df.loc[

            prediction_df["レースキー"] == race_key,

            "三連単\n払戻"

        ] = payout


        # ===================================================
        # 実際クラス
        # ===================================================

        result_class = get_result_class(

            payout

        )


        prediction_df.loc[

            prediction_df["レースキー"] == race_key,

            "実際\nクラス"

        ] = result_class


        # ===================================================
        # 的中判定
        # ===================================================

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


        # ===================================================
        # 着順
        # ===================================================

        order_columns = {

            1: "１着",

            2: "２着",

            3: "３着",

        }


        for order, column in order_columns.items():

            row = race_result[

                race_result["finish_order"]

                == order

            ]


            if row.empty:

                continue


            car_no = row["car_no"].iloc[0]


            if pd.isna(car_no):

                continue


            prediction_df.loc[

                prediction_df["レースキー"] == race_key,

                column

            ] = int(car_no)


        update_count += 1


        if update_count % 10000 == 0:

            log(
                f"更新中 : {update_count:,}"
            )


    print()

    log(
        f"結果更新レース数 : {update_count:,}"
    )

    log(
        f"結果なしレース数 : {no_result_count:,}"
    )

    print()

    return prediction_df


# ===========================================================
# CSV保存
# ===========================================================

def save_prediction(

    prediction_df,

):

    log(
        "======================================="
    )

    log(
        "2026 Prediction Result CSV 保存"
    )

    log(
        "======================================="
    )


    prediction_df.to_csv(

        OUTPUT_FILE,

        index=False,

        encoding="utf-8-sig",

    )


    log(
        f"Rows    : {len(prediction_df):,}"
    )

    log(
        f"Columns : {len(prediction_df.columns):,}"
    )

    log(
        f"保存先 : {OUTPUT_FILE}"
    )

    print()


# ===========================================================
# Main
# ===========================================================

def main():

    print()

    log(
        "======================================="
    )

    log(
        "012 Update Prediction Result"
    )

    log(
        "======================================="
    )

    # -------------------------------------------------------
    # Prediction
    # -------------------------------------------------------

    prediction_df = load_prediction()


    # -------------------------------------------------------
    # Result
    # -------------------------------------------------------

    result_df = load_result()


    # -------------------------------------------------------
    # 更新
    # -------------------------------------------------------

    prediction_df = update_prediction(

        prediction_df,

        result_df,

    )


    # -------------------------------------------------------
    # 保存
    # -------------------------------------------------------

    save_prediction(

        prediction_df,

    )


    # -------------------------------------------------------
    # 最終確認
    # -------------------------------------------------------

    print()

    print(
        "======================================="
    )

    print(
        "012 完了"
    )

    print(
        "======================================="
    )

    print()

    print(
        f"入力予測 : {PREDICTION_FILE}"
    )

    print(
        f"入力結果 : {RESULT_FILE}"
    )

    print(
        f"出力      : {OUTPUT_FILE}"
    )

    print()

    print(
        f"レコード数 : {len(prediction_df):,}"
    )

    print(
        f"列数       : {len(prediction_df.columns):,}"
    )

    print()

    log(
        "Complete"
    )


# ===========================================================
# 実行
# ===========================================================

if __name__ == "__main__":

    main()