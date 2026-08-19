"""
===========================================================
競輪AI Ver1.0
015_analyze_payout_class_candidates.py

払戻クラス最適化分析

【目的】

014で確認した1,000円単位の払戻分布を基に、

・5クラス
・6クラス
・7クラス
・8クラス
・10クラス

の候補を比較し、

「AI学習用の払戻クラスとして、どのクラス数・境界が
  2020～2022 / 2023～2026 の両期間で安定しているか」

を調査する。

※このコードではAIモデルを変更しない
※学習CSVを書き換えない
※クラス定義を決定するための調査のみ行う
===========================================================
"""

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

TRAINING_DIR = BASE / "csv" / "training"

ANALYSIS_DIR = (
    BASE
    / "csv"
    / "analysis"
    / "payout_distribution"
)

PREDICTION_OLD = (
    TRAINING_DIR
    / "training_prediction(2020.1.1~2022.12.31).csv"
)

PREDICTION_NEW = (
    TRAINING_DIR
    / "training_prediction(2023.1.1~2026.7.30).csv"
)

OUTPUT_XLSX = (
    ANALYSIS_DIR
    / "015_payout_class_candidates.xlsx"
)


# ===========================================================
# ログ
# ===========================================================

def log(message):
    print(
        f"[015_analyze_payout_class_candidates] {message}"
    )


# ===========================================================
# CSV読込
# ===========================================================

def load_csv(path):

    if not path.exists():
        raise FileNotFoundError(
            f"CSVがありません:\n{path}"
        )

    df = pd.read_csv(
        path,
        encoding="utf-8-sig",
        low_memory=False,
    )

    log(f"読込 : {path}")
    log(f"Rows    : {len(df):,}")
    log(f"Columns : {len(df.columns):,}")

    return df


# ===========================================================
# 払戻列検出
# ===========================================================

def find_payout_column(df):

    candidates = [
        "三連単\n払戻",
        "三連単払戻",
        "三連単 払戻",
        "三連単払戻金",
        "trifecta_payout",
    ]

    for column in candidates:
        if column in df.columns:
            return column

    raise KeyError(
        "三連単払戻列が見つかりません。\n"
        f"候補 : {candidates}\n"
        f"Columns : {list(df.columns)}"
    )


# ===========================================================
# 払戻データ準備
# ===========================================================

def prepare_payout(df):

    payout_column = find_payout_column(df)

    work = pd.DataFrame()

    work["払戻"] = pd.to_numeric(
        df[payout_column],
        errors="coerce",
    )

    work = work[
        work["払戻"].notna()
    ].copy()

    work = work[
        work["払戻"] >= 0
    ].copy()

    return work


# ===========================================================
# クラス境界候補
#
# 境界は「上限値」で定義。
# 例:
# [0, 3000, 10000, 30000, inf]
# =>
# 0～2,999
# 3,000～9,999
# 10,000～29,999
# 30,000以上
# ===========================================================

CLASS_CANDIDATES = {

    5: [
        0,
        3000,
        10000,
        30000,
        100000,
        float("inf"),
    ],

    6: [
        0,
        3000,
        10000,
        20000,
        30000,
        100000,
        float("inf"),
    ],

    7: [
        0,
        3000,
        10000,
        20000,
        30000,
        50000,
        100000,
        float("inf"),
    ],

    8: [
        0,
        2000,
        5000,
        10000,
        20000,
        30000,
        50000,
        100000,
        float("inf"),
    ],

    10: [
        0,
        1000,
        3000,
        5000,
        10000,
        20000,
        30000,
        50000,
        100000,
        200000,
        float("inf"),
    ],
}


# ===========================================================
# クラスラベル
# ===========================================================

def make_class_label(lower, upper):

    if upper == float("inf"):
        return f"{lower:,}円以上"

    return (
        f"{lower:,}～{int(upper) - 1:,}円"
    )


# ===========================================================
# クラス分析
# ===========================================================

