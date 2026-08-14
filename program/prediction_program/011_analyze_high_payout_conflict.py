"""
===========================================================
競輪AI Ver1.0
011_analyze_high_payout_conflict.py

高配当要因 vs 低配当要因 競合分析

【目的】

2020～2022年のレースを対象に、

A:
実際30,000円以上
AIも30,000円以上

B:
実際30,000円以上
AIは30,000円未満
※ AI見逃し高配当

C:
実際30,000円未満
AIも30,000円未満

D:
実際30,000円未満
AIは30,000円以上

の4グループを作る。

2,848特徴量を事前分類せず、

・高配当側に偏る特徴
・低配当側に偏る特徴
・AI見逃し側に偏る特徴
・高配当特徴が存在するのにAIが低配当にした可能性

を統計的に調査する。

【重要】

・再学習しない
・モデル変更しない
・特徴量変更しない
・予測しない
・分析のみ
・既存CSVを変更しない
===========================================================
"""

import os
from pathlib import Path

import numpy as np
import pandas as pd


# ===========================================================
# 基本設定
# ===========================================================

if os.name == "nt":
    BASE = Path(r"C:\競輪AI")
else:
    BASE = Path(__file__).resolve().parent.parent.parent


# ===========================================================
# 入力
# ===========================================================

PREDICTION_FILE = (
    BASE
    / "csv"
    / "training"
    / "training_prediction(2020.1.1~2022.12.31).csv"
)

FEATURE_FILE = (
    BASE
    / "csv"
    / "ai"
    / "training_race_features(2020.1.1~2022.12.31).csv"
)


# ===========================================================
# 出力
# ===========================================================

OUTPUT_DIR = (
    BASE
    / "csv"
    / "analysis"
    / "high_payout_conflict"
)

OUTPUT_XLSX = (
    OUTPUT_DIR
    / "011_high_payout_conflict_analysis.xlsx"
)

OUTPUT_MERGED = (
    OUTPUT_DIR
    / "011_merged_data.csv"
)


# ===========================================================
# 条件
# ===========================================================

HIGH_PAYOUT_THRESHOLD = 30000

MIN_SAMPLE_COUNT = 100

EFFECT_THRESHOLD = 0.20


# ===========================================================
# ログ
# ===========================================================

def log(message):
    print(
        f"[011_analyze_high_payout_conflict] "
        f"{message}"
    )


# ===========================================================
# CSV読込
# ===========================================================

def read_csv_safely(file):

    encodings = [
        "utf-8-sig",
        "utf-8",
        "cp932",
        "shift_jis",
    ]

    last_error = None

    for encoding in encodings:

        try:

            return pd.read_csv(
                file,
                encoding=encoding,
                low_memory=False,
            )

        except Exception as e:

            last_error = e

    raise last_error


# ===========================================================
# race_key正規化
# ===========================================================

def normalize_race_key(value):

    if pd.isna(value):
        return ""

    return str(value).strip()


# ===========================================================
# Prediction読込
# ===========================================================

def load_prediction():

    log("=======================================")
    log("Prediction CSV 読込")
    log("=======================================")

    if not PREDICTION_FILE.exists():

        raise FileNotFoundError(
            f"Prediction CSVがありません:\n"
            f"{PREDICTION_FILE}"
        )

    df = read_csv_safely(
        PREDICTION_FILE
    )

    log(
        f"Rows    : {len(df):,}"
    )

    log(
        f"Columns : {len(df.columns):,}"
    )

    required = [
        "レースキー",
        "AI予想",
        "三連単\n払戻",
    ]

    missing = [
        c
        for c in required
        if c not in df.columns
    ]

    if missing:

        raise KeyError(
            f"Prediction CSVに必要な列がありません:\n"
            f"{missing}"
        )

    df["race_key"] = (
        df["レースキー"]
        .astype(str)
        .str.strip()
    )

    df["_payout"] = pd.to_numeric(
        df["三連単\n払戻"],
        errors="coerce",
    )

    return df


