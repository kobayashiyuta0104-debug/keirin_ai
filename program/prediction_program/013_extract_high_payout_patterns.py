"""
===========================================================
競輪AI Ver1.0
013_extract_high_payout_patterns.py

高配当パターン抽出分析

目的：
012で確認した
「AIが見逃した高配当レース」
について、

単一特徴量ではなく
「特徴量 × 特徴量」
「特徴量 × 特徴量 × 特徴量」

の組み合わせから、

・高配当になりやすいパターン
・AIが見逃しやすいパターン
・10万円以上になりやすいパターン

を抽出する。

【グループ】

A：
実際高配当
+
AI高配当

B：
実際高配当
+
AI低配当
= 見逃し高配当

C：
実際低配当
+
AI低配当

D：
実際低配当
+
AI高配当

【主要比較】

B vs C
→ AIが低配当と判断した中で、
   実際に高配当になる条件

B vs A
→ 実際高配当の中で、
   AIが見逃した条件と
   正しく高配当と判断できた条件の違い

【高配当判定】

30,000円以上
50,000円以上
100,000円以上

【パターン評価】

・該当件数
・高配当件数
・高配当率
・全体高配当率
・リフト
・平均払戻
・中央値
・最高払戻
・カバレッジ

※既存CSVは変更しない。
※再学習・再予測は行わない。
===========================================================
"""

import os
import re
from pathlib import Path
from itertools import combinations

import numpy as np
import pandas as pd


# ===========================================================
# 基本設定
# ===========================================================

if os.name == "nt":
    BASE = Path(r"C:\競輪AI")
else:
    BASE = Path(__file__).resolve().parent.parent.parent

CSV_DIR = BASE / "csv"
TRAINING_DIR = CSV_DIR / "training"
AI_DIR = CSV_DIR / "ai"

OUTPUT_DIR = (
    CSV_DIR
    / "analysis"
    / "high_payout_patterns"
)

OUTPUT_XLSX = (
    OUTPUT_DIR
    / "013_high_payout_patterns.xlsx"
)

PREDICTION_CSV = (
    TRAINING_DIR
    / "training_prediction(2020.1.1~2022.12.31).csv"
)

FEATURE_CSV = (
    AI_DIR
    / "training_race_features(2020.1.1~2022.12.31).csv"
)


# ===========================================================
# 閾値
# ===========================================================

HIGH_THRESHOLD = 30_000
VERY_HIGH_THRESHOLD = 50_000
EXTREME_THRESHOLD = 100_000

# パターンとして最低限必要な件数
MIN_PATTERN_COUNT = 100

# 単一特徴量で上位何個を組み合わせ分析するか
TOP_FEATURES_FOR_PAIR = 60

# 3特徴量まで調べる上位数
TOP_FEATURES_FOR_TRIPLE = 20

# 連続値を何分割するか
N_BINS = 4

# 出力する上位件数
TOP_OUTPUT = 200


# ===========================================================
# ログ
# ===========================================================

def log(msg):
    print(
        f"[013_extract_high_payout_patterns] {msg}"
    )


# ===========================================================
# CSV読込
# ===========================================================

def read_csv_safely(file):

    last_error = None

    for enc in (
        "utf-8-sig",
        "utf-8",
        "cp932",
        "shift_jis",
    ):
        try:
            return pd.read_csv(
                file,
                encoding=enc,
                low_memory=False,
            )
        except Exception as e:
            last_error = e

    raise last_error


# ===========================================================
# Prediction
# ===========================================================

