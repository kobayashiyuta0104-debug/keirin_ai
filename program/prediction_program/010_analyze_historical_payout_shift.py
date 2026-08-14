"""
===========================================================
競輪AI Ver1.0
010_analyze_historical_payout_shift.py

高配当パターン 時代差分析

【目的】

2020～2022
        VS
2023～2026

の実際の高配当レースを比較し、

「高配当になるレースの特徴そのものが
 学習期間と過去期間で変化しているか」

を調査する。

さらに、

2020～2022の実際30,000円以上
        ↓
AIが低配当予想

となったレースを抽出し、

「AIが見逃した高配当レースには
 どんな特徴があるか」

を分析する。

===========================================================

【比較グループ】

A:
2020～2022
実際30,000円以上

B:
2023～2026
実際30,000円以上

C:
2020～2022
実際30,000円以上
かつAI低配当予想

===========================================================

【重要】

・再学習しない
・モデル変更しない
・特徴量変更しない
・予測しない
・分析のみ

===========================================================
"""

import os
import json
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
# データ保存場所
# ===========================================================

CSV_DIR = BASE / "csv"

ANALYSIS_DIR = (
    CSV_DIR
    / "analysis"
)

OUTPUT_DIR = (
    ANALYSIS_DIR
    / "historical_payout_shift"
)


# ===========================================================
# 入力ファイル
#
# ※ 実際のファイル名が多少違っていても、
#    下の検索処理で自動検出する。
# ===========================================================

# 予測CSVを探す候補フォルダ
PREDICTION_DIR_CANDIDATES = [
    CSV_DIR / "prediction",
    CSV_DIR / "predictions",
    CSV_DIR / "result",
    CSV_DIR,
]

# training race featuresを探す候補フォルダ
FEATURE_DIR_CANDIDATES = [
    CSV_DIR / "training_race_features",
    CSV_DIR / "training_features",
    CSV_DIR / "features",
    CSV_DIR,
]


# ===========================================================
# 期間
# ===========================================================

HIST_START = pd.Timestamp("2020-01-01")
HIST_END = pd.Timestamp("2022-12-31")

TRAIN_START = pd.Timestamp("2023-01-01")
TRAIN_END = pd.Timestamp("2026-07-30")


# ===========================================================
# 高配当判定
# ===========================================================

HIGH_PAYOUT_THRESHOLD = 30000


# ===========================================================
# 最低サンプル数
#
# 少数サンプルによるAUC等の暴走を防ぐ。
# ===========================================================

MIN_SAMPLE_COUNT = 100


# ===========================================================
# 出力ファイル
# ===========================================================

OUTPUT_XLSX = (
    OUTPUT_DIR
    / "010_historical_payout_shift_analysis.xlsx"
)


# ===========================================================
# ログ
# ===========================================================

def log(message):

    print(
        f"[010_analyze_historical_payout_shift] "
        f"{message}"
    )


# ===========================================================
# 出力フォルダ
# ===========================================================

def prepare_output():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


# ===========================================================
# CSV検索
# ===========================================================

def find_csv_files(
    candidates,
):

    files = []

    for folder in candidates:

        if not folder.exists():
            continue

        files.extend(
            folder.rglob("*.csv")
        )

    # 重複削除
    unique_files = {}

    for file in files:

        unique_files[
            str(file.resolve())
        ] = file

    return sorted(
        unique_files.values()
    )


# ===========================================================
# 日付抽出
# ===========================================================

def detect_period_from_filename(
    file,
):

    name = file.name

    # 20200101形式
    for date_text in [
        name[i:i + 8]
        for i in range(
            max(len(name) - 7, 0)
        )
    ]:

        if (
            date_text.isdigit()
            and len(date_text) == 8
        ):

            try:

                date = pd.Timestamp(
                    date_text
                )

                return date

            except Exception:

                pass

    return None


# ===========================================================
# CSVの内容から期間判定
# ===========================================================

def detect_date_column(
    df,
):

    candidates = [
        "date",
        "target_date",
        "開催日",
        "日付",
    ]

    for column in candidates:

        if column in df.columns:

            values = pd.to_datetime(
                df[column],
                errors="coerce",
            )

            if values.notna().sum() > 0:

                return column

    return None


# ===========================================================
# CSV読込
# ===========================================================

