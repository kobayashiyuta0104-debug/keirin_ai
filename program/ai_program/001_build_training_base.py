"""
001_build_training_base.py

競輪AI
Training Base 作成メインプログラム
"""

from pathlib import Path

from training_base_utils import (
    BASE,
    OUTPUT_CSV,
    load_csv,
    build_training_base,
)

from training_base_report import (
    print_quality_report,
)


# ==========================================================
# 保存フォルダ作成
# ==========================================================

OUTPUT_CSV.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================================
# メイン
# ==========================================================

def main():

    print()
    print("=" * 60)
    print("001 BUILD TRAINING BASE")
    print("=" * 60)

    # -----------------------------
    # レポート用入力CSV読込
    # -----------------------------

    player, race, lines, result = load_csv()

    # -----------------------------
    # training_base作成
    # -----------------------------

    training, warning_summary, elapsed = build_training_base(
        player,
        race,
        lines,
        result,
    )

    # -----------------------------
    # CSV保存
    # -----------------------------

    print()
    print("=" * 60)
    print("CSV保存")
    print("=" * 60)
    print(f"保存レコード数 : {len(training):,}")
    print(f"保存列数 : {len(training.columns):,}")

    training.to_csv(
        OUTPUT_CSV,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"保存先 : {OUTPUT_CSV}")

    # -----------------------------
    # レポート表示
    # -----------------------------

    print_quality_report(
        player,
        race,
        lines,
        result,
        training,
        warning_summary,
        elapsed
    )

    print()
    print("=" * 60)
    print("001 BUILD TRAINING BASE 完了")
    print("=" * 60)


# ==========================================================
# 実行
# ==========================================================

if __name__ == "__main__":

    main()

