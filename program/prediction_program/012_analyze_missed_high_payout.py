"""
競輪AI Ver1.0
012_analyze_missed_high_payout.py

AI見逃し高配当レース 詳細分析

対象：
2020.1.1～2022.12.31

見逃し高配当：
・実際の三連単払戻 >= 30,000円
・AI予想 < 30,000円
・011でいう B_実際高配当_AI低配当

調査内容：
1. 見逃し高配当 全体概要
2. 実際払戻クラス
   ・30,000～49,999円
   ・50,000～99,999円
   ・100,000円以上
3. AI予想クラス
   ・0～9,999円
   ・10,000～29,999円
4. AI確信度
5. ライン人数
6. ライン構成
   ・5～9車の全構成
   ・1車は単騎
   ・単騎はライン数に含めない
7. グレード
8. 開催場
9. レース番号
10. 競走種目
11. 既存特徴量による見逃し高配当内の差
12. 見逃しタイプ一覧

※再学習・予測・既存CSV変更は行わない。
"""

import os
import re
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

CSV_DIR = BASE / "csv"
TRAINING_DIR = CSV_DIR / "training"
AI_DIR = CSV_DIR / "ai"

OUTPUT_DIR = CSV_DIR / "analysis" / "missed_high_payout"
OUTPUT_XLSX = OUTPUT_DIR / "012_missed_high_payout_analysis.xlsx"

PREDICTION_CSV = TRAINING_DIR / "training_prediction(2020.1.1~2022.12.31).csv"
FEATURE_CSV = AI_DIR / "training_race_features(2020.1.1~2022.12.31).csv"

HIGH_THRESHOLD = 30000
VERY_HIGH_THRESHOLD = 100000
MIN_SAMPLE_COUNT = 100


# ===========================================================
# ログ
# ===========================================================

def log(msg):
    print(f"[012_analyze_missed_high_payout] {msg}")


# ===========================================================
# CSV読込
# ===========================================================

def read_csv_safely(file):
    last_error = None

    for enc in ("utf-8-sig", "utf-8", "cp932", "shift_jis"):
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
# Prediction CSV
# ===========================================================