# ===========================================================
# Feature読込
# ===========================================================

def load_feature():

    log("=======================================")
    log("Training Race Features CSV 読込")
    log("=======================================")

    if not FEATURE_FILE.exists():

        raise FileNotFoundError(
            f"Training Race Features CSVがありません:\n"
            f"{FEATURE_FILE}"
        )

    df = read_csv_safely(
        FEATURE_FILE
    )

    log(
        f"Rows    : {len(df):,}"
    )

    log(
        f"Columns : {len(df.columns):,}"
    )

    if "race_key" not in df.columns:

        raise KeyError(
            f"Feature CSVにrace_keyがありません:\n"
            f"{FEATURE_FILE}"
        )

    if len(df.columns) < 500:

        raise ValueError(
            "Feature CSVの特徴量数が少なすぎます。"
        )

    df["race_key"] = (
        df["race_key"]
        .astype(str)
        .str.strip()
    )

    return df


# ===========================================================
# Prediction + Feature結合
# ===========================================================

def merge_data(
    prediction_df,
    feature_df,
):

    log("=======================================")
    log("Prediction + Feature 結合")
    log("=======================================")

    pred = prediction_df.copy()
    feat = feature_df.copy()

    pred["race_key"] = (
        pred["race_key"]
        .apply(normalize_race_key)
    )

    feat["race_key"] = (
        feat["race_key"]
        .apply(normalize_race_key)
    )

    pred = pred.drop_duplicates(
        subset=["race_key"],
        keep="last",
    )

    feat = feat.drop_duplicates(
        subset=["race_key"],
        keep="last",
    )

    merged = pred.merge(
        feat,
        on="race_key",
        how="inner",
        suffixes=(
            "",
            "_feature",
        ),
    )

    log(
        f"結合後レース数 : "
        f"{len(merged):,}"
    )

    if len(merged) == 0:

        raise ValueError(
            "PredictionとFeatureの結合結果が0件です。"
        )

    return merged


# ===========================================================
# AIクラス判定
# ===========================================================

def is_ai_high(value):

    if pd.isna(value):
        return False

    text = str(value).strip()

    high_words = [
        "30,000～49,999",
        "50,000～99,999",
        "100,000",
        "100000",
    ]

    return any(
        word in text
        for word in high_words
    )


# ===========================================================
# グループ作成
# ===========================================================

def create_groups(df):

    result = df.copy()

    result["_actual_high"] = (
        result["_payout"]
        >= HIGH_PAYOUT_THRESHOLD
    )

    result["_ai_high"] = (
        result["AI予想"]
        .apply(is_ai_high)
    )

    # -------------------------------------------------------
    # A
    # 実際高配当 + AI高配当
    # -------------------------------------------------------

    result["_group"] = np.select(
        [
            (
                result["_actual_high"]
            )
            &
            (
                result["_ai_high"]
            ),

            (
                result["_actual_high"]
            )
            &
            (
                ~result["_ai_high"]
            ),

            (
                ~result["_actual_high"]
            )
            &
            (
                ~result["_ai_high"]
            ),

            (
                ~result["_actual_high"]
            )
            &
            (
                result["_ai_high"]
            ),
        ],
        [
            "A_実際高配当_AI高配当",
            "B_実際高配当_AI低配当",
            "C_実際低配当_AI低配当",
            "D_実際低配当_AI高配当",
        ],
        default="対象外",
    )

    return result


# ===========================================================
# 特徴量列取得
# ===========================================================

def get_feature_columns(df):

    exclude = {
        "race_key",

        "レースキー",

        "date",
        "target_date",
        "開催日",
        "日付",

        "jo_code",
        "jo_name",
        "race_no",
        "event_name",
        "grade",

        "trifecta",
        "trifecta_payout",
        "三連単\n払戻",

        "AI予想",
        "AI確信度",
        "実際\nクラス",
        "的中判定",

        "_payout",
        "_actual_high",
        "_ai_high",
        "_group",

        "_date",
        "_period",
        "_source_file",
        "_feature_date",
    }

    columns = []

    for column in df.columns:

        if column in exclude:
            continue

        if column.endswith(
            "_feature"
        ):
            continue

        if df[column].dtype == "object":
            continue

        numeric = pd.to_numeric(
            df[column],
            errors="coerce",
        )

        # 完全に数値化できない列は除外
        if numeric.notna().sum() == 0:
            continue

        columns.append(column)

    return columns


