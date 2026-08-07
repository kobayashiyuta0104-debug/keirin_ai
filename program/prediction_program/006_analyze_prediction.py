"""
===========================================================
競輪AI Ver1.0

006_analyze_prediction.py

AI分析ツール

【役割】

prediction.csv

↓

AI分析

↓

analysis CSV出力

Part1
・基本設定
・CSV読込
・分析フォルダ準備

===========================================================
"""

import os
from pathlib import Path

import pandas as pd


# ===========================================================
# GitHub対応
# ===========================================================

if os.name == "nt":

    BASE = Path(r"C:\競輪AI")

else:

    BASE = Path(__file__).resolve().parent.parent


# ===========================================================
# パス
# ===========================================================

PREDICTION_DIR = (

    BASE
    / "csv"
    / "prediction"

)

ANALYSIS_DIR = (

    BASE
    / "csv"
    / "analysis"

)

TRAINING_FILE = (

    BASE
    / "csv"
    / "training"
    / "training_prediction.csv"

)

ANALYSIS_DIR.mkdir(

    parents=True,

    exist_ok=True,

)


# ===========================================================
# ログ
# ===========================================================

def log(message):

    print(f"[006_analyze_prediction] {message}")


# ===========================================================
# Prediction CSV一覧取得
# ===========================================================

def get_prediction_files():

    files = sorted(

        PREDICTION_DIR.glob("*_prediction.csv")

    )

    if len(files) == 0:

        raise FileNotFoundError(

            "prediction.csv が見つかりません。"

        )

    log(f"Prediction CSV : {len(files):,} 件")

    print()

    return files


# ===========================================================
# Prediction CSV読込
# ===========================================================

def load_prediction():

    log("=======================================")
    log("Prediction CSV 読込")
    log("=======================================")

    df_list = []

    # -----------------------------
    # 日々Prediction
    # -----------------------------

    files = get_prediction_files()

    for file in files:

        log(f"読込 : {file.name}")

        df = pd.read_csv(

            file,

            encoding="utf-8-sig",

            low_memory=False,

        )

        df_list.append(df)

    # -----------------------------
    # 過去3年Prediction
    # -----------------------------

    if TRAINING_FILE.exists():

        log(f"読込 : {TRAINING_FILE.name}")

        training_df = pd.read_csv(

            TRAINING_FILE,

            encoding="utf-8-sig",

            low_memory=False,

        )

        df_list.append(training_df)

    prediction_df = pd.concat(

        df_list,

        ignore_index=True,

    )

    # -----------------------------
    # 重複削除
    # -----------------------------

    prediction_df = prediction_df.drop_duplicates(

        subset=["レースキー"],

        keep="last",

    )

    log("---------------------------------------")
    log(f"CSV数     : {len(df_list):,}")
    log(f"総レース数 : {len(prediction_df):,}")
    log(f"Columns   : {len(prediction_df.columns):,}")

    print()

    return prediction_df

# ===========================================================
# Overall分析
# ===========================================================

def analyze_overall(df):

    log("=======================================")
    log("Overall Analysis")
    log("=======================================")

    total = len(df)

    hit = (df["的中\n判定"] == "○").sum()

    hit_rate = (

        round(hit / total * 100, 2)

        if total > 0

        else 0

    )

    summary = pd.DataFrame({

        "項目": [

            "総レース数",

            "的中数",

            "的中率(%)",

            "平均払戻",

            "平均AI確信度",

        ],

        "値": [

            total,

            hit,

            hit_rate,

            round(

                pd.to_numeric(

                    df["三連単\n払戻"],

                    errors="coerce",

                ).mean(),

                0,

            ),

            round(

                pd.to_numeric(

                    df["AI確信度"]

                    .astype(str)

                    .str.replace("%","",regex=False)

                    .str.replace("％","",regex=False),

                    errors="coerce",

                ).mean(),

                2,

            ),

        ],

    })

    return summary


# ===========================================================
# Class分析
# ===========================================================

