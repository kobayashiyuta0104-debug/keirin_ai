"""
===========================================================
競輪AI Ver1.0
feature_relative.py

相対評価特徴量生成

【役割】
feature_rank.py の出力を受け取り、
相対評価特徴量を生成する。

生成特徴量

1 score_diff_top
2 win_rate_diff_top
3 quinella_rate_diff_top
4 trio_rate_diff_top
5 line_score_diff_top
6 line_win_rate_diff_top
7 line_quinella_rate_diff_top
8 line_trio_rate_diff_top

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

    print(f"[feature_relative] {message}")


# ===========================================================
# 必須カラム
# ===========================================================

REQUIRED_COLUMNS = [

    "race_key",

    "line_no",

    "average_score",

    "win_rate",

    "quinella_rate",

    "trio_rate",

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

    columns = [

        "average_score",

        "win_rate",

        "quinella_rate",

        "trio_rate",

    ]

    for col in columns:

        df[col] = pd.to_numeric(

            df[col],

            errors="coerce"

        )

    df[columns] = df[columns].fillna(0)

    df["average_score"] = df["average_score"].astype(float)

    df["win_rate"] = df["win_rate"].astype(float)

    df["quinella_rate"] = df["quinella_rate"].astype(float)

    df["trio_rate"] = df["trio_rate"].astype(float)

    log("数値変換完了")

    return df


# ===========================================================
# 共通相対差作成
# ===========================================================

def create_diff(
    df,
    group_columns,
    source_column,
    output_column,
):
    """
    共通相対差作成

    Parameters
    ----------
    group_columns : グループ化列

    source_column : 元データ列

    output_column : 出力列
    """

    log(f"{output_column} 作成")

    group_max = (

        df

        .groupby(group_columns)[source_column]

        .transform("max")

    )

    df[output_column] = (

        group_max

        - df[source_column]

    )

    log(f"{output_column} 完了")

    return df

# ===========================================================
# レース内相対差作成
# ===========================================================

def create_race_diff(df):
    """
    レース内相対差作成
    """

    log("=======================================")
    log("レース内相対差作成")
    log("=======================================")

    # --------------------------------------------------
    # レーストップ得点との差
    # --------------------------------------------------
    df = create_diff(

        df,

        ["race_key"],

        "average_score",

        "score_diff_top",

    )

    # --------------------------------------------------
    # レーストップ勝率との差
    # --------------------------------------------------
    df = create_diff(

        df,

        ["race_key"],

        "win_rate",

        "win_rate_diff_top",

    )

    # --------------------------------------------------
    # レーストップ2連対率との差
    # --------------------------------------------------
    df = create_diff(

        df,

        ["race_key"],

        "quinella_rate",

        "quinella_rate_diff_top",

    )

    # --------------------------------------------------
    # レーストップ3連対率との差
    # --------------------------------------------------
    df = create_diff(

        df,

        ["race_key"],

        "trio_rate",

        "trio_rate_diff_top",

    )

    log("レース内相対差 完了")

    return df


# ===========================================================
# ライン内相対差作成
# ===========================================================

def create_line_diff(df):
    """
    ライン内相対差作成
    """

    log("=======================================")
    log("ライン内相対差作成")
    log("=======================================")

    group_columns = [

        "race_key",

        "line_no",

    ]

    # --------------------------------------------------
    # ライントップ得点との差
    # --------------------------------------------------
    df = create_diff(

        df,

        group_columns,

        "average_score",

        "line_score_diff_top",

    )

    # --------------------------------------------------
    # ライントップ勝率との差
    # --------------------------------------------------
    df = create_diff(

        df,

        group_columns,

        "win_rate",

        "line_win_rate_diff_top",

    )

    # --------------------------------------------------
    # ライントップ2連対率との差
    # --------------------------------------------------
    df = create_diff(

        df,

        group_columns,

        "quinella_rate",

        "line_quinella_rate_diff_top",

    )

    # --------------------------------------------------
    # ライントップ3連対率との差
    # --------------------------------------------------
    df = create_diff(

        df,

        group_columns,

        "trio_rate",

        "line_trio_rate_diff_top",

    )

    log("ライン内相対差 完了")

    return df

# ===========================================================
# メイン処理
# ===========================================================

def build_feature_relative(df):
    """
    相対評価特徴量生成

    Parameters
    ----------
    df : pandas.DataFrame

    Returns
    -------
    pandas.DataFrame
    """

    print()

    log("=======================================")
    log("相対評価特徴量生成開始")
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
    # レース内相対差
    # -----------------------------
    df = create_race_diff(df)

    # -----------------------------
    # ライン内相対差
    # -----------------------------
    df = create_line_diff(df)

    print()

    log("生成特徴量")

    feature_columns = [

        "score_diff_top",

        "win_rate_diff_top",

        "quinella_rate_diff_top",

        "trio_rate_diff_top",

        "line_score_diff_top",

        "line_win_rate_diff_top",

        "line_quinella_rate_diff_top",

        "line_trio_rate_diff_top",

    ]

    for col in feature_columns:

        log(f"  OK  {col}")

    print()

    log("=======================================")
    log("相対評価特徴量生成完了")
    log(f"データ件数 : {len(df):,}")
    log(f"特徴量数   : {len(feature_columns)}")
    log("=======================================")

    print()

    return df


# ===========================================================
# 動作確認
# ===========================================================

if __name__ == "__main__":

    log("feature_relative.py")

    print()
    print("このファイルは")
    print("他プログラムからimportして使用します。")
    print()