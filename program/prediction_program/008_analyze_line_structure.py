# ===========================================================
#
# 競輪AI Ver1.0
# 008_analyze_line_structure.py
#
# ライン構造分析
#
# 【目的】
#
# training_race_features
#        ＋
# 2020～2022年 AI予想結果
#
# ↓
#
# ライン構造ごとの実際の高配当率を分析
#
# ↓
#
# 現在のAIがライン構造を
# どの程度予測に反映できているかを確認
#
# ===========================================================
#
# 【重要な仕様】
#
# ・1車ラインは「ライン数」に含めない
# ・1車ラインは「単騎」として別集計する
#
# 例：
#
# 3-2-1-1
#   ↓
# 実ライン数 = 2
# 単騎数     = 2
# ライン構成 = 3-2
#
# 5-3-1
#   ↓
# 実ライン数 = 2
# 単騎数     = 1
# ライン構成 = 5-3
#
# 5-2-2
#   ↓
# 実ライン数 = 3
# 単騎数     = 0
# ライン構成 = 5-2-2
#
# ===========================================================

import os

from pathlib import Path

import pandas as pd


# ===========================================================
# GitHub / Windows対応
# ===========================================================

if os.name == "nt":

    BASE = Path(r"C:\競輪AI")

else:

    BASE = (
        Path(__file__)
        .resolve()
        .parent
        .parent
        .parent
    )


# ===========================================================
# パス
# ===========================================================

TRAINING_DIR = (
    BASE
    / "csv"
    / "training"
)

AI_DIR = (
    BASE
    / "csv"
    / "ai"
)

ANALYSIS_DIR = (
    BASE
    / "csv"
    / "analysis"
    / "line_structure"
)


PREDICTION_CSV = (
    TRAINING_DIR
    / "training_prediction(2023.1.1~2026.7.30).csv"
)

FEATURE_CSV = (
    AI_DIR
    / "training_race_features(2023.1.1~2026.7.30).csv"
)

OUTPUT_XLSX = (
    ANALYSIS_DIR
    / "008_line_structure_analysis(2023.1.1~2026.7.30).xlsx"
)


# ===========================================================
# 払戻クラス
# ===========================================================

LOW_CLASS = "0～9,999円"

CLASS_10_30 = "10,000～29,999円"

CLASS_30 = "30,000～49,999円"

CLASS_50 = "50,000～99,999円"

CLASS_100 = "100,000円以上"


AI_CLASSES = [

    LOW_CLASS,

    CLASS_10_30,

    CLASS_30,

    CLASS_50,

    CLASS_100,

]


# ===========================================================
# 高配当AIクラス
# ===========================================================

AI_HIGH_30 = [

    CLASS_30,

    CLASS_50,

    CLASS_100,

]

AI_HIGH_50 = [

    CLASS_50,

    CLASS_100,

]

AI_HIGH_100 = [

    CLASS_100,

]


# ===========================================================
# ログ
# ===========================================================

def log(message):

    print(
        f"[008_analyze_line_structure] {message}"
    )


# ===========================================================
# Prediction CSV読込
# ===========================================================