# ===========================================================
# Cohen's d
# ===========================================================

def cohens_d(
    group1,
    group2,
):

    a = pd.to_numeric(
        group1,
        errors="coerce",
    ).dropna()

    b = pd.to_numeric(
        group2,
        errors="coerce",
    ).dropna()

    if (
        len(a) < 2
        or len(b) < 2
    ):
        return np.nan

    var_a = a.var(
        ddof=1
    )

    var_b = b.var(
        ddof=1
    )

    pooled = np.sqrt(
        (
            (
                len(a) - 1
            )
            * var_a
            +
            (
                len(b) - 1
            )
            * var_b
        )
        /
        (
            len(a)
            +
            len(b)
            -
            2
        )
    )

    if (
        pd.isna(pooled)
        or pooled == 0
    ):
        return np.nan

    return (
        a.mean()
        -
        b.mean()
    ) / pooled


# ===========================================================
# 効果量
# ===========================================================

def effect_strength(value):

    if pd.isna(value):
        return ""

    value = abs(
        float(value)
    )

    if value >= 0.8:
        return "大"

    if value >= 0.5:
        return "中"

    if value >= 0.2:
        return "小"

    return "極小"


# ===========================================================
# 2グループ比較
# ===========================================================

def compare_groups(
    df1,
    df2,
    feature_columns,
    name1,
    name2,
):

    rows = []

    for index, feature in enumerate(
        feature_columns,
        start=1,
    ):

        a = pd.to_numeric(
            df1[feature],
            errors="coerce",
        ).dropna()

        b = pd.to_numeric(
            df2[feature],
            errors="coerce",
        ).dropna()

        if (
            len(a) < MIN_SAMPLE_COUNT
            or
            len(b) < MIN_SAMPLE_COUNT
        ):
            continue

        mean_a = a.mean()
        mean_b = b.mean()

        median_a = a.median()
        median_b = b.median()

        d = cohens_d(
            a,
            b,
        )

        rows.append(
            {
                "feature": feature,

                f"{name1}_count":
                    len(a),

                f"{name2}_count":
                    len(b),

                f"{name1}_mean":
                    mean_a,

                f"{name2}_mean":
                    mean_b,

                "mean_difference":
                    mean_a - mean_b,

                f"{name1}_median":
                    median_a,

                f"{name2}_median":
                    median_b,

                "cohens_d":
                    d,

                "abs_cohens_d":
                    abs(d)
                    if not pd.isna(d)
                    else np.nan,

                "effect_strength":
                    effect_strength(d),
            }
        )

    result = pd.DataFrame(
        rows
    )

    if result.empty:
        return result

    result = result.sort_values(
        "abs_cohens_d",
        ascending=False,
    )

    result["rank"] = range(
        1,
        len(result) + 1,
    )

    return result


# ===========================================================
# 競合特徴量抽出
# ===========================================================

