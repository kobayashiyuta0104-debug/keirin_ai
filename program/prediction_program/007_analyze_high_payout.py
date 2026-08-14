# ===========================================================
#
# 競輪AI Ver1.0
# 007_analyze_high_payout.py
#
# 高配当特徴量分析
#
# 【目的】
#
# 現在のAIで使用している
# training_race_features
#
# ＋
#
# 2020～2022年のAI予想結果
#
# ↓
#
# 30,000円以上の高配当レースと
# 0～9,999円の低配当レースを比較
#
# ↓
#
# 「現在の特徴量の中に高配当を識別する情報が存在するか」
# を調査する
#
# ※AIモデル・特徴量は変更しない
# ※再学習は行わない
#
# ===========================================================

import os
from pathlib import Path

import numpy as np
import pandas as pd


# ===========================================================
# GitHub / Windows対応
# ===========================================================

if os.name == "nt":

    BASE = Path(r"C:\競輪AI")

else:

    BASE = Path(__file__).resolve().parent.parent.parent


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
    / "high_payout"
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
    / "007_high_payout_analysis(2023.1.1~2026.7.30).xlsx"
)


# ===========================================================
# 高配当クラス
# ===========================================================

LOW_CLASS = "0～9,999円"

CLASS_30 = "30,000～49,999円"

CLASS_50 = "50,000～99,999円"

CLASS_100 = "100,000円以上"

HIGH_CLASSES = [
    CLASS_30,
    CLASS_50,
    CLASS_100,
]


# ===========================================================
# ログ
# ===========================================================

def log(message):

    print(
        f"[007_analyze_high_payout] {message}"
    )


# ===========================================================
# CSV読込
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

    log(f"Rows    : {len(df):,}")
    log(f"Columns : {len(df.columns):,}")

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

    log(f"Rows    : {len(df):,}")
    log(f"Columns : {len(df.columns):,}")

    print()

    return df


# ===========================================================
# 必須列確認
# ===========================================================

def check_columns(
    prediction_df,
    feature_df,
):

    log("=======================================")
    log("必須列確認")
    log("=======================================")

    prediction_required = [
        "レースキー",
        "AI予想",
        "実際\nクラス",
    ]

    feature_required = [
        "race_key",
    ]

    for column in prediction_required:

        if column not in prediction_df.columns:

            raise KeyError(
                f"Prediction CSV に必要な列がありません: "
                f"{column}"
            )

    for column in feature_required:

        if column not in feature_df.columns:

            raise KeyError(
                f"Feature CSV に必要な列がありません: "
                f"{column}"
            )

    log("必須列OK")

    print()


# ===========================================================
# race_key統一
# ===========================================================

def normalize_prediction_key(
    prediction_df,
):

    df = prediction_df.copy()

    df["race_key"] = (
        df["レースキー"]
        .astype(str)
        .str.strip()
    )

    return df


# ===========================================================
# 特徴量結合
# ===========================================================

def merge_data(
    prediction_df,
    feature_df,
):

    log("=======================================")
    log("Prediction × Features 結合")
    log("=======================================")

    features = feature_df.copy()

    features["race_key"] = (
        features["race_key"]
        .astype(str)
        .str.strip()
    )

    # -------------------------------------------------------
    # race_key重複確認
    # -------------------------------------------------------

    duplicate_count = (
        features["race_key"]
        .duplicated()
        .sum()
    )

    log(
        f"Feature race_key 重複 : "
        f"{duplicate_count:,}"
    )

    if duplicate_count > 0:

        raise ValueError(
            "training_race_features に "
            "race_keyの重複があります。"
        )

    # -------------------------------------------------------
    # Prediction側
    # -------------------------------------------------------

    prediction = normalize_prediction_key(
        prediction_df
    )

    # -------------------------------------------------------
    # 結合
    # -------------------------------------------------------

    merged = prediction.merge(
        features,
        on="race_key",
        how="inner",
        suffixes=(
            "_prediction",
            "",
        ),
    )

    log(
        f"Prediction Rows : "
        f"{len(prediction):,}"
    )

    log(
        f"Feature Rows    : "
        f"{len(features):,}"
    )

    log(
        f"結合後 Rows     : "
        f"{len(merged):,}"
    )

    # -------------------------------------------------------
    # 結合率
    # -------------------------------------------------------

    if len(prediction) > 0:

        rate = (
            len(merged)
            / len(prediction)
            * 100
        )

    else:

        rate = 0

    log(
        f"結合率          : "
        f"{rate:.2f}%"
    )

    if rate < 99:

        log(
            "WARNING: race_key未結合データがあります"
        )

    print()

    return merged


