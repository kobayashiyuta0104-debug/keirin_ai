"""
============================================================
feature_player.py
------------------------------------------------------------
01_選手特徴量

役割
・選手特徴量の前処理
・カテゴリ変数の数値化
・脚質One-Hot化
・地区情報の付与
・数値型変換（Part2）
============================================================
"""

import pandas as pd
import json


# ============================================================
# 地区マスタ
# ============================================================

DISTRICT_MASTER_FILE = (
    r"C:\競輪AI\data_official\master\district_master.json"
)


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

    "prefecture",

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
# 地区マスタ読み込み
# ============================================================

def load_district_master():

    print("地区マスタ読み込み")

    try:

        with open(
            DISTRICT_MASTER_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            district_data = json.load(f)

    except FileNotFoundError:

        raise FileNotFoundError(
            f"地区マスタが見つかりません : "
            f"{DISTRICT_MASTER_FILE}"
        )

    except json.JSONDecodeError:

        raise ValueError(
            f"地区マスタのJSON形式が正しくありません : "
            f"{DISTRICT_MASTER_FILE}"
        )

    print(
        f"   地区マスタ件数 : {len(district_data)}"
    )

    return district_data


# ============================================================
# 地区情報付与
# ============================================================

def add_region(df):

    print("地区情報付与")

    district_data = load_district_master()

    # --------------------------------------------------------
    # 都道府県名 → 地区 の辞書を作成
    # --------------------------------------------------------

    prefecture_to_region = {}

    for row in district_data:

        prefecture = row.get("都道府県\n名")
        region = row.get("地区")

        if prefecture is None:
            continue

        prefecture = str(prefecture).strip()

        prefecture_to_region[prefecture] = region

    # --------------------------------------------------------
    # 選手の都道府県から地区を取得
    # --------------------------------------------------------

    df["prefecture"] = (
        df["prefecture"]
        .astype(str)
        .str.replace(r"\s+", "", regex=True)
    )

    df["region"] = (
        df["prefecture"]
        .map(prefecture_to_region)
    )

    # --------------------------------------------------------
    # 地区が取得できなかった場合
    # --------------------------------------------------------

    missing_region = df.loc[
        df["region"].isna(),
        "prefecture"
    ].drop_duplicates().tolist()

    if len(missing_region) > 0:

        raise ValueError(
            "地区を取得できない都道府県があります : "
            f"{missing_region}"
        )

    print(
        f"   地区付与完了 : {df['region'].nunique()}地区"
    )

    return df



# ============================================================
# 地元バンク特徴量付与
# ============================================================

def add_home_bank(df):
    """
    home_bank

    1 = 登録府県と開催バンクの都道府県が同じ
    2 = 同地区、または中国・四国間
    3 = その他
    """

    print("地元バンク特徴量付与")

    district_data = load_district_master()

    # ----------------------------------------
    # 都道府県ごとの地区・ホームバンク情報
    # ----------------------------------------

    prefecture_info = {}
    bank_to_prefecture = {}

    for row in district_data:

        prefecture = str(
            row.get("都道府県\n名", "")
        ).strip()

        region = str(
            row.get("地区", "")
        ).strip()

        if not prefecture:
            continue

        prefecture_info[prefecture] = {
            "region": region
        }

        for key in [
            "ホーム\nバンク①",
            "ホーム\nバンク②",
            "ホーム\nバンク③",
        ]:
            bank_name = row.get(key)

            if bank_name is None:
                continue

            bank_name = str(bank_name).strip()

            if bank_name:
                bank_to_prefecture[bank_name] = prefecture

    # ----------------------------------------
    # 開催場名・登録府県の表記を整える
    # ----------------------------------------

    df["prefecture"] = (
        df["prefecture"]
        .fillna("")
        .astype(str)
        .str.replace(r"\s+", "", regex=True)
    )

    df["jo_name"] = (
        df["jo_name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # ----------------------------------------
    # 開催場名から開催場の都道府県を特定
    # ----------------------------------------

    df["_venue_prefecture"] = df["jo_name"].map(
        bank_to_prefecture
    )

    # ----------------------------------------
    # home_bank 判定
    # ----------------------------------------

    def judge_home_bank(row):

        player_prefecture = row["prefecture"]
        venue_prefecture = row["_venue_prefecture"]

        # 開催場を特定できない場合はエラーにせず欠損扱い
        if not venue_prefecture:
            return pd.NA

        # ① 登録府県と開催場の都道府県が同じ
        if player_prefecture == venue_prefecture:
            return 1

        player_region = prefecture_info.get(
            player_prefecture, {}
        ).get("region")

        venue_region = prefecture_info.get(
            venue_prefecture, {}
        ).get("region")

        # ② 同地区
        if player_region and player_region == venue_region:
            return 2

        # ② 中国・四国間も同地区扱い
        china_shikoku = {"中国", "四国"}

        if (
            player_region in china_shikoku
            and venue_region in china_shikoku
        ):
            return 2

        # ③ その他
        return 3

    df["home_bank"] = df.apply(
        judge_home_bank,
        axis=1
    ).astype("Int64")

    # 内部処理用の列を削除
    df.drop(
        columns=["_venue_prefecture"],
        inplace=True
    )

    missing_venues = sorted(
        df.loc[
            df["home_bank"].isna(),
            "jo_name"
        ].unique().tolist()
    )

    if missing_venues:
        print(
            "開催場をマスターから特定できませんでした:",
            missing_venues
        )

    print("home_bank 付与完了")
    print(df["home_bank"].value_counts(dropna=False).sort_index())

    return df


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
    # 地区情報
    # --------------------------------------------------------

    df = add_region(df)

    # --------------------------------------------------------
    # 地元バンク情報
    # --------------------------------------------------------

    df = add_home_bank(df)

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

    print("")
    print("追加された地区特徴量")
    print("    region")

    print(f"Rows    : {len(df):,}")
    print(f"Columns : {len(df.columns):,}")
    print("")
    print("選手特徴量 作成完了")
    print("")

    return df