def load_prediction():
    log("=======================================")
    log("Prediction CSV 読込")
    log("=======================================")

    if not PREDICTION_CSV.exists():
        raise FileNotFoundError(
            f"Prediction CSVがありません:\n{PREDICTION_CSV}"
        )

    df = read_csv_safely(PREDICTION_CSV)

    required = [
        "レースキー",
        "AI予想",
        "三連単\n払戻",
    ]

    missing = [
        c for c in required
        if c not in df.columns
    ]

    if missing:
        raise KeyError(
            f"Prediction CSVに必要な列がありません: {missing}"
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

    # AIクラス判定
    df["_ai_low"] = df["_ai_class"].str.contains(
        r"0～9,999|0〜9,999|10,000～29,999|10,000〜29,999",
        regex=True,
        na=False,
    )

    df["_ai_high"] = df["_ai_class"].str.contains(
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

    log(f"Rows    : {len(df):,}")
    log(f"Columns : {len(df.columns):,}")

    return df


# ===========================================================
# Feature CSV
# ===========================================================

def load_features():
    log("=======================================")
    log("Training Race Features CSV 読込")
    log("=======================================")

    if not FEATURE_CSV.exists():
        raise FileNotFoundError(
            f"Feature CSVがありません:\n{FEATURE_CSV}"
        )

    df = read_csv_safely(FEATURE_CSV)

    if "race_key" not in df.columns:
        raise KeyError(
            "Feature CSVにrace_keyがありません。"
        )

    if len(df.columns) < 500:
        raise ValueError(
            f"Feature CSVの列数が少なすぎます: {len(df.columns)}"
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

    log(f"Rows    : {len(df):,}")
    log(f"Columns : {len(df.columns):,}")

    return df


# ===========================================================
# 結合
# ===========================================================

def merge_data(pred, feat):
    log("=======================================")
    log("Prediction + Feature 結合")
    log("=======================================")

    merged = pred.merge(
        feat,
        on="race_key",
        how="inner",
        suffixes=("", "_feature"),
    )

    log(f"結合後レース数 : {len(merged):,}")

    if merged.empty:
        raise ValueError(
            "PredictionとFeatureの結合結果が0件です。"
        )

    return merged


# ===========================================================
# 見逃し高配当抽出
# ===========================================================

def create_missed_high_payout(df):
    """
    011 Bグループ：
    実際30,000円以上
    +
    AI30,000円未満
    """

    missed = df[
        (df["_payout"] >= HIGH_THRESHOLD)
        &
        (df["_ai_low"])
    ].copy()

    if missed.empty:
        raise ValueError(
            "見逃し高配当レースが0件です。"
        )

    # -------------------------------------------------------
    # 実際払戻クラス
    # -------------------------------------------------------

    def payout_class(v):
        if pd.isna(v):
            return "不明"

        if v < 50000:
            return "30,000～49,999円"

        if v < 100000:
            return "50,000～99,999円"

        return "100,000円以上"

    missed["_actual_payout_class"] = (
        missed["_payout"]
        .apply(payout_class)
    )

    # -------------------------------------------------------
    # AI予想クラス
    # -------------------------------------------------------

    def normalize_ai_class(v):
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

        return s if s else "不明"

    missed["_ai_prediction_class"] = (
        missed["_ai_class"]
        .apply(normalize_ai_class)
    )

    return missed


# ===========================================================
# 共通：別名列取得
# ===========================================================

def find_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col

    return None


def get_dimension_series(df, candidates, default="不明"):
    col = find_column(df, candidates)

    if col is None:
        return pd.Series(
            [default] * len(df),
            index=df.index,
            dtype="object",
        ), None

    s = df[col].copy()

    s = s.where(
        s.notna(),
        default,
    )

    s = s.astype(str).str.strip()

    s = s.replace(
        {
            "": default,
            "nan": default,
            "None": default,
        }
    )

    return s, col


# ===========================================================
# AI確信度
# ===========================================================

def parse_confidence_value(value):
    if pd.isna(value):
        return np.nan

    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)

    s = str(value).strip()

    if not s:
        return np.nan

    # 数字だけ
    try:
        return float(s.replace(",", ""))
    except Exception:
        pass

    # 「85%」など
    m = re.search(
        r"[-+]?\d+(?:\.\d+)?",
        s.replace(",", ""),
    )

    if m:
        try:
            return float(m.group())
        except Exception:
            return np.nan

    return np.nan


def create_confidence_analysis(df):
    candidates = [
        "AI確信度",
        "AI\n確信度",
        "ai_confidence",
        "confidence",
        "confidence_score",
    ]

    col = find_column(df, candidates)

    if col is None:
        return pd.DataFrame(
            [
                {
                    "status": "AI確信度列なし",
                    "message": "Prediction CSVにAI確信度列が見つかりません。",
                }
            ]
        )

    temp = df.copy()

    temp["_confidence_numeric"] = temp[col].apply(
        parse_confidence_value
    )

    valid = temp["_confidence_numeric"].dropna()

    if valid.empty:
        return pd.DataFrame(
            [
                {
                    "status": "数値化不可",
                    "source_column": col,
                }
            ]
        )

    result = pd.DataFrame(
        {
            "source_column": [col],
            "race_count": [len(temp)],
            "valid_count": [len(valid)],
            "missing_count": [len(temp) - len(valid)],
            "mean": [valid.mean()],
            "median": [valid.median()],
            "min": [valid.min()],
            "max": [valid.max()],
        }
    )

    # 確信度帯
    bands = pd.cut(
        temp["_confidence_numeric"],
        bins=[
            -np.inf,
            20,
            40,
            60,
            80,
            np.inf,
        ],
        labels=[
            "～20",
            "20超～40",
            "40超～60",
            "60超～80",
            "80超",
        ],
    )

    band_summary = (
        pd.DataFrame(
            {
                "confidence_band": bands,
                "actual_payout_class": temp[
                    "_actual_payout_class"
                ],
            }
        )
        .groupby(
            ["confidence_band", "actual_payout_class"],
            observed=False,
        )
        .size()
        .reset_index(name="race_count")
    )

    band_summary["source_column"] = col

    # 別シート用に返す
    result.attrs["band_summary"] = band_summary

    return result


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
        "real_line_count": real_line_count,
        "tanki_count": tanki_count,
        "line_structure": line_structure,
        "max_line_size": max(line_sizes) if line_sizes else 1,
    }

def build_line_structure_data(
    df,
):

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
            df.reset_index(drop=True),
            structure_df,
        ],
        axis=1,
    )

    return result

