# ===========================================================
#
# 競輪AI Ver1.0
# 016_analyze_prediction_error.py
#
# 予想クラス・実際結果の誤差分析
#
# 【目的】
#
# AI予想が「的中 / ×」だけではなく、
# 実際の払戻が予想レンジからどの程度近いかを分析する。
#
# ① 完全的中
# ② クラス距離
# ③ 予想レンジ外の金額差（±）
# ④ 近い外れ / 遠い外れ
# ⑤ 予想クラス → 実際クラス遷移
# ⑥ 予想クラス別の誤差
# ⑦ 実際クラスに与えた予測確率
# ⑧ 実際クラスが予測確率何位だったか
# ⑨ 全レース詳細
#
# ※AIの再学習は行わない
# ※既存AI予想をそのまま評価する
#
# 金額差の定義
# -----------------------------------------------------------
# 予想：10,000～19,999円
#
# 実際：7,000円
# → -3,000円
#
# 実際：20,500円
# → +501円
#
# 実際：15,000円（予想範囲内）
# → 0円
#
# 「金額差」は予想クラスの最近接境界からの距離。
# マイナス = 予想より低い
# プラス   = 予想より高い
#
# ===========================================================

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

TRAINING_DIR = BASE / "csv" / "training"

ANALYSIS_DIR = (
    BASE
    / "csv"
    / "analysis"
    / "prediction_error"
)

ANALYSIS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# 入力ファイル名を固定しない。
# training_prediction*.csv の中から日付が新しいものを自動検出する。
PREDICTION_PATTERN = "training_prediction*.csv"

OUTPUT_XLSX = (
    ANALYSIS_DIR
    / "016_prediction_error_analysis.xlsx"
)


# ===========================================================
# 8クラス定義
# ===========================================================

CLASS_1 = "0～1,999円"
CLASS_2 = "2,000～4,999円"
CLASS_3 = "5,000～9,999円"
CLASS_4 = "10,000～19,999円"
CLASS_5 = "20,000～29,999円"
CLASS_6 = "30,000～49,999円"
CLASS_7 = "50,000～99,999円"
CLASS_8 = "100,000円以上"

CLASSES = [
    CLASS_1,
    CLASS_2,
    CLASS_3,
    CLASS_4,
    CLASS_5,
    CLASS_6,
    CLASS_7,
    CLASS_8,
]

CLASS_RANGES = {
    CLASS_1: (0, 1999),
    CLASS_2: (2000, 4999),
    CLASS_3: (5000, 9999),
    CLASS_4: (10000, 19999),
    CLASS_5: (20000, 29999),
    CLASS_6: (30000, 49999),
    CLASS_7: (50000, 99999),
    CLASS_8: (100000, None),
}

PROBABILITY_COLUMNS = {
    CLASS_1: "0～\n1,999",
    CLASS_2: "2,000～\n4,999",
    CLASS_3: "5,000～\n9,999",
    CLASS_4: "10,000～\n19,999",
    CLASS_5: "20,000～\n29,999",
    CLASS_6: "30,000～\n49,999",
    CLASS_7: "50,000～\n99,999",
    CLASS_8: "100,000\n以上",
}


# ===========================================================
# ログ
# ===========================================================

def log(message):
    print(
        f"[016_analyze_prediction_error] {message}"
    )


# ===========================================================
# 最新CSV自動検出
# ===========================================================

