"""
002_build_historical_training_base.py

競輪AI
2020/01/01 ～ 2022/12/31
Historical Training Base 作成
"""

from pathlib import Path
import pandas as pd

from training_base_utils import (
    build_training_base,
)

# ==========================================================
# 基本設定
# ==========================================================

BASE = Path(r"C:\競輪AI")

TARGET_START = "20200101"
TARGET_END = "20221231"

# ==========================================================
# Historical CSV
# ==========================================================

PLAYER_CSV = (
    BASE
    / "csv"
    / "historical_date"
    / "historical_player"
    / "historical_player_2020.1.1~2022.12.31.csv"
)

RACE_CSV = (
    BASE
    / "csv"
    / "historical_date"
    / "historical_race"
    / "historical_race_2020.1.1~2022.12.31.csv"
)

LINES_CSV = (
    BASE
    / "csv"
    / "historical_date"
    / "historical_lines"
    / "historical_lines_2020.1.1~2022.12.31.csv"
)

RESULT_CSV = (
    BASE
    / "csv"
    / "historical_date"
    / "historical_result"
    / "historical_result_2020.1.1~2022.12.31.csv"
)

# ==========================================================
# 出力
# ==========================================================

OUTPUT_CSV = (
    BASE
    / "csv"
    / "ai"
    / "historical_training_base_2020.1.1~2022.12.31.csv"
)

OUTPUT_CSV.parent.mkdir(
    parents=True,
    exist_ok=True
)

# ==========================================================
# CSV読込
# ==========================================================

def load_historical_csv():

    csv_files = {
        "Player": PLAYER_CSV,
        "Race": RACE_CSV,
        "Lines": LINES_CSV,
        "Result": RESULT_CSV,
    }

    print()
    print("=" * 60)
    print("Historical CSV 読込")
    print("=" * 60)

    for name, path in csv_files.items():

        if not path.exists():

            raise FileNotFoundError(
                f"{name} CSVがありません:\n{path}"
            )

        print(
            f"{name:<8}: {path}"
        )

    player = pd.read_csv(
        PLAYER_CSV,
        low_memory=False
    )

    race = pd.read_csv(
        RACE_CSV,
        low_memory=False
    )

    lines = pd.read_csv(
        LINES_CSV,
        low_memory=False
    )

    result = pd.read_csv(
        RESULT_CSV,
        low_memory=False
    )

    print()
    print(f"Player : {len(player):,}")
    print(f"Race   : {len(race):,}")
    print(f"Lines  : {len(lines):,}")
    print(f"Result : {len(result):,}")

    return (
        player,
        race,
        lines,
        result
    )

# ==========================================================
# メイン
# ==========================================================

def main():

    print()
    print("=" * 60)
    print("006 BUILD HISTORICAL TRAINING BASE")
    print("=" * 60)

    print()
    print(
        f"対象期間 : "
        f"{TARGET_START} ～ {TARGET_END}"
    )

    # ------------------------------------------------------
    # CSV読込
    # ------------------------------------------------------

    player, race, lines, result = (
        load_historical_csv()
    )

    # ------------------------------------------------------
    # training_base作成
    # ------------------------------------------------------

    print()
    print("=" * 60)
    print("Historical Training Base 作成")
    print("=" * 60)

    training, warning_summary, elapsed = (
        build_training_base(
            player,
            race,
            lines,
            result,
        )
    )

    # ------------------------------------------------------
    # CSV保存
    # ------------------------------------------------------

    print()
    print("=" * 60)
    print("CSV保存")
    print("=" * 60)

    print(
        f"保存レコード数 : "
        f"{len(training):,}"
    )

    print(
        f"保存列数 : "
        f"{len(training.columns):,}"
    )

    training.to_csv(
        OUTPUT_CSV,
        index=False,
        encoding="utf-8-sig"
    )

    print()
    print(
        f"保存先 : {OUTPUT_CSV}"
    )

    print()
    print("=" * 60)
    print("006 BUILD HISTORICAL TRAINING BASE 完了")
    print("=" * 60)


# ==========================================================
# 実行
# ==========================================================

if __name__ == "__main__":

    main()