def load_prediction():

    log("=======================================")
    log("Prediction CSV 読込")
    log("=======================================")

    if not PREDICTION_CSV.exists():
        raise FileNotFoundError(
            f"Prediction CSVがありません:\n"
            f"{PREDICTION_CSV}"
        )

    df = read_csv_safely(
        PREDICTION_CSV
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
            f"Prediction CSVに必要な列がありません: "
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

    df["_ai_class"] = (
        df["AI予想"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["_ai_low"] = df[
        "_ai_class"
    ].str.contains(
        r"0～9,999|0〜9,999|"
        r"10,000～29,999|10,000〜29,999",
        regex=True,
        na=False,
    )

    df["_ai_high"] = df[
        "_ai_class"
    ].str.contains(
        r"30,000～49,999|30,000〜49,999|"
        r"50,000～99,999|50,000〜99,999|"
        r"100,000円以上|100,000以上",
        regex=True,
        na=False,
    )

    df = df.drop_duplicates(
        "race_key",
        keep="last",
    )

    log(
        f"Rows    : {len(df):,}"
    )
    log(
        f"Columns : {len(df.columns):,}"
    )

    return df


# ===========================================================
# Feature
# ===========================================================

def load_features():

    log("=======================================")
    log("Training Race Features CSV 読込")
    log("=======================================")

    if not FEATURE_CSV.exists():
        raise FileNotFoundError(
            f"Feature CSVがありません:\n"
            f"{FEATURE_CSV}"
        )

    df = read_csv_safely(
        FEATURE_CSV
    )

    if "race_key" not in df.columns:
        raise KeyError(
            "Feature CSVにrace_keyがありません。"
        )

    df["race_key"] = (
        df["race_key"]
        .astype(str)
        .str.strip()
    )

    df = df.drop_duplicates(
        "race_key",
        keep="last",
    )

    log(
        f"Rows    : {len(df):,}"
    )
    log(
        f"Columns : {len(df.columns):,}"
    )

    return df


# ===========================================================
# 結合
# ===========================================================

def merge_data(
    pred,
    feat,
):

    log("=======================================")
    log("Prediction + Feature 結合")
    log("=======================================")

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

    if merged.empty:
        raise ValueError(
            "PredictionとFeatureの結合結果が0件です。"
        )

    return merged


# ===========================================================
# 払戻クラス
# ===========================================================

def add_payout_class(df):

    df = df.copy()

    def payout_class(v):

        if pd.isna(v):
            return "不明"

        if v < 30_000:
            return "0～29,999円"

        if v < 50_000:
            return "30,000～49,999円"

        if v < 100_000:
            return "50,000～99,999円"

        return "100,000円以上"

    df["_actual_payout_class"] = (
        df["_payout"]
        .apply(payout_class)
    )

    return df


# ===========================================================
# AIクラス
# ===========================================================

def add_ai_class(df):

    df = df.copy()

    def normalize(v):

        s = str(v).strip()

        if re.search(
            r"0～9,999|0〜9,999",
            s,
        ):
            return "0～9,999円"

        if re.search(
            r"10,000～29,999|10,000〜29,999",
            s,
        ):
            return "10,000～29,999円"

        if re.search(
            r"30,000～49,999|30,000〜49,999",
            s,
        ):
            return "30,000～49,999円"

        if re.search(
            r"50,000～99,999|50,000〜99,999",
            s,
        ):
            return "50,000～99,999円"

        if re.search(
            r"100,000円以上|100,000以上",
            s,
        ):
            return "100,000円以上"

        return "不明"

    df["_ai_prediction_class"] = (
        df["_ai_class"]
        .apply(normalize)
    )

    return df


# ===========================================================
# ライン構造
# ===========================================================

def position_exists(
    row,
    line_no,
    position,
):

    prefix = (
        f"L{line_no}_P{position}_"
    )

    columns = [
        column
        for column in row.index
        if column.startswith(prefix)
    ]

    if not columns:
        return False

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


def get_line_structure(row):

    line_sizes = []

    tanki_count = 0

    for line_no in range(1, 10):

        size = 0

        for position in range(1, 10):

            if position_exists(
                row,
                line_no,
                position,
            ):
                size += 1
            else:
                break

        if size == 0:
            continue

        if size == 1:
            tanki_count += 1
        else:
            line_sizes.append(size)

    line_sizes = sorted(
        line_sizes,
        reverse=True,
    )

    real_line_count = len(
        line_sizes
    )

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
        "max_line_size":
            max(line_sizes)
            if line_sizes
            else 1,
    }


def build_line_structure_data(
    df,
):

    records = []

    for _, row in df.iterrows():

        structure = get_line_structure(
            row
        )

        records.append(
            structure
        )

    structure_df = pd.DataFrame(
        records
    )

    return pd.concat(
        [
            df.reset_index(
                drop=True
            ),
            structure_df,
        ],
        axis=1,
    )


# ===========================================================
# 特徴量抽出
# ===========================================================

def get_feature_columns(df):

    exclude = {
        "race_key",
        "レースキー",
        "AI予想",
        "AI確信度",
        "AI\n確信度",
        "実際\nクラス",
        "的中判定",
        "三連単\n払戻",
        "trifecta_payout",
        "trifecta",
        "payout",
        "_payout",
        "_ai_class",
        "_ai_low",
        "_ai_high",
        "_actual_payout_class",
        "_ai_prediction_class",
        "line_structure",
        "line_sizes",
        "real_line_count",
        "tanki_count",
        "max_line_size",
        "line_count_excluding_tanki",
        "min_non_single_line_size",
    }

    cols = []

    for col in df.columns:

        if col in exclude:
            continue

        if col.endswith("_feature"):
            continue

        if df[col].dtype == "object":
            continue

        numeric = pd.to_numeric(
            df[col],
            errors="coerce",
        )

        valid_count = (
            numeric.notna().sum()
        )

        if valid_count < MIN_PATTERN_COUNT:
            continue

        if numeric.nunique(
            dropna=True
        ) <= 1:
            continue

        cols.append(col)

    return cols


# ===========================================================
# 数値特徴量を4分割
# ===========================================================

def make_feature_bins(
    df,
    features,
):

    log("=======================================")
    log("特徴量の区間化")
    log("=======================================")

    result = {}

    for idx, feature in enumerate(
        features,
        start=1,
    ):

        numeric = pd.to_numeric(
            df[feature],
            errors="coerce",
        )

        valid = numeric.dropna()

        if len(valid) < MIN_PATTERN_COUNT:
            continue

        unique = valid.nunique()

        # 少数カテゴリ的な数値
        if unique <= 6:

            values = numeric.round(8)

            result[feature] = values

            continue

        try:

            bins = pd.qcut(
                numeric,
                q=N_BINS,
                duplicates="drop",
            )

            result[feature] = (
                bins.astype(str)
                .replace(
                    "nan",
                    np.nan,
                )
            )

        except Exception:

            result[feature] = (
                numeric.round(8)
            )

    log(
        f"区間化特徴量 : "
        f"{len(result):,}"
    )

    return result


# ===========================================================
# グループ作成
# ===========================================================

def create_groups(df):

    high = (
        df["_payout"]
        >= HIGH_THRESHOLD
    )

    ai_high = df["_ai_high"]

    ai_low = df["_ai_low"]

    low_actual = (
        df["_payout"]
        < HIGH_THRESHOLD
    )

    very_high = (
        df["_payout"]
        >= VERY_HIGH_THRESHOLD
    )

    extreme = (
        df["_payout"]
        >= EXTREME_THRESHOLD
    )

    groups = {

        "A_実際高配当_AI高配当":
            df[high & ai_high].copy(),

        "B_実際高配当_AI低配当":
            df[high & ai_low].copy(),

        "C_実際低配当_AI低配当":
            df[low_actual & ai_low].copy(),

        "D_実際低配当_AI高配当":
            df[low_actual & ai_high].copy(),

        "B_5万円以上":
            df[
                very_high
                & ai_low
            ].copy(),

        "B_10万円以上":
            df[
                extreme
                & ai_low
            ].copy(),
    }

    for name, data in groups.items():

        log(
            f"{name} : "
            f"{len(data):,}"
        )

    return groups


# ===========================================================
# パターン評価
# ===========================================================

def evaluate_pattern(
    df,
    mask,
    label,
    target_mask,
):

    count = int(mask.sum())

    if count < MIN_PATTERN_COUNT:
        return None

    target_count = int(
        (mask & target_mask).sum()
    )

    if count == 0:
        return None

    rate = (
        target_count
        / count
        * 100
    )

    total_target = int(
        target_mask.sum()
    )

    total_count = len(df)

    if total_count == 0:
        return None

    baseline_rate = (
        total_target
        / total_count
        * 100
    )

    if baseline_rate <= 0:
        return None

    lift = (
        rate
        / baseline_rate
    )

    payouts = pd.to_numeric(
        df.loc[
            mask,
            "_payout",
        ],
        errors="coerce",
    ).dropna()

    if payouts.empty:
        return None

    coverage = (
        target_count
        / total_target
        * 100
    )

    return {
        "pattern":
            label,
        "sample_count":
            count,
        "target_count":
            target_count,
        "target_rate_%":
            rate,
        "baseline_target_rate_%":
            baseline_rate,
        "lift":
            lift,
        "coverage_%":
            coverage,
        "average_payout":
            payouts.mean(),
        "median_payout":
            payouts.median(),
        "max_payout":
            payouts.max(),
    }


# ===========================================================
# 単一特徴量ランキング
# ===========================================================

def analyze_single_features(
    df,
    feature_bins,
    target_mask,
    comparison_name,
):

    log(
        f"単一特徴量分析 : "
        f"{comparison_name}"
    )

    rows = []

    total_target = int(
        target_mask.sum()
    )

    baseline_rate = (
        total_target
        / len(df)
        * 100
    )

    for idx, (
        feature,
        values,
    ) in enumerate(
        feature_bins.items(),
        start=1,
    ):

        if idx % 100 == 0:

            log(
                f"単一特徴量 : "
                f"{idx:,}/"
                f"{len(feature_bins):,}"
            )

        temp = pd.DataFrame(
            {
                "_value":
                    values,
            },
            index=df.index,
        )

        temp = temp[
            temp["_value"].notna()
        ]

        if temp.empty:
            continue

        grouped = temp.groupby(
            "_value",
            observed=True,
        )

        for value, group in grouped:

            mask = pd.Series(
                False,
                index=df.index,
            )

            mask.loc[
                group.index
            ] = True

            result = evaluate_pattern(
                df,
                mask,
                (
                    f"{feature} = "
                    f"{value}"
                ),
                target_mask,
            )

            if result is None:
                continue

            result[
                "feature_count"
            ] = 1

            result[
                "feature_1"
            ] = feature

            result[
                "value_1"
            ] = value

            result[
                "comparison"
            ] = comparison_name

            rows.append(result)

    result_df = pd.DataFrame(rows)

    if result_df.empty:
        return result_df

    result_df = result_df.sort_values(
        [
            "lift",
            "target_count",
            "target_rate_%",
        ],
        ascending=False,
    )

    result_df.insert(
        0,
        "rank",
        np.arange(
            1,
            len(result_df) + 1,
        ),
    )

    return result_df


# ===========================================================
# 上位特徴量を抽出
# ===========================================================

def select_top_features(
    single_df,
):

    if single_df.empty:
        return []

    grouped = (
        single_df
        .groupby(
            "feature_1"
        )
        .agg(
            best_lift=(
                "lift",
                "max",
            ),
            best_rate=(
                "target_rate_%",
                "max",
            ),
            total_target=(
                "target_count",
                "max",
            ),
        )
        .reset_index()
    )

    grouped = grouped.sort_values(
        [
            "best_lift",
            "total_target",
        ],
        ascending=False,
    )

    return (
        grouped.head(
            TOP_FEATURES_FOR_PAIR
        )[
            "feature_1"
        ]
        .tolist()
    )


# ===========================================================
# 2特徴量パターン
# ===========================================================

def analyze_pair_patterns(
    df,
    feature_bins,
    selected_features,
    target_mask,
    comparison_name,
):

    log(
        f"2特徴量パターン分析 : "
        f"{comparison_name}"
    )

    pairs = list(
        combinations(
            selected_features,
            2,
        )
    )

    log(
        f"組み合わせ数 : "
        f"{len(pairs):,}"
    )

    rows = []

    for idx, (
        feature_1,
        feature_2,
    ) in enumerate(
        pairs,
        start=1,
    ):

        if idx % 100 == 0:

            log(
                f"2特徴量 : "
                f"{idx:,}/"
                f"{len(pairs):,}"
            )

        values_1 = (
            feature_bins[
                feature_1
            ]
        )

        values_2 = (
            feature_bins[
                feature_2
            ]
        )

        temp = pd.DataFrame(
            {
                "_v1":
                    values_1,
                "_v2":
                    values_2,
            },
            index=df.index,
        )

        temp = temp.dropna()

        if len(temp) < MIN_PATTERN_COUNT:
            continue

        grouped = temp.groupby(
            [
                "_v1",
                "_v2",
            ],
            observed=True,
        )

        for (
            value_1,
            value_2,
        ), group in grouped:

            count = len(group)

            if count < MIN_PATTERN_COUNT:
                continue

            mask = pd.Series(
                False,
                index=df.index,
            )

            mask.loc[
                group.index
            ] = True

            label = (
                f"{feature_1}={value_1}"
                f" × "
                f"{feature_2}={value_2}"
            )

            result = evaluate_pattern(
                df,
                mask,
                label,
                target_mask,
            )

            if result is None:
                continue

            result[
                "feature_count"
            ] = 2

            result[
                "feature_1"
            ] = feature_1

            result[
                "value_1"
            ] = value_1

            result[
                "feature_2"
            ] = feature_2

            result[
                "value_2"
            ] = value_2

            result[
                "comparison"
            ] = comparison_name

            rows.append(result)

    result_df = pd.DataFrame(rows)

    if result_df.empty:
        return result_df

    result_df = result_df.sort_values(
        [
            "lift",
            "target_count",
            "target_rate_%",
        ],
        ascending=False,
    )

    result_df.insert(
        0,
        "rank",
        np.arange(
            1,
            len(result_df) + 1,
        ),
    )

    return result_df


# ===========================================================
# 3特徴量パターン
# ===========================================================

def analyze_triple_patterns(
    df,
    feature_bins,
    selected_features,
    target_mask,
    comparison_name,
):

    log(
        f"3特徴量パターン分析 : "
        f"{comparison_name}"
    )

    features = selected_features[
        :TOP_FEATURES_FOR_TRIPLE
    ]

    triples = list(
        combinations(
            features,
            3,
        )
    )

    log(
        f"3特徴量組み合わせ数 : "
        f"{len(triples):,}"
    )

    rows = []

    for idx, (
        feature_1,
        feature_2,
        feature_3,
    ) in enumerate(
        triples,
        start=1,
    ):

        if idx % 100 == 0:

            log(
                f"3特徴量 : "
                f"{idx:,}/"
                f"{len(triples):,}"
            )

        temp = pd.DataFrame(
            {
                "_v1":
                    feature_bins[
                        feature_1
                    ],
                "_v2":
                    feature_bins[
                        feature_2
                    ],
                "_v3":
                    feature_bins[
                        feature_3
                    ],
            },
            index=df.index,
        )

        temp = temp.dropna()

        if len(temp) < MIN_PATTERN_COUNT:
            continue

        grouped = temp.groupby(
            [
                "_v1",
                "_v2",
                "_v3",
            ],
            observed=True,
        )

        for (
            value_1,
            value_2,
            value_3,
        ), group in grouped:

            count = len(group)

            if count < MIN_PATTERN_COUNT:
                continue

            mask = pd.Series(
                False,
                index=df.index,
            )

            mask.loc[
                group.index
            ] = True

            label = (
                f"{feature_1}={value_1}"
                f" × "
                f"{feature_2}={value_2}"
                f" × "
                f"{feature_3}={value_3}"
            )

            result = evaluate_pattern(
                df,
                mask,
                label,
                target_mask,
            )

            if result is None:
                continue

            result[
                "feature_count"
            ] = 3

            result[
                "feature_1"
            ] = feature_1

            result[
                "value_1"
            ] = value_1

            result[
                "feature_2"
            ] = feature_2

            result[
                "value_2"
            ] = value_2

            result[
                "feature_3"
            ] = feature_3

            result[
                "value_3"
            ] = value_3

            result[
                "comparison"
            ] = comparison_name

            rows.append(result)

    result_df = pd.DataFrame(rows)

    if result_df.empty:
        return result_df

    result_df = result_df.sort_values(
        [
            "lift",
            "target_count",
            "target_rate_%",
        ],
        ascending=False,
    )

    result_df.insert(
        0,
        "rank",
        np.arange(
            1,
            len(result_df) + 1,
        ),
    )

    return result_df


# ===========================================================
# 高配当閾値別パターン
# ===========================================================

def run_pattern_analysis(
    df,
    feature_bins,
    selected_features,
    comparison_name,
):

    targets = {

        "30,000円以上":
            (
                df["_payout"]
                >= HIGH_THRESHOLD
            ),

        "50,000円以上":
            (
                df["_payout"]
                >= VERY_HIGH_THRESHOLD
            ),

        "100,000円以上":
            (
                df["_payout"]
                >= EXTREME_THRESHOLD
            ),
    }

    all_single = []
    all_pair = []
    all_triple = []

    for target_name, target_mask in targets.items():

        log(
            "---------------------------------------"
        )

        log(
            f"対象 : {target_name}"
        )

        single = analyze_single_features(
            df,
            feature_bins,
            target_mask,
            comparison_name,
        )

        if not single.empty:

            single[
                "target_threshold"
            ] = target_name

            all_single.append(
                single
            )

            top_features = (
                select_top_features(
                    single
                )
            )

        else:

            top_features = []

        if top_features:

            pair = analyze_pair_patterns(
                df,
                feature_bins,
                top_features,
                target_mask,
                comparison_name,
            )

            if not pair.empty:

                pair[
                    "target_threshold"
                ] = target_name

                all_pair.append(
                    pair
                )

        if top_features:

            triple = analyze_triple_patterns(
                df,
                feature_bins,
                top_features,
                target_mask,
                comparison_name,
            )

            if not triple.empty:

                triple[
                    "target_threshold"
                ] = target_name

                all_triple.append(
                    triple
                )

    single_df = (
        pd.concat(
            all_single,
            ignore_index=True,
        )
        if all_single
        else pd.DataFrame()
    )

    pair_df = (
        pd.concat(
            all_pair,
            ignore_index=True,
        )
        if all_pair
        else pd.DataFrame()
    )

    triple_df = (
        pd.concat(
            all_triple,
            ignore_index=True,
        )
        if all_triple
        else pd.DataFrame()
    )

    return (
        single_df,
        pair_df,
        triple_df,
    )


# ===========================================================
# ライン構造パターン
# ===========================================================

def analyze_line_patterns(
    df,
):

    log(
        "ライン構造パターン分析"
    )

    rows = []

    group_cols = [
        "line_structure",
        "real_line_count",
        "tanki_count",
        "max_line_size",
    ]

    for cols in [
        ["line_structure"],
        [
            "real_line_count",
            "tanki_count",
        ],
        [
            "line_structure",
            "tanki_count",
        ],
        [
            "line_structure",
            "max_line_size",
        ],
    ]:

        grouped = (
            df.groupby(
                cols,
                dropna=False,
            )
            .agg(
                race_count=(
                    "race_key",
                    "size",
                ),
                average_payout=(
                    "_payout",
                    "mean",
                ),
                median_payout=(
                    "_payout",
                    "median",
                ),
                max_payout=(
                    "_payout",
                    "max",
                ),
                high_30k_count=(
                    "_payout",
                    lambda x:
                    (
                        x
                        >= HIGH_THRESHOLD
                    ).sum(),
                ),
                high_50k_count=(
                    "_payout",
                    lambda x:
                    (
                        x
                        >= VERY_HIGH_THRESHOLD
                    ).sum(),
                ),
                high_100k_count=(
                    "_payout",
                    lambda x:
                    (
                        x
                        >= EXTREME_THRESHOLD
                    ).sum(),
                ),
            )
            .reset_index()
        )

        grouped[
            "high_30k_rate_%"
        ] = (
            grouped[
                "high_30k_count"
            ]
            / grouped[
                "race_count"
            ]
            * 100
        )

        grouped[
            "high_50k_rate_%"
        ] = (
            grouped[
                "high_50k_count"
            ]
            / grouped[
                "race_count"
            ]
            * 100
        )

        grouped[
            "high_100k_rate_%"
        ] = (
            grouped[
                "high_100k_count"
            ]
            / grouped[
                "race_count"
            ]
            * 100
        )

        grouped[
            "analysis_dimension"
        ] = " × ".join(cols)

        rows.append(
            grouped
        )

    result = pd.concat(
        rows,
        ignore_index=True,
    )

    return result.sort_values(
        [
            "high_100k_rate_%",
            "high_50k_rate_%",
            "race_count",
        ],
        ascending=False,
    )


# ===========================================================
# B vs A
# ===========================================================

def compare_missed_vs_caught(
    b_df,
    a_df,
    features,
):

    rows = []

    for feature in features:

        b = pd.to_numeric(
            b_df[feature],
            errors="coerce",
        ).dropna()

        a = pd.to_numeric(
            a_df[feature],
            errors="coerce",
        ).dropna()

        if len(b) < MIN_PATTERN_COUNT:
            continue

        if len(a) < MIN_PATTERN_COUNT:
            continue

        b_mean = b.mean()
        a_mean = a.mean()

        b_std = b.std()
        a_std = a.std()

        pooled = np.sqrt(
            (
                (
                    len(b) - 1
                )
                * b.var(
                    ddof=1
                )
                +
                (
                    len(a) - 1
                )
                * a.var(
                    ddof=1
                )
            )
            /
            (
                len(b)
                + len(a)
                - 2
            )
        )

        if pooled == 0:
            d = np.nan
        else:
            d = (
                b_mean
                - a_mean
            ) / pooled

        rows.append(
            {
                "feature":
                    feature,
                "B_missed_mean":
                    b_mean,
                "A_caught_mean":
                    a_mean,
                "B_minus_A":
                    b_mean - a_mean,
                "cohens_d":
                    d,
                "B_count":
                    len(b),
                "A_count":
                    len(a),
            }
        )

    result = pd.DataFrame(rows)

    if result.empty:
        return result

    result[
        "abs_cohens_d"
    ] = result[
        "cohens_d"
    ].abs()

    return result.sort_values(
        [
            "abs_cohens_d",
            "B_count",
        ],
        ascending=False,
    ).reset_index(
        drop=True
    )


# ===========================================================
# パターンの信頼度評価
# ===========================================================

def add_pattern_score(
    df,
):

    if df.empty:
        return df

    result = df.copy()

    # リフトを重視しつつ
    # 件数も考慮。
    result[
        "pattern_score"
    ] = (
        result["lift"]
        *
        np.log1p(
            result[
                "target_count"
            ]
        )
    )

    return result.sort_values(
        [
            "pattern_score",
            "target_count",
        ],
        ascending=False,
    ).reset_index(
        drop=True
    )


# ===========================================================
# 概要
# ===========================================================

def create_overview(
    df,
    groups,
):

    total = len(df)

    rows = [

        {
            "item":
                "全レース数",
            "value":
                total,
        },

        {
            "item":
                "実際30,000円以上",
            "value":
                int(
                    (
                        df["_payout"]
                        >= 30_000
                    ).sum()
                ),
        },

        {
            "item":
                "実際50,000円以上",
            "value":
                int(
                    (
                        df["_payout"]
                        >= 50_000
                    ).sum()
                ),
        },

        {
            "item":
                "実際100,000円以上",
            "value":
                int(
                    (
                        df["_payout"]
                        >= 100_000
                    ).sum()
                ),
        },

        {
            "item":
                "B 見逃し高配当",
            "value":
                len(
                    groups[
                        "B_実際高配当_AI低配当"
                    ]
                ),
        },

        {
            "item":
                "B 5万円以上見逃し",
            "value":
                len(
                    groups[
                        "B_5万円以上"
                    ]
                ),
        },

        {
            "item":
                "B 10万円以上見逃し",
            "value":
                len(
                    groups[
                        "B_10万円以上"
                    ]
                ),
        },

        {
            "item":
                "A 正しく高配当予測",
            "value":
                len(
                    groups[
                        "A_実際高配当_AI高配当"
                    ]
                ),
        },
    ]

    return pd.DataFrame(rows)


# ===========================================================
# Excel保存
# ===========================================================

def save_excel(
    overview,
    groups_summary,
    single_b_c,
    pair_b_c,
    triple_b_c,
    single_b_a,
    pair_b_a,
    triple_b_a,
    line_patterns,
    missed_vs_caught,
    single_100k,
    pair_100k,
    triple_100k,
):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with pd.ExcelWriter(
        OUTPUT_XLSX,
        engine="openpyxl",
    ) as writer:

        overview.to_excel(
            writer,
            sheet_name="01_全体概要",
            index=False,
        )

        groups_summary.to_excel(
            writer,
            sheet_name="02_グループ",
            index=False,
        )

        single_b_c.head(
            TOP_OUTPUT
        ).to_excel(
            writer,
            sheet_name="03_BvsC_単一",
            index=False,
        )

        pair_b_c.head(
            TOP_OUTPUT
        ).to_excel(
            writer,
            sheet_name="04_BvsC_2特徴",
            index=False,
        )

        triple_b_c.head(
            TOP_OUTPUT
        ).to_excel(
            writer,
            sheet_name="05_BvsC_3特徴",
            index=False,
        )

        single_b_a.head(
            TOP_OUTPUT
        ).to_excel(
            writer,
            sheet_name="06_BvsA_単一",
            index=False,
        )

        pair_b_a.head(
            TOP_OUTPUT
        ).to_excel(
            writer,
            sheet_name="07_BvsA_2特徴",
            index=False,
        )

        triple_b_a.head(
            TOP_OUTPUT
        ).to_excel(
            writer,
            sheet_name="08_BvsA_3特徴",
            index=False,
        )

        line_patterns.head(
            TOP_OUTPUT
        ).to_excel(
            writer,
            sheet_name="09_ラインパターン",
            index=False,
        )

        missed_vs_caught.head(
            TOP_OUTPUT
        ).to_excel(
            writer,
            sheet_name="10_見逃しvs的中",
            index=False,
        )

        single_100k.head(
            TOP_OUTPUT
        ).to_excel(
            writer,
            sheet_name="11_10万円_単一",
            index=False,
        )

        pair_100k.head(
            TOP_OUTPUT
        ).to_excel(
            writer,
            sheet_name="12_10万円_2特徴",
            index=False,
        )

        triple_100k.head(
            TOP_OUTPUT
        ).to_excel(
            writer,
            sheet_name="13_10万円_3特徴",
            index=False,
        )

    log(
        f"保存先 : {OUTPUT_XLSX}"
    )


# ===========================================================
# メイン
# ===========================================================

def main():

    print()

    log("=======================================")
    log("013 High Payout Pattern Extraction")
    log("=======================================")

    # -------------------------------------------------------
    # 読込
    # -------------------------------------------------------

    pred = load_prediction()

    feat = load_features()

    # -------------------------------------------------------
    # 結合
    # -------------------------------------------------------

    df = merge_data(
        pred,
        feat,
    )

    # -------------------------------------------------------
    # クラス追加
    # -------------------------------------------------------

    df = add_payout_class(
        df
    )

    df = add_ai_class(
        df
    )

    # -------------------------------------------------------
    # グループ
    # -------------------------------------------------------

    log("=======================================")
    log("4グループ作成")
    log("=======================================")

    groups = create_groups(
        df
    )

    # -------------------------------------------------------
    # ライン構造
    # -------------------------------------------------------

    log("=======================================")
    log("ライン構造生成")
    log("=======================================")

    df = build_line_structure_data(
        df
    )

    # -------------------------------------------------------
    # 特徴量
    # -------------------------------------------------------

    features = get_feature_columns(
        df
    )

    log(
        f"分析対象特徴量 : "
        f"{len(features):,}"
    )

    # -------------------------------------------------------
    # 区間化
    # -------------------------------------------------------

    feature_bins = make_feature_bins(
        df,
        features,
    )

    # -------------------------------------------------------
    # B vs C
    # -------------------------------------------------------

    log("=======================================")
    log("B vs C : 見逃し高配当 vs 低配当")
    log("=======================================")

    b = groups[
        "B_実際高配当_AI低配当"
    ].copy()

    c = groups[
        "C_実際低配当_AI低配当"
    ].copy()

    bc_df = pd.concat(
        [
            b,
            c,
        ],
        ignore_index=False,
    )

    bc_target = (
        bc_df["_payout"]
        >= HIGH_THRESHOLD
    )

    bc_bins = {
        feature:
            feature_bins[feature].loc[
                bc_df.index
            ]
        for feature in feature_bins
        if feature in bc_df.columns
    }

    single_bc, pair_bc, triple_bc = (
        run_pattern_analysis(
            bc_df,
            bc_bins,
            list(bc_bins.keys()),
            "B_vs_C",
        )
    )

    # -------------------------------------------------------
    # B vs A
    # -------------------------------------------------------

    log("=======================================")
    log("B vs A : 見逃し vs 正しく高配当予測")
    log("=======================================")

    a = groups[
        "A_実際高配当_AI高配当"
    ].copy()

    ba_df = pd.concat(
        [
            b,
            a,
        ],
        ignore_index=False,
    )

    ba_target = (
        ba_df["_payout"]
        >= HIGH_THRESHOLD
    )

    ba_bins = {
        feature:
            feature_bins[feature].loc[
                ba_df.index
            ]
        for feature in feature_bins
        if feature in ba_df.columns
    }

    single_ba, pair_ba, triple_ba = (
        run_pattern_analysis(
            ba_df,
            ba_bins,
            list(ba_bins.keys()),
            "B_vs_A",
        )
    )

    # -------------------------------------------------------
    # ラインパターン
    # -------------------------------------------------------
 
    b = build_line_structure_data(b)

    line_patterns = (
        analyze_line_patterns(
            b
        )
    )

    # -------------------------------------------------------
    # B vs A 単一特徴量比較
    # -------------------------------------------------------

    missed_vs_caught = (
        compare_missed_vs_caught(
            b,
            a,
            features,
        )
    )

    # -------------------------------------------------------
    # 10万円以上専用
    # -------------------------------------------------------

    log("=======================================")
    log("10万円以上パターン分析")
    log("=======================================")

    extreme = groups[
        "B_10万円以上"
    ].copy()

    low_for_extreme = c.copy()

    extreme_compare = pd.concat(
        [
            extreme,
            low_for_extreme,
        ],
        ignore_index=False,
    )

    extreme_target = (
        extreme_compare["_payout"]
        >= EXTREME_THRESHOLD
    )

    extreme_bins = {
        feature:
            feature_bins[feature].loc[
                extreme_compare.index
            ]
        for feature in feature_bins
        if feature in extreme_compare.columns
    }

    (
        single_extreme,
        pair_extreme,
        triple_extreme,
    ) = run_pattern_analysis(
        extreme_compare,
        extreme_bins,
        list(extreme_bins.keys()),
        "10万円_vs_低配当",
    )

    # -------------------------------------------------------
    # スコア
    # -------------------------------------------------------

    single_bc = add_pattern_score(
        single_bc
    )

    pair_bc = add_pattern_score(
        pair_bc
    )

    triple_bc = add_pattern_score(
        triple_bc
    )

    single_ba = add_pattern_score(
        single_ba
    )

    pair_ba = add_pattern_score(
        pair_ba
    )

    triple_ba = add_pattern_score(
        triple_ba
    )

    single_extreme = add_pattern_score(
        single_extreme
    )

    pair_extreme = add_pattern_score(
        pair_extreme
    )

    triple_extreme = add_pattern_score(
        triple_extreme
    )

    # -------------------------------------------------------
    # グループ概要
    # -------------------------------------------------------

    groups_summary = pd.DataFrame(
        [
            {
                "group":
                    name,
                "race_count":
                    len(data),
                "average_payout":
                    data[
                        "_payout"
                    ].mean(),
                "median_payout":
                    data[
                        "_payout"
                    ].median(),
                "max_payout":
                    data[
                        "_payout"
                    ].max(),
            }
            for name, data
            in groups.items()
        ]
    )

    overview = create_overview(
        df,
        groups,
    )

    # -------------------------------------------------------
    # 保存
    # -------------------------------------------------------

    log("=======================================")
    log("Excel保存")
    log("=======================================")

    save_excel(
        overview,
        groups_summary,
        single_bc,
        pair_bc,
        triple_bc,
        single_ba,
        pair_ba,
        triple_ba,
        line_patterns,
        missed_vs_caught,
        single_extreme,
        pair_extreme,
        triple_extreme,
    )

    # -------------------------------------------------------
    # コンソール
    # -------------------------------------------------------

    print()

    log("=======================================")
    log("013 Summary")
    log("=======================================")

    print(
        overview.to_string(
            index=False
        )
    )

    print()

    print(
        "===== B vs C 2特徴パターン TOP30 ====="
    )

    if not pair_bc.empty:

        print(
            pair_bc[
                [
                    "rank",
                    "pattern",
                    "sample_count",
                    "target_count",
                    "target_rate_%",
                    "baseline_target_rate_%",
                    "lift",
                    "coverage_%",
                    "average_payout",
                    "max_payout",
                ]
            ]
            .head(30)
            .to_string(
                index=False
            )
        )

    print()

    print(
        "===== B vs C 3特徴パターン TOP30 ====="
    )

    if not triple_bc.empty:

        print(
            triple_bc[
                [
                    "rank",
                    "pattern",
                    "sample_count",
                    "target_count",
                    "target_rate_%",
                    "baseline_target_rate_%",
                    "lift",
                    "coverage_%",
                    "average_payout",
                    "max_payout",
                ]
            ]
            .head(30)
            .to_string(
                index=False
            )
        )

    print()

    print(
        "===== 10万円以上 2特徴パターン TOP30 ====="
    )

    if not pair_extreme.empty:

        print(
            pair_extreme[
                [
                    "rank",
                    "pattern",
                    "sample_count",
                    "target_count",
                    "target_rate_%",
                    "baseline_target_rate_%",
                    "lift",
                    "coverage_%",
                    "average_payout",
                    "max_payout",
                ]
            ]
            .head(30)
            .to_string(
                index=False
            )
        )

    print()

    log("013 Complete")


if __name__ == "__main__":
    main()