# ===========================================================
# 単純集計
# ===========================================================

def summarize_dimension(
    df,
    column,
    payout_col="_payout",
):
    temp = df.copy()

    temp[column] = (
        temp[column]
        .fillna("不明")
        .astype(str)
        .str.strip()
    )

    grouped = (
        temp.groupby(
            column,
            dropna=False,
        )
        .agg(
            race_count=(
                "race_key",
                "size",
            ),
            average_payout=(
                payout_col,
                "mean",
            ),
            median_payout=(
                payout_col,
                "median",
            ),
            max_payout=(
                payout_col,
                "max",
            ),
        )
        .reset_index()
    )

    for payout_class in [
        "30,000～49,999円",
        "50,000～99,999円",
        "100,000円以上",
    ]:

        counts = (
            temp[
                temp["_actual_payout_class"]
                == payout_class
            ]
            .groupby(column)
            .size()
            .rename(
                f"count_{payout_class}"
            )
        )

        grouped = grouped.merge(
            counts,
            on=column,
            how="left",
        )

    count_cols = [
        c for c in grouped.columns
        if c.startswith("count_")
    ]

    grouped[count_cols] = (
        grouped[count_cols]
        .fillna(0)
        .astype(int)
    )

    grouped["high_100k_rate_%"] = (
        grouped["count_100,000円以上"]
        / grouped["race_count"]
        * 100
    )

    grouped = grouped.sort_values(
        "race_count",
        ascending=False,
    )

    return grouped


# ===========================================================
# ライン人数分析
# ===========================================================

def create_line_count_analysis(df):
    temp = df.copy()

    temp["real_line_count"] = (
        pd.to_numeric(
            temp["real_line_count"],
            errors="coerce",
        )
    )

    temp = temp.dropna(
        subset=[
            "real_line_count"
        ]
    )

    temp[
        "real_line_count"
    ] = temp[
        "real_line_count"
    ].astype(int)

    return summarize_dimension(
        temp,
        "real_line_count",
    )


# ===========================================================
# ライン構成分析
# ===========================================================

def create_line_structure_analysis(df):
    result = summarize_dimension(
        df,
        "line_structure",
    )

    # 少ない構成も残す。
    # ただし分析時にノイズにならないよう
    # 件数順で出力。
    return result


# ===========================================================
# AI予想クラス分析
# ===========================================================

def create_ai_class_analysis(df):
    return summarize_dimension(
        df,
        "_ai_prediction_class",
    )


# ===========================================================
# グレード分析
# ===========================================================

def create_grade_analysis(df):
    s, col = get_dimension_series(
        df,
        [
            "grade",
            "グレード",
            "競走グレード",
            "開催グレード",
        ],
    )

    temp = df.copy()
    temp["_analysis_grade"] = s

    result = summarize_dimension(
        temp,
        "_analysis_grade",
    )

    result = result.rename(
        columns={
            "_analysis_grade": "grade",
        }
    )

    result.attrs["source_column"] = col

    return result


# ===========================================================
# 開催場分析
# ===========================================================

def create_venue_analysis(df):
    s, col = get_dimension_series(
        df,
        [
            "jo_name",
            "開催場",
            "競輪場",
            "競輪場名",
            "joName",
            "場名",
        ],
    )

    temp = df.copy()
    temp["_analysis_venue"] = s

    result = summarize_dimension(
        temp,
        "_analysis_venue",
    )

    result = result.rename(
        columns={
            "_analysis_venue": "venue",
        }
    )

    result.attrs["source_column"] = col

    return result


# ===========================================================
# レース番号分析
# ===========================================================

def create_race_no_analysis(df):
    s, col = get_dimension_series(
        df,
        [
            "race_no",
            "レース番号",
            "R",
            "raceNo",
            "レースNo",
        ],
    )

    temp = df.copy()
    temp["_analysis_race_no"] = s

    result = summarize_dimension(
        temp,
        "_analysis_race_no",
    )

    result = result.rename(
        columns={
            "_analysis_race_no": "race_no",
        }
    )

    result.attrs["source_column"] = col

    return result


