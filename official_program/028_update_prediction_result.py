"""
===========================================================
競輪AI Ver1.0
028_update_prediction_result.py

予想結果更新

【役割】

前日の prediction.csv

＋

前日の result.csv

↓

prediction.csv 更新

===========================================================
"""

import os
from pathlib import Path
from datetime import datetime, timedelta, timezone
import math

import pandas as pd


# ===========================================================
# GitHub対応
# ===========================================================

if os.name == "nt":

    BASE = Path(r"C:\競輪AI")

else:

    BASE = Path(__file__).resolve().parent.parent


# ===========================================================
# JST
# ===========================================================

JST = timezone(

    timedelta(hours=9)

)

YESTERDAY = (

    datetime.now(JST)

    - timedelta(days=1)

).strftime("%Y%m%d")


# ===========================================================
# パス
# ===========================================================

PREDICTION_DIR = (

    BASE

    / "csv"

    / "prediction"

)

RESULT_DIR = (

    BASE

    / "csv"

    / "result"

)


PREDICTION_FILE = (

    PREDICTION_DIR

    / f"{YESTERDAY}_prediction.csv"

)

RESULT_FILE = (

    RESULT_DIR

    / f"{YESTERDAY}_result.csv"

)

ODDS_DIR = (

    BASE

    / "csv"

    / "odds"

)

ODDS_FILE = (

    ODDS_DIR

    / f"{YESTERDAY}_odds.csv"

)


# ===========================================================
# ログ
# ===========================================================

def log(message):

    print(f"[028_update_prediction_result] {message}")


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

    # 列名の改行コードを統一
    df.columns = (
        df.columns
        .str.replace("\r\n", "\n", regex=False)
        .str.replace("\r", "\n", regex=False)
    )

    log(f"Rows    : {len(df):,}")

    log(f"Columns : {len(df.columns):,}")

    print()

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

    return df


# ===========================================================
# 前日オッズCSV読込
# ===========================================================

def load_odds():

    log("=======================================")
    log("前日オッズCSV 読込")
    log("=======================================")

    if not ODDS_FILE.exists():

        log(f"前日オッズCSVがありません。購入金額・収支は未更新: {ODDS_FILE}")

        print()

        return None

    df = pd.read_csv(

        ODDS_FILE,

        encoding="utf-8-sig",

        low_memory=False,

    )

    if "race_key" not in df.columns:

        log("前日オッズCSVにrace_key列がありません。購入金額・収支は未更新")

        print()

        return None

    df["race_key"] = (

        df["race_key"]

        .fillna("")

        .astype(str)

        .str.strip()

    )

    duplicate_count = int(df["race_key"].duplicated().sum())

    if duplicate_count:

        log(f"重複race_keyを検出: {duplicate_count:,}件。最後の行を使用します")

        df = df.drop_duplicates(

            subset=["race_key"],

            keep="last",

        )

    log(f"Rows    : {len(df):,}")

    log(f"Columns : {len(df.columns):,}")

    print()

    return df

# ===========================================================
# 払戻クラス判定
# ===========================================================

def get_result_class(payout):

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


# AI予想クラスの範囲は、前日オッズ×100円の払戻見込みに適用する。
PAYOUT_CLASS_RANGES = {

    "0～1,999円": (0, 2000),

    "2,000～4,999円": (2000, 5000),

    "5,000～9,999円": (5000, 10000),

    "10,000～19,999円": (10000, 20000),

    "20,000～29,999円": (20000, 30000),

    "30,000～49,999円": (30000, 50000),

    "50,000～99,999円": (50000, 100000),

    "100,000円以上": (100000, None),

}


def get_purchased_combinations(odds_row, predicted_class):

    payout_range = PAYOUT_CLASS_RANGES.get(

        str(predicted_class).strip()

    )

    if payout_range is None:

        return None

    minimum, maximum = payout_range

    purchased = set()

    for column, raw_odds in odds_row.items():

        parts = str(column).split("-")

        if len(parts) != 3:

            continue

        if not all(part.isdigit() for part in parts):

            continue

        car_numbers = [int(part) for part in parts]

        if (

            len(set(car_numbers)) != 3

            or any(car_no < 1 or car_no > 9 for car_no in car_numbers)

        ):

            continue

        if pd.isna(raw_odds) or str(raw_odds).strip() == "":

            continue

        try:

            odds = float(str(raw_odds).replace(",", ""))

        except (TypeError, ValueError):

            continue

        if not math.isfinite(odds) or odds <= 0:

            continue

        estimated_payout = odds * 100

        if (

            estimated_payout >= minimum

            and (maximum is None or estimated_payout < maximum)

        ):

            purchased.add("-".join(str(car_no) for car_no in car_numbers))

    return purchased