def analyze_class(df):

    log("=======================================")
    log("Class Analysis")
    log("=======================================")

    result = (

        df

        .groupby("AI予想")

        .agg(

            レース数=("AI予想","count"),

            的中数=("的中\n判定",lambda x:(x=="○").sum()),

            平均払戻=(

                "三連単\n払戻",

                lambda x: round(

                    pd.to_numeric(

                        x,

                        errors="coerce",

                    ).mean(),

                    0,

                ),

            ),

            平均確信度=(

                "AI確信度",

                lambda x: round(

                    pd.to_numeric(

                        x.astype(str)

                        .str.replace("%","",regex=False)

                        .str.replace("％","",regex=False),

                        errors="coerce",

                    ).mean(),

                    2,

                ),

            )

        )

        .reset_index()

    )

    result["的中率"] = (

        result["的中数"]

        /

        result["レース数"]

        *100

    ).round(2)

    return result


# ===========================================================
# Grade分析
# ===========================================================

def analyze_grade(df):

    log("=======================================")
    log("Grade Analysis")
    log("=======================================")

    result = (

        df

        .groupby("グレード")

        .agg(

            レース数=("グレード","count"),

            的中数=("的中\n判定",lambda x:(x=="○").sum()),

            平均払戻=(

                "三連単\n払戻",

                lambda x: round(

                    pd.to_numeric(

                        x,

                        errors="coerce",

                    ).mean(),

                    0,

                ),

            ),

            平均確信度=(

                "AI確信度",

                lambda x: round(

                    pd.to_numeric(

                        x.astype(str)

                        .str.replace("%","",regex=False)

                        .str.replace("％","",regex=False),

                        errors="coerce",

                    ).mean(),

                    2,

                ),

            )

        )

        .reset_index()

    )

    result["的中率"] = (
        result["的中数"]
        /
        result["レース数"]
        *100
    ).round(2)

    result = add_class_hit_rate(
        result,
        df,
        "グレード",
    )

    PERCENT_COLUMNS = [

        "的中率",

        "0～9,999円",

        "10,000～29,999円",

        "30,000～49,999円",

        "50,000～99,999円",

        "100,000円以上",

    ]

    for col in PERCENT_COLUMNS:

        result[col] = result[col].apply(

            lambda x: ""

            if pd.isna(x) or x == ""

            else f"{x:.2f}%"

        )

    return result


# ===========================================================
# RaceType分析
# ===========================================================

def analyze_race_type(df):

    log("=======================================")
    log("Race Type Analysis")
    log("=======================================")

    result = (

        df

        .groupby("レース種別")

        .agg(

            レース数=("レース種別","count"),

            的中数=("的中\n判定",lambda x:(x=="○").sum()),

            平均払戻=(

                "三連単\n払戻",

                    lambda x: round(

                    pd.to_numeric(

                        x,

                        errors="coerce",

                    ).mean(),

                    0,

                ),

            ),

            平均確信度=(

                "AI確信度",

                lambda x: round(

                    pd.to_numeric(

                        x.astype(str)

                        .str.replace("%","",regex=False)

                        .str.replace("％","",regex=False),

                        errors="coerce",

                    ).mean(),

                    2,

                ),

            )

        )

        .reset_index()

    )

    result["的中率"] = (

        result["的中数"]

        /

        result["レース数"]

        *100

    ).round(2)

    result = add_class_hit_rate(
        result,
        df,
        "レース種別",
    )

    PERCENT_COLUMNS = [

        "的中率",

        "0～9,999円",

        "10,000～29,999円",

        "30,000～49,999円",

        "50,000～99,999円",

        "100,000円以上",

    ]

    for col in PERCENT_COLUMNS:

        result[col] = result[col].apply(

           lambda x: ""

            if pd.isna(x) or x == ""

            else f"{x:.2f}%"

        )

    return result


CLASS_LIST = [

    "0～9,999円",

    "10,000～29,999円",

    "30,000～49,999円",

    "50,000～99,999円",

    "100,000円以上",

]


def add_class_hit_rate(result, df, group_column):

    for ai_class in CLASS_LIST:

        rates = []

        for value in result[group_column]:

            target = df[

                (df[group_column] == value)

                &

                (df["AI予想"] == ai_class)

            ]

            if len(target) == 0:

                rates.append("")

            else:

                hit = (

                    target["的中\n判定"] == "○"

                ).sum()

                rates.append(

                    round(

                        hit / len(target) * 100,

                        2,

                    )

                )

        result[ai_class] = rates

    return result

# ===========================================================
# Track分析
# ===========================================================

