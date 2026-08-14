"""
===========================================================
競輪AI Ver1.0
009_build_historical_features.py

2020/01/01 ～ 2022/12/31
Historical予測特徴量生成

【役割】

Historical JSON
    player
    race_data
    lines

↓

023_build_today_features.py と同じDataFrame構成

↓

Feature Generator
    Player
    Line
    Race
    Rank
    Relative

↓

1日分の特徴量

↓

全日分をCSVへ追加

↓

training_features(2020.1.1~2022.12.31).csv

※特徴量ロジックは023と同じ
※結果JSONは使用しない
===========================================================
"""

import json
import os
import sys
import tempfile

import pandas as pd

from pathlib import Path
from datetime import datetime, timedelta


# ===========================================================
# 基本設定
# ===========================================================

if os.name == "nt":

    BASE = Path(r"C:\競輪AI")

else:

    BASE = Path(__file__).resolve().parent.parent


# ===========================================================
# Feature Generator読込
# ===========================================================

sys.path.append(
    str(BASE / "program" / "ai_program")
)


from feature_generator.feature_player import (
    build_feature_player
)

from feature_generator.feature_line import (
    build_feature_line
)

from feature_generator.feature_race import (
    build_feature_race
)

from feature_generator.feature_rank import (
    build_feature_rank
)

from feature_generator.feature_relative import (
    build_feature_relative
)


# ===========================================================
# 対象期間
# ===========================================================

START_DATE = datetime(
    2020,
    1,
    1
)

END_DATE = datetime(
    2022,
    12,
    31
)


# ===========================================================
# Historical JSON
# ===========================================================

HISTORICAL_DIR = (
    BASE
    / "data_official"
    / "historical"
)


PLAYER_DIR = (
    HISTORICAL_DIR
    / "player"
)

RACE_DIR = (
    HISTORICAL_DIR
    / "race_data"
)

LINES_DIR = (
    HISTORICAL_DIR
    / "lines"
)


# ===========================================================
# Session Master
# ===========================================================

SESSION_MASTER = (
    BASE
    / "data_official"
    / "master"
    / "session_master.json"
)


# ===========================================================
# CSV保存先
# ===========================================================

OUTPUT_DIR = (
    BASE
    / "csv"
    / "ai"
)


OUTPUT_CSV = (
    OUTPUT_DIR
    / "training_features(2020.1.1~2022.12.31).csv"
)


# ===========================================================
# ログ
# ===========================================================

def log(message):

    print(
        f"[009_build_historical_features] {message}"
    )


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
# 日付生成
# ===========================================================

def generate_dates():

    current = START_DATE

    while current <= END_DATE:

        yield current.strftime("%Y%m%d")

        current += timedelta(days=1)


# ===========================================================
# Historical JSON読込
# ===========================================================

def load_historical_data(target_date):

    player_file = (
        PLAYER_DIR
        / f"{target_date}_player.json"
    )

    race_file = (
        RACE_DIR
        / f"{target_date}_race_data.json"
    )

    lines_file = (
        LINES_DIR
        / f"{target_date}_lines.json"
    )

    player_json = load_json(
        player_file
    )

    race_json = load_json(
        race_file
    )

    lines_json = load_json(
        lines_file
    )

    session_master = load_json(
        SESSION_MASTER
    )

    return (
        player_json,
        race_json,
        lines_json,
        session_master
    )


# ===========================================================
# Player DataFrame
#
# Historical player.json
#
# venues
#   └ races
#       └ jsj006
#           └ sensyuTypeInfo
#
# ↓
#
# 023と同じplayer DataFrame
# ===========================================================

