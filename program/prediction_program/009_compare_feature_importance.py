"""
===========================================================
競輪AI Ver1.0
009_compare_feature_importance.py

007 高配当特徴量分析
        +
LightGBM 実 Feature Importance
        +
feature_columns.json
        ↓
特徴量の統合分析

【役割】

007_high_payout_analysis.xlsx
        ↓
高配当との関連性
・AUC
・AUC識別力
・Cohen's d
・平均差

        ＋

lightgbm_model.pkl
        ↓
LightGBM実 Feature Importance

        ＋

feature_columns.json
        ↓
学習時特徴量一覧

        ↓

「高配当と関連する特徴量を
 AIが実際にどの程度利用しているか」
を確認する

【重要】

・モデル変更なし
・再学習なし
・特徴量変更なし
・予測処理なし
・分析のみ

===========================================================
"""

import os
import json
import joblib
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

MODEL_DIR = (
    BASE
    / "model"
)

ANALYSIS_DIR = (
    BASE
    / "csv"
    / "analysis"
    / "high_payout"
)

OUTPUT_DIR = (
    BASE
    / "csv"
    / "analysis"
    / "feature_importance"
)

MODEL_FILE = (
    MODEL_DIR
    / "lightgbm_model.pkl"
)

FEATURE_FILE = (
    MODEL_DIR
    / "feature_columns.json"
)

# 既存のfeature importance CSV
FEATURE_IMPORTANCE_CSV = (
    MODEL_DIR
    / "feature_importance.csv"
)

# 007のExcel
HIGH_PAYOUT_PATTERN = (
    "007_high_payout_analysis(2023.1.1~2026.7.30)*.xlsx"
)

OUTPUT_XLSX = (
    OUTPUT_DIR
    / "009_feature_importance_analysis(2023.1.1~2026.7.30).xlsx"
)


# ===========================================================
# 設定
# ===========================================================

# 007で使用している主要シート
ANALYSIS_SHEETS = [
    "全体比較",
    "高配当見逃し比較",
    "30_000以上",
    "50_000以上",
    "100_000以上",
]


# ===========================================================
# ログ
# ===========================================================

def log(message):

    print(
        f"[009_compare_feature_importance] "
        f"{message}"
    )


# ===========================================================
# フォルダ準備
# ===========================================================

def prepare_output():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


# ===========================================================
# モデル読込
# ===========================================================

def load_model():

    log("=======================================")
    log("LightGBM Model Load")
    log("=======================================")

    if not MODEL_FILE.exists():

        raise FileNotFoundError(
            f"LightGBMモデルがありません:\n"
            f"{MODEL_FILE}"
        )

    model = joblib.load(
        MODEL_FILE
    )

    log(
        f"Model : {MODEL_FILE}"
    )

    print()

    return model


# ===========================================================
# feature_columns読込
# ===========================================================

def load_feature_columns():

    log("=======================================")
    log("feature_columns.json Load")
    log("=======================================")

    if not FEATURE_FILE.exists():

        raise FileNotFoundError(
            f"feature_columns.json がありません:\n"
            f"{FEATURE_FILE}"
        )

    with open(
        FEATURE_FILE,
        "r",
        encoding="utf-8",
    ) as f:

        feature_columns = json.load(f)

    if not isinstance(
        feature_columns,
        list,
    ):

        raise ValueError(
            "feature_columns.json が "
            "list形式ではありません。"
        )

    log(
        f"Feature Columns : "
        f"{len(feature_columns):,}"
    )

    print()

    return feature_columns


# ===========================================================
# LightGBM実Feature Importance取得
# ===========================================================

