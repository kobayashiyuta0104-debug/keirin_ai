"""
===========================================================
競輪AI Ver1.0
014_analyze_payout_distribution_1000.py

払戻分布 1,000円単位分析

【目的】

2020～2022年
training_prediction(2020.1.1~2022.12.31).csv

2023～2026年
training_prediction(2023.1.1~2026.7.30).csv

の2つを比較し、

「実際の三連単払戻がどの価格帯に分布しているか」

を1,000円単位で分析する。

【分析内容】

・1,000円単位の払戻件数
・1,000円単位の割合
・累積件数
・累積割合
・期間間の件数差
・期間間の割合差
・期間間の増減率

※AIモデルは変更しない
※特徴量分析は行わない
※実際の払戻分布のみを分析する

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

TRAINING_DIR = (
    BASE
    / "csv"
    / "training"
)

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
    / "014_payout_distribution_1000.xlsx"
)


# ===========================================================
# ログ
# ===========================================================

def log(message):
    print(
        f"[014_analyze_payout_distribution_1000] {message}"
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

    log(
        f"読込 : {path}"
    )

    log(
        f"Rows    : {len(df):,}"
    )

    log(
        f"Columns : {len(df.columns):,}"
    )

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

    payout_column = find_payout_column(
        df
    )

    work = pd.DataFrame()

    work["払戻"] = pd.to_numeric(
        df[payout_column],
        errors="coerce",
    )

    # 払戻が存在するレースだけ対象
    work = work[
        work["払戻"].notna()
    ].copy()

    # 0円未満は除外
    work = work[
        work["払戻"] >= 0
    ].copy()

    return work


# ===========================================================
# 1,000円単位分布
# ===========================================================

def analyze_distribution(
    df,
    period_name,
):

    log(
        "======================================="
    )

    log(
        f"{period_name} 1,000円単位分布"
    )

    log(
        "======================================="
    )

    work = prepare_payout(
        df
    )

    if len(work) == 0:

        raise ValueError(
            f"{period_name} に有効な払戻データがありません。"
        )

    # -------------------------------------------------------
    # 最大払戻
    # -------------------------------------------------------

    max_payout = int(
        work["払戻"].max()
    )

    # 最大値を含むように1,000円単位で切り上げ
    max_upper = (
        (max_payout // 1000) + 1
    ) * 1000

    # -------------------------------------------------------
    # 1,000円単位の区切り
    # -------------------------------------------------------

    bins = list(
        range(
            0,
            max_upper + 1000,
            1000,
        )
    )

    labels = []

    for i in range(
        len(bins) - 1
    ):

        lower = bins[i]
        upper = bins[i + 1] - 1

        labels.append(
            f"{lower:,}～{upper:,}円"
        )

    # -------------------------------------------------------
    # 払戻帯
    # -------------------------------------------------------

    work["払戻帯"] = pd.cut(
        work["払戻"],
        bins=bins,
        labels=labels,
        right=False,
        include_lowest=True,
    )

    # -------------------------------------------------------
    # 件数
    # -------------------------------------------------------

    result = (
        work
        .groupby(
            "払戻帯",
            observed=False,
        )
        .size()
        .reset_index(
            name="件数"
        )
    )

    # -------------------------------------------------------
    # 割合
    # -------------------------------------------------------

    total = result["件数"].sum()

    result["割合(%)"] = (
        result["件数"]
        / total
        * 100
    ).round(4)

    # -------------------------------------------------------
    # 累積
    # -------------------------------------------------------

    result["累積件数"] = (
        result["件数"]
        .cumsum()
    )

    result["累積割合(%)"] = (
        result["割合(%)"]
        .cumsum()
    ).round(4)

    # -------------------------------------------------------
    # 期間名
    # -------------------------------------------------------

    result.insert(
        0,
        "期間",
        period_name,
    )

    # -------------------------------------------------------
    # 基本統計
    # -------------------------------------------------------

    summary = pd.DataFrame(
        [
            {
                "期間": period_name,
                "レース数": len(work),
                "平均払戻": round(
                    work["払戻"].mean(),
                    0,
                ),
                "中央値払戻": round(
                    work["払戻"].median(),
                    0,
                ),
                "最低払戻": round(
                    work["払戻"].min(),
                    0,
                ),
                "最高払戻": round(
                    work["払戻"].max(),
                    0,
                ),
            }
        ]
    )

    return (
        result,
        summary,
    )


# ===========================================================
# 2期間比較
# ===========================================================

def create_comparison(
    old_df,
    new_df,
):

    log(
        "======================================="
    )

    log(
        "2020～2022 vs 2023～2026 比較"
    )

    log(
        "======================================="
    )

    old = old_df[
        [
            "払戻帯",
            "件数",
            "割合(%)",
        ]
    ].copy()

    new = new_df[
        [
            "払戻帯",
            "件数",
            "割合(%)",
        ]
    ].copy()

    old = old.rename(
        columns={
            "件数":
                "2020～2022_件数",
            "割合(%)":
                "2020～2022_割合(%)",
        }
    )

    new = new.rename(
        columns={
            "件数":
                "2023～2026_件数",
            "割合(%)":
                "2023～2026_割合(%)",
        }
    )

    comparison = pd.merge(
        old,
        new,
        on="払戻帯",
        how="outer",
    )

    comparison[
        "2020～2022_件数"
    ] = comparison[
        "2020～2022_件数"
    ].fillna(0)

    comparison[
        "2023～2026_件数"
    ] = comparison[
        "2023～2026_件数"
    ].fillna(0)

    comparison[
        "2020～2022_割合(%)"
    ] = comparison[
        "2020～2022_割合(%)"
    ].fillna(0)

    comparison[
        "2023～2026_割合(%)"
    ] = comparison[
        "2023～2026_割合(%)"
    ].fillna(0)

    # -------------------------------------------------------
    # 件数差
    # -------------------------------------------------------

    comparison[
        "件数差"
    ] = (
        comparison[
            "2023～2026_件数"
        ]
        -
        comparison[
            "2020～2022_件数"
        ]
    )

    # -------------------------------------------------------
    # 割合差
    # -------------------------------------------------------

    comparison[
        "割合差(pp)"
    ] = (
        comparison[
            "2023～2026_割合(%)"
        ]
        -
        comparison[
            "2020～2022_割合(%)"
        ]
    ).round(4)

    # -------------------------------------------------------
    # 増減率
    # -------------------------------------------------------

    comparison[
        "件数増減率(%)"
    ] = np.where(
        comparison[
            "2020～2022_件数"
        ] > 0,

        (
            (
                comparison[
                    "2023～2026_件数"
                ]
                -
                comparison[
                    "2020～2022_件数"
                ]
            )
            /
            comparison[
                "2020～2022_件数"
            ]
            * 100
        ),

        np.nan,
    )

    comparison[
        "件数増減率(%)"
    ] = comparison[
        "件数増減率(%)"
    ].round(2)

    return comparison


# ===========================================================
# 高配当帯サマリー
# ===========================================================

def create_high_payout_summary(
    old_df,
    new_df,
):

    ranges = [
        (
            "30,000円以上",
            30000,
            float("inf"),
        ),
        (
            "50,000円以上",
            50000,
            float("inf"),
        ),
        (
            "100,000円以上",
            100000,
            float("inf"),
        ),
        (
            "200,000円以上",
            200000,
            float("inf"),
        ),
        (
            "500,000円以上",
            500000,
            float("inf"),
        ),
        (
            "1,000,000円以上",
            1000000,
            float("inf"),
        ),
    ]

    rows = []

    for label, lower, upper in ranges:

        old_count = 0
        new_count = 0

        # ---------------------------------------------------
        # 期間ごとの件数
        # ---------------------------------------------------

        for _, row in old_df.iterrows():

            text = str(
                row["払戻帯"]
            )

            value = int(
                text
                .split("～")[0]
                .replace(",", "")
            )

            if value >= lower:
                old_count += int(
                    row["件数"]
                )

        for _, row in new_df.iterrows():

            text = str(
                row["払戻帯"]
            )

            value = int(
                text
                .split("～")[0]
                .replace(",", "")
            )

            if value >= lower:
                new_count += int(
                    row["件数"]
                )

        old_total = old_df[
            "件数"
        ].sum()

        new_total = new_df[
            "件数"
        ].sum()

        old_rate = (
            old_count
            /
            old_total
            * 100
        )

        new_rate = (
            new_count
            /
            new_total
            * 100
        )

        rows.append(
            {
                "払戻条件": label,
                "2020～2022_件数": old_count,
                "2020～2022_割合(%)":
                    round(
                        old_rate,
                        4,
                    ),
                "2023～2026_件数": new_count,
                "2023～2026_割合(%)":
                    round(
                        new_rate,
                        4,
                    ),
                "件数差":
                    new_count - old_count,
                "割合差(pp)":
                    round(
                        new_rate
                        - old_rate,
                        4,
                    ),
            }
        )

    return pd.DataFrame(
        rows
    )


# ===========================================================
# Excel保存
# ===========================================================

def save_excel(
    old_distribution,
    new_distribution,
    comparison,
    high_summary,
    old_summary,
    new_summary,
):

    ANALYSIS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    log(
        "======================================="
    )

    log(
        "Excel保存"
    )

    log(
        "======================================="
    )

    with pd.ExcelWriter(
        OUTPUT_XLSX,
        engine="openpyxl",
    ) as writer:

        old_distribution.to_excel(
            writer,
            sheet_name="2020～2022_1000円分布",
            index=False,
        )

        new_distribution.to_excel(
            writer,
            sheet_name="2023～2026_1000円分布",
            index=False,
        )

        comparison.to_excel(
            writer,
            sheet_name="期間比較",
            index=False,
        )

        high_summary.to_excel(
            writer,
            sheet_name="高配当比較",
            index=False,
        )

        old_summary.to_excel(
            writer,
            sheet_name="2020～2022_基本統計",
            index=False,
        )

        new_summary.to_excel(
            writer,
            sheet_name="2023～2026_基本統計",
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

    log(
        "======================================="
    )

    log(
        "014 Payout Distribution 1,000 Analysis"
    )

    log(
        "======================================="
    )

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
    # 分析
    # -------------------------------------------------------

    (
        old_distribution,
        old_summary,
    ) = analyze_distribution(
        old_prediction,
        "2020～2022",
    )

    (
        new_distribution,
        new_summary,
    ) = analyze_distribution(
        new_prediction,
        "2023～2026",
    )

    # -------------------------------------------------------
    # 比較
    # -------------------------------------------------------

    comparison = create_comparison(
        old_distribution,
        new_distribution,
    )

    # -------------------------------------------------------
    # 高配当比較
    # -------------------------------------------------------

    high_summary = create_high_payout_summary(
        old_distribution,
        new_distribution,
    )

    # -------------------------------------------------------
    # 保存
    # -------------------------------------------------------

    save_excel(
        old_distribution,
        new_distribution,
        comparison,
        high_summary,
        old_summary,
        new_summary,
    )

    # -------------------------------------------------------
    # コンソール表示
    # -------------------------------------------------------

    print()

    log(
        "======================================="
    )

    log(
        "014 Summary"
    )

    log(
        "======================================="
    )

    print(
        high_summary.to_string(
            index=False
        )
    )

    print()

    log(
        "======================================="
    )

    log(
        "014 Complete"
    )

    log(
        "======================================="
    )

    print()


# ===========================================================
# 実行
# ===========================================================

if __name__ == "__main__":

    main()