def build_player_dataframe(player_json):

    log("Player DataFrame作成")

    rows = []

    venues = player_json.get(
        "venues",
        []
    )

    for venue in venues:

        venue_name = venue.get(
            "venue"
        )

        bank_code = str(
            venue.get(
                "bank_code",
                ""
            )
        ).zfill(2)

        races = venue.get(
            "races",
            []
        )

        for race in races:

            race_key = race.get(
                "race_key"
            )

            race_no = race.get(
                "race_no"
            )

            jsj006 = race.get(
                "jsj006"
            )

            if not isinstance(
                jsj006,
                dict
            ):
                continue

            players_raw = jsj006.get(
                "sensyuTypeInfo",
                []
            )

            if not isinstance(
                players_raw,
                list
            ):
                continue

            for p in players_raw:

                try:

                    car_no = int(
                        float(
                            str(
                                p.get(
                                    "syaban",
                                    ""
                                )
                            )
                        )
                    )

                except Exception:

                    car_no = None

                try:

                    player_id = str(
                        p.get(
                            "sensyuRegistNo",
                            ""
                        )
                    ).zfill(6)

                except Exception:

                    player_id = ""

                rows.append({

                    "race_key":
                        race_key,

                    "date":
                        player_json.get(
                            "target_date"
                        ),

                    "jo_code":
                        bank_code,

                    "jo_name":
                        venue_name,

                    "race_no":
                        race_no,

                    "car_no":
                        car_no,

                    "player_id":
                        player_id,

                    "player_name":
                        p.get(
                            "sensyuName"
                        ),

                    "prefecture":
                        p.get(
                            "huKen"
                        ),

                    "age":
                        p.get(
                            "age"
                        ),

                    "term":
                        p.get(
                            "sotugyouki"
                        ),

                    "class":
                        p.get(
                            "kyuhan"
                        ),

                    "previous_class":
                        p.get(
                            "prevKyuhan"
                        ),

                    "style":
                        p.get(
                            "kyakusitu"
                        ),

                    "average_score":
                        p.get(
                            "heikinTokuten"
                        ),

                    "win_rate":
                        p.get(
                            "syouritu"
                        ),

                    "quinella_rate":
                        p.get(
                            "rentairitu2"
                        ),

                    "trio_rate":
                        p.get(
                            "rentairitu3"
                        ),

                    "escape_count":
                        p.get(
                            "nigeCnt"
                        ),

                    "makuri_count":
                        p.get(
                            "makuriCnt"
                        ),

                    "sashi_count":
                        p.get(
                            "sasiCnt"
                        ),

                    "mark_count":
                        p.get(
                            "markCnt"
                        ),

                    "back_count":
                        p.get(
                            "backCnt"
                        ),

                    "home_count":
                        p.get(
                            "homeTori"
                        ),

                    "start_count":
                        p.get(
                            "stTori"
                        ),

                })

    player_df = pd.DataFrame(
        rows
    )

    log(
        f"Rows : {len(player_df):,}"
    )

    print()

    return player_df


# ===========================================================
# Race DataFrame
#
# 023と同じ変換
# ===========================================================

def build_race_dataframe(
    race_json,
    session_master
):

    log("Race DataFrame作成")

    race_df = pd.DataFrame(
        race_json.get(
            "races",
            []
        )
    )

    if race_df.empty:

        return race_df


    # -------------------------------------------------------
    # 023と同じrename
    # -------------------------------------------------------

    race_df = race_df.rename(
        columns={

            "開催日":
                "date",

            "競輪場コード":
                "jo_code",

            "競輪場名":
                "jo_name",

            "開催名":
                "event_name",

            "グレード":
                "grade",

            "レース番号":
                "race_no",

            "周長(m)":
                "track_length",

            "みなし直線(m)":
                "straight_length",

            "カント角(度)":
                "bank_angle",

            "レース種別":
                "race_type",

            "发走時刻":
                "race_time",

            "発走時刻":
                "race_time",

            "天候":
                "weather",

            "風速":
                "wind_speed",

        }
    )


    # -------------------------------------------------------
    # race_time → session
    # -------------------------------------------------------

    race_df["session"] = (
        race_df["race_time"]
    )


    def to_minutes(t):

        if pd.isna(t):

            return None

        t = str(t).strip()

        if not t:

            return None

        h, m = map(
            int,
            t.split(":")
        )

        return h * 60 + m


    race_df["race_minutes"] = (
        race_df["race_time"]
        .apply(to_minutes)
    )


    race_df["session"] = ""


    # -------------------------------------------------------
    # 開催ごとのSession判定
    #
    # 023と同じロジック
    # -------------------------------------------------------

    for (
        date,
        jo_name
    ), group in race_df.groupby(
        [
            "date",
            "jo_name"
        ]
    ):

        valid_times = (
            group["race_minutes"]
            .dropna()
        )

        if valid_times.empty:

            session_name = "不明"

        else:

            first_time = (
                valid_times.min()
            )

            last_time = (
                valid_times.max()
            )

            session_name = "不明"

            for item in session_master:

                if (

                    item["first_min"]
                    <= first_time
                    <= item["first_max"]

                    and

                    item["last_min"]
                    <= last_time
                    <= item["last_max"]

                ):

                    session_name = (
                        item["display_name"]
                    )

                    break


        race_df.loc[
            (
                race_df["date"]
                == date
            )
            &
            (
                race_df["jo_name"]
                == jo_name
            ),
            "session"
        ] = session_name


    # -------------------------------------------------------
    # 不要列削除
    #
    # 023と同じ
    # -------------------------------------------------------

    race_df = race_df.drop(
        columns=[

            "race_minutes",

            "距離",

            "周回数",

            "投票締切",

        ],
        errors="ignore"
    )


    log(
        f"Rows : {len(race_df):,}"
    )

    print()

    return race_df

# ===========================================================
# ラインJSON race_key → 正式race_key変換
# ===========================================================