# ===========================================================
# 数値化
# ===========================================================

def convert_numeric(
    series,
):

    return pd.to_numeric(
        series,
        errors="coerce",
    )


# ===========================================================
# Cohen's d
# ===========================================================

def calculate_cohens_d(
    group_high,
    group_low,
):

    high = pd.to_numeric(
        group_high,
        errors="coerce",
    ).dropna()

    low = pd.to_numeric(
        group_low,
        errors="coerce",
    ).dropna()

    if len(high) < 2 or len(low) < 2:

        return np.nan

    mean_high = high.mean()

    mean_low = low.mean()

    var_high = high.var(
        ddof=1
    )

    var_low = low.var(
        ddof=1
    )

    pooled = np.sqrt(
        (
            (
                len(high) - 1
            )
            * var_high
            +
            (
                len(low) - 1
            )
            * var_low
        )
        /
        (
            len(high)
            +
            len(low)
            -
            2
        )
    )

    if pooled == 0 or np.isnan(pooled):

        return 0

    return (
        mean_high
        -
        mean_low
    ) / pooled


# ===========================================================
# AUC計算
#
# 0.5 = ほぼ識別不能
# 1.0 = 高配当を完全に高く判定
# 0.0 = 完全に逆
#
# 絶対値が大きいほど識別力が高い
# ===========================================================

def calculate_auc(
    high,
    low,
):

    high = pd.to_numeric(
        high,
        errors="coerce",
    )

    low = pd.to_numeric(
        low,
        errors="coerce",
    )

    high = high.dropna()
    low = low.dropna()

    if len(high) == 0 or len(low) == 0:

        return np.nan

    combined = pd.concat(
        [
            high,
            low,
        ],
        ignore_index=True,
    )

    ranks = combined.rank(
        method="average"
    )

    n_high = len(high)

    n_low = len(low)

    rank_sum_high = (
        ranks.iloc[:n_high]
        .sum()
    )

    auc = (
        rank_sum_high
        -
        n_high * (n_high + 1) / 2
    ) / (
        n_high * n_low
    )

    return auc

# ===========================================================
# 分析対象外列
# ===========================================================
# レース後にしか分からない情報・AI予想結果などは
# 「レース前特徴量」の分析から除外する
# ===========================================================

EXCLUDE_ANALYSIS_COLUMNS = {
    # キー
    "race_key",
    "レースキー",

    # AI予想・判定
    "AI予想",
    "AI確信度",
    "AIコメント",
    "的中\n判定",
    "的中判定",

    # 実際の払戻・結果クラス
    "実際\nクラス",
    "実際クラス",
    "三連単\n払戻",
    "三連単払戻",
    "payout_class",

    # 実際の着順
    "１着",
    "２着",
    "３着",
    "1着",
    "2着",
    "3着",

    # 結果系
    "finish_order",
    "player_id_result",
    "result_status",
    "result_reason",
    "trifecta",
    "trifecta_payout",
    "popularity",

    # 予想日時
    "予想日時",
}

# ===========================================================
# ライン・ポジション存在判定
# ===========================================================
#
# L4_P2_average_score のような特徴量は、
# L4の2番手選手が存在しないレースでは空欄になる。
#
# これは「データ欠損」ではなく「その選手が存在しない」
# という正常な構造的空欄。
#
# そのため、Lx_Py系特徴量を分析するときは、
# 同じLx_Pyの選手が存在するレースだけを母集団にする。
#
# ===========================================================

