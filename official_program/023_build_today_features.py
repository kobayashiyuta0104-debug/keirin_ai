"""
===========================================================
競輪AI Ver1.0
023_build_today_features.py

当日予測特徴量生成

【役割】

today_player.json
today_race.json
today_lines.json

↓

DataFrame結合

↓

Feature Generator実行

↓

予測用CSV作成

today_features.csv 保存
（毎日上書き）

DataFrameもreturn

===========================================================
"""
import json
import os
import sys

import pandas as pd

from pathlib import Path

if os.name == "nt":

    BASE = Path(r"C:\競輪AI")

else:

    BASE = Path(__file__).resolve().parent.parent

sys.path.append(
    str(BASE / "program" / "ai_program")
)

from feature_generator.feature_player import build_feature_player
from feature_generator.feature_line import build_feature_line
from feature_generator.feature_race import build_feature_race
from feature_generator.feature_rank import build_feature_rank
from feature_generator.feature_relative import build_feature_relative

# ===========================================================
# 入力JSON
# ===========================================================

TODAY_DIR = (
    BASE
    / "data_official"
    / "today"
)

PLAYER_JSON = TODAY_DIR / "today_player.json"

RACE_JSON = TODAY_DIR / "today_race.json"

SESSION_MASTER = (
    BASE
    / "data_official"
    / "master"
    / "session_master.json"
)

LINES_JSON = TODAY_DIR / "today_lines.json"

CSV_AI = (
    BASE
    / "csv"
    / "ai"
)

OUTPUT_CSV = (
    CSV_AI
    / "today_features.csv"
)

# ===========================================================
# ログ
# ===========================================================

def log(message):

    print(f"[023_build_today_features] {message}")


# ===========================================================
# JSON読込
# ===========================================================

def load_json(path):

    if not path.exists():

        raise FileNotFoundError(path)

    with open(

        path,

        "r",

        encoding="utf-8"

    ) as f:

        return json.load(f)


# ===========================================================
# JSON読込
# ===========================================================

def load_today_data():

    log("=======================================")
    log("Today JSON 読込開始")
    log("=======================================")

    player_json = load_json(PLAYER_JSON)

    race_json = load_json(RACE_JSON)

    lines_json = load_json(LINES_JSON)

    session_master = load_json(SESSION_MASTER)

    log("読込完了")

    print()

    return (

        player_json,

        race_json,

        lines_json,

        session_master,

    )


# ===========================================================
# DataFrame作成
# ===========================================================

