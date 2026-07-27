"""
training_base_report.py

競輪AI
Training Base レポート表示
"""

# ==========================================================
# レポート表示
# ==========================================================

def print_quality_report(
    player,
    race,
    lines,
    result,
    training,
    warning_summary,
    elapsed,
):

    print()
    print("=" * 60)
    print("TRAINING BASE REPORT")
    print("=" * 60)

    # ------------------------------------------------------
    # 入力CSV
    # ------------------------------------------------------

    print()
    print("[入力データ]")

    print(f"Player Rows : {len(player):,}")
    print(f"Race Rows   : {len(race):,}")
    print(f"Lines Rows  : {len(lines):,}")
    print(f"Result Rows : {len(result):,}")

    # ------------------------------------------------------
    # 出力CSV
    # ------------------------------------------------------

    print()
    print("[出力データ]")

    print(f"Training Rows    : {len(training):,}")
    print(f"Training Columns : {len(training.columns):,}")
    print(f"Race Count       : {training['race_key'].nunique():,}")

    # ------------------------------------------------------
    # Warning Summary
    # ------------------------------------------------------

    print()
    print("[Warning Summary]")

    for key, value in warning_summary.items():
        print(f"{key:20} : {value:,}")

    # ------------------------------------------------------
    # 実行時間
    # ------------------------------------------------------

    print()
    print("[Performance]")

    print(f"Elapsed Time : {elapsed:.2f} sec")

    # ------------------------------------------------------
    # 完了
    # ------------------------------------------------------

    print()
    print("=" * 60)
    print("REPORT END")
    print("=" * 60)