def analyze_track(df):

    log("=======================================")
    log("Track Analysis")
    log("=======================================")

    result = (

        df

        .groupby("競輪場")

        .agg(

            レース数=("競輪場","count"),

            的中数=("的中\n判定",lambda x:(x=="○").sum()),

            平均払戻=(

                "三連単\n払戻",

                lambda x: round(

                    pd.to_numeric(

                        x,

                        errors="coerce",

                    ).mean(),

                    0,

                ),

            ),

            平均確信度=(

                "AI確信度",

                lambda x: round(

                    pd.to_numeric(

                        x.astype(str)

                        .str.replace("%","",regex=False)

                        .str.replace("％","",regex=False),

                        errors="coerce",

                    ).mean(),

                    2,

                ),

            )

        )

        .reset_index()

    )

    result["的中率"] = (

        result["的中数"]

        /

        result["レース数"]

        *100

    ).round(2)

    result = add_class_hit_rate(
        result,
        df,
        "競輪場",
    )

    PERCENT_COLUMNS = [

        "的中率",

        "0～9,999円",

        "10,000～29,999円",

        "30,000～49,999円",

        "50,000～99,999円",

        "100,000円以上",

    ]

    for col in PERCENT_COLUMNS:

        result[col] = result[col].apply(

            lambda x: ""

            if pd.isna(x) or x == ""

            else f"{x:.2f}%"

        )

    return result

# ===========================================================
# 払戻分布分析
# ===========================================================

def analyze_payout_distribution(df):

    log("=======================================")
    log("006 Payout Distribution")
    log("=======================================")

    work = df.copy()

    work["\n払戻"] = pd.to_numeric(

        work["三連単\n払戻"],

        errors="coerce",

    ).fillna(0)

    bins = [

        0,

        3000,

        10000,

        20000,

        30000,

        40000,

        50000,

        60000,

        70000,

        80000,

        90000,

        100000,

        150000,

        200000,

        float("inf"),

    ]

    labels = [

        "0～2,999",

        "3,000～9,999",

        "10,000～19,999",

        "20,000～29,999",

        "30,000～39,999",

        "40,000～49,999",

        "50,000～59,999",

        "60,000～69,999",

        "70,000～79,999",

        "80,000～89,999",

        "90,000～99,999",

        "100,000～149,999",

        "150,000～199,999",

        "200,000以上",

    ]

    work["払戻帯"] = pd.cut(

        work["三連単\n払戻"],

        bins=bins,

        labels=labels,

        right=False,

    )

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

    total = result["件数"].sum()

    result["割合(%)"] = (

        result["件数"]

        / total

        * 100

    ).round(2)

    result["累積件数"] = (

        result["件数"]

        .cumsum()

    )

    result["累積割合(%)"] = (

        result["割合(%)"]

        .cumsum()

    ).round(2)

    result["割合(%)"] = result["割合(%)"].apply(

        lambda x: f"{x:.2f}%"

    )

    result["累積割合(%)"] = result["累積割合(%)"].apply(

        lambda x: f"{x:.2f}%"

    )

    return result

# ===========================================================
# AI予想分布分析
# ===========================================================

def analyze_prediction_distribution(df):

    log("=======================================")
    log("007 AI Prediction Distribution")
    log("=======================================")

    result = (

        df["AI予想"]

        .value_counts(

            dropna=False,

        )

        .rename_axis(

            "AI予想"

        )

        .reset_index(

            name="件数"

        )

    )

    result["割合(%)"] = (

        result["件数"]

        /

        len(df)

        *100

    ).round(2)

    result["割合(%)"] = result["割合(%)"].apply(

        lambda x: f"{x:.2f}%"

    )

    return result


# ===========================================================
# 高配当検知分析
# ===========================================================