def get_player_position_mask(
    df,
    feature_column,
):
    
    # L1_P1_average_score
    # L4_P3_class
    # などから
    #
    # L1_P1
    # L4_P3
    #
    # を取り出す

    parts = feature_column.split("_")

    if len(parts) < 3:
        
        return pd.Series(
            True,
            index=df.index,
        )

    if not (
        parts[0].startswith("L")
        and
        parts[1].startswith("P")
    ):
        
        return pd.Series(
            True,
            index=df.index,
        )

    prefix = (
        parts[0]
        + "_"
        + parts[1]
    )

    # 同じ選手位置にある特徴量を探す
    #
    # 例：
    # L4_P2_average_score
    #
    # → L4_P2_age
    # → L4_P2_class
    # → L4_P2_player_id
    #
    # など

    position_columns = [
        column
        for column in df.columns
        if column.startswith(
            prefix + "_"
        )
    ]

    if not position_columns:
        
        return pd.Series(
            True,
            index=df.index,
        )

    # player_id があれば最優先
    player_id_column = (
        prefix
        + "_player_id"
    )

    if player_id_column in df.columns:

        player_id = (
            df[player_id_column]
            .astype(str)
            .str.strip()
        )

        return (
            player_id.notna()
            &
            (player_id != "")
            &
            (player_id != "nan")
            &
            (player_id != "None")
        )

    # player_id が無い場合は、
    # 同じポジションの特徴量のうち
    # 何か1つでも値が入っていれば
    # 選手が存在すると判断

    position_df = df[
        position_columns
    ]

    return position_df.notna().any(
        axis=1
    )

# ===========================================================
# 数値特徴量比較
# ===========================================================

def analyze_numeric_features(
    df,
    high_mask,
    low_mask,
):

    log("=======================================")
    log("Numeric Feature Analysis")
    log("=======================================")

    rows = []

    # -------------------------------------------------------
    # 分析対象列
    # -------------------------------------------------------

    exclude_columns = EXCLUDE_ANALYSIS_COLUMNS

    numeric_columns = []

    for column in df.columns:

        if column in exclude_columns:

            continue

        converted = pd.to_numeric(
            df[column],
            errors="coerce",
        )

        # 数値として扱えるデータが一定数以上ある
        if converted.notna().sum() >= 100:

            numeric_columns.append(
                column
            )

    log(
        f"Numeric Features : "
        f"{len(numeric_columns):,}"
    )

    # -------------------------------------------------------
    # 各特徴量
    # -------------------------------------------------------

    high_df = df.loc[
        high_mask
    ]

    low_df = df.loc[
        low_mask
    ]

    for column in numeric_columns:

        # -------------------------------------------------------
        # ライン・ポジション特徴量か確認
        # -------------------------------------------------------

        position_mask = get_player_position_mask(
            df,
            column,
        )

        # -------------------------------------------------------
        # 高配当側
        #
        # そのライン・ポジションに
        # 選手が存在するレースだけを対象
        # -------------------------------------------------------

        high_target_mask = (
            high_mask
            &
            position_mask
        )

        # -------------------------------------------------------
        # 低配当側
        #
        # 同じ条件で比較
        # -------------------------------------------------------

        low_target_mask = (
            low_mask
            &
            position_mask
        )

        high = pd.to_numeric(
            df.loc[
                high_target_mask,
                column,
            ],
            errors="coerce",
        )

        low = pd.to_numeric(
            df.loc[
                low_target_mask,
                column,
            ],
            errors="coerce",
        )

        # -------------------------------------------------------
        # 選手存在数
        # -------------------------------------------------------

        high_position_count = (
            high_target_mask.sum()
        )

        low_position_count = (
            low_target_mask.sum()
        )

        # -------------------------------------------------------
        # 実際に特徴量が存在する件数
        # -------------------------------------------------------

        high_valid = high.dropna()

        low_valid = low.dropna()

        if len(high_valid) == 0:

            continue

        if len(low_valid) == 0:

            continue

        # -------------------------------------------------------
        # 平均
        # -------------------------------------------------------

        mean_high = high_valid.mean()

        mean_low = low_valid.mean()

        # -------------------------------------------------------
        # 中央値
        # -------------------------------------------------------

        median_high = high_valid.median()

        median_low = low_valid.median()

        # -------------------------------------------------------
        # 本当の特徴量欠損率
        #
        # 「選手が存在しない」ことは欠損に含めない
        # -------------------------------------------------------

        high_missing = (
            high.isna().mean()
            * 100
        )

        low_missing = (
            low.isna().mean()
            * 100
        )

        # -------------------------------------------------------
        # 平均差
        # -------------------------------------------------------

        difference = (
            mean_high
            -
            mean_low
        )

        # -------------------------------------------------------
        # Cohen's d
        # -------------------------------------------------------

        cohens_d = calculate_cohens_d(
            high,
            low,
        )

        # -------------------------------------------------------
        # AUC
        # -------------------------------------------------------

        auc = calculate_auc(
            high,
            low,
        )

        auc_strength = abs(
            auc - 0.5
        )

        # -------------------------------------------------------
        # 結果
        # -------------------------------------------------------

        rows.append(
            {
                "feature": column,

                # 選手が存在するレース数
                "high_position_count":
                    high_position_count,

                "low_position_count":
                    low_position_count,

                # 実際に特徴量が入っている件数
                "high_count":
                    len(high_valid),

                "low_count":
                    len(low_valid),

                "high_mean":
                    mean_high,

                "low_mean":
                    mean_low,

                "mean_difference":
                    difference,

                "high_median":
                    median_high,

                "low_median":
                    median_low,

                "median_difference":
                    median_high
                    -
                    median_low,

                # 本当のデータ欠損率
                "high_missing_rate":
                    high_missing,

                "low_missing_rate":
                    low_missing,

                "cohens_d":
                    cohens_d,

                "auc":
                    auc,

                "auc_strength":
                    auc_strength,
            }
        )

    result = pd.DataFrame(
        rows
    )

    if result.empty:

        return result

    # -------------------------------------------------------
    # AUC識別力順
    # -------------------------------------------------------

    result = result.sort_values(
        "auc_strength",
        ascending=False,
    )

    result.insert(
        0,
        "rank",
        range(
            1,
            len(result) + 1,
        ),
    )

    return result