def convert_line_race_key(line_race_key, player_df):

    parts = str(line_race_key).split("_")

    if len(parts) != 3:
        raise ValueError(
            f"ラインJSONのrace_key形式が不正です: {line_race_key}"
        )

    date = parts[0]
    jo_code = parts[1]
    race_no = int(parts[2])

    # Player側から正式race_keyを探す
    candidates = player_df[
        (player_df["date"].astype(str) == date)
        &
        (player_df["jo_code"].astype(str).str.zfill(2) == jo_code.zfill(2))
        &
        (player_df["race_no"].astype(int) == race_no)
    ]

    if candidates.empty:

        raise ValueError(
            "正式race_keyが見つかりません: "
            f"{line_race_key}"
        )

    return candidates.iloc[0]["race_key"]

# ===========================================================
# Lines DataFrame
#
# Historical lines.json
#
# 023と同じ形式へ変換
# ===========================================================



def build_lines_dataframe(
    lines_json,
    player_df
):

    log("Lines DataFrame作成")

    line_rows = []

    for race in lines_json.get(
        "races",
        []
    ):

        line_race_key = race.get(
            "race_key"
        )

        race_key = convert_line_race_key(
            line_race_key,
            player_df
        )

        cars = race.get(
            "cars",
            {}
        )

        if not isinstance(
            cars,
            dict
        ):
            continue

        for car_no, info in cars.items():

            if not isinstance(
                info,
                dict
            ):
                continue

            if info.get(
                "line"
            ) is None:

                continue

            line_rows.append({

                "race_key":
                    race_key,

                "car_no":
                    int(car_no),

                "line_no":
                    info.get(
                        "line"
                    ),

                "line_position":
                    info.get(
                        "position"
                    ),

                "is_seri":
                    info.get(
                        "seri"
                    ),

            })


    lines_df = pd.DataFrame(
        line_rows
    )

    log(
        f"Rows : {len(lines_df):,}"
    )

    print()

    return lines_df


# ===========================================================
# DataFrame結合
#
# 023と同じ
# ===========================================================

def build_dataframe(
    player_json,
    race_json,
    lines_json,
    session_master
):

    # -------------------------------------------------------
    # Player
    # -------------------------------------------------------

    player_df = build_player_dataframe(
        player_json
    )


    # -------------------------------------------------------
    # Race
    # -------------------------------------------------------

    race_df = build_race_dataframe(
        race_json,
        session_master
    )


    # -------------------------------------------------------
    # Lines
    # -------------------------------------------------------

    lines_df = build_lines_dataframe(
        lines_json,
        player_df
    )


    # -------------------------------------------------------
    # PLAYER + RACE
    #
    # 023と同じ
    # -------------------------------------------------------

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
        errors="ignore"
    )


    df = pd.merge(

        player_df,

        race_df,

        on="race_key",

        how="left",

        validate="many_to_one"

    )


    log(
        f"Rows : {len(df):,}"
    )

    print()


    # -------------------------------------------------------
    # PLAYER + LINES
    #
    # 023と同じ
    # -------------------------------------------------------

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

        validate="one_to_one"

    )


    log(
        f"Rows : {len(df):,}"
    )

    print()


    # -------------------------------------------------------
    # Missing Check
    #
    # 023と同じ
    # -------------------------------------------------------

    print(
        "======================================="
    )

    print(
        "Missing Check"
    )

    print(
        "======================================="
    )

    print()

    race_missing = (
        df["event_name"]
        .isna()
        .sum()
    )

    line_missing = (
        df["line_no"]
        .isna()
        .sum()
    )

    print(
        "Race  :",
        race_missing
    )

    print(
        "Lines :",
        line_missing
    )

    print()

    if (
        race_missing
        or line_missing
    ):

        print(
            "WARNING"
        )

        print(
            "欠損データがあります"
        )

    else:

        print(
            "OK"
        )

    print()


    # -------------------------------------------------------
    # 並び替え
    #
    # 023と同じ
    # -------------------------------------------------------

    df = df.sort_values(
        [
            "race_key",
            "car_no"
        ]
    ).reset_index(
        drop=True
    )


    log(
        "DataFrame完成"
    )

    print()

    return df


# ===========================================================
# Feature Generator
#
# ★023と同じ
# ===========================================================

def build_historical_features(
    df
):

    log("=======================================")
    log("Feature Generator開始")
    log("=======================================")

    # -------------------------------------------------------
    # Player特徴量
    # -------------------------------------------------------

    df = build_feature_player(
        df
    )

    # -------------------------------------------------------
    # Line特徴量
    # -------------------------------------------------------

    df = build_feature_line(
        df
    )

    # -------------------------------------------------------
    # Race特徴量
    # -------------------------------------------------------

    df = build_feature_race(
        df
    )

    # -------------------------------------------------------
    # Rank特徴量
    # -------------------------------------------------------

    df = build_feature_rank(
        df
    )

    # -------------------------------------------------------
    # Relative特徴量
    # -------------------------------------------------------

    df = build_feature_relative(
        df
    )

    log("=======================================")
    log("Feature Generator完了")
    log("=======================================")

    print()

    return df