def analyze_high_payout(df):

    log("=======================================")
    log("008 High Payout Detection")
    log("=======================================")

    CONDITIONS = [

        (

            "30,000円以上",

            30000,

            [

                "30,000～49,999円",

                "50,000～99,999円",

                "100,000円以上",

            ],

        ),

        (

            "50,000円以上",

            50000,

            [

                "50,000～99,999円",

                "100,000円以上",

            ],

        ),

        (

            "100,000円以上",

            100000,

            [

                "100,000円以上",

            ],

        ),

    ]

    rows = []

    payout = pd.to_numeric(

        df["三連単\n払戻"],

        errors="coerce",

    )

    for name, border, ai_classes in CONDITIONS:

        actual = (

            payout >= border

        )

        detected = (

            actual

            &

            df["AI予想"].isin(

                ai_classes

            )

        )

        actual_count = int(

            actual.sum()

        )

        detect_count = int(

            detected.sum()

        )

        miss_count = (

            actual_count

            - detect_count

        )

        detect_rate = (

            round(

                detect_count

                / actual_count

                *100,

                2,

            )

            if actual_count > 0

            else 0

        )

        rows.append({

            "対象":

                name,

            "実際件数":

                actual_count,

            "AI検知件数":

                detect_count,

            "検知率(%)":

                detect_rate,

            "見逃し件数":

                miss_count,

        })

    result = pd.DataFrame(rows)

    result["検知率(%)"] = result["検知率(%)"].apply(

        lambda x: f"{x:.2f}%"

    )

    return result

# ===========================================================
# AI弱点分析
# ===========================================================

def analyze_weakness(df):

    log("=======================================")
    log("009 Weakness Analysis")
    log("=======================================")

    weakness_list = []

    ANALYSIS_COLUMNS = [

        "グレード",

        "レース種別",

        "競輪場",

    ]

    for column in ANALYSIS_COLUMNS:

        result = (

            df

            .groupby(column)

            .agg(

                レース数=(column, "count"),

                的中数=("的中\n判定", lambda x: (x == "○").sum()),

            )

            .reset_index()

        )

        result["的中率(%)"] = (

            result["的中数"]

            /

            result["レース数"]

            * 100

        ).round(2)

        result.insert(

            0,

            "分析項目",

            column,

        )

        result.rename(

            columns={

                column: "分類"

            },

            inplace=True,

        )

        weakness_list.append(result)

    weakness_df = pd.concat(

        weakness_list,

        ignore_index=True,

    )

    weakness_df = weakness_df.sort_values(

        "的中率(%)",

        ascending=True,

    )

    return weakness_df

# ===========================================================
# AI確信度分析
# ===========================================================

def analyze_confidence(df):

    log("=======================================")
    log("012 Confidence Analysis")
    log("=======================================")

    work = df.copy()

    work["AI確信度"] = (

    work["AI確信度"]

    .astype(str)

    .str.replace("%", "", regex=False)

    )

    work["AI確信度"] = pd.to_numeric(

        work["AI確信度"],

        errors="coerce",

    ).fillna(0)

    bins = [

        0,

        10,

        20,

        30,

        40,

        50,

        60,

        70,

        80,

        90,

        101,

    ]

    labels = [

        "0～9%",

        "10～19%",

        "20～29%",

        "30～39%",

        "40～49%",

        "50～59%",

        "60～69%",

        "70～79%",

        "80～89%",

        "90～100%",

    ]

    work["確信度帯"] = pd.cut(

        work["AI確信度"],

        bins=bins,

        labels=labels,

        right=False,

    )

    result = (

        work

        .groupby("確信度帯", observed=False)

        .agg(

            レース数=("確信度帯", "count"),

            的中数=("的中\n判定", lambda x: (x == "○").sum()),

            平均払戻=(

                "三連単\n払戻",

                lambda x: round(

                    pd.to_numeric(

                        x,

                        errors="coerce",

                    ).mean(),

                    0,

                ),

            ),

            平均AI確信度=(

                "AI確信度",

                "mean",

            ),

        )

        .reset_index()

    )

    result["的中率(%)"] = (

        result["的中数"]

        /

        result["レース数"]

        *100

    ).round(2)

    result["的中率(%)"] = result["的中率(%)"].apply(

        lambda x: f"{x:.2f}%"

    )

    result["平均AI確信度"] = result["平均AI確信度"].apply(

        lambda x: f"{x:.2f}%"

    )

    return result


# ===========================================================
# サマリー作成
# ===========================================================