def analyze_classes(df, period_name, class_count, boundaries):

    work = prepare_payout(df)

    rows = []

    total = len(work)

    for class_no in range(class_count):

        lower = boundaries[class_no]
        upper = boundaries[class_no + 1]

        if upper == float("inf"):
            mask = work["払戻"] >= lower
        else:
            mask = (
                (work["払戻"] >= lower)
                & (work["払戻"] < upper)
            )

        count = int(mask.sum())

        rate = (
            count / total * 100
            if total > 0
            else 0
        )

        if count > 0:
            mean_payout = float(
                work.loc[mask, "払戻"].mean()
            )
            median_payout = float(
                work.loc[mask, "払戻"].median()
            )
        else:
            mean_payout = np.nan
            median_payout = np.nan

        rows.append(
            {
                "期間": period_name,
                "クラス数": class_count,
                "Class": class_no,
                "払戻クラス": make_class_label(
                    lower,
                    upper,
                ),
                "下限": lower,
                "上限": (
                    np.nan
                    if upper == float("inf")
                    else upper
                ),
                "件数": count,
                "割合(%)": round(rate, 4),
                "平均払戻": round(
                    mean_payout,
                    0,
                ) if not np.isnan(mean_payout) else np.nan,
                "中央値払戻": round(
                    median_payout,
                    0,
                ) if not np.isnan(median_payout) else np.nan,
            }
        )

    result = pd.DataFrame(rows)

    return result


# ===========================================================
# 期間安定性・バランス評価
# ===========================================================

def evaluate_candidate(
    old_result,
    new_result,
    class_count,
):

    merged = pd.merge(
        old_result[
            [
                "Class",
                "払戻クラス",
                "件数",
                "割合(%)",
            ]
        ],
        new_result[
            [
                "Class",
                "件数",
                "割合(%)",
            ]
        ],
        on="Class",
        how="outer",
        suffixes=(
            "_2020_2022",
            "_2023_2026",
        ),
    )

    merged["割合差(pp)"] = (
        merged["割合(%)_2023_2026"]
        - merged["割合(%)_2020_2022"]
    ).round(4)

    merged["絶対割合差(pp)"] = (
        merged["割合差(pp)"]
        .abs()
        .round(4)
    )

    # 期間間の分布差
    total_distribution_shift = (
        merged["絶対割合差(pp)"].sum()
        / 2
    )

    max_distribution_shift = (
        merged["絶対割合差(pp)"].max()
    )

    # クラス件数バランス
    old_rates = old_result["割合(%)"].to_numpy()
    new_rates = new_result["割合(%)"].to_numpy()

    old_min = float(old_rates.min())
    new_min = float(new_rates.min())

    old_max = float(old_rates.max())
    new_max = float(new_rates.max())

    old_balance = old_min / old_max if old_max > 0 else 0
    new_balance = new_min / new_max if new_max > 0 else 0

    # 最小クラスが極端に小さい場合を確認
    min_rate = min(old_min, new_min)

    # 評価用の単純スコア
    # ・期間差が小さいほど良い
    # ・クラス間バランスが良いほど良い
    balance_score = (
        (old_balance + new_balance) / 2
    )

    stability_score = max(
        0,
        100 - total_distribution_shift
    )

    evaluation_score = (
        stability_score * 0.7
        + balance_score * 100 * 0.3
    )

    summary = {
        "クラス数": class_count,
        "期間分布差合計(pp)": round(
            total_distribution_shift,
            4,
        ),
        "最大クラス差(pp)": round(
            max_distribution_shift,
            4,
        ),
        "2020～2022_最小クラス割合(%)":
            round(old_min, 4),
        "2023～2026_最小クラス割合(%)":
            round(new_min, 4),
        "2020～2022_最大クラス割合(%)":
            round(old_max, 4),
        "2023～2026_最大クラス割合(%)":
            round(new_max, 4),
        "2020～2022_バランス比":
            round(old_balance, 4),
        "2023～2026_バランス比":
            round(new_balance, 4),
        "最小クラス割合(%)":
            round(min_rate, 4),
        "評価スコア":
            round(evaluation_score, 4),
    }

    return (
        pd.DataFrame([summary]),
        merged,
    )


# ===========================================================
# 高配当分離確認
# ===========================================================

def create_high_payout_check(
    class_results,
):

    rows = []

    thresholds = [
        30000,
        50000,
        100000,
        200000,
    ]

    for class_count, result in class_results.items():

        for threshold in thresholds:

            target = result[
                result["下限"] >= threshold
            ]

            rows.append(
                {
                    "クラス数": class_count,
                    "高配当基準": f"{threshold:,}円以上",
                    "該当Class数": len(target),
                    "該当クラス":
                        ",".join(
                            target["Class"]
                            .astype(str)
                            .tolist()
                        ),
                }
            )

    return pd.DataFrame(rows)


