"""
training_base_utils.py

競輪AI
001_build_training_base.py 共通関数

Version 1.0
"""

from pathlib import Path
import time
import pandas as pd


# ==========================================================
# パス設定
# ==========================================================

BASE = Path(r"C:\競輪AI")

PLAYER_DIR = BASE / "csv" / "historical_date" / "historical_player"
RACE_DIR = BASE / "csv" / "historical_date" / "historical_race"
LINES_DIR = BASE / "csv" / "historical_date" / "historical_lines"
RESULT_DIR = BASE / "csv" / "historical_date" / "historical_result"

OUTPUT_CSV = BASE / "csv" / "ai" / "training_base.csv"


# ==========================================================
# CSV読込
# ==========================================================

def load_csv():

    print()
    print("=" * 60)
    print("[1/8] CSV読込")
    print("=" * 60)

    # ======================================================
    # 読込対象ファイル
    # 2020～2022
    # 2023～2025
    # ======================================================

    target_periods = [
        "2020.1.1~2022.12.31",
        "2023.1.1~2025.12.31",
    ]

    def load_period_csv(directory, table_name):

        files = []

        for period in target_periods:

            matched = list(
                directory.glob(f"*{period}*.csv")
            )

            if not matched:

                raise FileNotFoundError(
                    f"{table_name} の {period} CSVが見つかりません："
                    f"{directory}"
                )

            files.extend(matched)

        print(
            f"{table_name} 読込ファイル数 : "
            f"{len(files)}"
        )

        frames = []

        for csv_file in sorted(files):

            print(
                f"  読込 : {csv_file.name}"
            )

            df = pd.read_csv(
                csv_file,
                low_memory=False
            )

            print(
                f"         {len(df):,} rows"
            )

            frames.append(df)

        combined = pd.concat(
            frames,
            ignore_index=True
        )

        print(
            f"  {table_name} 合計 : "
            f"{len(combined):,}"
        )

        print()

        return combined

    # ======================================================
    # 4種類のCSVを期間ごとに結合
    # ======================================================

    player = load_period_csv(
        PLAYER_DIR,
        "Player"
    )

    race = load_period_csv(
        RACE_DIR,
        "Race"
    )

    lines = load_period_csv(
        LINES_DIR,
        "Lines"
    )

    result = load_period_csv(
        RESULT_DIR,
        "Result"
    )

    # ======================================================
    # 最終件数
    # ======================================================

    print("=" * 60)
    print("CSV結合完了")
    print("=" * 60)

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
# カラム表示
# ==========================================================

def print_column_info(player, race, lines, result):

    print()
    print("=" * 60)
    print("[2/8] カラム情報")
    print("=" * 60)

    print(f"Player Columns : {len(player.columns)}")
    print(f"Race Columns   : {len(race.columns)}")
    print(f"Lines Columns  : {len(lines.columns)}")
    print(f"Result Columns : {len(result.columns)}")


# ==========================================================
# 必須カラムチェック
# ==========================================================

def check_required_columns(df, required_columns, table_name):

    missing = []

    for col in required_columns:

        if col not in df.columns:
            missing.append(col)

    if len(missing):

        print()
        print("=" * 60)
        print("FATAL ERROR")
        print("=" * 60)
        print(table_name)

        for col in missing:
            print(f"Missing : {col}")

        raise Exception("必須カラム不足")


def validate_columns(player, race, lines, result):

    print()
    print("=" * 60)
    print("[3/8] 必須カラム確認")
    print("=" * 60)

    check_required_columns(
        player,
        [
            "race_key",
            "car_no",
            "player_id"
        ],
        "PLAYER"
    )

    check_required_columns(
        race,
        [
            "race_key"
        ],
        "RACE"
    )

    check_required_columns(
        lines,
        [
            "race_key",
            "car_no"
        ],
        "LINES"
    )

    check_required_columns(
        result,
        [
            "race_key",
            "car_no",
            "player_id"
        ],
        "RESULT"
    )

    print("OK")