def create_conflict_analysis(
    high_vs_low,
    missed_vs_correct,
    missed_vs_low,
):

    if (
        high_vs_low.empty
        or missed_vs_correct.empty
        or missed_vs_low.empty
    ):
        return pd.DataFrame()

    a = high_vs_low[
        [
            "feature",
            "cohens_d",
            "abs_cohens_d",
        ]
    ].copy()

    a = a.rename(
        columns={
            "cohens_d":
                "d_high_vs_low",
            "abs_cohens_d":
                "abs_d_high_vs_low",
        }
    )

    b = missed_vs_correct[
        [
            "feature",
            "cohens_d",
            "abs_cohens_d",
        ]
    ].copy()

    b = b.rename(
        columns={
            "cohens_d":
                "d_missed_vs_correct",
            "abs_cohens_d":
                "abs_d_missed_vs_correct",
        }
    )

    c = missed_vs_low[
        [
            "feature",
            "cohens_d",
            "abs_cohens_d",
        ]
    ].copy()

    c = c.rename(
        columns={
            "cohens_d":
                "d_missed_vs_low",
            "abs_cohens_d":
                "abs_d_missed_vs_low",
        }
    )

    result = (
        a.merge(
            b,
            on="feature",
            how="inner",
        )
        .merge(
            c,
            on="feature",
            how="inner",
        )
    )

    # -------------------------------------------------------
    # 高配当シグナル
    #
    # high vs low が正
    # → 高配当側で値が高い
    #
    # high vs low が負
    # → 低配当側で値が高い
    # -------------------------------------------------------

    result["high_payout_direction"] = np.select(
        [
            result["d_high_vs_low"]
            >= EFFECT_THRESHOLD,

            result["d_high_vs_low"]
            <= -EFFECT_THRESHOLD,
        ],
        [
            "高配当側",
            "低配当側",
        ],
        default="差小",
    )

    # -------------------------------------------------------
    # 見逃し特徴
    # -------------------------------------------------------

    result["missed_direction"] = np.select(
        [
            result["d_missed_vs_correct"]
            >= EFFECT_THRESHOLD,

            result["d_missed_vs_correct"]
            <= -EFFECT_THRESHOLD,
        ],
        [
            "見逃し側",
            "的中側",
        ],
        default="差小",
    )

    # -------------------------------------------------------
    # 競合判定
    #
    # 高配当側では高い
    # しかし見逃し側では低い
    #
    # または
    #
    # 高配当側では低い
    # しかし見逃し側では高い
    # -------------------------------------------------------

    result["conflict_type"] = np.select(
        [
            (
                result["d_high_vs_low"]
                >= EFFECT_THRESHOLD
            )
            &
            (
                result["d_missed_vs_correct"]
                <= -EFFECT_THRESHOLD
            ),

            (
                result["d_high_vs_low"]
                <= -EFFECT_THRESHOLD
            )
            &
            (
                result["d_missed_vs_correct"]
                >= EFFECT_THRESHOLD
            ),
        ],
        [
            "高配当シグナルが見逃し側で弱い",
            "低配当シグナルが見逃し側で強い",
        ],
        default="明確な競合なし",
    )

    # -------------------------------------------------------
    # 競合スコア
    # -------------------------------------------------------

    result["conflict_score"] = (
        result["abs_d_high_vs_low"]
        *
        result["abs_d_missed_vs_correct"]
    )

    result = result.sort_values(
        "conflict_score",
        ascending=False,
    )

    result["rank"] = range(
        1,
        len(result) + 1,
    )

    return result


# ===========================================================
# グループ概要
# ===========================================================

def create_group_summary(
    df,
):

    rows = []

    group_names = [
        "A_実際高配当_AI高配当",
        "B_実際高配当_AI低配当",
        "C_実際低配当_AI低配当",
        "D_実際低配当_AI高配当",
    ]

    for group_name in group_names:

        temp = df[
            df["_group"]
            == group_name
        ]

        rows.append(
            {
                "group":
                    group_name,

                "race_count":
                    len(temp),

                "average_payout":
                    temp["_payout"].mean()
                    if len(temp)
                    else np.nan,

                "median_payout":
                    temp["_payout"].median()
                    if len(temp)
                    else np.nan,
            }
        )

    return pd.DataFrame(
        rows
    )


# ===========================================================
# AI予想クラス × 実際クラス
# ===========================================================