# ===========================================================
# CSV保存
#
# 1日ずつ追記
# ===========================================================

def append_csv(
    df,
    output_file,
    first_write
):

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(

        output_file,

        mode="w" if first_write else "a",

        header=first_write,

        index=False,

        encoding="utf-8-sig"

    )


# ===========================================================
# Main
# ===========================================================

def main():

    print()

    log("=======================================")
    log(
        "009 Historical Features"
    )
    log("=======================================")

    print()

    print(
        "START :",
        START_DATE.strftime(
            "%Y%m%d"
        )
    )

    print(
        "END   :",
        END_DATE.strftime(
            "%Y%m%d"
        )
    )

    print()

    # -------------------------------------------------------
    # 既存CSVがあれば削除
    #
    # 今回は最初から作り直す
    # -------------------------------------------------------

    if OUTPUT_CSV.exists():

        print(
            "既存CSVを削除します"
        )

        print(
            OUTPUT_CSV
        )

        OUTPUT_CSV.unlink()

        print()


    first_write = True

    total_rows = 0

    success_days = 0

    skip_days = 0

    error_days = 0

    total_days = (
        END_DATE
        - START_DATE
    ).days + 1


    # -------------------------------------------------------
    # 日付ループ
    # -------------------------------------------------------

    for index, target_date in enumerate(
        generate_dates(),
        start=1
    ):

        print()
        print(
            "=" * 70
        )

        print(
            f"[{index}/{total_days}] "
            f"{target_date}"
        )

        print(
            "=" * 70
        )

        # ---------------------------------------------------
        # ファイル確認
        # ---------------------------------------------------

        player_file = (
            PLAYER_DIR
            / f"{target_date}_player.json"
        )

        race_file = (
            RACE_DIR
            / f"{target_date}_race_data.json"
        )

        lines_file = (
            LINES_DIR
            / f"{target_date}_lines.json"
        )

        if not (
            player_file.exists()
            and race_file.exists()
            and lines_file.exists()
        ):

            print(
                "SKIP : 必要JSONがありません"
            )

            if not player_file.exists():

                print(
                    "  Missing :",
                    player_file
                )

            if not race_file.exists():

                print(
                    "  Missing :",
                    race_file
                )

            if not lines_file.exists():

                print(
                    "  Missing :",
                    lines_file
                )

            skip_days += 1

            continue


        try:

            # ------------------------------------------------
            # JSON読込
            # ------------------------------------------------

            (
                player_json,
                race_json,
                lines_json,
                session_master
            ) = load_historical_data(
                target_date
            )


            # ------------------------------------------------
            # DataFrame作成
            # ------------------------------------------------

            df = build_dataframe(

                player_json,

                race_json,

                lines_json,

                session_master

            )


            if df.empty:

                print(
                    "SKIP : データ0件"
                )

                skip_days += 1

                continue


            # ------------------------------------------------
            # Feature Generator
            # ------------------------------------------------

            df = build_historical_features(
                df
            )


            # ------------------------------------------------
            # CSVへ追加
            # ------------------------------------------------

            append_csv(

                df,

                OUTPUT_CSV,

                first_write

            )

            first_write = False

            rows = len(df)

            total_rows += rows

            success_days += 1


            print()

            print(
                f"DAY SAVE : {rows:,} rows"
            )

            print(
                f"TOTAL    : {total_rows:,} rows"
            )


        except Exception as e:

            error_days += 1

            print()

            print(
                "ERROR"
            )

            print(
                type(e).__name__
            )

            print(
                e
            )

            print()

            # ------------------------------------------------
            # 途中の1日で止めず、
            # 次の日へ進む
            # ------------------------------------------------

            continue


    # =======================================================
    # 完了
    # =======================================================

    print()

    print(
        "=" * 70
    )

    print(
        "009 Historical Features Complete"
    )

    print(
        "=" * 70
    )

    print()

    print(
        "対象期間 :",
        "2020/01/01 ～ 2022/12/31"
    )

    print(
        "成功日数 :",
        success_days
    )

    print(
        "スキップ :",
        skip_days
    )

    print(
        "エラー日数 :",
        error_days
    )

    print(
        "総レコード数 :",
        f"{total_rows:,}"
    )

    print(
        "保存先 :",
        OUTPUT_CSV
    )

    print()

    if OUTPUT_CSV.exists():

        print(
            "CSV保存確認 : OK"
        )

    else:

        print(
            "CSV保存確認 : NG"
        )

    print()

    log(
        "Complete"
    )


# ===========================================================
# 実行
# ===========================================================

if __name__ == "__main__":

    main()