def read_csv_safely(
    file,
):

    encodings = [
        "utf-8-sig",
        "utf-8",
        "cp932",
        "shift_jis",
    ]

    last_error = None

    for encoding in encodings:

        try:

            df = pd.read_csv(
                file,
                encoding=encoding,
                low_memory=False,
            )

            return df

        except Exception as e:

            last_error = e

    raise last_error


# ===========================================================
# 予測CSV候補の抽出
# ===========================================================

def identify_prediction_files():

    log(
        "======================================="
    )

    log(
        "Prediction CSV Search"
    )

    log(
        "======================================="
    )

    files = find_csv_files(
        PREDICTION_DIR_CANDIDATES
    )

    if len(files) == 0:

        raise FileNotFoundError(
            "Prediction CSVが見つかりません。"
        )

    results = []

    for file in files:

        try:

            # ファイル名で明らかにprediction系を優先
            name = file.name.lower()

            score = 0

            if (
                "prediction" in name
                or "predict" in name
                or "予想" in name
            ):
                score += 10

            if (
                "ai" in name
            ):
                score += 5

            if (
                "payout" in name
                or "result" in name
            ):
                score += 2

            # ヘッダーだけ確認
            df_head = pd.read_csv(
                file,
                encoding="utf-8-sig",
                nrows=3,
            )

            required = [
                "race_key",
            ]

            if not all(
                c in df_head.columns
                for c in required
            ):
                continue

            # AI予想系列
            if "AI予想" in df_head.columns:
                score += 20

            if "AI確信度" in df_head.columns:
                score += 10

            if "実際\nクラス" in df_head.columns:
                score += 10

            if "三連単\n払戻" in df_head.columns:
                score += 10

            results.append(
                (
                    score,
                    file,
                )
            )

        except Exception:

            continue

    results.sort(
        key=lambda x: x[0],
        reverse=True,
    )

    if len(results) == 0:

        raise FileNotFoundError(
            "AI予測用CSVを特定できませんでした。"
        )

    for score, file in results[:20]:

        log(
            f"候補 : {file}"
            f" / score={score}"
        )

    print()

    return [
        file
        for score, file in results
        if score >= 20
    ]


# ===========================================================
# 予測データ結合
# ===========================================================

def load_prediction_data():

    log(
        "======================================="
    )

    log(
        "Prediction CSV 読込"
    )

    log(
        "======================================="
    )

    prediction_files = [
        BASE
        / "csv"
        / "training"
        / "training_prediction(2020.1.1~2022.12.31).csv",

        BASE
        / "csv"
        / "training"
        / "training_prediction(2023.1.1~2026.7.30).csv",
    ]

    frames = []

    for file in prediction_files:

        log(
            f"読込 : {file}"
        )

        if not file.exists():

            raise FileNotFoundError(
                f"Prediction CSVがありません:\n{file}"
            )

        df = read_csv_safely(
            file
        )

        log(
            f"Rows    : {len(df):,}"
        )

        log(
            f"Columns : {len(df.columns):,}"
        )

        required_columns = [
            "レースキー",
            "AI予想",
            "三連単\n払戻",
        ]

        missing = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing:

            raise KeyError(
                f"Prediction CSVに必要な列がありません: "
                f"{missing}\n"
                f"File: {file}"
            )

        date_column = detect_date_column(
            df
        )

        if date_column is None:

            raise KeyError(
                f"Prediction CSVに日付列がありません:\n"
                f"{file}"
            )

        df[
            "_date"
        ] = pd.to_datetime(
            df[date_column],
            errors="coerce",
        )

        # Prediction側の「レースキー」を
        # 結合用の「race_key」に統一
        df["race_key"] = df["レースキー"].astype(str).str.strip()

        df[
            "_source_file"
        ] = str(file)

        frames.append(
            df
        )

    result = pd.concat(
        frames,
        ignore_index=True,
    )

    # race_key重複除去
    result = result.drop_duplicates(
        subset=["レースキー"],
        keep="last",
    )

    log(
        "======================================="
    )

    log(
        f"Prediction 合計 : "
        f"{len(result):,} レース"
    )

    log(
        "======================================="
    )

    return result

# ===========================================================
# Feature CSV候補検索
# ===========================================================