def load_model_feature_importance(
    model,
    feature_columns,
):

    log("=======================================")
    log("LightGBM Feature Importance")
    log("=======================================")

    # -------------------------------------------------------
    # feature_importances_
    # -------------------------------------------------------

    if not hasattr(
        model,
        "feature_importances_",
    ):

        raise AttributeError(
            "モデルに feature_importances_ がありません。"
        )

    importance = np.asarray(
        model.feature_importances_
    )

    log(
        f"Model Importance Count : "
        f"{len(importance):,}"
    )

    log(
        f"feature_columns Count  : "
        f"{len(feature_columns):,}"
    )

    # -------------------------------------------------------
    # 数が一致するか確認
    # -------------------------------------------------------

    if len(importance) != len(
        feature_columns
    ):

        raise ValueError(
            "\n"
            "LightGBMのFeature Importance数と\n"
            "feature_columns.jsonの列数が一致しません。\n"
            f"Importance : {len(importance)}\n"
            f"Features   : {len(feature_columns)}"
        )

    # -------------------------------------------------------
    # Boosterのfeature name確認
    # -------------------------------------------------------

    booster_names = []

    try:

        booster_names = list(
            model.booster_.feature_name()
        )

    except Exception:

        booster_names = []

    # -------------------------------------------------------
    # DataFrame作成
    # -------------------------------------------------------

    result = pd.DataFrame(
        {
            "feature": feature_columns,
            "lightgbm_importance": importance,
        }
    )

    # -------------------------------------------------------
    # Booster名
    # -------------------------------------------------------

    if len(booster_names) == len(
        feature_columns
    ):

        result[
            "booster_feature_name"
        ] = booster_names

        result[
            "feature_name_match"
        ] = (
            result["feature"]
            ==
            result["booster_feature_name"]
        )

    else:

        result[
            "booster_feature_name"
        ] = ""

        result[
            "feature_name_match"
        ] = ""

    # -------------------------------------------------------
    # Importance割合
    # -------------------------------------------------------

    total_importance = (
        result[
            "lightgbm_importance"
        ].sum()
    )

    if total_importance > 0:

        result[
            "importance_rate_%"
        ] = (
            result[
                "lightgbm_importance"
            ]
            / total_importance
            * 100
        )

    else:

        result[
            "importance_rate_%"
        ] = 0

    # -------------------------------------------------------
    # 順位
    # -------------------------------------------------------

    result[
        "importance_rank"
    ] = (
        result[
            "lightgbm_importance"
        ]
        .rank(
            method="min",
            ascending=False,
        )
        .astype(int)
    )

    result = result.sort_values(
        [
            "importance_rank",
            "feature",
        ],
        ascending=[
            True,
            True,
        ],
    )

    result = result.reset_index(
        drop=True
    )

    log(
        "Feature Importance取得完了"
    )

    print()

    return result


# ===========================================================
# 既存feature_importance.csv読込
# ===========================================================