def create_cross_summary(
    df,
):

    temp = df.copy()

    temp["_actual_class"] = pd.cut(
        temp["_payout"],
        bins=[
            -np.inf,
            9999,
            29999,
            49999,
            99999,
            np.inf,
        ],
        labels=[
            "0～9,999円",
            "10,000～29,999円",
            "30,000～49,999円",
            "50,000～99,999円",
            "100,000円以上",
        ],
    )

    result = pd.crosstab(
        temp["_actual_class"],
        temp["AI予想"],
        margins=True,
    )

    return result.reset_index()


# ===========================================================
# 保存
# ===========================================================

def save_excel(
    high_vs_low_df,
    missed_vs_correct_df,
    missed_vs_low_df,
    conflict_df,
    high_top_df,
    low_top_df,
    group_summary_df,
    cross_summary_df,
):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with pd.ExcelWriter(
        OUTPUT_XLSX,
        engine="openpyxl",
    ) as writer:

        group_summary_df.to_excel(
            writer,
            sheet_name="4グループ概要",
            index=False,
        )

        cross_summary_df.to_excel(
            writer,
            sheet_name="実際×AIクラス",
            index=False,
        )

        high_vs_low_df.to_excel(
            writer,
            sheet_name="高配当vs低配当",
            index=False,
        )

        missed_vs_correct_df.to_excel(
            writer,
            sheet_name="見逃しvsAI的中",
            index=False,
        )

        missed_vs_low_df.to_excel(
            writer,
            sheet_name="見逃しvs低配当",
            index=False,
        )

        conflict_df.to_excel(
            writer,
            sheet_name="高配当低配当競合",
            index=False,
        )

        high_top_df.to_excel(
            writer,
            sheet_name="高配当特徴TOP",
            index=False,
        )

        low_top_df.to_excel(
            writer,
            sheet_name="低配当特徴TOP",
            index=False,
        )

    log(
        f"Excel保存 : {OUTPUT_XLSX}"
    )


# ===========================================================
# Main
# ===========================================================

