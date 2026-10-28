"""
===========================================================
競輪AI Ver1.0
009_build_historical_features.py

2026/01/01 ～ 2026/08/18
Daily JSON予測特徴量生成

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

training_features(2026.1.1~2026.8.18).csv

※特徴量ロジックは023と同じ
※結果JSONは使用しない
===========================================================
"""

import json
import os
import re
import sys
import tempfile
import traceback

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
    2026,
    1,
    1
)

END_DATE = datetime(
    2026,
    8,
    18
)


# ===========================================================
# Daily JSON
# ===========================================================

DAILY_DIR = (
    BASE
    / "data_official"
    / "historical"
)


PLAYER_DIR = (
    DAILY_DIR
    / "player"
)

RACE_DIR = (
    DAILY_DIR
    / "race_data"
)

LINES_DIR = (
    DAILY_DIR
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
    / "training_features(2026.1.1~2026.8.18).csv"
)

ERROR_LOG = (
    OUTPUT_DIR
    / f"009_build_historical_features_errors_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.log"
)


# ===========================================================
# ログ
# ===========================================================

def log(message):

    print(
        f"[009_build_historical_features] {message}"
    )


def write_issue_log(target_date, level, message, details=None, exception=None):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"[{timestamp}] [{level}] [{target_date}] {message}"
    ]

    if details:
        if isinstance(details, (list, tuple)):
            lines.extend(f"  {item}" for item in details)
        else:
            lines.extend(f"  {item}" for item in str(details).splitlines())

    if exception is not None:
        lines.append("Traceback:")
        lines.append(
            "".join(
                traceback.format_exception(
                    type(exception),
                    exception,
                    exception.__traceback__
                )
            ).rstrip()
        )

    with ERROR_LOG.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n\n")


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
# Daily JSON読込
# ===========================================================

def load_daily_data(target_date):

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
# Daily player.json
#
# venues → races → jsj006 → sensyuTypeInfo
# or
# races → jsj006 → sensyuTypeInfo
#
# ↓
#
# 023と同じplayer DataFrame
# ===========================================================

def normalize_race_date(value):

    if value is None or pd.isna(value):
        return None

    digits = "".join(
        character
        for character in str(value).strip()
        if character.isdigit()
    )

    if len(digits) == 8:
        return digits

    return None


def normalize_race_number(value):

    if value is None or pd.isna(value):
        return None

    text = str(value).strip().upper()

    if not text:
        return None

    match = re.fullmatch(
        r"(?:R\s*)?0*(\d+)\s*R?",
        text
    )

    if match:
        return int(match.group(1))

    try:
        number = float(text)
    except (TypeError, ValueError):
        return None

    if number.is_integer():
        return int(number)

    return None


def normalize_venue_identifier(value):

    if value is None or pd.isna(value):
        return None

    text = re.sub(
        r"\s+",
        "",
        str(value).strip()
    )

    if not text:
        return None

    code_match = re.fullmatch(
        r"0*(\d+)(?:\.0+)?",
        text
    )

    if code_match:
        return f"code:{int(code_match.group(1))}"

    return f"name:{text}"


def parse_race_key(race_key):

    if race_key is None:
        return None

    text = str(race_key).strip()

    match = re.fullmatch(
        r"(?P<date>\d{8})[_*\-](?P<venue>.+?)[_*\-](?P<race>(?:R\s*)?\d+\s*R?)",
        text,
        flags=re.IGNORECASE
    )

    if not match:
        return None

    race_no = normalize_race_number(
        match.group("race")
    )

    if race_no is None:
        return None

    return {
        "date": match.group("date"),
        "venue": match.group("venue").strip(),
        "race_no": race_no
    }


def build_race_key_resolver(player_df):

    resolver = {
        "by_key": {},
        "by_identity": {}
    }

    if player_df.empty or "race_key" not in player_df.columns:
        return resolver

    race_columns = [
        column
        for column in (
            "race_key",
            "date",
            "jo_code",
            "jo_name",
            "race_no"
        )
        if column in player_df.columns
    ]

    race_rows = player_df[
        race_columns
    ].drop_duplicates(
        subset=["race_key"]
    )

    for _, row in race_rows.iterrows():

        canonical_key = str(
            row.get("race_key", "")
        ).strip()

        if not canonical_key:
            continue

        resolver["by_key"][canonical_key] = canonical_key

        date = normalize_race_date(
            row.get("date")
        )
        race_no = normalize_race_number(
            row.get("race_no")
        )

        parsed_key = parse_race_key(
            canonical_key
        )

        if date is None and parsed_key:
            date = parsed_key["date"]

        if race_no is None and parsed_key:
            race_no = parsed_key["race_no"]

        venue_identifiers = [
            normalize_venue_identifier(row.get("jo_code")),
            normalize_venue_identifier(row.get("jo_name"))
        ]

        if parsed_key:
            venue_identifiers.append(
                normalize_venue_identifier(parsed_key["venue"])
            )

        if date is None or race_no is None:
            continue

        for venue_identifier in set(venue_identifiers):

            if venue_identifier is None:
                continue

            identity = (
                date,
                venue_identifier,
                race_no
            )

            resolver["by_identity"].setdefault(
                identity,
                set()
            ).add(canonical_key)

    return resolver


