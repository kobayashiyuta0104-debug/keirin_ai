"""
============================================================
feature_player.py
------------------------------------------------------------
01_選手特徴量

役割
・選手特徴量の前処理
・カテゴリ変数の数値化
・脚質One-Hot化
・数値型変換（Part2）
============================================================
"""

import pandas as pd

# ============================================================
# 級班変換テーブル
# ============================================================

CLASS_MAP = {
    "SS": 8,
    "S1": 7,
    "S2": 6,
    "A1": 5,
    "A2": 4,
    "A3": 3,
    "L1": 2,
    "L2": 1,
}


# ============================================================
# 必須カラム確認
# ============================================================

REQUIRED_COLUMNS = [

    "age",
    "term",

    "class",
    "previous_class",
    "style",

    "average_score",
    "win_rate",
    "quinella_rate",
    "trio_rate",

    "escape_count",
    "makuri_count",
    "sashi_count",
    "mark_count",

    "back_count",
    "home_count",
    "start_count",

]


# ============================================================
# 必須カラムチェック
# ============================================================

def check_columns(df):

    missing = []

    for col in REQUIRED_COLUMNS:

        if col not in df.columns:
            missing.append(col)

    if len(missing) > 0:

        raise ValueError(
            f"必須カラムがありません : {missing}"
        )


# ============================================================
# 現級班 数値化
# ============================================================

def encode_class(df):

    print("現級班 数値化")

    df["class"] = (
        df["class"]
        .astype(str)
        .str.strip()
        .map(CLASS_MAP)
    )

    return df


# ============================================================
# 前級班 数値化
# ============================================================

def encode_previous_class(df):

    print("前級班 数値化")

    df["previous_class"] = (
        df["previous_class"]
        .astype(str)
        .str.strip()
        .map(CLASS_MAP)
    )

    return df


# ============================================================
# 脚質 One-Hot Encoding
# ============================================================

def encode_style(df):

    print("脚質 One-Hot Encoding")

    df["style"] = (
        df["style"]
        .astype(str)
        .str.strip()
    )

    style_dummy = pd.get_dummies(

        df["style"],
        prefix="style",
        dtype=int

    )

    df = pd.concat(

        [
            df,
            style_dummy
        ],

        axis=1

    )

    # 元の脚質列は不要なので削除
    df = df.drop(columns=["style"])

    return df


# ============================================================
# 数値変換対象
# ============================================================

NUMERIC_COLUMNS = [

    "age",

    "term",

    "average_score",

    "win_rate",

    "quinella_rate",

    "trio_rate",

    "escape_count",

    "makuri_count",

    "sashi_count",

    "mark_count",

    "back_count",

    "home_count",

    "start_count",

]

INT_COLUMNS = [

    "age",
    "term",

    "escape_count",
    "makuri_count",
    "sashi_count",
    "mark_count",

    "back_count",
    "home_count",
    "start_count",

]

FLOAT_COLUMNS = [

    "average_score",

    "win_rate",

    "quinella_rate",

    "trio_rate",

]

# ============================================================
# 数値型へ変換
# ============================================================

def convert_numeric(df):

    print("数値型へ変換")

    # 数値へ変換
    for col in NUMERIC_COLUMNS:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # int型
    for col in INT_COLUMNS:

        df[col] = df[col].astype("Int64")

    # float型
    for col in FLOAT_COLUMNS:

        df[col] = df[col].astype(float)

    return df


# ============================================================
# 欠損値処理
# ============================================================

def fill_missing(df):

    print("欠損値補完")

    # 級班
    df["class"] = (
        df["class"]
        .fillna(0)
        .astype(int)
    )

    df["previous_class"] = (
        df["previous_class"]
        .fillna(0)
        .astype(int)
    )

    # 数値列
    for col in NUMERIC_COLUMNS:

        df[col] = df[col].fillna(0)

    return df


# ============================================================
# 選手特徴量作成
# ============================================================

def build_feature_player(df):

    print("")
    print("============================================================")
    print("01 選手特徴量 作成開始")
    print("============================================================")

    # --------------------------------------------------------
    # 必須カラム確認
    # --------------------------------------------------------

    check_columns(df)

    # --------------------------------------------------------
    # 現級班
    # --------------------------------------------------------

    df = encode_class(df)

    # --------------------------------------------------------
    # 前級班
    # --------------------------------------------------------

    df = encode_previous_class(df)

    # --------------------------------------------------------
    # 脚質
    # --------------------------------------------------------

    df = encode_style(df)

    # --------------------------------------------------------
    # 数値変換
    # --------------------------------------------------------

    df = convert_numeric(df)

    # --------------------------------------------------------
    # 欠損値
    # --------------------------------------------------------

    df = fill_missing(df)

    print("")
    print("追加された脚質特徴量")

    style_columns = sorted(

        [

            c

            for c in df.columns

            if c.startswith("style_")

        ]

    )

    for col in style_columns:

        print("   ", col)

    print(f"Rows    : {len(df):,}")
    print(f"Columns : {len(df.columns):,}")
    print("")
    print("選手特徴量 作成完了")
    print("")

    return df