# ===========================================================
# 高配当見逃し比較
# ===========================================================

def analyze_missed_high_payout(
    df,
):

    log("=======================================")
    log("High Payout Miss Analysis")
    log("=======================================")

    # -------------------------------------------------------
    # 高配当なのにAIが低配当
    # -------------------------------------------------------

    missed_mask = (
        df["実際\nクラス"]
        .isin(HIGH_CLASSES)
        &
        (
            df["AI予想"]
            == LOW_CLASS
        )
    )

    # -------------------------------------------------------
    # 低配当を正しく低配当
    # -------------------------------------------------------

    correct_low_mask = (
        (
            df["実際\nクラス"]
            == LOW_CLASS
        )
        &
        (
            df["AI予想"]
            == LOW_CLASS
        )
    )

    missed_count = (
        missed_mask.sum()
    )

    correct_count = (
        correct_low_mask.sum()
    )

    log(
        f"高配当見逃し : "
        f"{missed_count:,}"
    )

    log(
        f"低配当正解   : "
        f"{correct_count:,}"
    )

    print()

    # -------------------------------------------------------
    # 数値特徴量
    # -------------------------------------------------------

    result = analyze_numeric_features(
        df,
        missed_mask,
        correct_low_mask,
    )

    return result


# ===========================================================
# クラス別分析
# ===========================================================

def analyze_payout_threshold(
    df,
    threshold_class,
    classes,
):

    mask_high = (
        df["実際\nクラス"]
        .isin(classes)
    )

    mask_low = (
        df["実際\nクラス"]
        == LOW_CLASS
    )

    result = analyze_numeric_features(
        df,
        mask_high,
        mask_low,
    )

    return result


# ===========================================================
# カテゴリ特徴量分析
# ===========================================================

def analyze_category_features(
    df,
    high_mask,
    low_mask,
):

    rows = []

    exclude_columns = EXCLUDE_ANALYSIS_COLUMNS

    for column in df.columns:

        if column in exclude_columns:

            continue

        # 数値列は対象外
        numeric = pd.to_numeric(
            df[column],
            errors="coerce",
        )

        if numeric.notna().sum() >= 100:

            continue

        high = (
            df.loc[
                high_mask,
                column
            ]
            .fillna("欠損")
            .astype(str)
        )

        low = (
            df.loc[
                low_mask,
                column
            ]
            .fillna("欠損")
            .astype(str)
        )

        if len(high) == 0 or len(low) == 0:

            continue

        high_counts = (
            high.value_counts(
                normalize=True
            )
        )

        low_counts = (
            low.value_counts(
                normalize=True
            )
        )

        categories = set(
            high_counts.index
        ) | set(
            low_counts.index
        )

        for category in categories:

            high_rate = (
                high_counts.get(
                    category,
                    0
                )
                * 100
            )

            low_rate = (
                low_counts.get(
                    category,
                    0
                )
                * 100
            )

            rows.append(
                {
                    "feature": column,

                    "value": category,

                    "high_rate_%":
                        high_rate,

                    "low_rate_%":
                        low_rate,

                    "difference_%":
                        high_rate
                        -
                        low_rate,

                    "abs_difference_%":
                        abs(
                            high_rate
                            -
                            low_rate
                        ),
                }
            )

    result = pd.DataFrame(
        rows
    )

    if result.empty:

        return result

    result = result.sort_values(
        "abs_difference_%",
        ascending=False,
    )

    return result


