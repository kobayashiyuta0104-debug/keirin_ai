"""
===========================================================
競輪AI 正式版

021_update_training_base.py

Part 1

・基本設定
・入力CSV設定
・バックアップ設定
・共通関数
・CSV読込
===========================================================
"""

import os
import shutil

from pathlib import Path
from datetime import datetime, timedelta, timezone

import pandas as pd


# ===========================================================
# 基本設定
# ===========================================================

if os.name == "nt":
    BASE = Path(r"C:\競輪AI")
else:
    BASE = Path(__file__).resolve().parent.parent


CSV_DIR = BASE / "csv"

PLAYER_DIR = CSV_DIR / "player"
RACE_DIR = CSV_DIR / "race"
LINES_DIR = CSV_DIR / "lines"
RESULT_DIR = CSV_DIR / "result"

AI_DIR = CSV_DIR / "ai"

TRAINING_BASE = AI_DIR / "training_base.csv"

BACKUP_DIR = AI_DIR / "backup"

BACKUP_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# ===========================================================
# 入力CSV
# ===========================================================

PLAYER_FILES = sorted(PLAYER_DIR.glob("*.csv"))

RACE_FILES = sorted(RACE_DIR.glob("*.csv"))

LINES_FILES = sorted(LINES_DIR.glob("*.csv"))

RESULT_FILES = sorted(RESULT_DIR.glob("*.csv"))

# ===========================================================
# ログ
# ===========================================================

def log(message):

    print(message)


# ===========================================================
# ファイル存在確認
# ===========================================================

def check_input_files():

    print()
    print("入力CSV確認")
    print("------------------------------")

    if len(PLAYER_FILES) == 0:
        raise FileNotFoundError("playerフォルダにCSVがありません")

    if len(RACE_FILES) == 0:
        raise FileNotFoundError("raceフォルダにCSVがありません")

    if len(LINES_FILES) == 0:
        raise FileNotFoundError("linesフォルダにCSVがありません")

    if len(RESULT_FILES) == 0:
        raise FileNotFoundError("resultフォルダにCSVがありません")

    print("Player :", len(PLAYER_FILES))
    print("Race   :", len(RACE_FILES))
    print("Lines  :", len(LINES_FILES))
    print("Result :", len(RESULT_FILES))

# ===========================================================
# CSV読込
# ===========================================================

def load_csv(files):

    print()

    df_list = []

    for path in files:

        print("読込 :", path.name)

        df = pd.read_csv(

            path,

            encoding="utf-8-sig",

            low_memory=False,

        )

        print("Rows :", len(df))

        df_list.append(df)

    merged = pd.concat(

        df_list,

        ignore_index=True,

    )

    print("------------------")

    print("Total :", len(merged))

    return merged

# ===========================================================
# training_base読込
# ===========================================================

def load_training_base():

    if not TRAINING_BASE.exists():

        print()

        print("training_base.csv がありません")

        print("新規作成します")

        return pd.DataFrame()

    print()

    print("training_base.csv 読込")

    df = pd.read_csv(

        TRAINING_BASE,

        encoding="utf-8-sig",

        low_memory=False,

    )

    print("Rows :", len(df))

    return df


# ===========================================================
# バックアップ
# ===========================================================

def backup_training_base():

    if not TRAINING_BASE.exists():

        return

    today = datetime.now().strftime("%Y%m%d")

    backup_file = (

        BACKUP_DIR /

        f"training_base_{today}.csv"

)

    shutil.copy2(

        TRAINING_BASE,

        backup_file,

    )

    print()

    print("Backup")

    print(backup_file)

# ===========================================================
# player + race
# ===========================================================

def merge_race(

    player_df,
    race_df,

):

    print()
    print("========================================")
    print("PLAYER + RACE")
    print("========================================")

    df = pd.merge(
        player_df,
        race_df,
        on="race_key",
        how="left",
        validate="many_to_one",
        suffixes=("", "_race"),
    )

    print("Rows :", len(df))

    return df


# ===========================================================
# player + lines
# ===========================================================

def merge_lines(

    df,
    lines_df,

):

    print()
    print("========================================")
    print("PLAYER + LINES")
    print("========================================")

    df = pd.merge(

        df,

        lines_df,

        on=[

            "race_key",

            "car_no",

        ],

        how="left",

        validate="one_to_one",

    )

    print("Rows :", len(df))

    return df


# ===========================================================
# player + result
# ===========================================================

def merge_result(

    df,
    result_df,

):

    print()
    print("========================================")
    print("PLAYER + RESULT")
    print("========================================")

    df = pd.merge(

        df,

        result_df,

        on=[

            "race_key",

            "car_no",

        ],

        how="left",

        validate="one_to_one",

    )

    print("Rows :", len(df))
    print(df.columns.tolist())

    return df 

# ===========================================================
# 欠損チェック
# ===========================================================

def check_missing(df):

    print()
    print("========================================")
    print("Missing Check")
    print("========================================")

    race_missing = (

        df["jo_name"]

        .isna()

        .sum()

    )

    line_missing = (

        df["line_no"]

        .isna()

        .sum()

    )

    result_missing = (

        df["finish_order"]

        .isna()

        .sum()

    )

    print()

    print("Race   :", race_missing)

    print("Lines  :", line_missing)

    print("Result :", result_missing)

    if (

        race_missing

        or line_missing

        or result_missing

    ):

        print()

        print("WARNING")

        print("欠損データがあります。")

    else:

        print()

        print("OK")

