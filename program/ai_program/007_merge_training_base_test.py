"""
007_merge_training_base.py

競輪AI

現在の training_base.csv
+
2020～2022 Historical Training Base

↓

統合版 Training Base 作成

※既存 training_base.csv は直接上書きしない
※まず merged_test.csv として保存する
"""

import pandas as pd
from pathlib import Path


# ==========================================================
# 基本設定
# ==========================================================

BASE = Path(r"C:\競輪AI")

AI_DIR = (
    BASE
    / "csv"
    / "ai"
)

# ==========================================================
# 入力CSV
# ==========================================================

CURRENT_CSV = (
    AI_DIR
    / "training_base.csv"
)

HISTORICAL_CSV = (
    AI_DIR
    / "historical_training_base_2020.1.1~2022.12.31.csv"
)

# ==========================================================
# テスト出力
# ==========================================================

OUTPUT_CSV = (
    AI_DIR
    / "training_base_merged_test.csv"
)


# ==========================================================
# CSV読込
# ==========================================================

def load_csv(path, name):

    print()
    print(f"{name} 読込")
    print("-" * 60)
    print(f"ファイル : {path}")

    if not path.exists():

        raise FileNotFoundError(
            f"{name} CSVが見つかりません:\n{path}"
        )

    df = pd.read_csv(
        path,
        low_memory=False
    )

    print(
        f"レコード数 : {len(df):,}"
    )

    print(
        f"列数       : {len(df.columns):,}"
    )

    return df


# ==========================================================
# 列構成確認
# ==========================================================

def check_columns(
    current,
    historical,
):

    print()
    print("=" * 60)
    print("列構成チェック")
    print("=" * 60)

    current_columns = list(
        current.columns
    )

    historical_columns = list(
        historical.columns
    )

    print()
    print(
        f"現在 : {len(current_columns)}列"
    )

    print(
        f"過去 : {len(historical_columns)}列"
    )

    # ------------------------------------------------------
    # 現在にはあるが過去にはない列
    # ------------------------------------------------------

    current_only = [
        column
        for column in current_columns
        if column not in historical_columns
    ]

    # ------------------------------------------------------
    # 過去にはあるが現在にはない列
    # ------------------------------------------------------

    historical_only = [
        column
        for column in historical_columns
        if column not in current_columns
    ]

    print()

    print("【現在のtraining_baseにだけ存在】")

    if current_only:

        for column in current_only:
            print(
                f"  - {column}"
            )

    else:

        print("  なし")

    print()

    print("【2020～2022にだけ存在】")

    if historical_only:

        for column in historical_only:
            print(
                f"  - {column}"
            )

    else:

        print("  なし")

    # ------------------------------------------------------
    # 共通列
    # ------------------------------------------------------

    common_columns = [
        column
        for column in current_columns
        if column in historical_columns
    ]

    print()

    print(
        f"共通列 : {len(common_columns)}列"
    )

    # ------------------------------------------------------
    # 順番が違うか確認
    # ------------------------------------------------------

    if (
        not current_only
        and not historical_only
        and current_columns != historical_columns
    ):

        print()
        print(
            "WARNING"
        )

        print(
            "列数は同じですが列順が違います"
        )

        return False

    # ------------------------------------------------------
    # 列が違う場合
    # ------------------------------------------------------

    if current_only or historical_only:

        print()
        print(
            "WARNING"
        )

        print(
            "列構成が違うため、"
            "今回は結合せず停止します"
        )

        return False

    print()
    print("OK")
    print("列構成は完全一致")

    return True

# ==========================================================
# 日付情報
# ==========================================================