# ===========================================================
# 競輪場・グレード・レース種別
# ===========================================================

def analyze_basic_categories(
    df,
    column,
    high_mask,
    low_mask,
):

    if column not in df.columns:

        return pd.DataFrame()

    high = (
        df.loc[
            high_mask,
            column
        ]
        .fillna("欠損")
        .astype(str)
    )

    low = (
        df.loc[
            low_mask,
            column
        ]
        .fillna("欠損")
        .astype(str)
    )

    high_count = (
        high.value_counts()
        .rename("high_count")
    )

    low_count = (
        low.value_counts()
        .rename("low_count")
    )

    result = pd.concat(
        [
            high_count,
            low_count,
        ],
        axis=1,
    ).fillna(0)

    result["high_rate_%"] = (
        result["high_count"]
        /
        result["high_count"].sum()
        * 100
    )

    result["low_rate_%"] = (
        result["low_count"]
        /
        result["low_count"].sum()
        * 100
    )

    result["difference_%"] = (
        result["high_rate_%"]
        -
        result["low_rate_%"]
    )

    result = result.sort_values(
        "difference_%",
        ascending=False,
    )

    result = result.reset_index()

    result = result.rename(
        columns={
            "index": column
        }
    )

    return result


# ===========================================================
# 対象件数
# ===========================================================

def build_count_summary(
    df,
):

    rows = []

    actual_classes = [
        LOW_CLASS,
        "10,000～29,999円",
        CLASS_30,
        CLASS_50,
        CLASS_100,
    ]

    for class_name in actual_classes:

        count = (
            df["実際\nクラス"]
            == class_name
        ).sum()

        rows.append(
            {
                "区分":
                    f"実際 {class_name}",

                "レース数":
                    count,
            }
        )

    # -------------------------------------------------------
    # 高配当合計
    # -------------------------------------------------------

    high_count = (
        df["実際\nクラス"]
        .isin(HIGH_CLASSES)
        .sum()
    )

    low_count = (
        df["実際\nクラス"]
        == LOW_CLASS
    ).sum()

    missed_count = (
        (
            df["実際\nクラス"]
            .isin(HIGH_CLASSES)
        )
        &
        (
            df["AI予想"]
            == LOW_CLASS
        )
    ).sum()

    correct_low_count = (
        (
            df["実際\nクラス"]
            == LOW_CLASS
        )
        &
        (
            df["AI予想"]
            == LOW_CLASS
        )
    ).sum()

    rows.extend(
        [
            {
                "区分":
                    "実際30,000円以上 合計",

                "レース数":
                    high_count,
            },
            {
                "区分":
                    "実際0～9,999円",

                "レース数":
                    low_count,
            },
            {
                "区分":
                    "高配当なのにAIが0～9,999円",

                "レース数":
                    missed_count,
            },
            {
                "区分":
                    "低配当をAIが0～9,999円と正解",

                "レース数":
                    correct_low_count,
            },
        ]
    )

    return pd.DataFrame(
        rows
    )


# ===========================================================
# Excel保存
# ===========================================================