def load_prediction():

    log("=======================================")

    log("Prediction CSV 読込")

    log("=======================================")

    if not PREDICTION_CSV.exists():

        raise FileNotFoundError(
            f"Prediction CSV がありません:\n"
            f"{PREDICTION_CSV}"
        )

    df = pd.read_csv(

        PREDICTION_CSV,

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
# Feature CSV読込
# ===========================================================

def load_features():

    log("=======================================")

    log("Training Race Features CSV 読込")

    log("=======================================")

    if not FEATURE_CSV.exists():

        raise FileNotFoundError(
            f"Feature CSV がありません:\n"
            f"{FEATURE_CSV}"
        )

    df = pd.read_csv(

        FEATURE_CSV,

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
# race_key統一
# ===========================================================

def normalize_race_key(
    prediction_df,
    feature_df,
):

    log("=======================================")

    log("race_key 統一")

    log("=======================================")

    # -------------------------------------------------------
    # Prediction側
    # -------------------------------------------------------

    if "race_key" in prediction_df.columns:

        prediction_df["_race_key"] = (
            prediction_df["race_key"]
            .astype(str)
            .str.strip()
        )

    elif "レースキー" in prediction_df.columns:

        prediction_df["_race_key"] = (
            prediction_df["レースキー"]
            .astype(str)
            .str.strip()
        )

    else:

        raise KeyError(
            "Prediction CSV に race_key / レースキー がありません"
        )

    # -------------------------------------------------------
    # Feature側
    # -------------------------------------------------------

    if "race_key" in feature_df.columns:

        feature_df["_race_key"] = (
            feature_df["race_key"]
            .astype(str)
            .str.strip()
        )

    else:

        raise KeyError(
            "Feature CSV に race_key がありません"
        )

    return (
        prediction_df,
        feature_df,
    )


# ===========================================================
# 予想と特徴量を結合
# ===========================================================

def merge_data(
    prediction_df,
    feature_df,
):

    log("=======================================")

    log("Prediction + Feature 結合")

    log("=======================================")

    # -------------------------------------------------------
    # predictionは1レース1行を想定
    # -------------------------------------------------------

    prediction_work = (
        prediction_df[
            [
                "_race_key",
                "AI予想",
                "AI確信度",
                "三連単\n払戻",
                "実際\nクラス",
            ]
        ]
        .drop_duplicates(
            subset="_race_key"
        )
        .copy()
    )

    # -------------------------------------------------------
    # Featureも1レース1行を想定
    # -------------------------------------------------------

    feature_work = (
        feature_df
        .drop_duplicates(
            subset="_race_key"
        )
        .copy()
    )

    merged = feature_work.merge(

        prediction_work,

        on="_race_key",

        how="inner",

    )

    log(
        f"結合後レース数 : "
        f"{len(merged):,}"
    )

    print()

    return merged


# ===========================================================
# ラインポジション存在判定
# ===========================================================
#
# L1_P1
# L1_P2
# L1_P3
#
# のような選手枠から、
# そのラインに何人存在するかを判定する。
#
# 「line_size」には依存しない。
#
# ===========================================================

def position_exists(
    row,
    line_no,
    position,
):

    prefix = (
        f"L{line_no}_P{position}_"
    )

    # -------------------------------------------------------
    # 同じポジションの列を取得
    # -------------------------------------------------------

    columns = [

        column

        for column in row.index

        if column.startswith(prefix)

    ]

    if not columns:

        return False

    # -------------------------------------------------------
    # どれか1つでも値が入っていれば
    # その選手ポジションは存在
    # -------------------------------------------------------

    for column in columns:

        value = row[column]

        if pd.notna(value):

            if str(value).strip() not in [

                "",

                "nan",

                "None",

            ]:

                return True

    return False


# ===========================================================
# レースのライン構成取得
# ===========================================================

def get_line_structure(row):

    line_sizes = []

    tanki_count = 0

    # -------------------------------------------------------
    # L1～L9を確認
    # -------------------------------------------------------

    for line_no in range(1, 10):

        size = 0

        # P1～P9
        for position in range(1, 10):

            if position_exists(
                row,
                line_no,
                position,
            ):

                size += 1

            else:

                # ポジションは連続している想定
                # 最初の欠損以降は選手なし
                break

        # ---------------------------------------------------
        # ラインが存在しない
        # ---------------------------------------------------

        if size == 0:

            continue

        # ---------------------------------------------------
        # 1車ライン
        # ---------------------------------------------------

        if size == 1:

            tanki_count += 1

        # ---------------------------------------------------
        # 2車以上
        # ---------------------------------------------------

        else:

            line_sizes.append(size)

    # -------------------------------------------------------
    # 大きいライン順
    # -------------------------------------------------------

    line_sizes = sorted(

        line_sizes,

        reverse=True,

    )

    # -------------------------------------------------------
    # 実ライン数
    #
    # 1車ラインは含めない
    # -------------------------------------------------------

    real_line_count = len(
        line_sizes
    )

    # -------------------------------------------------------
    # ライン構成
    #
    # 例：
    # [5, 3]
    # ↓
    # "5-3"
    # -------------------------------------------------------

    if line_sizes:

        line_structure = "-".join(

            str(size)

            for size in line_sizes

        )

    else:

        line_structure = "単騎のみ"

    return {

        "line_sizes": line_sizes,

        "real_line_count":
            real_line_count,

        "tanki_count":
            tanki_count,

        "line_structure":
            line_structure,

    }


# ===========================================================
# 全レースにライン構造を付与
# ===========================================================

def build_line_structure_data(
    df,
):

    log("=======================================")

    log("ライン構造生成")

    log("=======================================")

    records = []

    for index, row in df.iterrows():

        structure = get_line_structure(
            row
        )

        records.append(

            structure

        )

    structure_df = pd.DataFrame(
        records
    )

    result = pd.concat(

        [
            df.reset_index(
                drop=True
            ),

            structure_df,

        ],

        axis=1,

    )

    log(
        f"ライン構造生成完了 : "
        f"{len(result):,} レース"
    )

    print()

    return result


# ===========================================================
# 基本ライン構造集計
# ===========================================================

def analyze_structure_category(
    df,
    column,
):

    rows = []

    groups = (

        df.groupby(
            column,
            dropna=False,
            sort=False,
        )

    )

    for value, group in groups:

        payout = pd.to_numeric(

            group[
                "三連単\n払戻"
            ],

            errors="coerce",

        )

        actual_30 = (
            payout >= 30000
        )

        actual_50 = (
            payout >= 50000
        )

        actual_100 = (
            payout >= 100000
        )

        ai_30 = (
            group["AI予想"]
            .isin(AI_HIGH_30)
        )

        ai_50 = (
            group["AI予想"]
            .isin(AI_HIGH_50)
        )

        ai_100 = (
            group["AI予想"]
            .isin(AI_HIGH_100)
        )

        count = len(group)

        actual_30_rate = (
            actual_30.mean()
            * 100
            if count > 0
            else 0
        )

        actual_50_rate = (
            actual_50.mean()
            * 100
            if count > 0
            else 0
        )

        actual_100_rate = (
            actual_100.mean()
            * 100
            if count > 0
            else 0
        )

        ai_30_rate = (
            ai_30.mean()
            * 100
            if count > 0
            else 0
        )

        ai_50_rate = (
            ai_50.mean()
            * 100
            if count > 0
            else 0
        )

        ai_100_rate = (
            ai_100.mean()
            * 100
            if count > 0
            else 0
        )

        rows.append({

            "条件":
                column,

            "値":
                value,

            "レース数":
                count,

            "30,000円以上_実際率":
                round(
                    actual_30_rate,
                    2,
                ),

            "50,000円以上_実際率":
                round(
                    actual_50_rate,
                    2,
                ),

            "100,000円以上_実際率":
                round(
                    actual_100_rate,
                    2,
                ),

            "AI30,000円以上予想率":
                round(
                    ai_30_rate,
                    2,
                ),

            "AI50,000円以上予想率":
                round(
                    ai_50_rate,
                    2,
                ),

            "AI100,000円以上予想率":
                round(
                    ai_100_rate,
                    2,
                ),

            "実際30万- AI30万差":
                round(
                    actual_30_rate
                    -
                    ai_30_rate,
                    2,
                ),

            "実際50万- AI50万差":
                round(
                    actual_50_rate
                    -
                    ai_50_rate,
                    2,
                ),

            "実際100万- AI100万差":
                round(
                    actual_100_rate
                    -
                    ai_100_rate,
                    2,
                ),

        })

    return pd.DataFrame(rows)


# ===========================================================
# ライン人数別分析
# ===========================================================

def analyze_line_size(
    df,
):

    log("ライン人数別分析")

    rows = []

    # -------------------------------------------------------
    # 各レースの各ラインを1本ずつ展開
    # -------------------------------------------------------

    for _, row in df.iterrows():

        for size in row["line_sizes"]:

            rows.append({

                "line_size":
                    size,

                "race_key":
                    row["_race_key"],

                "AI予想":
                    row["AI予想"],

                "AI確信度":
                    row["AI確信度"],

                "payout":
                    row["三連単\n払戻"],

            })

    work = pd.DataFrame(rows)

    if work.empty:

        return pd.DataFrame()

    result_rows = []

    for size, group in work.groupby(
        "line_size",
        sort=True,
    ):

        payout = pd.to_numeric(

            group["payout"],

            errors="coerce",

        )

        actual_30 = (
            payout >= 30000
        )

        actual_50 = (
            payout >= 50000
        )

        actual_100 = (
            payout >= 100000
        )

        count = len(group)

        result_rows.append({

            "ライン人数":
                int(size),

            "対象ライン数":
                count,

            "対象レース数":
                group[
                    "race_key"
                ].nunique(),

            "30,000円以上率":
                round(
                    actual_30.mean()
                    * 100,
                    2,
                ),

            "50,000円以上率":
                round(
                    actual_50.mean()
                    * 100,
                    2,
                ),

            "100,000円以上率":
                round(
                    actual_100.mean()
                    * 100,
                    2,
                ),

        })

    return pd.DataFrame(
        result_rows
    )


# ===========================================================
# ライン構成分析
# ===========================================================

def analyze_line_structure(
    df,
):

    log("ライン構成分析")

    result = analyze_structure_category(

        df,

        "line_structure",

    )

    # -------------------------------------------------------
    # 件数の少ない構成も残す
    #
    # 後で人間が確認できるようにする
    # -------------------------------------------------------

    return result.sort_values(

        "レース数",

        ascending=False,

    ).reset_index(
        drop=True
    )


# ===========================================================
# ライン数分析
# ===========================================================

def analyze_real_line_count(
    df,
):

    return analyze_structure_category(

        df,

        "real_line_count",

    )


# ===========================================================
# 単騎数分析
# ===========================================================

def analyze_tanki_count(
    df,
):

    return analyze_structure_category(

        df,

        "tanki_count",

    )


# ===========================================================
# AI5クラス分布
# ===========================================================

def analyze_ai_distribution_by_condition(
    df,
    condition_column,
):

    rows = []

    for value, group in df.groupby(
        condition_column,
        dropna=False,
        sort=False,
    ):

        total = len(group)

        if total == 0:

            continue

        counts = (
            group["AI予想"]
            .value_counts()
        )

        row = {

            "条件":
                condition_column,

            "値":
                value,

            "レース数":
                total,

        }

        for ai_class in AI_CLASSES:

            count = counts.get(
                ai_class,
                0,
            )

            row[
                f"AI_{ai_class}_件数"
            ] = int(count)

            row[
                f"AI_{ai_class}_率"
            ] = round(

                count
                /
                total
                *
                100,

                2,

            )

        rows.append(row)

    return pd.DataFrame(rows)


# ===========================================================
# 全体構成AI分布
# ===========================================================

def build_ai_distribution_sheets(
    df,
):

    sheets = {}

    for column, sheet_name in [

        (
            "line_structure",
            "構成_AI分布",
        ),

        (
            "real_line_count",
            "ライン数_AI分布",
        ),

        (
            "tanki_count",
            "単騎数_AI分布",
        ),

    ]:

        sheets[
            sheet_name
        ] = analyze_ai_distribution_by_condition(

            df,

            column,

        )

    return sheets


# ===========================================================
# ライン構造 × 実際クラス
# ===========================================================

def analyze_actual_class_distribution(
    df,
):

    rows = []

    for value, group in df.groupby(
        "line_structure",
        dropna=False,
        sort=False,
    ):

        total = len(group)

        counts = (
            group[
                "実際\nクラス"
            ]
            .value_counts()
        )

        row = {

            "ライン構成":
                value,

            "レース数":
                total,

        }

        for payout_class in [

            LOW_CLASS,

            CLASS_10_30,

            CLASS_30,

            CLASS_50,

            CLASS_100,

        ]:

            count = counts.get(
                payout_class,
                0,
            )

            row[
                f"{payout_class}_件数"
            ] = int(count)

            row[
                f"{payout_class}_率"
            ] = round(

                count
                /
                total
                *
                100,

                2,

            )

        rows.append(row)

    return pd.DataFrame(rows)


# ===========================================================
# Excel保存
# ===========================================================

def save_excel(
    sheets,
):

    log("=======================================")

    log("Excel保存")

    log("=======================================")

    ANALYSIS_DIR.mkdir(

        parents=True,

        exist_ok=True,

    )

    with pd.ExcelWriter(

        OUTPUT_XLSX,

        engine="openpyxl",

    ) as writer:

        for sheet_name, data in sheets.items():

            if data is None:

                continue

            if len(data) == 0:

                continue

            # Excelシート名31文字制限
            safe_name = (
                str(sheet_name)[:31]
            )

            data.to_excel(

                writer,

                sheet_name=safe_name,

                index=False,

            )

    log(
        f"保存先 : {OUTPUT_XLSX}"
    )

    print()


# ===========================================================
# Main
# ===========================================================

def main():

    print()

    log("=======================================")

    log("008 Analyze Line Structure")

    log("=======================================")

    # -------------------------------------------------------
    # CSV読込
    # -------------------------------------------------------

    prediction_df = load_prediction()

    feature_df = load_features()

    # -------------------------------------------------------
    # race_key統一
    # -------------------------------------------------------

    prediction_df, feature_df = (
        normalize_race_key(
            prediction_df,
            feature_df,
        )
    )

    # -------------------------------------------------------
    # 結合
    # -------------------------------------------------------

    df = merge_data(

        prediction_df,

        feature_df,

    )

    # -------------------------------------------------------
    # ライン構造生成
    # -------------------------------------------------------

    df = build_line_structure_data(
        df
    )

    # -------------------------------------------------------
    # 基本分析
    # -------------------------------------------------------

    sheets = {}

    sheets[
        "ライン人数別"
    ] = analyze_line_size(
        df
    )

    sheets[
        "実ライン数"
    ] = analyze_real_line_count(
        df
    )

    sheets[
        "単騎数"
    ] = analyze_tanki_count(
        df
    )

    sheets[
        "ライン構成"
    ] = analyze_line_structure(
        df
    )

    # -------------------------------------------------------
    # AI予測分布
    # -------------------------------------------------------

    ai_sheets = (
        build_ai_distribution_sheets(
            df
        )
    )

    sheets.update(
        ai_sheets
    )

    # -------------------------------------------------------
    # ライン構成 × 実際の5クラス
    # -------------------------------------------------------

    sheets[
        "構成_実際クラス"
    ] = analyze_actual_class_distribution(
        df
    )

    # -------------------------------------------------------
    # 全レース構造データ
    # -------------------------------------------------------

    structure_columns = [

        "_race_key",

        "line_sizes",

        "real_line_count",

        "tanki_count",

        "line_structure",

        "AI予想",

        "AI確信度",

        "三連単\n払戻",

        "実際\nクラス",

    ]

    existing_columns = [

        column

        for column in structure_columns

        if column in df.columns

    ]

    sheets[
        "レース別ライン構造"
    ] = df[
        existing_columns
    ].copy()

    # -------------------------------------------------------
    # Excel保存
    # -------------------------------------------------------

    save_excel(
        sheets
    )

    log("Complete")

    print()


# ===========================================================
# 実行
# ===========================================================

if __name__ == "__main__":

    main()