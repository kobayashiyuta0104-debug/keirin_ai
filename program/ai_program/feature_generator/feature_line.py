"""
===========================================================
競輪AI Ver1.0
feature_line.py

ライン特徴量生成

【役割】
feature_player.py の出力を受け取り、
ラインに関する特徴量を生成する。

生成特徴量

1 line_count
2 line_size
3 tanki_count
4 max_line_size
5 min_line_size
6 is_tanki
7 is_head
8 is_second
9 is_third
10 is_fourth_plus

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
    print(f"[feature_line] {message}")


# ===========================================================
# 必須カラム
# ===========================================================

REQUIRED_COLUMNS = [

    "race_key",

    "line_no",

    "line_position",

]


# ===========================================================
# 必須カラムチェック
# ===========================================================

def check_required_columns(df):
    """
    必須カラム存在確認
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
    line_no
    line_position

    数値へ変換
    """

    log("数値変換開始")

    columns = [

        "line_no",

        "line_position",

    ]

    for col in columns:

        df[col] = pd.to_numeric(

            df[col],

            errors="coerce"

        )

    df[columns] = df[columns].fillna(0)

    df[columns] = df[columns].astype(int)

    log("数値変換完了")

    return df


# ===========================================================
# ライン人数作成
# ===========================================================

def create_line_size(df):
    """
    line_size

    同じline_noに所属する人数
    """

    log("ライン人数作成")

    line_size = (

        df

        .groupby(

            [

                "race_key",

                "line_no"

            ]

        )

        .size()

        .reset_index(

            name="line_size"

        )

    )

    df = df.merge(

        line_size,

        on=[

            "race_key",

            "line_no"

        ],

        how="left"

    )

    log("line_size 完了")

    return df

# ===========================================================
# ライン情報作成
# ===========================================================

def create_line_info(df):
    """
    ライン情報作成

    各レース・各ラインを
    1行にまとめる
    """

    line_info = (

        df[
            [
                "race_key",
                "line_no",
                "line_size"
            ]
        ]

        .drop_duplicates()

    )

    return line_info
# ===========================================================
# ライン数作成
# ===========================================================

def create_line_count(df):
    """
    line_count

    レース内ライン数

    単騎は除外
    """

    log("ライン数作成")

    line_info = create_line_info(df)

    line_info = line_info[

        line_info["line_size"] >= 2

    ]

    line_count = (

        line_info

        .groupby(

            "race_key"

        )

        .size()

        .reset_index(

            name="line_count"

        )

    )

    df = df.merge(

        line_count,

        on="race_key",

        how="left"

    )

    df["line_count"] = (

        df["line_count"]

        .fillna(0)

        .astype(int)

    )

    log("line_count 完了")

    return df

# ===========================================================
# 単騎人数作成
# ===========================================================

def create_tanki_count(df):
    """
    tanki_count

    レース内の単騎人数
    """

    log("単騎人数作成")

    line_info = create_line_info(df)

    tanki = line_info[

        line_info["line_size"] == 1

    ]

    tanki_count = (

        tanki

        .groupby(

            "race_key"

        )

        .size()

        .reset_index(

            name="tanki_count"

        )

    )

    df = df.merge(

        tanki_count,

        on="race_key",

        how="left"

    )

    df["tanki_count"] = (

        df["tanki_count"]

        .fillna(0)

        .astype(int)

    )

    log("tanki_count 完了")

    return df


# ===========================================================
# 最大ライン人数作成
# ===========================================================

def create_max_line_size(df):
    """
    max_line_size

    単騎を除いた最大ライン人数
    """

    log("最大ライン人数作成")

    line_info = create_line_info(df)

    line_info = line_info[

        line_info["line_size"] >= 2

    ]

    max_size = (

        line_info

        .groupby(

            "race_key"

        )["line_size"]

        .max()

        .reset_index(

            name="max_line_size"

        )

    )

    df = df.merge(

        max_size,

        on="race_key",

        how="left"

    )

    df["max_line_size"] = (

        df["max_line_size"]

        .fillna(0)

        .astype(int)

    )

    log("max_line_size 完了")

    return df


# ===========================================================
# 最小ライン人数作成
# ===========================================================

def create_min_line_size(df):
    """
    min_line_size

    単騎を除いた最小ライン人数
    """

    log("最小ライン人数作成")

    line_info = create_line_info(df)

    line_info = line_info[

        line_info["line_size"] >= 2

    ]

    min_size = (

        line_info

        .groupby(

            "race_key"

        )["line_size"]

        .min()

        .reset_index(

            name="min_line_size"

        )

    )

    df = df.merge(

        min_size,

        on="race_key",

        how="left"

    )

    df["min_line_size"] = (

        df["min_line_size"]

        .fillna(0)

        .astype(int)

    )

    log("min_line_size 完了")

    return df


# ===========================================================
# 単騎フラグ
# ===========================================================

def create_is_tanki(df):
    """
    is_tanki

    単騎なら1
    """

    log("単騎フラグ作成")

    df["is_tanki"] = np.where(

        df["line_size"] == 1,

        1,

        0

    )

    return df


# ===========================================================
# ライン先頭フラグ
# ===========================================================

def create_is_head(df):
    """
    is_head

    ライン先頭なら1
    """

    log("先頭フラグ作成")

    df["is_head"] = np.where(

        df["line_position"] == 1,

        1,

        0

    )

    return df


# ===========================================================
# ライン番手フラグ
# ===========================================================

def create_is_second(df):
    """
    is_second

    ライン2番手なら1
    """

    log("番手フラグ作成")

    df["is_second"] = np.where(

        df["line_position"] == 2,

        1,

        0

    )

    return df


# ===========================================================
# ライン三番手フラグ
# ===========================================================

def create_is_third(df):
    """
    is_third

    ライン3番手なら1
    """

    log("三番手フラグ作成")

    df["is_third"] = np.where(

        df["line_position"] == 3,

        1,

        0

    )

    return df


# ===========================================================
# ライン四番手以降フラグ
# ===========================================================

def create_is_fourth_plus(df):
    """
    is_fourth_plus

    ライン4番手以降なら1
    """

    log("四番手以降フラグ作成")

    df["is_fourth_plus"] = np.where(

        df["line_position"] >= 4,

        1,

        0

    )

    return df

# ===========================================================
# メイン処理
# ===========================================================

def build_feature_line(df):
    """
    ライン特徴量生成

    Parameters
    ----------
    df : pandas.DataFrame

    Returns
    -------
    pandas.DataFrame
    """

    print()
    log("=======================================")
    log("ライン特徴量生成開始")
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
    # ライン人数
    # -----------------------------
    df = create_line_size(df)

    # -----------------------------
    # ライン数
    # -----------------------------
    df = create_line_count(df)

    # -----------------------------
    # 単騎人数
    # -----------------------------
    df = create_tanki_count(df)

    # -----------------------------
    # 最大ライン人数
    # -----------------------------
    df = create_max_line_size(df)

    # -----------------------------
    # 最小ライン人数
    # -----------------------------
    df = create_min_line_size(df)

    # -----------------------------
    # 単騎フラグ
    # -----------------------------
    df = create_is_tanki(df)

    # -----------------------------
    # 先頭フラグ
    # -----------------------------
    df = create_is_head(df)

    # -----------------------------
    # 番手フラグ
    # -----------------------------
    df = create_is_second(df)

    # -----------------------------
    # 三番手フラグ
    # -----------------------------
    df = create_is_third(df)

    # -----------------------------
    # 四番手以降フラグ
    # -----------------------------
    df = create_is_fourth_plus(df)

    print()

    log("生成特徴量")

    feature_columns = [

        "line_count",

        "line_size",

        "tanki_count",

        "max_line_size",

        "min_line_size",

        "is_tanki",

        "is_head",

        "is_second",

        "is_third",

        "is_fourth_plus",

    ]

    for col in feature_columns:

        log(f"  OK  {col}")

    print()

    log("=======================================")
    log("ライン特徴量生成完了")
    log(f"データ件数 : {len(df):,}")
    log(f"特徴量数   : {len(feature_columns)}")
    log("=======================================")

    print()

    return df


# ===========================================================
# 動作確認
# ===========================================================

if __name__ == "__main__":

    log("feature_line.py")

    print()
    print("このファイルは")
    print("他プログラムからimportして使用します。")
    print()