def identify_feature_files():

    log(
        "======================================="
    )

    log(
        "Training Race Features Search"
    )

    log(
        "======================================="
    )

    files = find_csv_files(
        FEATURE_DIR_CANDIDATES
    )

    candidates = []

    for file in files:

        name = file.name.lower()

        score = 0

        if (
            "training_race_features"
            in name
        ):
            score += 20

        if (
            "race_features"
            in name
        ):
            score += 10

        if (
            "training" in name
        ):
            score += 5

        if (
            "feature" in name
        ):
            score += 5

        try:

            df_head = pd.read_csv(
                file,
                encoding="utf-8-sig",
                nrows=2,
            )

            if "race_key" in df_head.columns:

                score += 20

            if "trifecta_payout" in df_head.columns:

                score += 20

            if "三連単\n払戻" in df_head.columns:

                score += 20

            if len(df_head.columns) > 500:

                score += 20

        except Exception:

            continue

        candidates.append(
            (
                score,
                file,
            )
        )

    candidates.sort(
        key=lambda x: x[0],
        reverse=True,
    )

    if len(candidates) == 0:

        raise FileNotFoundError(
            "Training Race Features CSVが"
            "見つかりません。"
        )

    for score, file in candidates[:20]:

        log(
            f"候補 : {file}"
            f" / score={score}"
        )

    print()

    return [
        file
        for score, file in candidates
        if score >= 30
    ]


# ===========================================================
# Feature CSV読込
# ===========================================================

def load_feature_data():

    log(
        "======================================="
    )

    log(
        "Training Race Features CSV 読込"
    )

    log(
        "======================================="
    )

    feature_files = [
        BASE
        / "csv"
        / "ai"
        / "training_race_features(2020.1.1~2022.12.31).csv",

        BASE
        / "csv"
        / "ai"
        / "training_race_features(2023.1.1~2026.7.30).csv",
    ]

    frames = []

    for file in feature_files:

        log(
            f"読込 : {file}"
        )

        if not file.exists():

            raise FileNotFoundError(
                f"Training Race Features CSVがありません:\n{file}"
            )

        df = read_csv_safely(
            file
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
                f"{file}"
            )

        if len(df.columns) < 500:

            raise ValueError(
                f"Feature CSVの特徴量数が少なすぎます。\n"
                f"Columns = {len(df.columns)}\n"
                f"File = {file}"
            )

        df[
            "_source_file"
        ] = str(file)

        frames.append(
            df
        )

    result = pd.concat(
        frames,
        ignore_index=True,
    )

    # race_key重複除去
    result = result.drop_duplicates(
        subset=["race_key"],
        keep="last",
    )

    log(
        "======================================="
    )

    log(
        f"Feature 合計 : "
        f"{len(result):,} レース"
    )

    log(
        f"Feature Columns : "
        f"{len(result.columns):,}"
    )

    log(
        "======================================="
    )

    return result

# ===========================================================
# race_key統一
# ===========================================================

def normalize_race_key(
    value,
):

    if pd.isna(value):

        return ""

    text = str(
        value
    ).strip()

    # 20200101_22_01
    # ↓
    # 20200101_前橋_1R
    #
    # ここでは22→競輪場名の変換が必要になるため、
    # 既に統一済みのrace_keyを優先する。
    #
    # 数値形式の場合は後段で
    # Prediction側のrace_keyとの一致を確認する。

    return text


# ===========================================================
# 実際払戻列検出
# ===========================================================

def find_payout_column(
    df,
):

    candidates = [
        "三連単\n払戻",
        "trifecta_payout",
        "trifecta",
        "payout",
    ]

    for column in candidates:

        if column in df.columns:

            return column

    raise KeyError(
        "三連単払戻列が見つかりません。"
    )


# ===========================================================
# AI予想クラス正規化
# ===========================================================

def normalize_ai_class(
    value,
):

    if pd.isna(value):

        return ""

    text = str(
        value
    ).strip()

    return text


# ===========================================================
# 高配当判定
# ===========================================================