def main():

    print()

    log(
        "======================================="
    )

    log(
        "011 High Payout Conflict Analysis"
    )

    log(
        "======================================="
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # -------------------------------------------------------
    # 読込
    # -------------------------------------------------------

    prediction_df = load_prediction()

    feature_df = load_feature()

    # -------------------------------------------------------
    # 結合
    # -------------------------------------------------------

    merged = merge_data(
        prediction_df,
        feature_df,
    )

    # -------------------------------------------------------
    # グループ
    # -------------------------------------------------------

    merged = create_groups(
        merged
    )

    log(
        "======================================="
    )

    log(
        "4グループ作成"
    )

    log(
        "======================================="
    )

    group_counts = (
        merged["_group"]
        .value_counts()
    )

    for group_name, count in group_counts.items():

        log(
            f"{group_name} : {count:,}"
        )

    print()

    # -------------------------------------------------------
    # 特徴量
    # -------------------------------------------------------

    feature_columns = (
        get_feature_columns(
            merged
        )
    )

    log(
        f"分析対象特徴量 : "
        f"{len(feature_columns):,}"
    )

    # -------------------------------------------------------
    # グループ抽出
    # -------------------------------------------------------

    group_a = merged[
        merged["_group"]
        == "A_実際高配当_AI高配当"
    ].copy()

    group_b = merged[
        merged["_group"]
        == "B_実際高配当_AI低配当"
    ].copy()

    group_c = merged[
        merged["_group"]
        == "C_実際低配当_AI低配当"
    ].copy()

    group_d = merged[
        merged["_group"]
        == "D_実際低配当_AI高配当"
    ].copy()

    # -------------------------------------------------------
    # A vs C
    #
    # 高配当特徴 vs 低配当
    # -------------------------------------------------------

    log(
        "======================================="
    )

    log(
        "A vs C : 高配当特徴分析"
    )

    high_vs_low_df = compare_groups(
        group_a,
        group_c,
        feature_columns,
        "actual_high_ai_high",
        "actual_low_ai_low",
    )

    # -------------------------------------------------------
    # B vs A
    #
    # 高配当AI見逃し vs AI的中
    # -------------------------------------------------------

    log(
        "B vs A : 見逃し特徴分析"
    )

    missed_vs_correct_df = compare_groups(
        group_b,
        group_a,
        feature_columns,
        "missed_high",
        "correct_high",
    )

    # -------------------------------------------------------
    # B vs C
    #
    # 見逃し高配当 vs 普通の低配当
    # -------------------------------------------------------

    log(
        "B vs C : 見逃し高配当 vs 低配当"
    )

    missed_vs_low_df = compare_groups(
        group_b,
        group_c,
        feature_columns,
        "missed_high",
        "normal_low",
    )

    # -------------------------------------------------------
    # 競合分析
    # -------------------------------------------------------

    log(
        "======================================="
    )

    log(
        "高配当特徴 vs 低配当特徴 競合分析"
    )

    conflict_df = create_conflict_analysis(
        high_vs_low_df,
        missed_vs_correct_df,
        missed_vs_low_df,
    )

    # -------------------------------------------------------
    # 高配当側TOP
    # -------------------------------------------------------

    high_top_df = (
        high_vs_low_df
        .sort_values(
            "cohens_d",
            ascending=False,
        )
        .head(100)
        .copy()
    )

    # -------------------------------------------------------
    # 低配当側TOP
    # -------------------------------------------------------

    low_top_df = (
        high_vs_low_df
        .sort_values(
            "cohens_d",
            ascending=True,
        )
        .head(100)
        .copy()
    )

    # -------------------------------------------------------
    # 概要
    # -------------------------------------------------------

    group_summary_df = (
        create_group_summary(
            merged
        )
    )

    cross_summary_df = (
        create_cross_summary(
            merged
        )
    )

    # -------------------------------------------------------
    # 保存
    # -------------------------------------------------------

    save_excel(
        high_vs_low_df,
        missed_vs_correct_df,
        missed_vs_low_df,
        conflict_df,
        high_top_df,
        low_top_df,
        group_summary_df,
        cross_summary_df,
    )

    # -------------------------------------------------------
    # CSV保存
    # -------------------------------------------------------

    merged[
        [
            "race_key",
            "AI予想",
            "三連単\n払戻",
            "_payout",
            "_actual_high",
            "_ai_high",
            "_group",
        ]
    ].to_csv(
        OUTPUT_MERGED,
        index=False,
        encoding="utf-8-sig",
    )

    # -------------------------------------------------------
    # コンソール表示
    # -------------------------------------------------------

    print()

    log(
        "======================================="
    )

    log(
        "011 Summary"
    )

    log(
        "======================================="
    )

    print(
        group_summary_df.to_string(
            index=False
        )
    )

    print()

    print(
        "===== 高配当特徴 TOP20 ====="
    )

    if not high_top_df.empty:

        print(
            high_top_df[
                [
                    "rank",
                    "feature",
                    "cohens_d",
                    "effect_strength",
                ]
            ]
            .head(20)
            .to_string(
                index=False
            )
        )

    print()

    print(
        "===== 低配当特徴 TOP20 ====="
    )

    if not low_top_df.empty:

        print(
            low_top_df[
                [
                    "rank",
                    "feature",
                    "cohens_d",
                    "effect_strength",
                ]
            ]
            .head(20)
            .to_string(
                index=False
            )
        )

    print()

    print(
        "===== 競合特徴 TOP30 ====="
    )

    if not conflict_df.empty:

        print(
            conflict_df[
                [
                    "rank",
                    "feature",
                    "d_high_vs_low",
                    "d_missed_vs_correct",
                    "d_missed_vs_low",
                    "high_payout_direction",
                    "missed_direction",
                    "conflict_type",
                    "conflict_score",
                ]
            ]
            .head(30)
            .to_string(
                index=False
            )
        )

    print()

    log(
        "011 Complete"
    )

    log(
        f"保存先 : {OUTPUT_XLSX}"
    )

    log(
        f"確認用CSV : {OUTPUT_MERGED}"
    )


# ===========================================================
# 実行
# ===========================================================

if __name__ == "__main__":
    main()