# ==========================================================
# 重複チェック
# ==========================================================

def duplicate_check(df, keys, table_name):

    dup = df[df.duplicated(keys, keep=False)]

    if len(dup):

        print()
        print("=" * 60)
        print("FATAL ERROR")
        print("=" * 60)

        print(table_name)
        print(f"Duplicate Key : {keys}")
        print(f"Duplicate Rows : {len(dup):,}")

        print()

        print(
            dup[keys]
            .sort_values(keys)
            .head(20)
        )

        raise Exception("重複データ検出")


def validate_duplicates(player, race, lines, result):

    print()
    print("=" * 60)
    print("[4/8] 重複チェック")
    print("=" * 60)

    duplicate_check(
        race,
        ["race_key"],
        "RACE"
    )

    duplicate_check(
        player,
        ["race_key", "car_no"],
        "PLAYER"
    )

    duplicate_check(
        lines,
        ["race_key", "car_no"],
        "LINES"
    )

    duplicate_check(
        result,
        ["race_key", "car_no"],
        "RESULT"
    )

    print("OK")


# ==========================================================
# merge対象列取得
# ==========================================================

def get_unique_columns(left_df, right_df, join_keys):

    columns = []

    for col in right_df.columns:

        if col in join_keys:
            continue

        if col in left_df.columns:
            continue

        columns.append(col)

    return join_keys + columns


# ==========================================================
# Warning列初期化
# ==========================================================

def initialize_warning_columns(df):

    df["data_status"] = ""
    df["warning_count"] = 0

    return df

# ==========================================================
# Warning追加
# ==========================================================

def add_warning(df, mask, warning_name):

    if mask.sum() == 0:
        return

    empty_mask = mask & (df["data_status"] == "")

    df.loc[
        empty_mask,
        "data_status"
    ] = warning_name

    exist_mask = mask & (df["data_status"] != "")

    df.loc[
        exist_mask,
        "data_status"
    ] = (
        df.loc[
            exist_mask,
            "data_status"
        ]
        + ";"
        + warning_name
    )

    df.loc[
        mask,
        "warning_count"
    ] += 1


# ==========================================================
# CSV結合
# ==========================================================

def merge_training_tables(player, race, lines, result):

    print()
    print("=" * 60)
    print("[5/8] CSV結合")
    print("=" * 60)

    training = player.copy()

    training = initialize_warning_columns(training)

    # --------------------------------------------------
    # Race
    # --------------------------------------------------

    race_columns = get_unique_columns(
        training,
        race,
        ["race_key"]
    )

    training = training.merge(
        race[race_columns],
        how="left",
        on="race_key",
        validate="many_to_one",
        indicator="_merge_race"
    )

    print("Race   OK")

    # --------------------------------------------------
    # Lines
    # --------------------------------------------------

    lines_columns = get_unique_columns(
        training,
        lines,
        [
            "race_key",
            "car_no"
        ]
    )

    training = training.merge(
        lines[lines_columns],
        how="left",
        on=[
            "race_key",
            "car_no"
        ],
        validate="one_to_one",
        indicator="_merge_lines"
    )

    print("Lines  OK")

    # --------------------------------------------------
    # Result
    # --------------------------------------------------

    result_tmp = result.rename(
        columns={
            "player_id": "player_id_result"
        }
    )

    result_columns = get_unique_columns(
        training,
        result_tmp,
        [
            "race_key",
            "car_no"
        ]
    )

    training = training.merge(
        result_tmp[result_columns],
        how="left",
        on=[
            "race_key",
            "car_no"
        ],
        validate="one_to_one",
        indicator="_merge_result"
    )

    print("Result OK")

    print()
    print("CSV結合完了")
    print(f"Training Rows : {len(training):,}")
    print(
        f"Race Count : "
        f"{training['race_key'].nunique():,}"
    )

    return training


# ==========================================================
# Warning生成
# ==========================================================