# ===========================================================
# クラス定義一覧
# ===========================================================

def create_definition_table():

    rows = []

    for class_count, boundaries in CLASS_CANDIDATES.items():

        for class_no in range(class_count):

            lower = boundaries[class_no]
            upper = boundaries[class_no + 1]

            rows.append(
                {
                    "クラス数": class_count,
                    "Class": class_no,
                    "払戻クラス":
                        make_class_label(
                            lower,
                            upper,
                        ),
                    "下限": lower,
                    "上限":
                        np.nan
                        if upper == float("inf")
                        else upper,
                }
            )

    return pd.DataFrame(rows)


# ===========================================================
# Excel保存
# ===========================================================

def save_excel(
    all_results,
    evaluations,
    cross_summaries,
    high_check,
    definitions,
):

    ANALYSIS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    log("=======================================")
    log("Excel保存")
    log("=======================================")

    with pd.ExcelWriter(
        OUTPUT_XLSX,
        engine="openpyxl",
    ) as writer:

        evaluations.to_excel(
            writer,
            sheet_name="候補比較",
            index=False,
        )

        definitions.to_excel(
            writer,
            sheet_name="クラス定義",
            index=False,
        )

        high_check.to_excel(
            writer,
            sheet_name="高配当分離確認",
            index=False,
        )

        for class_count, result in all_results.items():

            result.to_excel(
                writer,
                sheet_name=f"{class_count}クラス_分布",
                index=False,
            )

        for class_count, summary in cross_summaries.items():

            summary.to_excel(
                writer,
                sheet_name=f"{class_count}クラス_期間比較",
                index=False,
            )

    log(f"保存先 : {OUTPUT_XLSX}")


# ===========================================================
# Main
# ===========================================================

def main():

    print()

    log("=======================================")
    log("015 Payout Class Candidate Analysis")
    log("=======================================")

    # -------------------------------------------------------
    # 読込
    # -------------------------------------------------------

    old_prediction = load_csv(
        PREDICTION_OLD
    )

    new_prediction = load_csv(
        PREDICTION_NEW
    )

    # -------------------------------------------------------
    # クラス分析
    # -------------------------------------------------------

    all_results = {}
    cross_summaries = {}
    evaluation_rows = []

    for class_count, boundaries in CLASS_CANDIDATES.items():

        log("---------------------------------------")
        log(f"{class_count}クラス候補分析")
        log("---------------------------------------")

        old_result = analyze_classes(
            old_prediction,
            "2020～2022",
            class_count,
            boundaries,
        )

        new_result = analyze_classes(
            new_prediction,
            "2023～2026",
            class_count,
            boundaries,
        )

        combined = pd.concat(
            [
                old_result,
                new_result,
            ],
            ignore_index=True,
        )

        all_results[class_count] = combined

        evaluation, cross = evaluate_candidate(
            old_result,
            new_result,
            class_count,
        )

        evaluation_rows.append(
            evaluation
        )

        cross["クラス数"] = class_count

        cross_summaries[class_count] = cross

    # -------------------------------------------------------
    # 候補比較
    # -------------------------------------------------------

    evaluations = pd.concat(
        evaluation_rows,
        ignore_index=True,
    )

    evaluations = evaluations.sort_values(
        "評価スコア",
        ascending=False,
    ).reset_index(drop=True)

    evaluations.insert(
        0,
        "順位",
        range(
            1,
            len(evaluations) + 1,
        ),
    )

    # -------------------------------------------------------
    # 高配当分離
    # -------------------------------------------------------

    high_check = create_high_payout_check(
        all_results
    )

    # -------------------------------------------------------
    # クラス定義
    # -------------------------------------------------------

    definitions = create_definition_table()

    # -------------------------------------------------------
    # 保存
    # -------------------------------------------------------

    save_excel(
        all_results,
        evaluations,
        cross_summaries,
        high_check,
        definitions,
    )

    # -------------------------------------------------------
    # コンソール表示
    # -------------------------------------------------------

    print()

    log("=======================================")
    log("015 Candidate Ranking")
    log("=======================================")

    print(
        evaluations.to_string(
            index=False
        )
    )

    print()

    log("=======================================")
    log("015 Complete")
    log("=======================================")

    print()


if __name__ == "__main__":
    main()