def build_dataframe(

    player_json,

    race_json,

    lines_json,

    session_master,

):
    log("Player DataFrame作成")

    player_df = pd.DataFrame(

        player_json["players"]

    )

    log(f"Rows : {len(player_df):,}")

    print()

    # ------------------------------------------------------
    # Race
    # ------------------------------------------------------

    log("Race DataFrame作成")

    race_df = pd.DataFrame(

        race_json["races"]

    )

    race_df = race_df.rename(columns={

    "開催日": "date",

    "競輪場コード": "jo_code",

    "競輪場名": "jo_name",

    "開催名": "event_name",

    "グレード": "grade",

    "レース番号": "race_no",

    "周長(m)": "track_length",

    "みなし直線(m)": "straight_length",

    "カント角(度)": "bank_angle",

    "レース種別": "race_type",

    "発走時刻": "race_time",

    "天候": "weather",

    "風速": "wind_speed",

    })

    race_df["session"] = race_df["race_time"]

    # ------------------------------------------------------
    # 開催区分(session)判定
    # ------------------------------------------------------

    def to_minutes(t):
        h, m = map(int, t.split(":"))
        return h * 60 + m

    race_df["race_minutes"] = race_df["race_time"].apply(to_minutes)

    race_df["session"] = ""

    for (date, jo_name), group in race_df.groupby(["date", "jo_name"]):

        first_time = group["race_minutes"].min()
        last_time = group["race_minutes"].max()

        session_name = "不明"

        for item in session_master:

            if (
                item["first_min"] <= first_time <= item["first_max"]
                and
                item["last_min"] <= last_time <= item["last_max"]
            ):

                session_name = item["display_name"]
                break

        race_df.loc[
            (race_df["date"] == date)
            &
            (race_df["jo_name"] == jo_name),
            "session"
        ] = session_name

    race_df = race_df.drop(columns=["race_minutes"])

    race_df = race_df.drop(

        columns=[

            "距離",

            "周回数",

            "投票締切",

        ],

        errors="ignore",

    )

    log(f"Rows : {len(race_df):,}")

    print()

    # ------------------------------------------------------
    # Lines
    # ------------------------------------------------------

    log("Lines DataFrame作成")

    line_rows = []

    for race in lines_json["races"]:

        race_key = race["race_key"]

        for car_no, info in race["cars"].items():

            if info["line"] is None:

                continue

            row = {

                "race_key": race_key,

                "car_no": int(car_no),

                "line_no": info["line"],

                "line_position": info["position"],

                "is_seri": info["seri"],

            }

            line_rows.append(row)

    lines_df = pd.DataFrame(line_rows)

    log(f"Rows : {len(lines_df):,}")

    print()

    # ------------------------------------------------------
    # PLAYER + RACE
    # ------------------------------------------------------

    log("=======================================")
    log("PLAYER + RACE")
    log("=======================================")

    race_df = race_df.drop(

        columns=[

            "date",

            "jo_code",

            "jo_name",

            "race_no",

        ],

        errors="ignore",

    )

    df = pd.merge(

        player_df,

        race_df,

        on="race_key",

        how="left",

        validate="many_to_one",

    )

    log(f"Rows : {len(df):,}")

    print()

    # ------------------------------------------------------
    # PLAYER + LINES
    # ------------------------------------------------------

    log("=======================================")
    log("PLAYER + LINES")
    log("=======================================")

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

    log(f"Rows : {len(df):,}")

    print()

    print("=======================================")
    print("Missing Check")
    print("=======================================")
    
    print()
    
    print(
        "Race  :",
        df["event_name"].isna().sum()
    )
    
    print(
        "Lines :",
        df["line_no"].isna().sum()
    )
    
    print()
    
    if (
        df["event_name"].isna().sum()
        or
        df["line_no"].isna().sum()
    ):
    
        print("WARNING")
        print("欠損データがあります")
    
    else:
    
        print("OK")
    
    print()

    # ------------------------------------------------------
    # 並び替え
    # ------------------------------------------------------

    df = df.sort_values(

        [

            "race_key",

            "car_no",

        ]

    ).reset_index(

        drop=True

    )
    
    log("DataFrame完成")

    print()

    return df

# ===========================================================
# CSV保存
# ===========================================================

def save_today_features(df):

    log("=======================================")
    log("today_features.csv 保存")
    log("=======================================")

    OUTPUT_CSV.parent.mkdir(

        parents=True,

        exist_ok=True,

    )

    df.to_csv(

        OUTPUT_CSV,

        index=False,

        encoding="utf-8-sig",

    )

    log(f"保存先 : {OUTPUT_CSV}")

    print()


# ===========================================================
# Feature Generator実行
# ===========================================================

def build_today_features():

    """
    当日予測特徴量生成
    """

    (
        player_json,
        race_json,
        lines_json,
        session_master,
    ) = load_today_data()

    df = build_dataframe(

        player_json,

        race_json,

        lines_json,

        session_master,

    )

    log("=======================================")
    log("Feature Generator開始")
    log("=======================================")

    # --------------------------------------------------
    # Player特徴量
    # --------------------------------------------------

    df = build_feature_player(df)

    # --------------------------------------------------
    # Line特徴量
    # --------------------------------------------------

    df = build_feature_line(df)

    # --------------------------------------------------
    # Race特徴量
    # --------------------------------------------------

    df = build_feature_race(df)

    # --------------------------------------------------
    # Rank特徴量
    # --------------------------------------------------

    df = build_feature_rank(df)

    # --------------------------------------------------
    # Relative特徴量
    # --------------------------------------------------

    df = build_feature_relative(df)

    log("=======================================")
    log("Feature Generator完了")
    log("=======================================")

    print()

    return df


# ===========================================================
# Main
# ===========================================================

def main():

    print()

    log("=======================================")
    log("023 Today Features")
    log("=======================================")

    df = build_today_features()

    save_today_features(df)

    print(df.info())

    print()

    print(df.head())

    print()

    print(df.tail())

    print()

    log("Rows : {:,}".format(len(df)))

    log("Columns : {:,}".format(len(df.columns)))

    print()

    log("Complete")


# ===========================================================
# 実行
# ===========================================================

if __name__ == "__main__":

    main()