"""
===========================================================
競輪AI Ver1.0
feature_target.py

目的変数生成

【役割】
feature_relative.py の出力を受け取り、
AI学習用目的変数を生成する。

生成特徴量

1 payout_class

===========================================================
"""

import pandas as pd
import numpy as np


# ===========================================================
# ログ表示
# ===========================================================

def log(message):
    """
    ログ表示
    """

    print(f"[feature_target] {message}")


# ===========================================================
# 必須カラム
# ===========================================================

REQUIRED_COLUMNS = [

    "trifecta_payout",

]


# ===========================================================
# 必須カラムチェック
# ===========================================================

def check_required_columns(df):
    """
    必須カラム確認
    """

    log("必須カラム確認開始")

    missing = []

    for col in REQUIRED_COLUMNS:

        if col not in df.columns:

            missing.append(col)

    if len(missing) > 0:

        print()

        print("========================================")
        print("ERROR")
        print("必須カラムが不足しています")
        print("----------------------------------------")

        for col in missing:

            print(col)

        print("========================================")

        raise ValueError("必須カラム不足")

    log("OK")


# ===========================================================
# 数値変換
# ===========================================================

def convert_numeric(df):
    """
    数値変換
    """

    log("数値変換開始")

    df["trifecta_payout"] = pd.to_numeric(

        df["trifecta_payout"],

        errors="coerce"

    )

    df["trifecta_payout"] = (

        df["trifecta_payout"]

        .fillna(0)

        .astype(int)

    )

    log("数値変換完了")

    return df

# ===========================================================
# 目的変数作成
# ===========================================================

def create_payout_class(df):
    """
    AI学習用目的変数作成

    trifecta_payoutから
    payout_classを生成する。
    """

    log("payout_class 作成")

    conditions = [

        df["trifecta_payout"] <= 9999,

        (df["trifecta_payout"] >= 10000) &
        (df["trifecta_payout"] <= 29999),

        (df["trifecta_payout"] >= 30000) &
        (df["trifecta_payout"] <= 59999),

        (df["trifecta_payout"] >= 60000) &
        (df["trifecta_payout"] <= 99999),

        df["trifecta_payout"] >= 100000,

    ]

    values = [

        0,

        1,

        2,

        3,

        4,

    ]

    df["payout_class"] = np.select(

        conditions,

        values,

        default=0

    ).astype(int)

    log("payout_class 完了")

    return df

# ===========================================================
# メイン処理
# ===========================================================

def build_feature_target(df):
    """
    目的変数生成

    Parameters
    ----------
    df : pandas.DataFrame

    Returns
    -------
    pandas.DataFrame
    """

    print()

    log("=======================================")
    log("目的変数生成開始")
    log("=======================================")

    # -----------------------------
    # 必須カラム確認
    # -----------------------------
    check_required_columns(df)

    # -----------------------------
    # 数値変換
    # -----------------------------
    df = convert_numeric(df)

    # -----------------------------
    # 目的変数作成
    # -----------------------------
    df = create_payout_class(df)

    print()

    log("生成特徴量")

    feature_columns = [

        "payout_class",

    ]

    for col in feature_columns:

        log(f"  OK  {col}")

    print()

    log("=======================================")
    log("目的変数生成完了")
    log(f"データ件数 : {len(df):,}")
    log(f"特徴量数   : {len(feature_columns)}")
    log("=======================================")

    print()

    return df


# ===========================================================
# 動作確認
# ===========================================================

if __name__ == "__main__":

    log("feature_target.py")

    print()
    print("このファイルは")
    print("他プログラムからimportして使用します。")
    print()