# ===========================================================
# 競走種目分析
# ===========================================================

def create_event_type_analysis(df):
    s, col = get_dimension_series(
        df,
        [
            "event_name",
            "競走種目",
            "競走種目名",
            "種目",
            "syumoku",
            "nameKyosou",
        ],
    )

    temp = df.copy()
    temp["_analysis_event_type"] = s

    result = summarize_dimension(
        temp,
        "_analysis_event_type",
    )

    result = result.rename(
        columns={
            "_analysis_event_type": "event_type",
        }
    )

    result.attrs["source_column"] = col

    return result


# ===========================================================
# 既存特徴量抽出
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
        "date",
        "target_date",
        "開催日",
        "日付",
        "jo_code",
        "jo_name",
        "race_no",
        "event_name",
        "grade",
        "_payout",
        "_ai_class",
        "_ai_low",
        "_ai_high",
        "_actual_payout_class",
        "_ai_prediction_class",
        "line_structure",
        "real_line_count",
        "max_line_size",
        "min_non_single_line_size",
        "tanki_count",
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

        if numeric.notna().sum() < MIN_SAMPLE_COUNT:
            continue

        if numeric.nunique(
            dropna=True
        ) <= 1:
            continue

        cols.append(col)

    return cols


# ===========================================================
# Cohen's d
# ===========================================================