def resolve_race_key(
    race_key,
    race_key_resolver,
    date=None,
    jo_code=None,
    jo_name=None,
    race_no=None,
    allow_unresolved=False
):

    raw_key = "" if race_key is None else str(race_key).strip()
    exact_match = race_key_resolver["by_key"].get(raw_key)

    if exact_match is not None:
        return exact_match

    parsed_key = parse_race_key(raw_key)

    normalized_date = normalize_race_date(date)
    if normalized_date is None and parsed_key:
        normalized_date = parsed_key["date"]

    normalized_race_no = normalize_race_number(race_no)
    if normalized_race_no is None and parsed_key:
        normalized_race_no = parsed_key["race_no"]

    venue_values = [
        jo_code,
        jo_name
    ]
    if parsed_key:
        venue_values.append(
            parsed_key["venue"]
        )

    if normalized_date is not None and normalized_race_no is not None:

        for venue_value in venue_values:

            venue_identifier = normalize_venue_identifier(
                venue_value
            )

            if venue_identifier is None:
                continue

            identity = (
                normalized_date,
                venue_identifier,
                normalized_race_no
            )
            candidates = race_key_resolver["by_identity"].get(
                identity,
                set()
            )

            if len(candidates) == 1:
                return next(iter(candidates))

            if len(candidates) > 1:
                raise ValueError(
                    "レースキーに対応する選手データが複数あります: "
                    f"{race_key or identity}"
                )

    if allow_unresolved:
        return raw_key or None

    raise ValueError(
        "選手データに対応する正式race_keyが見つかりません: "
        f"{race_key}"
    )