def build_warning_status(training):

    print()
    print("=" * 60)
    print("[6/8] Warning生成")
    print("=" * 60)

    add_warning(
        training,
        training["_merge_race"] == "left_only",
        "MISSING_RACE"
    )

    add_warning(
        training,
        training["_merge_lines"] == "left_only",
        "MISSING_LINES"
    )

    add_warning(
        training,
        training["_merge_result"] == "left_only",
        "MISSING_RESULT"
    )

    training.loc[
        training["warning_count"] == 0,
        "data_status"
    ] = "OK"

    print("OK")

    return training


# ==========================================================
# player_id整合性チェック
# ==========================================================

def validate_player_id(training):

    print()
    print("=" * 60)
    print("[7/8] player_id整合性チェック")
    print("=" * 60)

    if "player_id_result" not in training.columns:

        print("Result列なし")
        return

    check = (
        training["player_id_result"].notna()
        &
        (
            training["player_id"]
            !=
            training["player_id_result"]
        )
    )

    if check.sum():

        print()
        print("=" * 60)
        print("FATAL ERROR")
        print("=" * 60)

        print(
            training.loc[
                check,
                [
                    "race_key",
                    "car_no",
                    "player_id",
                    "player_id_result"
                ]
            ].head(20)
        )

        raise Exception("player_id mismatch")

    print("OK")

# ==========================================================
# レコード数チェック
# ==========================================================

def validate_record_count(player, training):

    print()
    print("=" * 60)
    print("[8/8] レコード数チェック")
    print("=" * 60)

    if len(training) != len(player):

        print()
        print("=" * 60)
        print("FATAL ERROR")
        print("=" * 60)
        print(f"Player   : {len(player):,}")
        print(f"Training : {len(training):,}")

        raise Exception("レコード数不一致")

    print("OK")


# ==========================================================
# merge補助列削除
# ==========================================================

def cleanup_columns(training):

    drop_columns = [
        "_merge_race",
        "_merge_lines",
        "_merge_result"
    ]

    for col in drop_columns:

        if col in training.columns:

            training.drop(
                columns=col,
                inplace=True
            )

    return training


# ==========================================================
# Warning集計
# ==========================================================

def build_warning_summary(training):

    summary = {
        "OK": 0,
        "MISSING_RACE": 0,
        "MISSING_LINES": 0,
        "MISSING_RESULT": 0,
        "MULTIPLE_WARNING": 0,
        "TOTAL": len(training)
    }

    summary["OK"] = (
        training["warning_count"] == 0
    ).sum()

    summary["MISSING_RACE"] = (
        training["data_status"]
        .str.contains(
            "MISSING_RACE",
            na=False
        )
    ).sum()

    summary["MISSING_LINES"] = (
        training["data_status"]
        .str.contains(
            "MISSING_LINES",
            na=False
        )
    ).sum()

    summary["MISSING_RESULT"] = (
        training["data_status"]
        .str.contains(
            "MISSING_RESULT",
            na=False
        )
    ).sum()

    summary["MULTIPLE_WARNING"] = (
        training["warning_count"] > 1
    ).sum()

    print()

    for k, v in summary.items():
        print(f"{k:20} : {v:,}")

    return summary


# ==========================================================
# training_base作成
# ==========================================================

def build_training_base(
    player,
    race,
    lines,
    result,
):

    start_time = time.time()
    print_column_info(
        player,
        race,
        lines,
        result
    )

    validate_columns(
        player,
        race,
        lines,
        result
    )

    validate_duplicates(
        player,
        race,
        lines,
        result
    )

    training = merge_training_tables(
        player,
        race,
        lines,
        result
    )

    training = build_warning_status(training)

    validate_player_id(training)

    validate_record_count(
        player,
        training
    )

    training = cleanup_columns(training)

    warning_summary = build_warning_summary(training)

    elapsed = time.time() - start_time

    return (
        training,
        warning_summary,
        elapsed
    )