def get_winning_combination(race_result):

    trifecta_columns = [

        "trifecta_1st",

        "trifecta_2nd",

        "trifecta_3rd",

    ]

    if all(column in race_result.columns for column in trifecta_columns):

        values = race_result.iloc[0][trifecta_columns]

        car_numbers = []

        for value in values:

            numeric_value = pd.to_numeric(value, errors="coerce")

            if pd.isna(numeric_value):

                car_numbers = []

                break

            car_numbers.append(int(numeric_value))

        if (

            len(car_numbers) == 3

            and len(set(car_numbers)) == 3

            and all(1 <= car_no <= 9 for car_no in car_numbers)

        ):

            return "-".join(str(car_no) for car_no in car_numbers)

    if not {"finish_order", "car_no"}.issubset(race_result.columns):

        return None

    finish_order = pd.to_numeric(

        race_result["finish_order"],

        errors="coerce",

    )

    car_numbers = []

    for order in [1, 2, 3]:

        rows = race_result.loc[finish_order == order]

        if rows.empty:

            return None

        car_no = pd.to_numeric(

            rows["car_no"].iloc[0],

            errors="coerce",

        )

        if pd.isna(car_no):

            return None

        car_numbers.append(int(car_no))

    if (

        len(set(car_numbers)) != 3

        or any(car_no < 1 or car_no > 9 for car_no in car_numbers)

    ):

        return None

    return "-".join(str(car_no) for car_no in car_numbers)


# ===========================================================
# Prediction更新
# ===========================================================

def update_prediction(

    prediction_df,

    result_df,

    odds_df,

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

    for column in ["購入金額", "収支"]:

        if column not in prediction_df.columns:

            prediction_df[column] = ""

        prediction_df[column] = prediction_df[column].astype(object)

    odds_by_key = {}

    if odds_df is not None:

        for _, row in odds_df.iterrows():

            race_key = str(row.get("race_key", "")).strip()

            if race_key:

                odds_by_key[race_key] = row

    update_count = 0

    purchase_update_count = 0

    profit_update_count = 0

    missing_odds_count = 0

    # --------------------------------------------------
    # レース単位処理
    # --------------------------------------------------

    for race_key in prediction_df["レースキー"].unique():

        prediction_mask = prediction_df["レースキー"] == race_key

        prediction_row = prediction_df.loc[prediction_mask].iloc[0]

        purchased_combinations = None

        purchase_amount = None

        odds_row = odds_by_key.get(str(race_key).strip())

        if odds_row is None:

            missing_odds_count += 1

        else:

            purchased_combinations = get_purchased_combinations(

                odds_row,

                prediction_row.get("AI予想", ""),

            )

            if purchased_combinations is not None:

                purchase_amount = len(purchased_combinations) * 100

                prediction_df.loc[

                    prediction_mask,

                    "購入金額",

                ] = purchase_amount

                purchase_update_count += 1

        race_result = result_df[

            result_df["race_key"] == race_key

        ]

        if race_result.empty:

            continue

        # ------------------------------
        # 払戻
        # ------------------------------
        payout_raw = race_result["trifecta_payout"].iloc[0]

        # 払戻が空欄の場合はスキップ
        if pd.isna(payout_raw):
            continue

        payout = int(
            float(
                str(payout_raw).replace(",", "")
            )
        )

        prediction_df.loc[
            prediction_df["レースキー"] == race_key,
            "三連単\n払戻"
        ] = payout

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

        # ------------------------------
        # 購入金額・収支
        # ------------------------------

        if purchased_combinations is not None:

            winning_combination = get_winning_combination(

                race_result,

            )

            if winning_combination is not None:

                actual_return = (

                    payout

                    if winning_combination in purchased_combinations

                    else 0

                )

                prediction_df.loc[

                    prediction_mask,

                    "収支",

                ] = actual_return - purchase_amount

                profit_update_count += 1

        update_count += 1

    print()

    log(f"更新レース数 : {update_count:,}")

    log(f"購入金額更新 : {purchase_update_count:,}")

    log(f"収支更新     : {profit_update_count:,}")

    log(f"前日オッズなし: {missing_odds_count:,}")

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
    log("028 Update Prediction Result")
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
    # 前日オッズ
    # --------------------------------------------------

    odds_df = load_odds()

    # --------------------------------------------------
    # 更新
    # --------------------------------------------------

    prediction_df = update_prediction(

        prediction_df,

        result_df,

        odds_df,

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