def build_player_dataframe(player_json):

    log("Player DataFrame作成")

    rows = []

    race_items = []

    venues = player_json.get(
        "venues",
        []
    )

    if isinstance(venues, list):

        for venue in venues:

            venue_name = venue.get(
                "venue"
            )

            bank_code = venue.get(
                "bank_code"
            )

            for race in venue.get("races", []):
                race_items.append((
                    venue_name,
                    bank_code,
                    race,
                    None
                ))

    if not race_items:

        for race in player_json.get("races", []):

            jsj006 = race.get("jsj006")
            if not isinstance(jsj006, dict):
                jsj006 = {}

            race_items.append((
                race.get("venue") or race.get("jo_name"),
                race.get("jo_code") or jsj006.get("bKeirinjyoCd"),
                race,
                race.get("race_date")
            ))

    for venue_name, raw_bank_code, race, race_date in race_items:

        bank_code = (
            str(raw_bank_code).zfill(2)
            if raw_bank_code is not None
            else ""
        )

        race_key = race.get(
            "race_key"
        )

        race_no = race.get(
            "race_no",
            race.get("レース番号")
        )

        if race_no is None:
            parsed_key = parse_race_key(race_key)
            if parsed_key:
                race_no = parsed_key["race_no"]

        normalized_race_no = normalize_race_number(race_no)
        if normalized_race_no is not None:
            race_no = normalized_race_no

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

                "race_key": race_key,

                "date": (
                    race_date
                    or race.get("開催日")
                    or player_json.get("target_date")
                ),

                "jo_code": bank_code,

                "jo_name": venue_name,

                "race_no": race_no,

                "car_no": car_no,

                "player_id": player_id,

                "player_name": p.get("sensyuName"),

                "prefecture": p.get("huKen"),

                "age": p.get("age"),

                "term": p.get("sotugyouki"),

                "class": p.get("kyuhan"),

                "previous_class": p.get("prevKyuhan"),

                "style": p.get("kyakusitu"),

                "average_score": p.get("heikinTokuten"),

                "win_rate": p.get("syouritu"),

                "quinella_rate": p.get("rentairitu2"),

                "trio_rate": p.get("rentairitu3"),

                "escape_count": p.get("nigeCnt"),

                "makuri_count": p.get("makuriCnt"),

                "sashi_count": p.get("sasiCnt"),

                "mark_count": p.get("markCnt"),

                "back_count": p.get("backCnt"),

                "home_count": p.get("homeTori"),

                "start_count": p.get("stTori"),

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
    session_master,
    race_key_resolver=None
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

    if race_key_resolver is not None:

        if "race_key" not in race_df.columns:
            race_df["race_key"] = None

        race_df["race_key"] = race_df.apply(
            lambda row: resolve_race_key(
                row.get("race_key"),
                race_key_resolver,
                date=row.get("date"),
                jo_code=row.get("jo_code"),
                jo_name=row.get("jo_name"),
                race_no=row.get("race_no"),
                allow_unresolved=True
            ),
            axis=1
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

def convert_line_race_key(
    line_race_key,
    race_key_resolver,
    date=None,
    jo_code=None,
    jo_name=None,
    race_no=None
):

    return resolve_race_key(
        line_race_key,
        race_key_resolver,
        date=date,
        jo_code=jo_code,
        jo_name=jo_name,
        race_no=race_no
    )

# ===========================================================
# Lines DataFrame
#
# Daily lines.json
#
# 023と同じ形式へ変換
# ===========================================================



def build_lines_dataframe(
    lines_json,
    race_key_resolver
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
            race_key_resolver,
            date=(
                race.get("date")
                or race.get("race_date")
                or lines_json.get("target_date")
            ),
            jo_code=race.get("jo_code"),
            jo_name=race.get("jo_name"),
            race_no=race.get("race_no")
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

    race_key_resolver = build_race_key_resolver(
        player_df
    )


    # -------------------------------------------------------
    # Race
    # -------------------------------------------------------

    race_df = build_race_dataframe(
        race_json,
        session_master,
        race_key_resolver
    )


    # -------------------------------------------------------
    # Lines
    # -------------------------------------------------------

    lines_df = build_lines_dataframe(
        lines_json,
        race_key_resolver
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

def build_feature_player_with_foreign_handling(df, target_date):

    # These raw huKen values are overseas origin labels, not Japanese prefectures.
    foreign_values = ('オラン', 'フラン', 'ニュー', 'イギリ')
    normalized_prefecture = (
        df["prefecture"]
        .fillna("")
        .astype(str)
        .str.strip()
    )
    foreign_mask = normalized_prefecture.isin(foreign_values)

    if not foreign_mask.any():
        return build_feature_player(df)

    original_prefecture = df.loc[
        foreign_mask,
        "prefecture"
    ].copy()
    value_counts = normalized_prefecture.loc[
        foreign_mask
    ].value_counts().sort_index()

    write_issue_log(
        target_date,
        "INFO",
        "Overseas-origin riders are handled as no-home-bank entries.",
        details=[
            f"{value}: {int(count)} rows"
            for value, count in value_counts.items()
        ]
    )

    # Use a valid prefecture only while the existing generator performs its
    # required prefecture-to-region lookup. These temporary results are
    # overwritten immediately after build_feature_player returns.
    df = df.copy()
    df.loc[foreign_mask, "prefecture"] = '東京'
    df = build_feature_player(df)

    # Preserve the raw huKen value, label the region as overseas, and use
    # home_bank=3, which the existing feature generator defines as "other".
    df.loc[foreign_mask, "prefecture"] = original_prefecture
    df.loc[foreign_mask, "region"] = '海外'
    df.loc[foreign_mask, "home_bank"] = 3

    log(
        f"Overseas-origin riders handled: {int(foreign_mask.sum())} rows; "
        "region=overseas, home_bank=3"
    )

    return df


def build_daily_features(
    df,
    target_date
):

    log("=======================================")
    log("Feature Generator開始")
    log("=======================================")

    # -------------------------------------------------------
    # Player特徴量
    # -------------------------------------------------------

    df = build_feature_player_with_foreign_handling(
        df,
        target_date
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

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    ERROR_LOG.write_text(
        "009_build_historical_features diagnostic log\n",
        encoding="utf-8"
    )

    print()
    log(f"Error log : {ERROR_LOG}")

    log("=======================================")
    log(
        "009 Daily Features"
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

            missing_files = [
                str(path)
                for path in (player_file, race_file, lines_file)
                if not path.exists()
            ]
            write_issue_log(
                target_date,
                "SKIP",
                "Required daily JSON file(s) are missing.",
                details=missing_files
            )

            skip_days += 1

            continue


        stage = "daily JSON loading"

        try:

            # ------------------------------------------------
            # JSON読込
            # ------------------------------------------------

            (
                player_json,
                race_json,
                lines_json,
                session_master
            ) = load_daily_data(
                target_date
            )


            # ------------------------------------------------
            # DataFrame作成
            # ------------------------------------------------

            stage = "DataFrame creation"
            df = build_dataframe(

                player_json,

                race_json,

                lines_json,

                session_master

            )


            if df.empty:

                write_issue_log(
                    target_date,
                    "SKIP",
                    "DataFrame is empty after daily data was loaded."
                )

                print(
                    "SKIP : データ0件"
                )

                skip_days += 1

                continue


            # ------------------------------------------------
            # Feature Generator
            # ------------------------------------------------

            stage = "feature generation"
            df = build_daily_features(
                df,
                target_date
            )


            # ------------------------------------------------
            # CSVへ追加
            # ------------------------------------------------

            stage = "CSV append"
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
            write_issue_log(
                target_date,
                "ERROR",
                f"{stage} failed: {type(e).__name__}: {e}",
                exception=e
            )

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
        "009 Daily Features Complete"
    )

    print(
        "=" * 70
    )

    print()

    print(
        "対象期間 :",
        "2026/01/01 ～ 2026/08/18"
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

    print("Error log :", ERROR_LOG)
    write_issue_log(
        "ALL",
        "SUMMARY",
        f"success_days={success_days}, skip_days={skip_days}, "
        f"error_days={error_days}, total_rows={total_rows}"
    )

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
