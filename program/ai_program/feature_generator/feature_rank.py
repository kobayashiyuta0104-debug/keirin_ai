"""
===========================================================
競輪AI Ver1.0
feature_rank.py

順位特徴量生成

【役割】
feature_race.py の出力を受け取り、
順位に関する特徴量を生成する。

生成特徴量

1 score_rank
2 win_rate_rank
3 quinella_rate_rank
4 trio_rate_rank
5 line_score_rank
6 line_win_rate_rank
7 line_quinella_rate_rank
8 line_trio_rate_rank

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

    print(f"[feature_rank] {message}")


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
# 共通順位作成
# ===========================================================

def create_rank(
    df,
    group_columns,
    source_column,
    output_column,
):
    """
    共通順位作成

    Parameters
    ----------
    group_columns : グループ化列

    source_column : 順位元列

    output_column : 出力列
    """

    log(f"{output_column} 作成")

    df[output_column] = (

        df

        .groupby(group_columns)[source_column]

        .rank(

            method="min",

            ascending=False

        )

        .astype(int)

    )

    log(f"{output_column} 完了")

    return df

# ===========================================================
# レース内順位作成
# ===========================================================

def create_race_rank(df):
    """
    レース内順位作成
    """

    log("=======================================")
    log("レース内順位作成")
    log("=======================================")

    # --------------------------------------------------
    # 得点順位
    # --------------------------------------------------
    df = create_rank(

        df,

        ["race_key"],

        "average_score",

        "score_rank",

    )

    # --------------------------------------------------
    # 勝率順位
    # --------------------------------------------------
    df = create_rank(

        df,

        ["race_key"],

        "win_rate",

        "win_rate_rank",

    )

    # --------------------------------------------------
    # 2連対率順位
    # --------------------------------------------------
    df = create_rank(

        df,

        ["race_key"],

        "quinella_rate",

        "quinella_rate_rank",

    )

    # --------------------------------------------------
    # 3連対率順位
    # --------------------------------------------------
    df = create_rank(

        df,

        ["race_key"],

        "trio_rate",

        "trio_rate_rank",

    )

    log("レース内順位 完了")

    return df


# ===========================================================
# ライン内順位作成
# ===========================================================

def create_line_rank(df):
    """
    ライン内順位作成
    """

    log("=======================================")
    log("ライン内順位作成")
    log("=======================================")

    group_columns = [

        "race_key",

        "line_no",

    ]

    # --------------------------------------------------
    # ライン得点順位
    # --------------------------------------------------
    df = create_rank(

        df,

        group_columns,

        "average_score",

        "line_score_rank",

    )

    # --------------------------------------------------
    # ライン勝率順位
    # --------------------------------------------------
    df = create_rank(

        df,

        group_columns,

        "win_rate",

        "line_win_rate_rank",

    )

    # --------------------------------------------------
    # ライン2連対率順位
    # --------------------------------------------------
    df = create_rank(

        df,

        group_columns,

        "quinella_rate",

        "line_quinella_rate_rank",

    )

    # --------------------------------------------------
    # ライン3連対率順位
    # --------------------------------------------------
    df = create_rank(

        df,

        group_columns,

        "trio_rate",

        "line_trio_rate_rank",

    )

    log("ライン内順位 完了")

    return df

# ===========================================================
# メイン処理
# ===========================================================

def build_feature_rank(df):
    """
    順位特徴量生成

    Parameters
    ----------
    df : pandas.DataFrame

    Returns
    -------
    pandas.DataFrame
    """

    print()

    log("=======================================")
    log("順位特徴量生成開始")
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
    # レース内順位
    # -----------------------------
    df = create_race_rank(df)

    # -----------------------------
    # ライン内順位
    # -----------------------------
    df = create_line_rank(df)

    print()

    log("生成特徴量")

    feature_columns = [

        "score_rank",

        "win_rate_rank",

        "quinella_rate_rank",

        "trio_rate_rank",

        "line_score_rank",

        "line_win_rate_rank",

        "line_quinella_rate_rank",

        "line_trio_rate_rank",

    ]

    for col in feature_columns:

        log(f"  OK  {col}")

    print()

    log("=======================================")
    log("順位特徴量生成完了")
    log(f"データ件数 : {len(df):,}")
    log(f"特徴量数   : {len(feature_columns)}")
    log("=======================================")

    print()

    return df


# ===========================================================
# 動作確認
# ===========================================================

if __name__ == "__main__":

    log("feature_rank.py")

    print()
    print("このファイルは")
    print("他プログラムからimportして使用します。")
    print()