def add_basic_labels(
    df,
):

    result = df.copy()

    payout_column = find_payout_column(
        result
    )

    result[
        "_payout"
    ] = pd.to_numeric(
        result[payout_column],
        errors="coerce",
    )

    result[
        "_is_high_payout"
    ] = (
        result[
            "_payout"
        ]
        >= HIGH_PAYOUT_THRESHOLD
    )

    # -------------------------------------------------------
    # 期間
    # -------------------------------------------------------

    result[
        "_period"
    ] = np.select(
        [
            (
                result["_date"]
                >= HIST_START
            )
            &
            (
                result["_date"]
                <= HIST_END
            ),

            (
                result["_date"]
                >= TRAIN_START
            )
            &
            (
                result["_date"]
                <= TRAIN_END
            ),
        ],
        [
            "2020-2022",
            "2023-2026",
        ],
        default="対象外",
    )

    # -------------------------------------------------------
    # AI予想
    # -------------------------------------------------------

    result[
        "_ai_class"
    ] = result[
        "AI予想"
    ].apply(
        normalize_ai_class
    )

    # 30,000円未満を低配当予想とする
    #
    # 0～9,999円
    # 10,000～29,999円
    #
    # の両方を「AIが30,000円以上を予想できなかった」
    # として扱う。
    result[
        "_ai_low"
    ] = (
        result[
            "_ai_class"
        ]
        .astype(str)
        .str.contains(
            "0～9,999|10,000～29,999",
            regex=True,
        )
    )

    return result


# ===========================================================
# Prediction + Feature結合
# ===========================================================

def merge_prediction_feature(
    prediction_df,
    feature_df,
):

    log(
        "======================================="
    )

    log(
        "Prediction + Feature Merge"
    )

    log(
        "======================================="
    )

    pred = prediction_df.copy()
    feat = feature_df.copy()

    pred[
        "race_key"
    ] = pred[
        "race_key"
    ].apply(
        normalize_race_key
    )

    feat[
        "race_key"
    ] = feat[
        "race_key"
    ].apply(
        normalize_race_key
    )

    # feature側の日付を使う
    date_column = detect_date_column(
        feat
    )

    if date_column is not None:

        feat[
            "_feature_date"
        ] = pd.to_datetime(
            feat[date_column],
            errors="coerce",
        )

    # Prediction側の日付を優先
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
            "race_keyを確認してください。"
        )

    return merged


# ===========================================================
# 特徴量列取得
# ===========================================================