def cohens_d(a, b):
    a = pd.to_numeric(
        a,
        errors="coerce",
    ).dropna()

    b = pd.to_numeric(
        b,
        errors="coerce",
    ).dropna()

    if len(a) < 2 or len(b) < 2:
        return np.nan

    va = a.var(ddof=1)
    vb = b.var(ddof=1)

    pooled = np.sqrt(
        (
            (len(a) - 1) * va
            +
            (len(b) - 1) * vb
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

    if pooled == 0 or pd.isna(pooled):
        return np.nan

    return (
        a.mean()
        -
        b.mean()
    ) / pooled


# ===========================================================
# 3クラス特徴量分析
# ===========================================================

def eta_squared_three_groups(
    group_values,
):
    """
    3つの払戻クラス間で、
    特徴量がどれだけクラス差を持つかを見る。

    0に近い：
        クラスによる差が小さい

    大きい：
        払戻クラスによる差が大きい
    """

    valid_groups = [
        pd.to_numeric(
            x,
            errors="coerce",
        ).dropna()
        for x in group_values
    ]

    valid_groups = [
        x for x in valid_groups
        if len(x) >= 2
    ]

    if len(valid_groups) < 2:
        return np.nan

    all_values = pd.concat(
        valid_groups,
        ignore_index=True,
    )

    grand_mean = all_values.mean()

    between = 0.0
    total = 0.0

    for x in valid_groups:
        between += (
            len(x)
            *
            (x.mean() - grand_mean) ** 2
        )

        total += (
            ((x - grand_mean) ** 2)
            .sum()
        )

    if total == 0:
        return np.nan

    return between / total


def create_feature_analysis(df, features):
    classes = [
        "30,000～49,999円",
        "50,000～99,999円",
        "100,000円以上",
    ]

    rows = []

    for idx, feature in enumerate(features, start=1):

        if idx % 250 == 0:
            log(
                f"特徴量分析 : {idx:,}/{len(features):,}"
            )

        class_values = []

        for cls in classes:
            values = pd.to_numeric(
                df.loc[
                    df["_actual_payout_class"]
                    == cls,
                    feature,
                ],
                errors="coerce",
            ).dropna()

            class_values.append(values)

        counts = [
            len(x)
            for x in class_values
        ]

        if min(counts) < MIN_SAMPLE_COUNT:
            continue

        means = [
            x.mean()
            for x in class_values
        ]

        medians = [
            x.median()
            for x in class_values
        ]

        d_1_2 = cohens_d(
            class_values[0],
            class_values[1],
        )

        d_2_3 = cohens_d(
            class_values[1],
            class_values[2],
        )

        d_1_3 = cohens_d(
            class_values[0],
            class_values[2],
        )

        eta2 = eta_squared_three_groups(
            class_values
        )

        rows.append(
            {
                "feature": feature,
                "30k_49k_count": counts[0],
                "50k_99k_count": counts[1],
                "100k_plus_count": counts[2],
                "30k_49k_mean": means[0],
                "50k_99k_mean": means[1],
                "100k_plus_mean": means[2],
                "30k_49k_median": medians[0],
                "50k_99k_median": medians[1],
                "100k_plus_median": medians[2],
                "d_30k_vs_50k": d_1_2,
                "d_50k_vs_100k": d_2_3,
                "d_30k_vs_100k": d_1_3,
                "eta_squared": eta2,
                "max_abs_cohens_d": np.nanmax(
                    np.abs(
                        [
                            d_1_2,
                            d_2_3,
                            d_1_3,
                        ]
                    )
                ),
            }
        )

    result = pd.DataFrame(rows)

    if result.empty:
        return result

    return result.sort_values(
        [
            "eta_squared",
            "max_abs_cohens_d",
        ],
        ascending=False,
    ).reset_index(
        drop=True
    ).assign(
        rank=lambda x: np.arange(
            1,
            len(x) + 1,
        )
    )


# ===========================================================
# 見逃しタイプ分類
# ===========================================================

def create_missed_type_summary(df):
    """
    見逃し高配当を、
    払戻クラス × AI予想クラス × ライン構成
    の組み合わせで分類。

    目的：
    「どの見逃しタイプが大量に存在するか」
    を確認する。
    """

    group_cols = [
        "_actual_payout_class",
        "_ai_prediction_class",
        "line_structure",
    ]

    result = (
        df.groupby(
            group_cols,
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
            average_line_count=(
                "real_line_count",
                "mean",
            ),
            average_max_line_size=(
                "max_line_size",
                "mean",
            ),
            average_tanki_count=(
                "tanki_count",
                "mean",
            ),
        )
        .reset_index()
    )

    result["share_%"] = (
        result["race_count"]
        /
        len(df)
        *
        100
    )

    result = result.sort_values(
        [
            "race_count",
            "average_payout",
        ],
        ascending=False,
    ).reset_index(
        drop=True
    )

    result.insert(
        0,
        "rank",
        np.arange(
            1,
            len(result) + 1,
        ),
    )

    return result


# ===========================================================
# 見逃しタイプ 上位分類
# ===========================================================

def create_simple_type_summary(df):
    """
    より粗い分類。

    払戻クラス × AI予想クラス ×
    ライン数 × 単騎数
    """

    temp = df.copy()

    result = (
        temp.groupby(
            [
                "_actual_payout_class",
                "_ai_prediction_class",
                "real_line_count",
                "tanki_count",
            ],
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
        )
        .reset_index()
    )

    result["share_%"] = (
        result["race_count"]
        /
        len(df)
        *
        100
    )

    return result.sort_values(
        "race_count",
        ascending=False,
    ).reset_index(
        drop=True
    )


# ===========================================================
# 100,000円以上の詳細
# ===========================================================

def create_very_high_analysis(df):
    temp = df[
        df["_actual_payout_class"]
        == "100,000円以上"
    ].copy()

    if temp.empty:
        return pd.DataFrame(
            [
                {
                    "message":
                    "100,000円以上の見逃し高配当はありません。"
                }
            ]
        )

    rows = []

    for label, col in [
        (
            "AI予想クラス",
            "_ai_prediction_class",
        ),
        (
            "ライン構成",
            "line_structure",
        ),
        (
            "ライン数（単騎除外）",
            "real_line_count",
        ),
        (
            "単騎数",
            "tanki_count",
        ),
    ]:

        grouped = (
            temp.groupby(
                col,
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
                max_payout=(
                    "_payout",
                    "max",
                ),
            )
            .reset_index()
        )

        grouped["analysis_item"] = label
        grouped = grouped.rename(
            columns={
                col: "value",
            }
        )

        rows.append(grouped)

    return pd.concat(
        rows,
        ignore_index=True,
    )


# ===========================================================
# 基本概要
# ===========================================================

def create_overview(df):
    total = len(df)

    rows = [
        {
            "item": "見逃し高配当レース数",
            "value": total,
        },
        {
            "item": "平均払戻",
            "value": df["_payout"].mean(),
        },
        {
            "item": "中央値払戻",
            "value": df["_payout"].median(),
        },
        {
            "item": "最低払戻",
            "value": df["_payout"].min(),
        },
        {
            "item": "最高払戻",
            "value": df["_payout"].max(),
        },
        {
            "item": "30,000～49,999円",
            "value": (
                (
                    df["_actual_payout_class"]
                    == "30,000～49,999円"
                ).sum()
            ),
        },
        {
            "item": "50,000～99,999円",
            "value": (
                (
                    df["_actual_payout_class"]
                    == "50,000～99,999円"
                ).sum()
            ),
        },
        {
            "item": "100,000円以上",
            "value": (
                (
                    df["_actual_payout_class"]
                    == "100,000円以上"
                ).sum()
            ),
        },
    ]

    result = pd.DataFrame(rows)

    result["share_%"] = np.nan

    for i, row in result.iterrows():
        if row["item"] in [
            "30,000～49,999円",
            "50,000～99,999円",
            "100,000円以上",
        ]:
            result.loc[i, "share_%"] = (
                row["value"]
                /
                total
                *
                100
            )

    return result


# ===========================================================
# 主要項目横断集計
# ===========================================================

def create_cross_summary(df):
    """
    払戻クラスごとの主要構造を一つにまとめる。
    """

    rows = []

    for cls in [
        "30,000～49,999円",
        "50,000～99,999円",
        "100,000円以上",
    ]:

        sub = df[
            df["_actual_payout_class"]
            == cls
        ].copy()

        if sub.empty:
            continue

        rows.append(
            {
                "actual_payout_class": cls,
                "race_count": len(sub),
                "share_%": (
                    len(sub)
                    /
                    len(df)
                    *
                    100
                ),
                "average_payout": sub[
                    "_payout"
                ].mean(),
                "median_payout": sub[
                    "_payout"
                ].median(),
                "average_line_count": sub[
                    "real_line_count"
                ].mean(),
                "average_max_line_size": sub[
                    "max_line_size"
                ].mean(),
                "average_tanki_count": sub[
                    "tanki_count"
                ].mean(),
                "AI_0_9999_count": (
                    sub[
                        "_ai_prediction_class"
                    ]
                    == "0～9,999円"
                ).sum(),
                "AI_10000_29999_count": (
                    sub[
                        "_ai_prediction_class"
                    ]
                    == "10,000～29,999円"
                ).sum(),
            }
        )

    return pd.DataFrame(rows)


# ===========================================================
# Excel保存
# ===========================================================

def save_excel(
    overview,
    payout_class,
    ai_class,
    confidence,
    confidence_band,
    line_count,
    line_structure,
    grade,
    venue,
    race_no,
    event_type,
    feature_analysis,
    missed_types,
    simple_types,
    very_high,
    cross_summary,
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

        payout_class.to_excel(
            writer,
            sheet_name="02_払戻クラス",
            index=False,
        )

        ai_class.to_excel(
            writer,
            sheet_name="03_AI予想クラス",
            index=False,
        )

        confidence.to_excel(
            writer,
            sheet_name="04_AI確信度",
            index=False,
        )

        confidence_band.to_excel(
            writer,
            sheet_name="05_確信度帯",
            index=False,
        )

        line_count.to_excel(
            writer,
            sheet_name="06_ライン人数",
            index=False,
        )

        line_structure.to_excel(
            writer,
            sheet_name="07_ライン構成",
            index=False,
        )

        grade.to_excel(
            writer,
            sheet_name="08_グレード",
            index=False,
        )

        venue.to_excel(
            writer,
            sheet_name="09_開催場",
            index=False,
        )

        race_no.to_excel(
            writer,
            sheet_name="10_レース番号",
            index=False,
        )

        event_type.to_excel(
            writer,
            sheet_name="11_競走種目",
            index=False,
        )

        feature_analysis.to_excel(
            writer,
            sheet_name="12_既存特徴量分析",
            index=False,
        )

        missed_types.to_excel(
            writer,
            sheet_name="13_見逃しタイプ",
            index=False,
        )

        simple_types.to_excel(
            writer,
            sheet_name="14_簡易タイプ",
            index=False,
        )

        very_high.to_excel(
            writer,
            sheet_name="15_10万円以上",
            index=False,
        )

        cross_summary.to_excel(
            writer,
            sheet_name="16_横断概要",
            index=False,
        )

    log(f"保存先 : {OUTPUT_XLSX}")


# ===========================================================
# メイン
# ===========================================================

def main():

    print()

    log("=======================================")
    log("012 Missed High Payout Analysis")
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
    # 見逃し抽出
    # -------------------------------------------------------

    log("=======================================")
    log("見逃し高配当抽出")
    log("=======================================")

    missed = create_missed_high_payout(
        df
    )

    log(
        f"見逃し高配当 : "
        f"{len(missed):,} レース"
    )

    # -------------------------------------------------------
    # ライン構造
    # -------------------------------------------------------

    log("=======================================")
    log("ライン構造生成")
    log("=======================================")

    missed = build_line_structure_data(
        missed
    )

    # -------------------------------------------------------
    # 特徴量
    # -------------------------------------------------------

    features = get_feature_columns(
        missed
    )

    log(
        f"分析対象既存特徴量 : "
        f"{len(features):,}"
    )

    # -------------------------------------------------------
    # 各分析
    # -------------------------------------------------------

    log("=======================================")
    log("各項目分析")
    log("=======================================")

    overview = create_overview(
        missed
    )

    payout_class = summarize_dimension(
        missed,
        "_actual_payout_class",
    )

    ai_class = create_ai_class_analysis(
        missed
    )

    confidence = create_confidence_analysis(
        missed
    )

    confidence_band = confidence.attrs.get(
        "band_summary",
        pd.DataFrame(),
    )

    line_count = create_line_count_analysis(
        missed
    )

    line_structure = create_line_structure_analysis(
        missed
    )

    grade = create_grade_analysis(
        missed
    )

    venue = create_venue_analysis(
        missed
    )

    race_no = create_race_no_analysis(
        missed
    )

    event_type = create_event_type_analysis(
        missed
    )

    # -------------------------------------------------------
    # 既存特徴量分析
    # -------------------------------------------------------

    log("=======================================")
    log("既存特徴量分析")
    log("=======================================")

    feature_analysis = create_feature_analysis(
        missed,
        features,
    )

    # -------------------------------------------------------
    # 見逃しタイプ
    # -------------------------------------------------------

    log("=======================================")
    log("見逃しタイプ分類")
    log("=======================================")

    missed_types = create_missed_type_summary(
        missed
    )

    simple_types = create_simple_type_summary(
        missed
    )

    very_high = create_very_high_analysis(
        missed
    )

    cross_summary = create_cross_summary(
        missed
    )

    # -------------------------------------------------------
    # 保存
    # -------------------------------------------------------

    log("=======================================")
    log("Excel保存")
    log("=======================================")

    save_excel(
        overview,
        payout_class,
        ai_class,
        confidence,
        confidence_band,
        line_count,
        line_structure,
        grade,
        venue,
        race_no,
        event_type,
        feature_analysis,
        missed_types,
        simple_types,
        very_high,
        cross_summary,
    )

    # -------------------------------------------------------
    # コンソール概要
    # -------------------------------------------------------

    print()

    log("=======================================")
    log("012 Summary")
    log("=======================================")

    print(
        overview.to_string(
            index=False
        )
    )

    print()

    print(
        "===== 払戻クラス ====="
    )

    print(
        payout_class.to_string(
            index=False
        )
    )

    print()

    print(
        "===== ライン構成 TOP20 ====="
    )

    if not line_structure.empty:
        print(
            line_structure.head(20).to_string(
                index=False
            )
        )

    print()

    print(
        "===== 見逃しタイプ TOP30 ====="
    )

    if not missed_types.empty:
        print(
            missed_types.head(30).to_string(
                index=False
            )
        )

    print()

    print(
        "===== 既存特徴量 TOP30 ====="
    )

    if not feature_analysis.empty:
        display_cols = [
            "rank",
            "feature",
            "30k_49k_mean",
            "50k_99k_mean",
            "100k_plus_mean",
            "d_30k_vs_50k",
            "d_50k_vs_100k",
            "d_30k_vs_100k",
            "eta_squared",
            "max_abs_cohens_d",
        ]

        display_cols = [
            c for c in display_cols
            if c in feature_analysis.columns
        ]

        print(
            feature_analysis[
                display_cols
            ]
            .head(30)
            .to_string(
                index=False
            )
        )

    print()

    log("012 Complete")


if __name__ == "__main__":
    main()