def find_latest_prediction_csv():

    candidates = []

    for path in TRAINING_DIR.glob(PREDICTION_PATTERN):

        if not path.is_file():
            continue

        candidates.append(path)

    if not candidates:

        raise FileNotFoundError(
            "training_prediction*.csv が見つかりません:\n"
            f"{TRAINING_DIR}"
        )

    candidates.sort(
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    return candidates[0]


# ===========================================================
# CSV読込
# ===========================================================

def load_prediction():

    log("=======================================")
    log("Prediction CSV 読込")
    log("=======================================")

    prediction_path = find_latest_prediction_csv()

    log(
        f"入力ファイル : {prediction_path}"
    )

    df = pd.read_csv(
        prediction_path,
        encoding="utf-8-sig",
        low_memory=False,
    )

    log(f"Rows    : {len(df):,}")
    log(f"Columns : {len(df.columns):,}")

    print()

    return df, prediction_path


# ===========================================================
# 必須列確認
# ===========================================================

def check_columns(df):

    required = [
        "レースキー",
        "AI予想",
        "実際\nクラス",
        "三連単\n払戻",
    ]

    log("=======================================")
    log("必須列確認")
    log("=======================================")

    for column in required:

        if column not in df.columns:

            raise KeyError(
                "Prediction CSV に必要な列がありません: "
                f"{column}"
            )

    missing_probability = [
        column
        for column in PROBABILITY_COLUMNS.values()
        if column not in df.columns
    ]

    if missing_probability:

        log(
            "WARNING: 一部の予測確率列がありません"
        )

        for column in missing_probability:
            log(f"  {column}")

    log("必須列OK")
    print()


# ===========================================================
# 払戻金額の数値化
# ===========================================================

def convert_payout(value):

    if pd.isna(value):
        return np.nan

    text = str(value).strip()

    if text == "":
        return np.nan

    text = (
        text
        .replace(",", "")
        .replace("円", "")
        .replace("%", "")
        .strip()
    )

    try:
        return float(text)
    except Exception:
        return np.nan


# ===========================================================
# クラス正規化
# ===========================================================

def normalize_class(value):

    if pd.isna(value):
        return np.nan

    text = (
        str(value)
        .replace("\n", "")
        .replace("\r", "")
        .replace(" ", "")
        .replace("　", "")
    )

    mapping = {
        "0～1,999円": CLASS_1,
        "0～1999円": CLASS_1,

        "2,000～4,999円": CLASS_2,
        "2000～4999円": CLASS_2,

        "5,000～9,999円": CLASS_3,
        "5000～9999円": CLASS_3,

        "10,000～19,999円": CLASS_4,
        "10000～19999円": CLASS_4,

        "20,000～29,999円": CLASS_5,
        "20000～29999円": CLASS_5,

        "30,000～49,999円": CLASS_6,
        "30000～49999円": CLASS_6,

        "50,000～99,999円": CLASS_7,
        "50000～99999円": CLASS_7,

        "100,000円以上": CLASS_8,
        "100000円以上": CLASS_8,
    }

    return mapping.get(text, value)


# ===========================================================
# 実際クラスを払戻金額から補完
# ===========================================================

def class_from_payout(payout):

    if pd.isna(payout):
        return np.nan

    for class_name in CLASSES:

        lower, upper = CLASS_RANGES[class_name]

        if upper is None:

            if payout >= lower:
                return class_name

        else:

            if lower <= payout <= upper:
                return class_name

    return np.nan


# ===========================================================
# クラス番号
# ===========================================================

def class_number(class_name):

    if class_name not in CLASSES:
        return np.nan

    return CLASSES.index(class_name) + 1


# ===========================================================
# 金額差・クラス距離判定
# ===========================================================

def calculate_error_info(predicted_class, actual_payout):

    if (
        predicted_class not in CLASS_RANGES
        or pd.isna(actual_payout)
    ):
        return {
            "actual_class_calc": np.nan,
            "class_distance": np.nan,
            "error_direction": "判定不可",
            "signed_boundary_difference": np.nan,
            "absolute_boundary_difference": np.nan,
            "near_miss_class": "判定不可",
        }

    actual_class = class_from_payout(
        actual_payout
    )

    predicted_no = class_number(
        predicted_class
    )

    actual_no = class_number(
        actual_class
    )

    class_distance = (
        actual_no - predicted_no
    )

    lower, upper = CLASS_RANGES[
        predicted_class
    ]

    # 予想クラス内
    if lower <= actual_payout and (
        upper is None
        or actual_payout <= upper
    ):

        signed_difference = 0
        absolute_difference = 0
        direction = "予想範囲内"
        near_miss = "完全的中"

    # 予想クラスより下
    elif actual_payout < lower:

        signed_difference = (
            actual_payout - lower
        )

        absolute_difference = abs(
            signed_difference
        )

        direction = "予想より低い"

        if absolute_difference <= 1000:
            near_miss = "超惜しい"
        elif absolute_difference <= 3000:
            near_miss = "惜しい"
        elif absolute_difference <= 5000:
            near_miss = "やや惜しい"
        elif absolute_difference <= 10000:
            near_miss = "やや遠い"
        else:
            near_miss = "遠い"

    # 予想クラスより上
    else:

        signed_difference = (
            actual_payout - upper
        )

        absolute_difference = abs(
            signed_difference
        )

        direction = "予想より高い"

        if absolute_difference <= 1000:
            near_miss = "超惜しい"
        elif absolute_difference <= 3000:
            near_miss = "惜しい"
        elif absolute_difference <= 5000:
            near_miss = "やや惜しい"
        elif absolute_difference <= 10000:
            near_miss = "やや遠い"
        else:
            near_miss = "遠い"

    return {
        "actual_class_calc": actual_class,
        "class_distance": class_distance,
        "error_direction": direction,
        "signed_boundary_difference": signed_difference,
        "absolute_boundary_difference": absolute_difference,
        "near_miss_class": near_miss,
    }


# ===========================================================
# 予測確率の数値化
# ===========================================================

def convert_probability(value):

    if pd.isna(value):
        return np.nan

    text = (
        str(value)
        .replace("%", "")
        .replace(",", "")
        .strip()
    )

    try:
        return float(text)
    except Exception:
        return np.nan


# ===========================================================
# 予測確率分析
# ===========================================================

def calculate_probability_info(row, actual_class):

    probabilities = {}

    for class_name, column in PROBABILITY_COLUMNS.items():

        if column not in row.index:
            continue

        value = convert_probability(
            row[column]
        )

        if not pd.isna(value):
            probabilities[class_name] = value

    if not probabilities or actual_class not in probabilities:

        return {
            "actual_class_probability": np.nan,
            "actual_class_probability_rank": np.nan,
        }

    sorted_classes = sorted(
        probabilities.items(),
        key=lambda x: x[1],
        reverse=True,
    )

    rank = next(
        (
            index + 1
            for index, (class_name, _) in enumerate(
                sorted_classes
            )
            if class_name == actual_class
        ),
        np.nan,
    )

    return {
        "actual_class_probability":
            probabilities[actual_class],
        "actual_class_probability_rank":
            rank,
    }


# ===========================================================
# 詳細データ作成
# ===========================================================

def build_detail(df):

    log("=======================================")
    log("誤差詳細データ作成")
    log("=======================================")

    result = df.copy()

    result["予想クラス"] = (
        result["AI予想"]
        .apply(normalize_class)
    )

    result["実際払戻_数値"] = (
        result["三連単\n払戻"]
        .apply(convert_payout)
    )

    result["実際クラス_正規化"] = (
        result["実際\nクラス"]
        .apply(normalize_class)
    )

    # 実際クラスが欠損している場合は
    # 払戻金額から補完
    result["実際クラス"] = (
        result["実際クラス_正規化"]
        .where(
            result["実際クラス_正規化"].notna(),
            result["実際払戻_数値"].apply(
                class_from_payout
            ),
        )
    )

    error_records = []

    for _, row in result.iterrows():

        info = calculate_error_info(
            row["予想クラス"],
            row["実際払戻_数値"],
        )

        prob_info = calculate_probability_info(
            row,
            row["実際クラス"],
        )

        error_records.append(
            {
                **info,
                **prob_info,
            }
        )

    error_df = pd.DataFrame(
        error_records,
        index=result.index,
    )

    result = pd.concat(
        [
            result,
            error_df,
        ],
        axis=1,
    )

    result["予想クラス番号"] = (
        result["予想クラス"]
        .apply(class_number)
    )

    result["実際クラス番号"] = (
        result["実際クラス"]
        .apply(class_number)
    )

    # クラス距離の名称
    result["クラス距離区分"] = (
        result["class_distance"]
        .apply(
            lambda x:
                "判定不可"
                if pd.isna(x)
                else (
                    "完全的中"
                    if x == 0
                    else (
                        f"{abs(int(x))}クラス上"
                        if x > 0
                        else
                        f"{abs(int(x))}クラス下"
                    )
                )
        )
    )

    # 金額差方向を短い名称でも保持
    result["金額差"] = (
        result["signed_boundary_difference"]
    )

    result["絶対金額差"] = (
        result["absolute_boundary_difference"]
    )

    # 最重要の分析列を先頭側に追加
    preferred = [
        "レースキー",
        "日付",
        "競輪場",
        "レース\n番号",
        "予想クラス",
        "実際クラス",
        "三連単\n払戻",
        "的中\n判定",
        "class_distance",
        "クラス距離区分",
        "error_direction",
        "金額差",
        "絶対金額差",
        "near_miss_class",
        "actual_class_probability",
        "actual_class_probability_rank",
    ]

    existing = [
        column
        for column in preferred
        if column in result.columns
    ]

    remaining = [
        column
        for column in result.columns
        if column not in existing
    ]

    result = result[
        existing + remaining
    ]

    return result


# ===========================================================
# 件数集計
# ===========================================================

def build_summary(detail):

    total = len(detail)

    valid = detail[
        detail["実際払戻_数値"].notna()
    ]

    exact = (
        valid["class_distance"] == 0
    ).sum()

    one_class = (
        valid["class_distance"].abs() == 1
    ).sum()

    two_class = (
        valid["class_distance"].abs() == 2
    ).sum()

    three_or_more = (
        valid["class_distance"].abs() >= 3
    ).sum()

    rows = [
        {
            "区分": "全レース",
            "件数": total,
            "割合_%":
                total / total * 100
                if total else 0,
        },
        {
            "区分": "払戻確認可能",
            "件数": len(valid),
            "割合_%":
                len(valid) / total * 100
                if total else 0,
        },
        {
            "区分": "完全的中（同一クラス）",
            "件数": exact,
            "割合_%":
                exact / len(valid) * 100
                if len(valid) else 0,
        },
        {
            "区分": "1クラス外れ",
            "件数": one_class,
            "割合_%":
                one_class / len(valid) * 100
                if len(valid) else 0,
        },
        {
            "区分": "2クラス外れ",
            "件数": two_class,
            "割合_%":
                two_class / len(valid) * 100
                if len(valid) else 0,
        },
        {
            "区分": "3クラス以上外れ",
            "件数": three_or_more,
            "割合_%":
                three_or_more / len(valid) * 100
                if len(valid) else 0,
        },
    ]

    return pd.DataFrame(rows)


# ===========================================================
# クラス距離集計
# ===========================================================

def build_distance_summary(detail):

    valid = detail[
        detail["class_distance"].notna()
    ].copy()

    if valid.empty:
        return pd.DataFrame()

    result = (
        valid["class_distance"]
        .value_counts()
        .sort_index()
        .rename_axis("クラス距離")
        .reset_index(name="件数")
    )

    total = result["件数"].sum()

    result["割合_%"] = (
        result["件数"]
        / total
        * 100
    )

    return result


# ===========================================================
# 近い外れ・遠い外れ集計
# ===========================================================

def build_near_miss_summary(detail):

    valid = detail[
        detail["class_distance"].notna()
    ].copy()

    result = (
        valid["near_miss_class"]
        .value_counts()
        .reindex(
            [
                "完全的中",
                "超惜しい",
                "惜しい",
                "やや惜しい",
                "やや遠い",
                "遠い",
                "判定不可",
            ],
            fill_value=0,
        )
        .rename_axis("近さ区分")
        .reset_index(name="件数")
    )

    total = result["件数"].sum()

    result["割合_%"] = (
        result["件数"]
        / total
        * 100
        if total
        else 0
    )

    return result


# ===========================================================
# 予想 → 実際クラス遷移
# ===========================================================

def build_transition(detail):

    valid = detail[
        detail["予想クラス"].isin(CLASSES)
        & detail["実際クラス"].isin(CLASSES)
    ].copy()

    result = pd.crosstab(
        valid["予想クラス"],
        valid["実際クラス"],
        dropna=False,
    )

    result = result.reindex(
        index=CLASSES,
        columns=CLASSES,
        fill_value=0,
    )

    result.index.name = "AI予想"
    result.columns.name = "実際クラス"

    return result.reset_index()


# ===========================================================
# 予想クラス別分析
# ===========================================================

def build_predicted_class_summary(detail):

    rows = []

    for predicted_class in CLASSES:

        subset = detail[
            detail["予想クラス"]
            == predicted_class
        ]

        valid = subset[
            subset["class_distance"].notna()
        ]

        count = len(valid)

        exact = (
            valid["class_distance"] == 0
        ).sum()

        one_class = (
            valid["class_distance"].abs() == 1
        ).sum()

        near_1000 = (
            valid["absolute_boundary_difference"]
            <= 1000
        ).sum()

        near_3000 = (
            valid["absolute_boundary_difference"]
            <= 3000
        ).sum()

        near_5000 = (
            valid["absolute_boundary_difference"]
            <= 5000
        ).sum()

        near_10000 = (
            valid["absolute_boundary_difference"]
            <= 10000
        ).sum()

        rows.append(
            {
                "AI予想クラス": predicted_class,
                "件数": count,
                "完全的中件数": exact,
                "完全的中率_%":
                    exact / count * 100
                    if count else 0,
                "1クラス外れ": one_class,
                "1クラス外れ率_%":
                    one_class / count * 100
                    if count else 0,
                "±1,000円以内": near_1000,
                "±3,000円以内": near_3000,
                "±5,000円以内": near_5000,
                "±10,000円以内": near_10000,
                "平均絶対金額差":
                    valid[
                        "absolute_boundary_difference"
                    ].mean(),
                "中央値絶対金額差":
                    valid[
                        "absolute_boundary_difference"
                    ].median(),
            }
        )

    return pd.DataFrame(rows)


# ===========================================================
# 実際クラス別分析
# ===========================================================

def build_actual_class_summary(detail):

    rows = []

    for actual_class in CLASSES:

        subset = detail[
            detail["実際クラス"]
            == actual_class
        ]

        valid = subset[
            subset["class_distance"].notna()
        ]

        count = len(valid)

        ai_top = (
            valid["AI予想"]
            == actual_class
        ).sum()

        rows.append(
            {
                "実際クラス": actual_class,
                "件数": count,
                "AIが同一クラス予想": ai_top,
                "AI同一クラス率_%":
                    ai_top / count * 100
                    if count else 0,
                "平均実際払戻":
                    valid["実際払戻_数値"].mean(),
                "中央値実際払戻":
                    valid["実際払戻_数値"].median(),
                "平均絶対金額差":
                    valid[
                        "absolute_boundary_difference"
                    ].mean(),
            }
        )

    return pd.DataFrame(rows)


# ===========================================================
# 確率分析
# ===========================================================

def build_probability_summary(detail):

    valid = detail[
        detail["actual_class_probability"].notna()
    ].copy()

    if valid.empty:
        return pd.DataFrame()

    rows = []

    for rank in range(1, 9):

        subset = valid[
            valid["actual_class_probability_rank"]
            == rank
        ]

        rows.append(
            {
                "実際クラスの予測確率順位": rank,
                "件数": len(subset),
                "割合_%":
                    len(subset)
                    / len(valid)
                    * 100,
                "平均実際クラス確率_%":
                    subset[
                        "actual_class_probability"
                    ].mean(),
            }
        )

    return pd.DataFrame(rows)


# ===========================================================
# 金額差方向集計
# ===========================================================

def build_direction_summary(detail):

    valid = detail[
        detail["class_distance"].notna()
    ].copy()

    result = (
        valid["error_direction"]
        .value_counts()
        .reindex(
            [
                "予想範囲内",
                "予想より低い",
                "予想より高い",
                "判定不可",
            ],
            fill_value=0,
        )
        .rename_axis("方向")
        .reset_index(name="件数")
    )

    total = result["件数"].sum()

    result["割合_%"] = (
        result["件数"]
        / total
        * 100
        if total
        else 0
    )

    return result


# ===========================================================
# Excel保存
# ===========================================================

def save_excel(
    summary_df,
    distance_df,
    near_miss_df,
    direction_df,
    transition_df,
    predicted_df,
    actual_df,
    probability_df,
    detail_df,
):

    log("=======================================")
    log("Excel保存")
    log("=======================================")

    with pd.ExcelWriter(
        OUTPUT_XLSX,
        engine="openpyxl",
    ) as writer:

        summary_df.to_excel(
            writer,
            sheet_name="対象件数",
            index=False,
        )

        distance_df.to_excel(
            writer,
            sheet_name="クラス距離",
            index=False,
        )

        near_miss_df.to_excel(
            writer,
            sheet_name="近い外れ遠い外れ",
            index=False,
        )

        direction_df.to_excel(
            writer,
            sheet_name="金額差方向",
            index=False,
        )

        transition_df.to_excel(
            writer,
            sheet_name="予想実際遷移",
            index=False,
        )

        predicted_df.to_excel(
            writer,
            sheet_name="予想クラス別",
            index=False,
        )

        actual_df.to_excel(
            writer,
            sheet_name="実際クラス別",
            index=False,
        )

        probability_df.to_excel(
            writer,
            sheet_name="予測確率順位",
            index=False,
        )

        detail_df.to_excel(
            writer,
            sheet_name="全レース詳細",
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
    log("016 Prediction Error Analysis")
    log("=======================================")

    # -------------------------------------------------------
    # CSV読込
    # -------------------------------------------------------

    df, input_path = load_prediction()

    # -------------------------------------------------------
    # 必須列確認
    # -------------------------------------------------------

    check_columns(df)

    # -------------------------------------------------------
    # 詳細作成
    # -------------------------------------------------------

    detail_df = build_detail(df)

    # -------------------------------------------------------
    # 各種集計
    # -------------------------------------------------------

    summary_df = build_summary(
        detail_df
    )

    distance_df = build_distance_summary(
        detail_df
    )

    near_miss_df = build_near_miss_summary(
        detail_df
    )

    direction_df = build_direction_summary(
        detail_df
    )

    transition_df = build_transition(
        detail_df
    )

    predicted_df = build_predicted_class_summary(
        detail_df
    )

    actual_df = build_actual_class_summary(
        detail_df
    )

    probability_df = build_probability_summary(
        detail_df
    )

    # -------------------------------------------------------
    # ログ
    # -------------------------------------------------------

    log("=======================================")
    log("分析結果")
    log("=======================================")

    print(summary_df.to_string(index=False))
    print()

    # -------------------------------------------------------
    # Excel保存
    # -------------------------------------------------------

    save_excel(
        summary_df,
        distance_df,
        near_miss_df,
        direction_df,
        transition_df,
        predicted_df,
        actual_df,
        probability_df,
        detail_df,
    )

    # -------------------------------------------------------
    # 完了
    # -------------------------------------------------------

    log("=======================================")
    log("016 Complete")
    log("=======================================")

    print()


# ===========================================================
# 実行
# ===========================================================

if __name__ == "__main__":
    main()
