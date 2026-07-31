"""
===========================================================
競輪AI Ver1.0
022_build_training_features.py

特徴量生成

【役割】

training_base.csv を読み込み、
Feature Generatorを順番に実行し、
training_features.csv を生成する。

入力

C:\競輪AI\csv\ai\training_base.csv

出力

C:\競輪AI\csv\ai\training_features.csv

===========================================================
"""
import sys
from pathlib import Path
import os

if os.name == "nt":
    BASE = Path(r"C:\競輪AI")
else:
    BASE = Path(__file__).resolve().parent.parent

sys.path.append(str(BASE / "program" / "ai_program"))

import pandas as pd

from feature_generator.feature_player import build_feature_player
from feature_generator.feature_line import build_feature_line
from feature_generator.feature_race import build_feature_race
from feature_generator.feature_rank import build_feature_rank
from feature_generator.feature_relative import build_feature_relative
from feature_generator.feature_target import build_feature_target


# ===========================================================
# パス設定
# ===========================================================

import os

if os.name == "nt":
    BASE = Path(r"C:\競輪AI")
else:
    BASE = Path(__file__).resolve().parent.parent

CSV_AI = BASE / "csv" / "ai"

INPUT_CSV = CSV_AI / "training_base.csv"

OUTPUT_CSV = CSV_AI / "training_features.csv"


# ===========================================================
# ログ表示
# ===========================================================

def log(message):
    """
    ログ表示
    """

    print(f"[022_build_training_features] {message}")


# ===========================================================
# CSV読込
# ===========================================================

def load_training_base():
    """
    training_base.csv読込
    """

    log("=======================================")
    log("training_base.csv 読込開始")
    log("=======================================")

    if not INPUT_CSV.exists():

        print()

        print("=======================================")
        print("ERROR")
        print("training_base.csv が存在しません")
        print(INPUT_CSV)
        print("=======================================")

        raise FileNotFoundError(INPUT_CSV)

    df = pd.read_csv(

        INPUT_CSV,

        encoding="utf-8-sig",

        low_memory=False,

    )

    log(f"読込完了 : {len(df):,} 件")

    print()

    return df

# ===========================================================
# Feature Generator実行
# ===========================================================

def build_features(df):
    """
    Feature Generator実行
    """

    log("=======================================")
    log("特徴量生成開始")
    log("=======================================")

    input_rows = len(df)

    # --------------------------------------------------
    # Player特徴量
    # --------------------------------------------------
    log("Player特徴量生成")

    df = build_feature_player(df)

    # --------------------------------------------------
    # Line特徴量
    # --------------------------------------------------
    log("Line特徴量生成")

    df = build_feature_line(df)

    # --------------------------------------------------
    # Race特徴量
    # --------------------------------------------------
    log("Race特徴量生成")

    df = build_feature_race(df)

    # --------------------------------------------------
    # Rank特徴量
    # --------------------------------------------------
    log("Rank特徴量生成")

    df = build_feature_rank(df)

    # --------------------------------------------------
    # Relative特徴量
    # --------------------------------------------------
    log("Relative特徴量生成")

    df = build_feature_relative(df)

    # --------------------------------------------------
    # Target生成
    # --------------------------------------------------
    log("Target生成")

    df = build_feature_target(df)

    output_rows = len(df)

    print()

    log("=======================================")
    log("特徴量生成完了")
    log("=======================================")

    log(f"入力件数 : {input_rows:,}")
    log(f"出力件数 : {output_rows:,}")

    print()

    log("DataFrame情報")

    print()

    df.info()

    print()

    log("先頭5件")

    print(df.head())

    print()

    log("末尾5件")

    print(df.tail())

    print()

    return df

# ===========================================================
# CSV保存
# ===========================================================

def save_training_features(df):
    """
    training_features.csv保存
    """

    log("=======================================")
    log("training_features.csv 保存開始")
    log("=======================================")

    CSV_AI.mkdir(

        parents=True,

        exist_ok=True,

    )

    df.to_csv(

        OUTPUT_CSV,

        index=False,

        encoding="utf-8-sig",

    )

    log("保存完了")

    log(f"保存先 : {OUTPUT_CSV}")

    print()


# ===========================================================
# メイン処理
# ===========================================================

def main():
    """
    メイン処理
    """

    print()

    log("=======================================")
    log("022 特徴量生成開始")
    log("=======================================")

    # -----------------------------
    # CSV読込
    # -----------------------------
    df = load_training_base()

    # -----------------------------
    # Feature Generator実行
    # -----------------------------
    df = build_features(df)

    # -----------------------------
    # CSV保存
    # -----------------------------
    save_training_features(df)

    log("=======================================")
    log("022 特徴量生成 完了")
    log("=======================================")

    print()


# ===========================================================
# 実行
# ===========================================================

if __name__ == "__main__":

    main()