def get_feature_columns(
    df,
):

    exclude = {
        "race_key",
        "date",
        "target_date",
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
        "_date",
        "_period",
        "_payout",
        "_is_high_payout",
        "_ai_class",
        "_ai_low",
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

        # race/player/resultの文字列情報などを除外
        if (
            df[column].dtype
            == "object"
        ):

            continue

        columns.append(
            column
        )

    return columns


# ===========================================================
# 数値化
# ===========================================================

def numeric_series(
    series,
):

    return pd.to_numeric(
        series,
        errors="coerce",
    )


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

    if len(a) < 2 or len(b) < 2:

        return np.nan

    var1 = a.var(
        ddof=1
    )

    var2 = b.var(
        ddof=1
    )

    pooled = np.sqrt(
        (
            (
                len(a) - 1
            )
            * var1
            +
            (
                len(b) - 1
            )
            * var2
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

    if pooled == 0:

        return np.nan

    return (
        a.mean()
        -
        b.mean()
    ) / pooled


# ===========================================================
# 効果量判定
# ===========================================================

def effect_strength(
    value,
):

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
    group1_name,
    group2_name,
):

    rows = []

    for feature in feature_columns:

        a = numeric_series(
            df1[feature]
        ).dropna()

        b = numeric_series(
            df2[feature]
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
                "feature":
                    feature,

                f"{group1_name}_count":
                    len(a),

                f"{group2_name}_count":
                    len(b),

                f"{group1_name}_mean":
                    mean_a,

                f"{group2_name}_mean":
                    mean_b,

                "mean_difference":
                    mean_a - mean_b,

                f"{group1_name}_median":
                    median_a,

                f"{group2_name}_median":
                    median_b,

                "cohens_d":
                    d,

                "effect_strength":
                    effect_strength(d),
            }
        )

    result = pd.DataFrame(
        rows
    )

    if result.empty:

        return result

    result[
        "abs_cohens_d"
    ] = result[
        "cohens_d"
    ].abs()

    result = result.sort_values(
        "abs_cohens_d",
        ascending=False,
    )

    result[
        "rank"
    ] = range(
        1,
        len(result) + 1,
    )

    return result


# ===========================================================
# 高配当構造比較
# ===========================================================

def analyze_line_structure(
    df,
):

    rows = []

    # -------------------------------------------------------
    # 既存のline_size / line_count等を利用
    # -------------------------------------------------------

    candidate_columns = [
        "line_count",
        "line_size",
        "max_line_size",
        "min_line_size",
        "tanki_count",
    ]

    available = [
        c
        for c in candidate_columns
        if c in df.columns
    ]

    for column in available:

        temp = df[
            [
                "_period",
                "_is_high_payout",
                column,
            ]
        ].copy()

        temp[
            column
        ] = pd.to_numeric(
            temp[column],
            errors="coerce",
        )

        temp = temp.dropna(
            subset=[column]
        )

        if temp.empty:

            continue

        grouped = (
            temp
            .groupby(
                [
                    "_period",
                    column,
                ],
                dropna=False,
            )
            .agg(
                race_count=(
                    "_is_high_payout",
                    "size",
                ),
                high_payout_count=(
                    "_is_high_payout",
                    "sum",
                ),
            )
            .reset_index()
        )

        grouped[
            "high_payout_rate_%"
        ] = (
            grouped[
                "high_payout_count"
            ]
            /
            grouped[
                "race_count"
            ]
            * 100
        )

        grouped[
            "feature_name"
        ] = column

        grouped[
            "value"
        ] = grouped[
            column
        ]

        rows.append(
            grouped[
                [
                    "_period",
                    "feature_name",
                    "value",
                    "race_count",
                    "high_payout_count",
                    "high_payout_rate_%",
                ]
            ]
        )

    if not rows:

        return pd.DataFrame()

    return pd.concat(
        rows,
        ignore_index=True,
    )


# ===========================================================
# ライン構成文字列から分布比較
# ===========================================================

def create_line_structure_from_columns(
    df,
):

    # -------------------------------------------------------
    # L1_P1 ～ L9_P9 の存在確認
    # -------------------------------------------------------

    line_columns = []

    for line_no in range(1, 10):

        for pos in range(1, 10):

            column = (
                f"L{line_no}_P{pos}_"
                "car_no"
            )

            if column in df.columns:

                line_columns.append(
                    column
                )

    # car_noがない場合は、
    # line_no / line_position等から
    #構造を取得する方式にはしない。
    #
    # 既存008のline_count等を優先する。

    return df


# ===========================================================
# AI見逃し分析
# ===========================================================

def analyze_ai_missed_high_payout(
    df,
    feature_columns,
):

    # -------------------------------------------------------
    # 2020～2022
    # 実際30,000以上
    # AI 0～9,999
    # -------------------------------------------------------

    hist_high = df[
        (
            df["_period"]
            == "2020-2022"
        )
        &
        (
            df["_is_high_payout"]
        )
    ].copy()

    missed = hist_high[
        hist_high["_ai_low"]
    ].copy()

    # -------------------------------------------------------
    # 実際高配当全体
    # vs
    # AI見逃し
    # -------------------------------------------------------

    comparison = compare_groups(
        hist_high,
        missed,
        feature_columns,
        "historical_high",
        "ai_missed_high",
    )

    return (
        hist_high,
        missed,
        comparison,
    )


# ===========================================================
# 期間ごとの高配当件数
# ===========================================================

def create_period_summary(
    df,
):

    rows = []

    for period in [
        "2020-2022",
        "2023-2026",
    ]:

        temp = df[
            df["_period"]
            == period
        ]

        total = len(
            temp
        )

        high = int(
            temp[
                "_is_high_payout"
            ].sum()
        )

        rate = (
            high
            /
            total
            * 100
            if total > 0
            else 0
        )

        rows.append(
            {
                "period":
                    period,

                "race_count":
                    total,

                "high_payout_count":
                    high,

                "high_payout_rate_%":
                    rate,
            }
        )

    return pd.DataFrame(
        rows
    )


# ===========================================================
# 高配当クラス分布
# ===========================================================

def create_ai_prediction_summary(
    df,
):

    rows = []

    hist = df[
        df["_period"]
        == "2020-2022"
    ].copy()

    high = hist[
        hist["_is_high_payout"]
    ].copy()

    if len(high) == 0:

        return pd.DataFrame()

    grouped = (
        high
        .groupby(
            "_ai_class",
            dropna=False,
        )
        .size()
        .reset_index(
            name="race_count"
        )
    )

    grouped[
        "rate_%"
    ] = (
        grouped[
            "race_count"
        ]
        /
        len(high)
        * 100
    )

    return grouped.sort_values(
        "race_count",
        ascending=False,
    )


# ===========================================================
# 3グループ比較
# ===========================================================

def create_three_group_summary(
    df,
):

    hist_high = df[
        (
            df["_period"]
            == "2020-2022"
        )
        &
        (
            df["_is_high_payout"]
        )
    ]

    train_high = df[
        (
            df["_period"]
            == "2023-2026"
        )
        &
        (
            df["_is_high_payout"]
        )
    ]

    hist_missed = hist_high[
        hist_high["_ai_low"]
    ]

    rows = []

    groups = [
        (
            "2020-2022実際高配当",
            hist_high,
        ),
        (
            "2023-2026実際高配当",
            train_high,
        ),
        (
            "2020-2022高配当AI見逃し",
            hist_missed,
        ),
    ]

    for name, group in groups:

        rows.append(
            {
                "group":
                    name,

                "race_count":
                    len(group),

                "average_payout":
                    group[
                        "_payout"
                    ].mean()
                    if len(group)
                    else np.nan,

                "median_payout":
                    group[
                        "_payout"
                    ].median()
                    if len(group)
                    else np.nan,
            }
        )

    return pd.DataFrame(
        rows
    )


# ===========================================================
# 特徴量差が大きいもの
# ===========================================================

def create_shift_summary(
    comparison_df,
):

    if comparison_df.empty:

        return pd.DataFrame()

    result = comparison_df.copy()

    result[
        "abs_mean_difference"
    ] = result[
        "mean_difference"
    ].abs()

    result[
        "abs_cohens_d"
    ] = result[
        "cohens_d"
    ].abs()

    result = result.sort_values(
        "abs_cohens_d",
        ascending=False,
    )

    result[
        "shift_rank"
    ] = range(
        1,
        len(result) + 1,
    )

    return result


# ===========================================================
# Excel保存
# ===========================================================

def save_excel(
    summary_df,
    three_group_df,
    period_structure_df,
    historical_vs_training_df,
    missed_vs_all_high_df,
    ai_prediction_summary_df,
    merged_df,
):

    log(
        "======================================="
    )

    log(
        "Excel Save"
    )

    log(
        "======================================="
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with pd.ExcelWriter(
        OUTPUT_XLSX,
        engine="openpyxl",
    ) as writer:

        summary_df.to_excel(
            writer,
            sheet_name="期間概要",
            index=False,
        )

        three_group_df.to_excel(
            writer,
            sheet_name="3グループ概要",
            index=False,
        )

        period_structure_df.to_excel(
            writer,
            sheet_name="ライン構造",
            index=False,
        )

        historical_vs_training_df.to_excel(
            writer,
            sheet_name="高配当_2020vs2023",
            index=False,
        )

        missed_vs_all_high_df.to_excel(
            writer,
            sheet_name="高配当見逃し分析",
            index=False,
        )

        ai_prediction_summary_df.to_excel(
            writer,
            sheet_name="2020高配当AI予想分布",
            index=False,
        )

        # 結合データは確認用
        merged_df.to_csv(
            OUTPUT_DIR
            / "010_merged_data.csv",
            index=False,
            encoding="utf-8-sig",
        )

    log(
        f"保存先 : {OUTPUT_XLSX}"
    )

    log(
        "Excel保存完了"
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
        "010 Historical Payout Shift Analysis"
    )

    log(
        "======================================="
    )

    # -------------------------------------------------------
    # 出力フォルダ
    # -------------------------------------------------------

    prepare_output()

    # -------------------------------------------------------
    # Prediction
    # -------------------------------------------------------

    prediction_df = (
        load_prediction_data()
    )

    # -------------------------------------------------------
    # Feature
    # -------------------------------------------------------

    feature_df = (
        load_feature_data()
    )

    # -------------------------------------------------------
    # Merge
    # -------------------------------------------------------

    merged = (
        merge_prediction_feature(
            prediction_df,
            feature_df,
        )
    )

    # -------------------------------------------------------
    # 基本ラベル
    # -------------------------------------------------------

    merged = add_basic_labels(
        merged
    )

    # -------------------------------------------------------
    # 対象期間だけ
    # -------------------------------------------------------

    merged = merged[
        merged[
            "_period"
        ].isin(
            [
                "2020-2022",
                "2023-2026",
            ]
        )
    ].copy()

    log(
        "======================================="
    )

    log(
        "対象期間フィルタ完了"
    )

    log(
        f"2020-2022 : "
        f"{(
            merged['_period']
            == '2020-2022'
        ).sum():,}"
    )

    log(
        f"2023-2026 : "
        f"{(
            merged['_period']
            == '2023-2026'
        ).sum():,}"
    )

    print()

    # -------------------------------------------------------
    # Feature columns
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

    print()

    # -------------------------------------------------------
    # 期間概要
    # -------------------------------------------------------

    summary_df = (
        create_period_summary(
            merged
        )
    )

    # -------------------------------------------------------
    # 3グループ概要
    # -------------------------------------------------------

    three_group_df = (
        create_three_group_summary(
            merged
        )
    )

    # -------------------------------------------------------
    # ライン構造
    # -------------------------------------------------------

    period_structure_df = (
        analyze_line_structure(
            merged
        )
    )

    # -------------------------------------------------------
    # 高配当
    # 2020～2022 vs 2023～2026
    # -------------------------------------------------------

    historical_high = merged[
        (
            merged["_period"]
            == "2020-2022"
        )
        &
        (
            merged[
                "_is_high_payout"
            ]
        )
    ].copy()

    training_high = merged[
        (
            merged["_period"]
            == "2023-2026"
        )
        &
        (
            merged[
                "_is_high_payout"
            ]
        )
    ].copy()

    log(
        "======================================="
    )

    log(
        "高配当 2020～2022 vs 2023～2026"
    )

    log(
        f"2020～2022 : "
        f"{len(historical_high):,}"
    )

    log(
        f"2023～2026 : "
        f"{len(training_high):,}"
    )

    print()

    historical_vs_training_df = (
        compare_groups(
            historical_high,
            training_high,
            feature_columns,
            "2020_2022_high",
            "2023_2026_high",
        )
    )

    historical_vs_training_df = (
        create_shift_summary(
            historical_vs_training_df
        )
    )

    # -------------------------------------------------------
    # AI見逃し
    # -------------------------------------------------------

    (
        hist_high,
        missed_high,
        missed_vs_all_high_df,
    ) = analyze_ai_missed_high_payout(
        merged,
        feature_columns,
    )

    # -------------------------------------------------------
    # AI予想分布
    # -------------------------------------------------------

    ai_prediction_summary_df = (
        create_ai_prediction_summary(
            merged
        )
    )

    # -------------------------------------------------------
    # 保存
    # -------------------------------------------------------

    save_excel(
        summary_df,
        three_group_df,
        period_structure_df,
        historical_vs_training_df,
        missed_vs_all_high_df,
        ai_prediction_summary_df,
        merged,
    )

    # -------------------------------------------------------
    # コンソール
    # -------------------------------------------------------

    print()

    log(
        "======================================="
    )

    log(
        "010 Summary"
    )

    log(
        "======================================="
    )

    print(
        summary_df.to_string(
            index=False
        )
    )

    print()

    print(
        "===== 2020～2022高配当 vs "
        "2023～2026高配当 TOP20 ====="
    )

    if not historical_vs_training_df.empty:

        display_columns = [
            "shift_rank",
            "feature",
            "2020_2022_high_count",
            "2023_2026_high_count",
            "2020_2022_high_mean",
            "2023_2026_high_mean",
            "mean_difference",
            "cohens_d",
            "effect_strength",
        ]

        display_columns = [
            c
            for c in display_columns
            if c in (
                historical_vs_training_df.columns
            )
        ]

        print(
            historical_vs_training_df[
                display_columns
            ]
            .head(20)
            .to_string(
                index=False
            )
        )

    print()

    print(
        "===== 2020～2022高配当 "
        "AI見逃し TOP20 ====="
    )

    if not missed_vs_all_high_df.empty:

        display_columns = [
            "rank",
            "feature",
            "historical_high_count",
            "ai_missed_high_count",
            "historical_high_mean",
            "ai_missed_high_mean",
            "mean_difference",
            "cohens_d",
            "effect_strength",
        ]

        display_columns = [
            c
            for c in display_columns
            if c in (
                missed_vs_all_high_df.columns
            )
        ]

        print(
            missed_vs_all_high_df[
                display_columns
            ]
            .head(20)
            .to_string(
                index=False
            )
        )

    print()

    log(
        "010 Complete"
    )

    print()


# ===========================================================
# 実行
# ===========================================================

if __name__ == "__main__":

    main()