def load_existing_importance():

    log("=======================================")
    log("Existing feature_importance.csv")
    log("=======================================")

    if not FEATURE_IMPORTANCE_CSV.exists():

        log(
            "feature_importance.csv はありません。"
        )

        print()

        return pd.DataFrame()

    df = pd.read_csv(
        FEATURE_IMPORTANCE_CSV,
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
# 007 Excel一覧取得
# ===========================================================

def get_high_payout_files():

    log("=======================================")
    log("007 High Payout Excel Search")
    log("=======================================")

    files = sorted(
        ANALYSIS_DIR.glob(
            HIGH_PAYOUT_PATTERN
        )
    )

    if len(files) == 0:

        raise FileNotFoundError(
            "\n"
            "007_high_payout_analysis*.xlsx "
            "が見つかりません。\n"
            f"検索先:\n{ANALYSIS_DIR}"
        )

    for file in files:

        log(
            f"発見 : {file.name}"
        )

    log(
        f"007 Excel : {len(files):,} 件"
    )

    print()

    return files


# ===========================================================
# 007 Excel読込
# ===========================================================

def load_007_analysis():

    files = get_high_payout_files()

    all_rows = []

    for file in files:

        log("=======================================")

        log(
            f"007読込 : {file.name}"
        )

        try:

            excel = pd.ExcelFile(
                file,
                engine="openpyxl",
            )

        except Exception as e:

            log(
                f"Excel読込失敗 : {e}"
            )

            continue

        for sheet_name in ANALYSIS_SHEETS:

            if sheet_name not in (
                excel.sheet_names
            ):

                continue

            log(
                f"Sheet : {sheet_name}"
            )

            df = pd.read_excel(
                file,
                sheet_name=sheet_name,
                engine="openpyxl",
            )

            if df.empty:

                continue

            if "feature" not in df.columns:

                log(
                    f"feature列なし : "
                    f"{sheet_name}"
                )

                continue

            work = df.copy()

            work[
                "analysis_file"
            ] = file.name

            work[
                "analysis_sheet"
            ] = sheet_name

            all_rows.append(
                work
            )

    if len(all_rows) == 0:

        raise ValueError(
            "007 Excelから "
            "feature列を持つ分析結果を取得できませんでした。"
        )

    result = pd.concat(
        all_rows,
        ignore_index=True,
    )

    log(
        f"007分析行数 : "
        f"{len(result):,}"
    )

    log(
        f"007特徴量数 : "
        f"{result['feature'].nunique():,}"
    )

    print()

    return result


# ===========================================================
# 007 × LightGBM 結合
# ===========================================================

def merge_analysis(
    importance_df,
    analysis_df,
):

    log("=======================================")
    log("007 × LightGBM Importance")
    log("=======================================")

    importance = importance_df.copy()

    analysis = analysis_df.copy()

    importance[
        "feature"
    ] = (
        importance["feature"]
        .astype(str)
        .str.strip()
    )

    analysis[
        "feature"
    ] = (
        analysis["feature"]
        .astype(str)
        .str.strip()
    )

    # -------------------------------------------------------
    # 007の同一featureをまとめる
    # -------------------------------------------------------

    grouped = (
        analysis
        .groupby(
            "feature",
            as_index=False,
        )
        .agg(
            payout_analysis_count=(
                "analysis_sheet",
                "count",
            ),
            max_auc_strength=(
                "auc_strength",
                "max",
            ),
            mean_auc_strength=(
                "auc_strength",
                "mean",
            ),
            max_auc=(
                "auc",
                "max",
            ),
            min_auc=(
                "auc",
                "min",
            ),
            max_cohens_d=(
                "cohens_d",
                lambda x: np.nanmax(
                    pd.to_numeric(
                        x,
                        errors="coerce",
                    )
                ),
            ),
        )
    )

    # -------------------------------------------------------
    # AUCが存在しない場合の安全処理
    # -------------------------------------------------------

    for column in [
        "max_auc_strength",
        "mean_auc_strength",
        "max_auc",
        "min_auc",
        "max_cohens_d",
    ]:

        if column not in grouped.columns:

            grouped[column] = np.nan

    # -------------------------------------------------------
    # 結合
    # -------------------------------------------------------

    merged = importance.merge(
        grouped,
        on="feature",
        how="left",
    )

    # -------------------------------------------------------
    # 007に存在するか
    # -------------------------------------------------------

    merged[
        "007_analysis_match"
    ] = (
        merged[
            "payout_analysis_count"
        ]
        .fillna(0)
        > 0
    )

    # -------------------------------------------------------
    # AUC強度順位
    # -------------------------------------------------------

    merged[
        "payout_auc_rank"
    ] = np.nan

    valid_auc = (
        merged[
            "max_auc_strength"
        ]
        .notna()
    )

    if valid_auc.any():

        merged.loc[
            valid_auc,
            "payout_auc_rank",
        ] = (
            merged.loc[
                valid_auc,
                "max_auc_strength",
            ]
            .rank(
                method="min",
                ascending=False,
            )
        )

    # -------------------------------------------------------
    # AI重要度順位
    # -------------------------------------------------------

    merged[
        "importance_rank"
    ] = (
        merged[
            "importance_rank"
        ]
        .astype(int)
    )

    # -------------------------------------------------------
    # 総合的な見方
    #
    # 高配当関連が強い
    # +
    # AI重要度が高い
    #
    # を優先
    # -------------------------------------------------------

    merged[
        "importance_percentile"
    ] = (
        1
        -
        (
            merged[
                "importance_rank"
            ]
            - 1
        )
        /
        max(
            len(merged) - 1,
            1,
        )
    ) * 100

    # -------------------------------------------------------
    # 高配当関連強度
    # -------------------------------------------------------

    merged[
        "payout_strength_percentile"
    ] = np.nan

    valid = (
        merged[
            "max_auc_strength"
        ]
        .notna()
    )

    if valid.any():

        auc_rank = (
            merged.loc[
                valid,
                "max_auc_strength",
            ]
            .rank(
                method="average",
                ascending=True,
                pct=True,
            )
        )

        merged.loc[
            valid,
            "payout_strength_percentile",
        ] = auc_rank * 100

    # -------------------------------------------------------
    # 総合スコア
    #
    # AI重要度50%
    # 高配当関連50%
    # -------------------------------------------------------

    merged[
        "combined_score"
    ] = (
        merged[
            "importance_percentile"
        ].fillna(0)
        * 0.5
        +
        merged[
            "payout_strength_percentile"
        ].fillna(0)
        * 0.5
    )

    merged = merged.sort_values(
        [
            "007_analysis_match",
            "combined_score",
            "lightgbm_importance",
        ],
        ascending=[
            False,
            False,
            False,
        ],
    )

    merged = merged.reset_index(
        drop=True
    )

    merged.insert(
        0,
        "combined_rank",
        range(
            1,
            len(merged) + 1,
        ),
    )

    log(
        "結合完了"
    )

    log(
        f"結合特徴量 : "
        f"{merged['007_analysis_match'].sum():,}"
    )

    print()

    return merged


# ===========================================================
# 007に存在するがモデルで重要度0の特徴量
# ===========================================================

def analyze_007_unimportant(
    merged_df,
):

    result = merged_df[
        merged_df[
            "007_analysis_match"
        ]
        &
        (
            merged_df[
                "lightgbm_importance"
            ]
            <= 0
        )
    ].copy()

    result = result.sort_values(
        [
            "max_auc_strength",
            "max_cohens_d",
        ],
        ascending=[
            False,
            False,
        ],
    )

    return result


# ===========================================================
# モデル重要度上位
# ===========================================================

def analyze_top_importance(
    importance_df,
    top_n=100,
):

    result = (
        importance_df
        .sort_values(
            "lightgbm_importance",
            ascending=False,
        )
        .head(top_n)
        .copy()
    )

    return result


# ===========================================================
# 007に存在しないモデル特徴量
# ===========================================================

def analyze_model_only(
    merged_df,
):

    result = merged_df[
        ~merged_df[
            "007_analysis_match"
        ]
    ].copy()

    result = result.sort_values(
        "lightgbm_importance",
        ascending=False,
    )

    return result


# ===========================================================
# 007高配当関連 × AI重要度 上位
# ===========================================================

def analyze_high_value_features(
    merged_df,
    top_n=100,
):

    result = merged_df[
        merged_df[
            "007_analysis_match"
        ]
    ].copy()

    result = result.sort_values(
        [
            "combined_score",
            "max_auc_strength",
            "lightgbm_importance",
        ],
        ascending=[
            False,
            False,
            False,
        ],
    )

    result = result.head(
        top_n
    )

    return result


# ===========================================================
# feature_columns整合性確認
# ===========================================================

def build_feature_check(
    model,
    feature_columns,
    importance_df,
):

    rows = []

    # -------------------------------------------------------
    # feature_columns数
    # -------------------------------------------------------

    rows.append(
        {
            "項目":
                "feature_columns数",
            "値":
                len(feature_columns),
            "判定":
                "OK",
        }
    )

    # -------------------------------------------------------
    # model importance数
    # -------------------------------------------------------

    rows.append(
        {
            "項目":
                "LightGBM Importance数",
            "値":
                len(
                    importance_df
                ),
            "判定":
                "OK"
                if len(importance_df)
                ==
                len(feature_columns)
                else "NG",
        }
    )

    # -------------------------------------------------------
    # feature name一致
    # -------------------------------------------------------

    if (
        "feature_name_match"
        in importance_df.columns
    ):

        match_count = int(
            importance_df[
                "feature_name_match"
            ].sum()
        )

        total = len(
            importance_df
        )

        rows.append(
            {
                "項目":
                    "Booster Feature Name一致",
                "値":
                    f"{match_count}/{total}",
                "判定":
                    "OK"
                    if match_count == total
                    else "NG",
            }
        )

    # -------------------------------------------------------
    # Importance合計
    # -------------------------------------------------------

    total_importance = (
        importance_df[
            "lightgbm_importance"
        ].sum()
    )

    rows.append(
        {
            "項目":
                "Importance合計",
            "値":
                total_importance,
            "判定":
                "OK"
                if total_importance > 0
                else "NG",
        }
    )

    # -------------------------------------------------------
    # Importance > 0
    # -------------------------------------------------------

    positive_count = int(
        (
            importance_df[
                "lightgbm_importance"
            ]
            > 0
        ).sum()
    )

    rows.append(
        {
            "項目":
                "Importance > 0 特徴量数",
            "値":
                positive_count,
            "判定":
                "OK",
        }
    )

    return pd.DataFrame(
        rows
    )


# ===========================================================
# 既存CSVとの比較
# ===========================================================

def compare_existing_importance(
    model_df,
    existing_df,
):

    if existing_df.empty:

        return pd.DataFrame()

    # -------------------------------------------------------
    # feature列確認
    # -------------------------------------------------------

    feature_column = None

    for column in [
        "feature",
        "Feature",
        "feature_name",
        "Feature Name",
    ]:

        if column in existing_df.columns:

            feature_column = column
            break

    if feature_column is None:

        return pd.DataFrame(
            [
                {
                    "判定":
                        "既存CSVにfeature列がありません",
                }
            ]
        )

    # -------------------------------------------------------
    # importance列確認
    # -------------------------------------------------------

    importance_column = None

    for column in [
        "importance",
        "feature_importance",
        "Feature Importance",
        "gain",
        "split",
    ]:

        if column in existing_df.columns:

            importance_column = column
            break

    if importance_column is None:

        return pd.DataFrame(
            [
                {
                    "判定":
                        "既存CSVにimportance列がありません",
                }
            ]
        )

    old = existing_df[
        [
            feature_column,
            importance_column,
        ]
    ].copy()

    old.columns = [
        "feature",
        "existing_importance",
    ]

    old[
        "feature"
    ] = (
        old["feature"]
        .astype(str)
        .str.strip()
    )

    old[
        "existing_importance"
    ] = pd.to_numeric(
        old[
            "existing_importance"
        ],
        errors="coerce",
    )

    result = model_df[
        [
            "feature",
            "lightgbm_importance",
        ]
    ].merge(
        old,
        on="feature",
        how="outer",
    )

    result[
        "importance_difference"
    ] = (
        result[
            "lightgbm_importance"
        ]
        -
        result[
            "existing_importance"
        ]
    )

    result[
        "importance_match"
    ] = np.isclose(
        result[
            "lightgbm_importance"
        ].fillna(0),
        result[
            "existing_importance"
        ].fillna(0),
        equal_nan=True,
    )

    return result


# ===========================================================
# Excel保存
# ===========================================================

def save_excel(
    feature_check_df,
    importance_df,
    merged_df,
    high_value_df,
    top_importance_df,
    model_only_df,
    unimportant_df,
    existing_compare_df,
    analysis_df,
):

    log("=======================================")
    log("009 Excel Save")
    log("=======================================")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with pd.ExcelWriter(
        OUTPUT_XLSX,
        engine="openpyxl",
    ) as writer:

        # ---------------------------------------------------
        # 1
        # ---------------------------------------------------

        feature_check_df.to_excel(
            writer,
            sheet_name="整合性確認",
            index=False,
        )

        # ---------------------------------------------------
        # 2
        # ---------------------------------------------------

        importance_df.to_excel(
            writer,
            sheet_name="LightGBM重要度",
            index=False,
        )

        # ---------------------------------------------------
        # 3
        # ---------------------------------------------------

        merged_df.to_excel(
            writer,
            sheet_name="007×AI重要度",
            index=False,
        )

        # ---------------------------------------------------
        # 4
        # ---------------------------------------------------

        high_value_df.to_excel(
            writer,
            sheet_name="高配当関連×AI上位",
            index=False,
        )

        # ---------------------------------------------------
        # 5
        # ---------------------------------------------------

        top_importance_df.to_excel(
            writer,
            sheet_name="AI重要度TOP100",
            index=False,
        )

        # ---------------------------------------------------
        # 6
        # ---------------------------------------------------

        model_only_df.to_excel(
            writer,
            sheet_name="007未分析特徴量",
            index=False,
        )

        # ---------------------------------------------------
        # 7
        # ---------------------------------------------------

        unimportant_df.to_excel(
            writer,
            sheet_name="007関連だが重要度0",
            index=False,
        )

        # ---------------------------------------------------
        # 8
        # ---------------------------------------------------

        if not existing_compare_df.empty:

            existing_compare_df.to_excel(
                writer,
                sheet_name="既存Importance比較",
                index=False,
            )

        # ---------------------------------------------------
        # 9
        # ---------------------------------------------------

        analysis_df.to_excel(
            writer,
            sheet_name="007分析元データ",
            index=False,
        )

    log(
        f"保存先 : {OUTPUT_XLSX}"
    )

    print()

    log(
        "Excel保存完了"
    )


# ===========================================================
# Main
# ===========================================================

def main():

    print()

    log("=======================================")
    log("009 Feature Importance Analysis")
    log("=======================================")

    # -------------------------------------------------------
    # 出力フォルダ
    # -------------------------------------------------------

    prepare_output()

    # -------------------------------------------------------
    # Model
    # -------------------------------------------------------

    model = load_model()

    # -------------------------------------------------------
    # feature_columns
    # -------------------------------------------------------

    feature_columns = (
        load_feature_columns()
    )

    # -------------------------------------------------------
    # LightGBM実Importance
    # -------------------------------------------------------

    importance_df = (
        load_model_feature_importance(
            model,
            feature_columns,
        )
    )

    # -------------------------------------------------------
    # 既存CSV
    # -------------------------------------------------------

    existing_df = (
        load_existing_importance()
    )

    # -------------------------------------------------------
    # 007
    # -------------------------------------------------------

    analysis_df = (
        load_007_analysis()
    )

    # -------------------------------------------------------
    # 007 × Importance
    # -------------------------------------------------------

    merged_df = merge_analysis(
        importance_df,
        analysis_df,
    )

    # -------------------------------------------------------
    # 高配当関連 × AI重要度
    # -------------------------------------------------------

    high_value_df = (
        analyze_high_value_features(
            merged_df,
            top_n=100,
        )
    )

    # -------------------------------------------------------
    # AI重要度TOP100
    # -------------------------------------------------------

    top_importance_df = (
        analyze_top_importance(
            importance_df,
            top_n=100,
        )
    )

    # -------------------------------------------------------
    # 007にあるがAI重要度0
    # -------------------------------------------------------

    unimportant_df = (
        analyze_007_unimportant(
            merged_df,
        )
    )

    # -------------------------------------------------------
    # 007で分析されていない特徴量
    # -------------------------------------------------------

    model_only_df = (
        analyze_model_only(
            merged_df,
        )
    )

    # -------------------------------------------------------
    # feature_columns整合性
    # -------------------------------------------------------

    feature_check_df = (
        build_feature_check(
            model,
            feature_columns,
            importance_df,
        )
    )

    # -------------------------------------------------------
    # 既存CSVとの比較
    # -------------------------------------------------------

    existing_compare_df = (
        compare_existing_importance(
            importance_df,
            existing_df,
        )
    )

    # -------------------------------------------------------
    # Excel
    # -------------------------------------------------------

    save_excel(
        feature_check_df,
        importance_df,
        merged_df,
        high_value_df,
        top_importance_df,
        model_only_df,
        unimportant_df,
        existing_compare_df,
        analysis_df,
    )

    # -------------------------------------------------------
    # コンソール結果
    # -------------------------------------------------------

    print()
    log("=======================================")
    log("009 Summary")
    log("=======================================")

    print(
        f"feature_columns : "
        f"{len(feature_columns):,}"
    )

    print(
        f"AI Importance   : "
        f"{len(importance_df):,}"
    )

    print(
        "007 Features    : "
        f"{analysis_df['feature'].nunique():,}"
    )

    print(
        f"007 × AI Match  : "
        f"{merged_df['007_analysis_match'].sum():,}"
    )

    positive_importance_count = int(
        (
            importance_df[
                "lightgbm_importance"
            ] > 0
        ).sum()
    )

    print(
        f"AI Importance >0: "
        f"{positive_importance_count:,}"
    )

    print(
        f"007関連 & AI重要度0 : "
        f"{len(unimportant_df):,}"
    )

    print()

    print(
        "===== 高配当関連 × AI重要度 TOP20 ====="
    )

    display_columns = [
        "combined_rank",
        "feature",
        "lightgbm_importance",
        "importance_rank",
        "max_auc",
        "max_auc_strength",
        "max_cohens_d",
        "combined_score",
    ]

    available_columns = [
        c
        for c in display_columns
        if c in high_value_df.columns
    ]

    print(
        high_value_df[
            available_columns
        ].head(20).to_string(
            index=False
        )
    )

    print()

    log(
        "009 Complete"
    )

    print()


# ===========================================================
# 実行
# ===========================================================

if __name__ == "__main__":

    main()