# ===========================================================
# 重複チェック
# ===========================================================

def check_duplicate(df):

    print()
    print("========================================")
    print("Duplicate Check")
    print("========================================")

    duplicate_count = (

        df.duplicated(

            subset=[

                "race_key",

                "car_no",

            ]

        )

        .sum()

    )

    print()

    print("Duplicate :", duplicate_count)

    if duplicate_count > 0:

        raise ValueError(

            "重複データがあります"

        )

    print("OK")


# ===========================================================
# training_base更新
# ===========================================================

def update_training_base(

    training_df,
    add_df,

):

    print()
    print("========================================")
    print("Training Base Update")
    print("========================================")

    before_rows = len(training_df)

    # -------------------------------------
    # 既存race_key除外
    # -------------------------------------

    if before_rows > 0:

        existing_keys = set(

            training_df["race_key"]

        )

        before_add = len(add_df)

        add_df = add_df[
            ~add_df["race_key"].isin(existing_keys)
        ]

        print()

        print("Already Exists :", before_add - len(add_df))

        print("New Race       :", len(add_df))

    add_rows = len(add_df)

    if before_rows == 0:

        merged = add_df.copy()

    else:

        merged = pd.concat(
            [
                training_df,
                add_df,
            ],
            ignore_index=True,
        )

        merged = merged.reindex(
            columns=training_df.columns
        )


    merged = merged.drop_duplicates(

        subset=[

            "race_key",

            "car_no",

        ],

        keep="last",

    )

    after_rows = len(merged)

    print()

    print("Before :", before_rows)

    print("Added  :", add_rows)

    print("After  :", after_rows)

    return merged



# ===========================================================
# 保存
# ===========================================================

def save_training_base(df):

    print()
    print("========================================")
    print("Save")
    print("========================================")

    AI_DIR.mkdir(

        parents=True,

        exist_ok=True,

    )

    df.to_csv(

        TRAINING_BASE,

        index=False,

        encoding="utf-8-sig",

    )

    print()

    print("SAVE")

    print(TRAINING_BASE)


# ===========================================================
# main
# ===========================================================

def main():

    print()
    print("========================================")
    print("021 Update Training Base")
    print("========================================")
    print()

    # -------------------------------------
    # 入力確認
    # -------------------------------------

    check_input_files()

    # -------------------------------------
    # バックアップ
    # -------------------------------------

    backup_training_base()

    # -------------------------------------
    # CSV読込
    # -------------------------------------

    player_df = load_csv(PLAYER_FILES)


    race_df = load_csv(RACE_FILES)

    race_df = race_df[
        [
            "race_key",
            "event_name",
            "grade",
            "track_length",
            "straight_length",
            "bank_angle",
            "race_type",
            "session",
            "weather",
            "wind_speed",
        ]
    ]

    lines_df = load_csv(LINES_FILES)

    lines_df = lines_df[
        [
            "race_key",
            "car_no",
            "line_no",
            "line_position",
            "is_seri",
        ]
    ]

    result_df = load_csv(RESULT_FILES)

    result_df = result_df[
        [
            "race_key",
            "car_no",
            "player_id",
            "finish_order",
            "result_status",
            "result_reason",
            "trifecta",
            "trifecta_payout",
            "popularity",
        ]
    ]

    # -------------------------------------
    # 結合
    # -------------------------------------

    df = merge_race(

        player_df,

        race_df,

    )

    df = merge_lines(

        df,

        lines_df,

    )

    df = merge_result(

        df,

        result_df,

    )

    # ==========================================
    # 列名整理
    # ==========================================

    df = df.drop(
        columns=[
            "date_y",
            "jo_code_y",
            "jo_name_y",
            "race_no_y",
        ],
        errors="ignore",
    )

    df = df.rename(
        columns={

            "date_x": "date",

            "jo_code_x": "jo_code",

            "jo_name_x": "jo_name",

            "race_no_x": "race_no",

            "player_id_x": "player_id",

            "player_id_y": "player_id_result",

        }
    )

    # ==========================================
    # 不要列削除
    # ==========================================

    df = df.drop(

        columns=[

            "date_y",

            "jo_code_y",

            "jo_name_y",

            "race_no_y",

        ],

        errors="ignore",

    )

    # ==========================================
    # 列順固定
    # ==========================================

    COLUMN_ORDER = [

        "race_key",

        "date",

        "jo_code",

        "jo_name",

        "race_no",

        "car_no",

        "player_id",

        "player_name",

        "prefecture",

        "age",

        "term",

        "class",

        "previous_class",

        "style",

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

        "event_name",

        "grade",

        "track_length",

        "straight_length",

        "bank_angle",

        "race_type",

        "session",

        "weather",

        "wind_speed",

        "line_no",

        "line_position",

        "is_seri",

        "player_id_result",

        "finish_order",

        "result_status",

        "result_reason",

        "trifecta",

        "trifecta_payout",

        "popularity",

    ]

    df = df[COLUMN_ORDER]

    # -------------------------------------
    # チェック
    # -------------------------------------

    check_missing(df)
    check_duplicate(df)

    # -------------------------------------
    # training_base更新
    # -------------------------------------

    training_df = load_training_base()

    training_df = update_training_base(

        training_df,

        df,

    )

    # -------------------------------------
    # 保存
    # -------------------------------------

    save_training_base(

        training_df,

    )

    print()
    print("========================================")
    print("Complete")
    print("========================================")


# ===========================================================
# 実行
# ===========================================================

if __name__ == "__main__":

    main()