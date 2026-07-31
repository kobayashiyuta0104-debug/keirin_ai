"""
===========================================================
競輪AI Ver1.0
026_build_training_race_features.py

学習用レース特徴量生成

【役割】

training_features.csv
（1選手1行）

↓

1レース1行へ変換

↓

training_race_features.csv

※Part1
・基本設定
・CSV読込
・特徴量定義
・race_keyグループ作成

===========================================================
"""

import os

import pandas as pd

from pathlib import Path


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

CSV_AI = (
    BASE
    / "csv"
    / "ai"
)

INPUT_CSV = (
    CSV_AI
    / "training_features.csv"
)

OUTPUT_CSV = (
    CSV_AI
    / "training_race_features.csv"
)


# ===========================================================
# ログ
# ===========================================================

def log(message):

    print(f"[026_build_training_race_features] {message}")


# ===========================================================
# レース特徴量
# ===========================================================

RACE_COLUMNS = [

    "race_key",

    "date",

    "jo_code",

    "jo_name",

    "race_no",

    "weekday",

    "grade",

    "race_type",

    "session",

    "bank_type",

    "straight_type",

    "bank_angle",

]


# ===========================================================
# 選手特徴量
# ===========================================================

PLAYER_FEATURE_COLUMNS = [

    "age",

    "term",

    "class",

    "previous_class",

    "average_score",

    "win_rate",

    "quinella_rate",

    "trio_rate",

    "escape_count",

    "makuri_count",

    "sashi_count",

    "mark_count",

    "back_count",

    "home_count",

    "start_count",

    "style_両",

    "style_追",

    "style_逃",

    "is_seri",

    "score_rank",

    "win_rate_rank",

    "quinella_rate_rank",

    "trio_rate_rank",

    "line_score_rank",

    "line_win_rate_rank",

    "line_quinella_rate_rank",

    "line_trio_rate_rank",

    "score_diff_top",

    "win_rate_diff_top",

    "quinella_rate_diff_top",

    "trio_rate_diff_top",

    "line_score_diff_top",

    "line_win_rate_diff_top",

    "line_quinella_rate_diff_top",

    "line_trio_rate_diff_top",

]


# ===========================================================
# CSV読込
# ===========================================================

def load_training_features():

    log("=======================================")
    log("training_features.csv 読込")
    log("=======================================")

    if not INPUT_CSV.exists():

        raise FileNotFoundError(INPUT_CSV)

    df = pd.read_csv(

        INPUT_CSV,

        encoding="utf-8-sig",

        low_memory=False,

    )

    log(f"Rows    : {len(df):,}")

    log(f"Columns : {len(df.columns):,}")

    print()

    return df


# ===========================================================
# race_key グループ作成
# ===========================================================

def create_race_groups(df):

    log("=======================================")
    log("race_key Group")
    log("=======================================")

    race_groups = list(

        df.groupby(

            "race_key",

            sort=False,

        )

    )

    log(f"Race Count : {len(race_groups):,}")

    print()

    return race_groups

# ===========================================================
# 1レース1行へ横展開
# ===========================================================

def build_training_race_features(race_groups):

    log("=======================================")
    log("Build Race Features")
    log("=======================================")

    # 最終的にここへ1レース1辞書ずつ追加する
    race_rows = []

    # =======================================================
    # race_keyごとに処理
    # =======================================================

    for race_index, (race_key, race_df) in enumerate(race_groups, start=1):

        log(f"[{race_index}/{len(race_groups)}] {race_key}")

        # レース1行分
        race_row = {}

        # ---------------------------------------------------
        # レース情報
        # （同一レースなので先頭行を採用）
        # ---------------------------------------------------

        first_row = race_df.iloc[0]

        for column in RACE_COLUMNS:

            if column in race_df.columns:

                race_row[column] = first_row[column]

            else:

                race_row[column] = pd.NA

        # ---------------------------------------------------
        # ライン番号順
        # ---------------------------------------------------

        for line_no in range(1, 10):

            # 該当ラインのみ抽出
            line_df = race_df[
                race_df["line_no"] == line_no
            ].copy()

            # ライン内順位順
            if len(line_df) > 0:

                line_df = line_df.sort_values(
                    "line_position"
                )

            # -----------------------------------------------
            # ライン内 P1～P9
            # -----------------------------------------------

            for position in range(1, 10):

                prefix = f"L{line_no}_P{position}"

                # -------------------------------
                # 選手が存在する場合
                # -------------------------------

                if position <= len(line_df):

                    player = line_df.iloc[position - 1]

                    for feature in PLAYER_FEATURE_COLUMNS:

                        column_name = f"{prefix}_{feature}"

                        if feature in player.index:

                            race_row[column_name] = player[feature]

                        else:

                            race_row[column_name] = pd.NA

                # -------------------------------
                # 存在しない選手
                # -------------------------------

                else:

                    for feature in PLAYER_FEATURE_COLUMNS:

                        column_name = f"{prefix}_{feature}"

                        race_row[column_name] = pd.NA

# ===========================================================
# 教師データ追加
# ===========================================================

        # payout_class は同一レースで共通なので先頭行を採用
        if "payout_class" in race_df.columns:

            race_row["payout_class"] = first_row["payout_class"]

        else:

            race_row["payout_class"] = pd.NA

        # 1レース分追加
        race_rows.append(race_row)

    print()

    log(f"Race Rows : {len(race_rows):,}")

    print()

    return pd.DataFrame(race_rows)


# ===========================================================
# CSV保存
# ===========================================================

def save_training_race_features(df):

    log("=======================================")
    log("Save CSV")
    log("=======================================")

    # 出力フォルダが無ければ作成
    OUTPUT_CSV.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(

        OUTPUT_CSV,

        index=False,

        encoding="utf-8-sig",

    )

    log(f"Save : {OUTPUT_CSV}")

    log(f"Rows : {len(df):,}")

    log(f"Columns : {len(df.columns):,}")

    print()


# ===========================================================
# Main
# ===========================================================

def main():

    print()

    log("=======================================")
    log("026 Build Training Race Features")
    log("=======================================")

    # CSV読込
    df = load_training_features()

    # race_keyごとにグループ化
    race_groups = create_race_groups(df)

    # 1レース1行へ変換
    race_feature_df = build_training_race_features(
        race_groups
    )

    # CSV保存
    save_training_race_features(
        race_feature_df
    )

    log("Complete")


# ===========================================================
# 実行
# ===========================================================

if __name__ == "__main__":

    main()