def save_excel(
    count_df,
    numeric_df,
    missed_df,
    category_df,
    venue_df,
    grade_df,
    race_type_df,
    class30_df,
    class50_df,
    class100_df,
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

        count_df.to_excel(
            writer,
            sheet_name="対象件数",
            index=False,
        )

        numeric_df.to_excel(
            writer,
            sheet_name="全体比較",
            index=False,
        )

        missed_df.to_excel(
            writer,
            sheet_name="高配当見逃し比較",
            index=False,
        )

        category_df.to_excel(
            writer,
            sheet_name="カテゴリ比較",
            index=False,
        )

        venue_df.to_excel(
            writer,
            sheet_name="高配当競輪場",
            index=False,
        )

        grade_df.to_excel(
            writer,
            sheet_name="高配当グレード",
            index=False,
        )

        race_type_df.to_excel(
            writer,
            sheet_name="高配当レース種別",
            index=False,
        )

        class30_df.to_excel(
            writer,
            sheet_name="30_000以上",
            index=False,
        )

        class50_df.to_excel(
            writer,
            sheet_name="50_000以上",
            index=False,
        )

        class100_df.to_excel(
            writer,
            sheet_name="100_000以上",
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
    log("007 High Payout Analysis")
    log("=======================================")

    # -------------------------------------------------------
    # CSV読込
    # -------------------------------------------------------

    prediction_df = load_prediction()

    feature_df = load_features()

    # -------------------------------------------------------
    # 必須列確認
    # -------------------------------------------------------

    check_columns(
        prediction_df,
        feature_df,
    )

    # -------------------------------------------------------
    # 結合
    # -------------------------------------------------------

    df = merge_data(
        prediction_df,
        feature_df,
    )

    # -------------------------------------------------------
    # クラス確認
    # -------------------------------------------------------

    log("=======================================")
    log("実際クラス確認")
    log("=======================================")

    print(
        df["実際\nクラス"]
        .value_counts(
            dropna=False
        )
    )

    print()

    # -------------------------------------------------------
    # 30,000円以上
    # -------------------------------------------------------

    high_30_mask = (
        df["実際\nクラス"]
        .isin(
            [
                CLASS_30,
                CLASS_50,
                CLASS_100,
            ]
        )
    )

    low_mask = (
        df["実際\nクラス"]
        == LOW_CLASS
    )

    # -------------------------------------------------------
    # 全体比較
    # -------------------------------------------------------

    log("30,000円以上 vs 0～9,999円")

    numeric_df = analyze_numeric_features(
        df,
        high_30_mask,
        low_mask,
    )

    # -------------------------------------------------------
    # 高配当見逃し
    # -------------------------------------------------------

    missed_df = analyze_missed_high_payout(
        df
    )

    # -------------------------------------------------------
    # カテゴリ比較
    # -------------------------------------------------------

    category_df = analyze_category_features(
        df,
        high_30_mask,
        low_mask,
    )

    # -------------------------------------------------------
    # 競輪場
    # -------------------------------------------------------

    venue_df = analyze_basic_categories(
        df,
        "jo_name",
        high_30_mask,
        low_mask,
    )

    # -------------------------------------------------------
    # グレード
    # -------------------------------------------------------

    grade_df = analyze_basic_categories(
        df,
        "grade",
        high_30_mask,
        low_mask,
    )

    # -------------------------------------------------------
    # レース種別
    # -------------------------------------------------------

    race_type_df = analyze_basic_categories(
        df,
        "race_type",
        high_30_mask,
        low_mask,
    )

    # -------------------------------------------------------
    # 30,000円以上
    # -------------------------------------------------------

    class30_df = analyze_payout_threshold(
        df,
        CLASS_30,
        [
            CLASS_30,
            CLASS_50,
            CLASS_100,
        ],
    )

    # -------------------------------------------------------
    # 50,000円以上
    # -------------------------------------------------------

    class50_df = analyze_payout_threshold(
        df,
        CLASS_50,
        [
            CLASS_50,
            CLASS_100,
        ],
    )

    # -------------------------------------------------------
    # 100,000円以上
    # -------------------------------------------------------

    class100_df = analyze_payout_threshold(
        df,
        CLASS_100,
        [
            CLASS_100,
        ],
    )

    # -------------------------------------------------------
    # 件数
    # -------------------------------------------------------

    count_df = build_count_summary(
        df
    )

    # -------------------------------------------------------
    # Excel保存
    # -------------------------------------------------------

    save_excel(
        count_df,
        numeric_df,
        missed_df,
        category_df,
        venue_df,
        grade_df,
        race_type_df,
        class30_df,
        class50_df,
        class100_df,
    )

    # -------------------------------------------------------
    # 完了
    # -------------------------------------------------------

    log("=======================================")
    log("Complete")
    log("=======================================")

    print()


# ===========================================================
# 実行
# ===========================================================

if __name__ == "__main__":

    main()