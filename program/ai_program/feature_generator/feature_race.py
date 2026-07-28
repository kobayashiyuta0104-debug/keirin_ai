"""
===========================================================
競輪AI Ver1.0
feature_race.py

レース特徴量生成

【役割】
feature_line.py の出力を受け取り、
レースに関する特徴量を生成する。

生成特徴量

1 weekday
2 jo_name
3 grade
4 race_type
5 session
6 weather
7 wind_speed
8 bank_type
9 straight_type
10 bank_angle

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

    print(f"[feature_race] {message}")


# ===========================================================
# 必須カラム
# ===========================================================

REQUIRED_COLUMNS = [

    "date",

    "jo_name",

    "grade",

    "race_type",

    "session",

    "weather",

    "wind_speed",

    "track_length",

    "straight_length",

    "bank_angle",

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

        "wind_speed",

        "track_length",

        "straight_length",

        "bank_angle",

    ]

    for col in columns:

        df[col] = pd.to_numeric(

            df[col],

            errors="coerce"

        )

    df[columns] = df[columns].fillna(0)

    df["wind_speed"] = df["wind_speed"].astype(float)

    df["track_length"] = df["track_length"].astype(int)

    df["straight_length"] = df["straight_length"].astype(float)

    df["bank_angle"] = df["bank_angle"].astype(float)

    log("数値変換完了")

    return df


# ===========================================================
# 曜日作成
# ===========================================================

def create_weekday(df):
    """
    開催曜日作成
    """

    log("曜日作成")

    df["date"] = pd.to_datetime(

        df["date"],

        format="%Y%m%d",

        errors="coerce"

    )

    weekday_map = {

        0: "月",

        1: "火",

        2: "水",

        3: "木",

        4: "金",

        5: "土",

        6: "日",

    }

    df["weekday"] = (

        df["date"]

        .dt.weekday

        .map(weekday_map)

    )

    df["weekday"] = df["weekday"].fillna("不明")

    log("weekday 完了")

    return df

# ===========================================================
# カテゴリ列整形
# ===========================================================

def clean_category_columns(df):
    """
    カテゴリ列整形

    前後の空白除去
    欠損補完
    """

    log("カテゴリ列整形")

    columns = [

        "jo_name",

        "grade",

        "race_type",

        "session",

        "weather",

    ]

    for col in columns:

        df[col] = (

            df[col]

            .fillna("不明")

            .astype(str)

            .str.strip()

        )

    log("カテゴリ列整形完了")

    return df


# ===========================================================
# バンク種別作成
# ===========================================================

def create_bank_type(df):
    """
    bank_type

    track_lengthから生成
    """

    log("bank_type 作成")

    conditions = [

        df["track_length"].isin([333, 335]),

        df["track_length"] == 400,

        df["track_length"] == 500,

    ]

    values = [

        "333・335系",

        "400系",

        "500系",

    ]

    df["bank_type"] = np.select(

        conditions,

        values,

        default="不明"

    )

    log("bank_type 完了")

    return df


# ===========================================================
# みなし直線区分作成
# ===========================================================

def create_straight_type(df):
    """
    straight_type

    straight_lengthから生成
    """

    log("straight_type 作成")

    conditions = [

        df["straight_length"] <= 45,

        (df["straight_length"] >= 46) &
        (df["straight_length"] <= 50),

        (df["straight_length"] >= 51) &
        (df["straight_length"] <= 55),

        (df["straight_length"] >= 56) &
        (df["straight_length"] <= 60),

        (df["straight_length"] >= 61) &
        (df["straight_length"] <= 65),

        df["straight_length"] >= 66,

    ]

    values = [

        1,

        2,

        3,

        4,

        5,

        6,

    ]

    df["straight_type"] = np.select(

        conditions,

        values,

        default=0

    ).astype(int)

    log("straight_type 完了")

    return df


# ===========================================================
# カント角作成
# ===========================================================

def create_bank_angle(df):
    """
    bank_angle

    四捨五入して整数化
    """

    log("bank_angle 作成")

    df["bank_angle"] = (

        df["bank_angle"]

        .round()

        .astype(int)

    )

    log("bank_angle 完了")

    return df

# ===========================================================
# メイン処理
# ===========================================================

def build_feature_race(df):
    """
    レース特徴量生成

    Parameters
    ----------
    df : pandas.DataFrame

    Returns
    -------
    pandas.DataFrame
    """

    print()

    log("=======================================")
    log("レース特徴量生成開始")
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
    # カテゴリ列整形
    # -----------------------------
    df = clean_category_columns(df)

    # -----------------------------
    # 曜日
    # -----------------------------
    df = create_weekday(df)

    # -----------------------------
    # バンク種別
    # -----------------------------
    df = create_bank_type(df)

    # -----------------------------
    # みなし直線区分
    # -----------------------------
    df = create_straight_type(df)

    # -----------------------------
    # カント角
    # -----------------------------
    df = create_bank_angle(df)

    print()

    log("生成特徴量")

    feature_columns = [

        "weekday",

        "jo_name",

        "grade",

        "race_type",

        "session",

        "weather",

        "wind_speed",

        "bank_type",

        "straight_type",

        "bank_angle",

    ]

    for col in feature_columns:

        log(f"  OK  {col}")

    print()

    log("=======================================")
    log("レース特徴量生成完了")
    log(f"データ件数 : {len(df):,}")
    log(f"特徴量数   : {len(feature_columns)}")
    log("=======================================")

    print()

    return df


# ===========================================================
# 動作確認
# ===========================================================

if __name__ == "__main__":

    log("feature_race.py")

    print()
    print("このファイルは")
    print("他プログラムからimportして使用します。")
    print()