def show_date_range(
    df,
    name
):

    if "date" not in df.columns:

        print(
            f"{name} : date列なし"
        )

        return

    # ------------------------------------------------------
    # YYYYMMDD形式として解釈
    # ------------------------------------------------------

    dates = pd.to_datetime(
        df["date"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    valid_dates = dates.dropna()

    if len(valid_dates) == 0:

        print(
            f"{name} : 有効な日付なし"
        )

        return

    print(
        f"{name} : "
        f"{valid_dates.min().strftime('%Y/%m/%d')}"
        f" ～ "
        f"{valid_dates.max().strftime('%Y/%m/%d')}"
    )


# ==========================================================
# 重複チェック
# ==========================================================

def check_duplicates(df):

    print()
    print("=" * 60)
    print("重複チェック")
    print("=" * 60)

    required_columns = [
        "race_key",
        "car_no",
    ]

    for column in required_columns:

        if column not in df.columns:

            print(
                f"ERROR : {column}列がありません"
            )

            return False

    duplicate_mask = df.duplicated(
        subset=[
            "race_key",
            "car_no",
        ],
        keep=False
    )

    duplicate_count = int(
        duplicate_mask.sum()
    )

    duplicate_keys = int(
        df.loc[
            duplicate_mask,
            [
                "race_key",
                "car_no"
            ]
        ].drop_duplicates().shape[0]
    )

    print(
        f"重複レコード数 : "
        f"{duplicate_count:,}"
    )

    print(
        f"重複キー数     : "
        f"{duplicate_keys:,}"
    )

    if duplicate_count > 0:

        print()
        print(
            "WARNING"
        )

        print(
            "race_key + car_no に重複があります"
        )

        print()
        print(
            df.loc[
                duplicate_mask,
                [
                    "race_key",
                    "car_no",
                    "date"
                ]
            ].head(20).to_string(
                index=False
            )
        )

        return False

    print()
    print(
        "OK"
    )

    print(
        "race_key + car_no の重複なし"
    )

    return True


# ==========================================================
# データ結合
# ==========================================================

def merge_training_base(
    current,
    historical
):

    print()
    print("=" * 60)
    print("Training Base 結合")
    print("=" * 60)

    print(
        f"現在データ : {len(current):,}"
    )

    print(
        f"過去データ : {len(historical):,}"
    )

    merged = pd.concat(
        [
            historical,
            current
        ],
        axis=0,
        ignore_index=True
    )

    print()
    print(
        f"結合後 : {len(merged):,}"
    )

    # ------------------------------------------------------
    # 日付順
    # ------------------------------------------------------

    if "date" in merged.columns:

        merged["_sort_date"] = (
            pd.to_datetime(
                merged["date"],
                errors="coerce"
            )
        )

        merged = (
            merged
            .sort_values(
                [
                    "_sort_date",
                    "race_key",
                    "car_no"
                ],
                na_position="last"
            )
            .drop(
                columns=["_sort_date"]
            )
            .reset_index(
                drop=True
            )
        )

    return merged


# ==========================================================
# メイン
# ==========================================================

def main():

    print()
    print("=" * 70)
    print("007 MERGE TRAINING BASE")
    print("=" * 70)

    # ------------------------------------------------------
    # ファイル確認
    # ------------------------------------------------------

    print()
    print("入力ファイル")
    print("-" * 60)

    print(
        "現在 :",
        CURRENT_CSV
    )

    print(
        "過去 :",
        HISTORICAL_CSV
    )

    # ------------------------------------------------------
    # 読込
    # ------------------------------------------------------

    current = load_csv(
        CURRENT_CSV,
        "現在のtraining_base"
    )

    historical = load_csv(
        HISTORICAL_CSV,
        "2020～2022 Historical Training Base"
    )

    # ------------------------------------------------------
    # 日付範囲
    # ------------------------------------------------------

    print()
    print("=" * 60)
    print("日付範囲")
    print("=" * 60)

    show_date_range(
        historical,
        "Historical"
    )

    show_date_range(
        current,
        "Current"
    )

    # ------------------------------------------------------
    # Historical側の品質管理列を除外
    # ------------------------------------------------------

    REMOVE_COLUMNS = [
        "data_status",
        "warning_count",
    ]

    print()
    print("=" * 60)
    print("Historical Training Base 列調整")
    print("=" * 60)

    for column in REMOVE_COLUMNS:

        if column in historical.columns:

            print(
               f"削除 : {column}"
            )

            historical = historical.drop(
                columns=[column]
            )

        else:

            print(
                f"対象列なし : {column}"
            )

    print()
    print(
        f"Historical列数 : "
        f"{len(historical.columns)}"
    )

    # ------------------------------------------------------
    # 列構成確認
    # ------------------------------------------------------

    if not check_columns(
        current,
        historical
    ):

        raise ValueError(
            "列構成が一致していないため処理を中止しました"
        )

    # ------------------------------------------------------
    # 結合
    # ------------------------------------------------------

    merged = merge_training_base(
        current,
        historical
    )

    # ------------------------------------------------------
    # 重複確認
    # ------------------------------------------------------

    duplicate_ok = check_duplicates(
        merged
    )

    if not duplicate_ok:

        raise ValueError(
            "重複が確認されたためCSV保存を中止しました"
        )

    # ------------------------------------------------------
    # 最終確認
    # ------------------------------------------------------

    print()
    print("=" * 60)
    print("最終確認")
    print("=" * 60)

    print(
        f"現在レコード数   : "
        f"{len(current):,}"
    )

    print(
        f"過去レコード数   : "
        f"{len(historical):,}"
    )

    print(
        f"統合レコード数   : "
        f"{len(merged):,}"
    )

    print(
        f"列数             : "
        f"{len(merged.columns):,}"
    )

    print()
    print(
        "計算上のレコード数 : "
        f"{len(current) + len(historical):,}"
    )

    # ------------------------------------------------------
    # 保存
    # ------------------------------------------------------

    print()
    print("=" * 60)
    print("CSV保存")
    print("=" * 60)

    merged.to_csv(
        OUTPUT_CSV,
        index=False,
        encoding="utf-8-sig"
    )

    print()
    print(
        f"保存先 : {OUTPUT_CSV}"
    )

    print()
    print("=" * 70)
    print("007 MERGE TRAINING BASE 完了")
    print("=" * 70)


# ==========================================================
# 実行
# ==========================================================

if __name__ == "__main__":

    main()