def build_summary(

    overall_df,

    grade_df,

    high_payout_df,

):

    log("=======================================")
    log("010 Summary")
    log("=======================================")

    best_grade = (

        grade_df

        .sort_values(

            "的中率",

            ascending=False,

        )

        .iloc[0]

    )

    worst_grade = (

        grade_df

        .sort_values(

            "的中率",

            ascending=True,

        )

        .iloc[0]

    )

    summary = pd.DataFrame({

        "項目": [

            "総レース数",

            "的中数",

            "的中率",

            "平均払戻",

            "平均AI確信度",

            "",

            "30,000円以上検知率",

            "50,000円以上検知率",

            "100,000円以上検知率",

            "",

            "最も得意なグレード",

            "最も苦手なグレード",

        ],

        "内容": [

            overall_df.loc[0, "値"],

            overall_df.loc[1, "値"],

            f'{overall_df.loc[2,"値"]}%',

            f'{pd.to_numeric(

            overall_df.loc[3,"値"],

            errors="coerce"

            ):,.0f}円',

            overall_df.loc[4, "値"],

            "",

            f'{high_payout_df.loc[0,"検知率(%)"]}%',

            f'{high_payout_df.loc[1,"検知率(%)"]}%',

            f'{high_payout_df.loc[2,"検知率(%)"]}%',

            "",

            f'{best_grade["グレード"]} ({best_grade["的中率"]})',

            f'{worst_grade["グレード"]} ({worst_grade["的中率"]})',

        ],

    })

    return summary

# ===========================================================
# Excel保存
# ===========================================================

def save_excel(

    summary_df,

    overall_df,

    class_df,

    grade_df,

    race_type_df,

    track_df,

    payout_distribution_df,

    prediction_distribution_df,

    high_payout_df,

    weakness_df,

    confidence_df,

):

    log("=======================================")
    log("011 Excel Save")
    log("=======================================")

    output_file = (

        ANALYSIS_DIR

        / "競輪AI分析レポート.xlsx"

    )

    ANALYSIS_DIR.mkdir(

        parents=True,

        exist_ok=True,

    )

    with pd.ExcelWriter(

        output_file,

        engine="openpyxl",

    ) as writer:

        summary_df.to_excel(

            writer,

            sheet_name="サマリー",

            index=False,

        )

        overall_df.to_excel(

            writer,

            sheet_name="全体分析",

            index=False,

        )

        class_df.to_excel(

            writer,

            sheet_name="クラス分析",

            index=False,

        )

        grade_df.to_excel(

            writer,

            sheet_name="グレード分析",

            index=False,

        )

        race_type_df.to_excel(

            writer,

            sheet_name="レース種別分析",

            index=False,

        )

        track_df.to_excel(

            writer,

            sheet_name="競輪場分析",

            index=False,

        )

        payout_distribution_df.to_excel(

            writer,

            sheet_name="払戻分布分析",

            index=False,

        )

        prediction_distribution_df.to_excel(

            writer,

            sheet_name="AI予想分布",

            index=False,

        )

        high_payout_df.to_excel(

            writer,

            sheet_name="高配当検知分析",

            index=False,

        )

        weakness_df.to_excel(

            writer,

            sheet_name="AI弱点分析",

            index=False,

        )

        confidence_df.to_excel(

            writer,

            sheet_name="AI確信度分析",

            index=False,

        )

    log(f"保存先 : {output_file}")

    print()

    log("Excel保存完了")

# ===========================================================
# Main
# ===========================================================

def main():

    print()

    log("=======================================")
    log("006 Analyze Prediction")
    log("=======================================")

    prediction_df = load_prediction()

    overall_df = analyze_overall(
        prediction_df,
    )

    class_df = analyze_class(
        prediction_df,
    )

    grade_df = analyze_grade(
        prediction_df,
    )

    race_type_df = analyze_race_type(
        prediction_df,
    )

    track_df = analyze_track(
        prediction_df,
    )

    payout_distribution_df = analyze_payout_distribution(
        prediction_df,
    )

    prediction_distribution_df = analyze_prediction_distribution(
        prediction_df,
    )

    high_payout_df = analyze_high_payout(
        prediction_df,
    )

    weakness_df = analyze_weakness(
        prediction_df,
    )
    
    confidence_df = analyze_confidence(
        prediction_df,
    )

    summary_df = build_summary(
        overall_df,
        grade_df,
        high_payout_df,
    )

    save_excel(

        summary_df,

        overall_df,

        class_df,

        grade_df,

        race_type_df,

        track_df,

        payout_distribution_df,

        prediction_distribution_df,

        high_payout_df,

        weakness_df,

        confidence_df,

    )

    log("=======================================")
    log("006 Analyze Complete")
    log("=======================================")

    print()


# ===========================================================
# 実行
# ===========================================================

if __name__ == "__main__":

    main()
