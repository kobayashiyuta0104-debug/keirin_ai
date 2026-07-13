"""
===========================================================
競輪AI 正式版
004_collect_historical_raw.py

Part 1
・基本設定
・大量過去RAW収集設定
・保存フォルダ設定
・Session設定
・共通関数
===========================================================
"""

import json
import time
import os
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter

import requests


# ===========================================================
# Part 1
# 基本設定
# ===========================================================


# ===========================================================
# フォルダ設定
# ===========================================================

import os

if os.name == "nt":
    BASE = Path(r"C:\競輪AI")
else:
    BASE = Path(__file__).resolve().parent.parent

DATA_OFFICIAL_DIR = (
    BASE
    / "data_official"
)

HISTORICAL_DIR = (
    DATA_OFFICIAL_DIR
    / "historical_raw"
)

DAILY_RAW_DIR = (
    HISTORICAL_DIR
    / "daily"
)

LOG_DIR = (
    HISTORICAL_DIR
    / "logs"
)


DAILY_RAW_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ===========================================================
# 保存ファイル
# ===========================================================

PROGRESS_FILE = (
    HISTORICAL_DIR
    / "004_collection_progress.json"
)

VALIDATION_FILE = (
    HISTORICAL_DIR
    / "004_collection_validation.json"
)

FAILED_DATES_FILE = (
    LOG_DIR
    / "004_failed_dates.json"
)


# ===========================================================
# 収集日付設定
# ===========================================================

START_DATE = "20260601"

END_DATE = "20260704"


# ===========================================================
# 通信設定
# ===========================================================

REQUEST_TIMEOUT = 30

REQUEST_RETRY = 3

RETRY_WAIT_SECONDS = 2

REQUEST_INTERVAL_SECONDS = 0.15


# ===========================================================
# KEIRIN JSON URL
# ===========================================================

KEIRIN_JSON_URL = (
    "https://www.keirin.jp/pc/json"
)


# ===========================================================
# Session設定
# ===========================================================

SESSION = requests.Session()

SESSION.headers.update({

    "User-Agent":
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/142.0 Safari/537.36",

    "Referer":
        "https://www.keirin.jp/pc/top",

    "Accept":
        "application/json,"
        "text/plain,"
        "*/*",

})


# ===========================================================
# JSON保存
# ===========================================================

def save_json(
    path,
    data,
):
    """
    JSONをUTF-8で保存
    """

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )


# ===========================================================
# JSON読込
# ===========================================================

def load_json(
    path,
    default=None,
):
    """
    JSON読込

    ファイルが存在しない場合は
    defaultを返す
    """

    if not path.exists():

        return default

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


# ===========================================================
# 日付文字列変換
# ===========================================================

def parse_date(date_text):
    """
    YYYYMMDD -> datetime
    """

    return datetime.strptime(
        date_text,
        "%Y%m%d",
    )


# ===========================================================
# 日付文字列生成
# ===========================================================

def format_date(date_value):
    """
    datetime -> YYYYMMDD
    """

    return date_value.strftime(
        "%Y%m%d"
    )


# ===========================================================
# 対象日付一覧生成
# ===========================================================

def build_target_dates(
    start_date,
    end_date,
):
    """
    START_DATE～END_DATEを
    1日単位で生成
    """

    start = parse_date(
        start_date
    )

    end = parse_date(
        end_date
    )

    if start > end:

        raise ValueError(
            "START_DATEがEND_DATEより後です"
        )

    dates = []

    current = start

    while current <= end:

        dates.append(
            format_date(
                current
            )
        )

        current += timedelta(
            days=1
        )

    return dates


# ===========================================================
# 日別RAW保存PATH
# ===========================================================

def build_daily_raw_path(
    kday,
):
    """
    日別RAW保存先
    """

    return (
        DAILY_RAW_DIR
        / f"{kday}_raw.json"
    )


# ===========================================================
# 通信待機
# ===========================================================

def request_wait():
    """
    KEIRINサイトへの連続通信間隔
    """

    if REQUEST_INTERVAL_SECONDS > 0:

        time.sleep(
            REQUEST_INTERVAL_SECONDS
        )


# ===========================================================
# JSON GET
# ===========================================================

def get_json(
    params,
):
    """
    KEIRIN JSON API取得

    retry付き
    """

    last_error = None

    for attempt in range(
        1,
        REQUEST_RETRY + 1,
    ):

        try:

            response = SESSION.get(

                KEIRIN_JSON_URL,

                params=params,

                timeout=REQUEST_TIMEOUT,

            )

            response.raise_for_status()

            data = response.json()

            request_wait()

            return {

                "ok":
                    True,

                "data":
                    data,

                "http_status":
                    response.status_code,

                "text_length":
                    len(
                        response.text
                    ),

                "attempt":
                    attempt,

                "error":
                    None,

            }

        except Exception as e:

            last_error = repr(e)

            if attempt < REQUEST_RETRY:

                time.sleep(
                    RETRY_WAIT_SECONDS
                )

    return {

        "ok":
            False,

        "data":
            None,

        "http_status":
            None,

        "text_length":
            None,

        "attempt":
            REQUEST_RETRY,

        "error":
            last_error,

    }


# ===========================================================
# 進捗初期構造
# ===========================================================

def build_empty_progress():
    """
    004進捗管理初期構造
    """

    return {

        "script":
            "004_collect_historical_raw.py",

        "start_date":
            START_DATE,

        "end_date":
            END_DATE,

        "completed_dates":
            [],

        "failed_dates":
            [],

        "last_completed_date":
            None,

        "updated_at":
            None,

    }


# ===========================================================
# 進捗読込
# ===========================================================

def load_progress():
    """
    既存進捗を読込
    """

    progress = load_json(
        PROGRESS_FILE,
        default=None,
    )

    if not isinstance(
        progress,
        dict,
    ):

        progress = (
            build_empty_progress()
        )

    return progress


# ===========================================================
# 進捗保存
# ===========================================================

def save_progress(
    progress,
):
    """
    進捗保存
    """

    progress[
        "updated_at"
    ] = datetime.now().isoformat(
        timespec="seconds"
    )

    save_json(
        PROGRESS_FILE,
        progress,
    )


# ===========================================================
# End Part 1
# ===========================================================


# ===========================================================
# Part 2
# 1日分レース地図取得
# JSJ057 -> JSJ001 -> encParaR
# ===========================================================


# ===========================================================
# JSJ057取得
# ===========================================================

def fetch_jsj057(kday):
    """
    指定日の開催会場一覧を取得
    """

    result = get_json({

        "kday":
            kday,

        "type":
            "JSJ057",

    })

    if not result["ok"]:

        return {

            "ok":
                False,

            "kday":
                kday,

            "data":
                None,

            "venues":
                [],

            "error":
                result["error"],

        }

    data = result["data"]

    if not isinstance(
        data,
        dict,
    ):

        return {

            "ok":
                False,

            "kday":
                kday,

            "data":
                data,

            "venues":
                [],

            "error":
                "JSJ057_TOP_NOT_DICT",

        }

    venues = data.get(
        "kInfo"
    )

    if not isinstance(
        venues,
        list,
    ):

        venues = []

    return {

        "ok":
            True,

        "kday":
            kday,

        "data":
            data,

        "venues":
            venues,

        "http_status":
            result["http_status"],

        "text_length":
            result["text_length"],

        "error":
            None,

    }


# ===========================================================
# JSJ001取得
# ===========================================================

def fetch_jsj001(enc_prm):
    """
    JSJ057のencPrmから
    会場レース地図を取得

    239成功方式:
    encp = encPrm
    """

    result = get_json({

        "encp":
            enc_prm,

        "type":
            "JSJ001",

    })

    if not result["ok"]:

        return {

            "ok":
                False,

            "data":
                None,

            "races":
                [],

            "error":
                result["error"],

        }

    data = result["data"]

    if not isinstance(
        data,
        dict,
    ):

        return {

            "ok":
                False,

            "data":
                data,

            "races":
                [],

            "error":
                "JSJ001_TOP_NOT_DICT",

        }

    c0201 = data.get(
        "C0201data"
    )

    if not isinstance(
        c0201,
        dict,
    ):

        return {

            "ok":
                False,

            "data":
                data,

            "races":
                [],

            "error":
                "JSJ001_C0201DATA_MISSING",

        }

    races = c0201.get(
        "C0201race"
    )

    if not isinstance(
        races,
        list,
    ):

        races = []

    return {

        "ok":
            True,

        "data":
            data,

        "c0201":
            c0201,

        "races":
            races,

        "selected_date":
            c0201.get(
                "selKaisai"
            ),

        "selected_race":
            c0201.get(
                "selRaceNo"
            ),

        "http_status":
            result["http_status"],

        "text_length":
            result["text_length"],

        "error":
            None,

    }


# ===========================================================
# レース番号取得
# ===========================================================

def extract_race_no(race):
    """
    JSJ001 race構造から
    レース番号を取得
    """

    if not isinstance(
        race,
        dict,
    ):

        return None

    candidates = [

        race.get("raceNo"),

        race.get("RaceNo"),

        race.get("race_no"),

        race.get("txtRaceNo"),

    ]

    for value in candidates:

        if value in (
            None,
            "",
        ):

            continue

        text = (
            str(value)
            .replace("Ｒ", "")
            .replace("R", "")
            .strip()
        )

        try:

            return int(
                float(text)
            )

        except Exception:

            continue

    return None


# ===========================================================
# encParaR取得
# ===========================================================

def extract_race_enc_para(race):
    """
    JSJ001 race構造から
    encParaRを取得
    """

    if not isinstance(
        race,
        dict,
    ):

        return None

    value = race.get(
        "encParaR"
    )

    if value in (
        None,
        "",
    ):

        return None

    return str(value)


# ===========================================================
# 1会場レース地図生成
# ===========================================================

def build_venue_race_map(
    kday,
    venue,
):
    """
    1会場分のJSJ001を取得し
    全レースencParaR地図を生成
    """

    venue_name = venue.get(
        "jyoName"
    )

    venue_code = (
        venue.get("KeirinCd")
        or venue.get("bKeirinCd")
    )

    enc_prm = venue.get(
        "encPrm"
    )

    venue_result = {

        "venue":
            venue_name,

        "venue_code":
            venue_code,

        "entry_encPrm":
            enc_prm,

        "jsj001":
            None,

        "race_count":
            0,

        "races":
            [],

        "problems":
            [],

    }

    if not enc_prm:

        venue_result[
            "problems"
        ].append({

            "problem":
                "ENC_PRM_MISSING",

        })

        return venue_result

    jsj001_result = fetch_jsj001(
        enc_prm
    )

    if not jsj001_result["ok"]:

        venue_result[
            "problems"
        ].append({

            "problem":
                "JSJ001_FETCH_ERROR",

            "error":
                jsj001_result[
                    "error"
                ],

        })

        return venue_result

    venue_result[
        "jsj001"
    ] = jsj001_result[
        "data"
    ]

    for race_index, race in enumerate(
        jsj001_result["races"],
        1,
    ):

        race_no = extract_race_no(
            race
        )

        enc_para_r = (
            extract_race_enc_para(
                race
            )
        )

        if race_no is None:

            race_no = race_index

        race_key = (

            f"{kday}_"
            f"{venue_name}_"
            f"{race_no}R"

        )

        race_item = {

            "race_key":
                race_key,

            "race_no":
                race_no,

            "encParaR":
                enc_para_r,

            "jsj001_race":
                race,

        }

        if not enc_para_r:

            venue_result[
                "problems"
            ].append({

                "race_key":
                    race_key,

                "problem":
                    "ENC_PARA_R_MISSING",

            })

        venue_result[
            "races"
        ].append(
            race_item
        )

    venue_result[
        "race_count"
    ] = len(
        venue_result["races"]
    )

    return venue_result


# ===========================================================
# 1日分レース地図生成
# ===========================================================

def build_daily_race_map(kday):
    """
    JSJ057
    ↓
    全会場JSJ001
    ↓
    全レースencParaR

    1日分の正式レース地図を生成
    """

    daily_result = {

        "kday":
            kday,

        "jsj057":
            None,

        "venue_count":
            0,

        "race_count":
            0,

        "venues":
            [],

        "problems":
            [],

    }

    jsj057_result = fetch_jsj057(
        kday
    )

    if not jsj057_result["ok"]:

        daily_result[
            "problems"
        ].append({

            "date":
                kday,

            "problem":
                "JSJ057_FETCH_ERROR",

            "error":
                jsj057_result[
                    "error"
                ],

        })

        return daily_result

    daily_result[
        "jsj057"
    ] = jsj057_result[
        "data"
    ]

    venues = jsj057_result[
        "venues"
    ]

    daily_result[
        "venue_count"
    ] = len(
        venues
    )

    for venue_index, venue in enumerate(
        venues,
        1,
    ):

        venue_name = venue.get(
            "jyoName"
        )

        print(

            f"    [会場 "
            f"{venue_index}/"
            f"{len(venues)}] "
            f"{venue_name}"

        )

        venue_result = (
            build_venue_race_map(
                kday,
                venue,
            )
        )

        daily_result[
            "venues"
        ].append(
            venue_result
        )

        daily_result[
            "race_count"
        ] += venue_result[
            "race_count"
        ]

        for problem in venue_result[
            "problems"
        ]:

            daily_result[
                "problems"
            ].append({

                "date":
                    kday,

                "venue":
                    venue_name,

                **problem,

            })

        print(

            "      レース地図:",
            venue_result[
                "race_count"
            ],

        )

    return daily_result


# ===========================================================
# End Part 2
# ===========================================================


# ===========================================================
# Part 3
# レースRAW取得
# encParaR -> JSJ006 / JSJ012
# ===========================================================


# ===========================================================
# encParaR JSON取得
# ===========================================================

def fetch_race_json(
    enc_para_r,
    json_type,
):
    """
    encParaRから指定JSONを取得

    json_type:
    JSJ006
    JSJ012
    """

    result = get_json({

        "encp":
            enc_para_r,

        "type":
            json_type,

    })

    if not result["ok"]:

        return {

            "ok":
                False,

            "data":
                None,

            "http_status":
                result["http_status"],

            "text_length":
                result["text_length"],

            "error":
                result["error"],

        }

    data = result["data"]

    if not isinstance(
        data,
        dict,
    ):

        return {

            "ok":
                False,

            "data":
                data,

            "http_status":
                result["http_status"],

            "text_length":
                result["text_length"],

            "error":
                f"{json_type}_TOP_NOT_DICT",

        }

    return {

        "ok":
            True,

        "data":
            data,

        "http_status":
            result["http_status"],

        "text_length":
            result["text_length"],

        "error":
            None,

    }


# ===========================================================
# JSJ006選手構造探索
# ===========================================================

def find_jsj006_player_list(obj):
    """
    JSJ006内部から
    sensyuTypeInfo listを探索
    """

    if isinstance(
        obj,
        dict,
    ):

        players = obj.get(
            "sensyuTypeInfo"
        )

        if isinstance(
            players,
            list,
        ):

            return players

        for value in obj.values():

            found = (
                find_jsj006_player_list(
                    value
                )
            )

            if found is not None:

                return found

    elif isinstance(
        obj,
        list,
    ):

        for value in obj:

            found = (
                find_jsj006_player_list(
                    value
                )
            )

            if found is not None:

                return found

    return None


# ===========================================================
# JSJ012着順構造探索
# ===========================================================

def find_jsj012_result_list(obj):
    """
    JSJ012内部から
    tyakujyunItemSubData listを探索
    """

    if isinstance(
        obj,
        dict,
    ):

        results = obj.get(
            "tyakujyunItemSubData"
        )

        if isinstance(
            results,
            list,
        ):

            return results

        for value in obj.values():

            found = (
                find_jsj012_result_list(
                    value
                )
            )

            if found is not None:

                return found

    elif isinstance(
        obj,
        list,
    ):

        for value in obj:

            found = (
                find_jsj012_result_list(
                    value
                )
            )

            if found is not None:

                return found

    return None


# ===========================================================
# JSJ012払戻構造探索
# ===========================================================

def find_jsj012_harai_data(obj):
    """
    JSJ012内部から
    haraiGakuSubData dictを探索
    """

    if isinstance(
        obj,
        dict,
    ):

        harai = obj.get(
            "haraiGakuSubData"
        )

        if isinstance(
            harai,
            dict,
        ):

            return harai

        for value in obj.values():

            found = (
                find_jsj012_harai_data(
                    value
                )
            )

            if found is not None:

                return found

    elif isinstance(
        obj,
        list,
    ):

        for value in obj:

            found = (
                find_jsj012_harai_data(
                    value
                )
            )

            if found is not None:

                return found

    return None


# ===========================================================
# 3連単払戻存在確認
# ===========================================================

def validate_trifecta_result(
    harai_data,
):
    """
    RT3HaraiGakuDispItemSubDataから
    3連単結果存在を確認
    """

    if not isinstance(
        harai_data,
        dict,
    ):

        return False

    rt3 = harai_data.get(
        "RT3HaraiGakuDispItemSubData"
    )

    if not isinstance(
        rt3,
        list,
    ):

        return False

    for item in rt3:

        if not isinstance(
            item,
            dict,
        ):

            continue

        combination = item.get(
            "kumiBan"
        )

        payout = item.get(
            "haraiGaku"
        )

        if combination in (
            None,
            "",
        ):

            continue

        if payout in (
            None,
            "",
            "【未発売】",
        ):

            continue

        return True

    return False


# ===========================================================
# 1レースRAW取得
# ===========================================================

def fetch_race_raw(
    kday,
    venue_name,
    race_item,
):
    """
    1レース分の
    JSJ006 + JSJ012を取得
    """

    race_key = race_item.get(
        "race_key"
    )

    race_no = race_item.get(
        "race_no"
    )

    enc_para_r = race_item.get(
        "encParaR"
    )

    result = {

        "race_key":
            race_key,

        "race_date":
            kday,

        "venue":
            venue_name,

        "race_no":
            race_no,

        "encParaR":
            enc_para_r,

        "jsj001_race":
            race_item.get(
                "jsj001_race"
            ),

        "jsj006":
            None,

        "jsj012":
            None,

        "player_count":
            0,

        "result_count":
            0,

        "has_trifecta_result":
            False,

        "complete":
            False,

        "problems":
            [],

    }

    if not enc_para_r:

        result[
            "problems"
        ].append({

            "problem":
                "ENC_PARA_R_MISSING",

        })

        return result

    jsj006_result = fetch_race_json(

        enc_para_r,

        "JSJ006",

    )

    if not jsj006_result["ok"]:

        result[
            "problems"
        ].append({

            "problem":
                "JSJ006_FETCH_ERROR",

            "error":
                jsj006_result[
                    "error"
                ],

        })

    else:

        result[
            "jsj006"
        ] = jsj006_result[
            "data"
        ]

    jsj012_result = fetch_race_json(

        enc_para_r,

        "JSJ012",

    )

    if not jsj012_result["ok"]:

        result[
            "problems"
        ].append({

            "problem":
                "JSJ012_FETCH_ERROR",

            "error":
                jsj012_result[
                    "error"
                ],

        })

    else:

        result[
            "jsj012"
        ] = jsj012_result[
            "data"
        ]

    players = (
        find_jsj006_player_list(
            result["jsj006"]
        )
    )

    if not isinstance(
        players,
        list,
    ):

        players = []

    results = (
        find_jsj012_result_list(
            result["jsj012"]
        )
    )

    if not isinstance(
        results,
        list,
    ):

        results = []

    harai_data = (
        find_jsj012_harai_data(
            result["jsj012"]
        )
    )

    result[
        "player_count"
    ] = len(
        players
    )

    result[
        "result_count"
    ] = len(
        results
    )

    result[
        "has_trifecta_result"
    ] = validate_trifecta_result(
        harai_data
    )

    if not players:

        result[
            "problems"
        ].append({

            "problem":
                "JSJ006_PLAYER_STRUCTURE_MISSING",

        })

    if not results:

        result[
            "problems"
        ].append({

            "problem":
                "JSJ012_RESULT_STRUCTURE_MISSING",

        })

    if (
        players
        and results
        and len(players)
        != len(results)
    ):

        result[
            "problems"
        ].append({

            "problem":
                "PLAYER_RESULT_COUNT_MISMATCH",

            "player_count":
                len(players),

            "result_count":
                len(results),

        })

    if not result[
        "has_trifecta_result"
    ]:

        result[
            "problems"
        ].append({

            "problem":
                "TRIFECTA_RESULT_MISSING",

        })

    result[
        "complete"
    ] = (

        len(
            result["problems"]
        )
        == 0

    )

    return result


# ===========================================================
# 1日分全レースRAW取得
# ===========================================================

def fetch_daily_race_raw(
    daily_race_map,
):
    """
    1日分の全会場・全レースから
    JSJ006 + JSJ012を取得
    """

    kday = daily_race_map.get(
        "kday"
    )

    daily_races = []

    problems = list(
        daily_race_map.get(
            "problems",
            [],
        )
    )

    complete_count = 0

    race_total = daily_race_map.get(
        "race_count",
        0,
    )

    race_current = 0

    for venue in daily_race_map.get(
        "venues",
        [],
    ):

        venue_name = venue.get(
            "venue"
        )

        for race_item in venue.get(
            "races",
            [],
        ):

            race_current += 1

            race_key = race_item.get(
                "race_key"
            )

            print(

                f"      [レース "
                f"{race_current}/"
                f"{race_total}] "
                f"{race_key}"

            )

            race_result = fetch_race_raw(

                kday,

                venue_name,

                race_item,

            )

            daily_races.append(
                race_result
            )

            if race_result[
                "complete"
            ]:

                complete_count += 1

                print(
                    "        OK"
                )

            else:

                print(
                    "        NG:",
                    [
                        x.get(
                            "problem"
                        )
                        for x
                        in race_result[
                            "problems"
                        ]
                    ],
                )

            for problem in race_result[
                "problems"
            ]:

                problems.append({

                    "date":
                        kday,

                    "race_key":
                        race_key,

                    **problem,

                })

    return {

        "kday":
            kday,

        "jsj057":
            daily_race_map.get(
                "jsj057"
            ),

        "venue_count":
            daily_race_map.get(
                "venue_count"
            ),

        "race_count":
            len(
                daily_races
            ),

        "complete_race_count":
            complete_count,

        "races":
            daily_races,

        "problem_count":
            len(
                problems
            ),

        "problems":
            problems,

    }


# ===========================================================
# End Part 3
# ===========================================================


# ===========================================================
# Part 4
# 日別保存・進捗管理・途中再開
# ===========================================================


# ===========================================================
# 完了日判定
# ===========================================================

def is_daily_collection_complete(
    daily_data,
):
    """
    日別RAWが正式完了条件を
    満たしているか判定

    開催なし:
        race_count == 0
        problem_count == 0
        -> 正常完了

    開催あり:
        全レースcomplete
        problem_count == 0
        -> 正常完了
    """

    if not isinstance(
        daily_data,
        dict,
    ):

        return False

    race_count = daily_data.get(
        "race_count",
        0,
    )

    complete_race_count = daily_data.get(
        "complete_race_count",
        0,
    )

    problem_count = daily_data.get(
        "problem_count",
        0,
    )

    if problem_count != 0:

        return False

    if race_count == 0:

        return True

    return (
        race_count
        == complete_race_count
    )


# ===========================================================
# 保存済み日別RAW検証
# ===========================================================

def validate_saved_daily_raw(
    kday,
):
    """
    保存済み日別RAWを読み込み、
    正式完了済みか確認
    """

    daily_path = build_daily_raw_path(
        kday
    )

    if not daily_path.exists():

        return {

            "exists":
                False,

            "complete":
                False,

            "data":
                None,

            "error":
                None,

        }

    try:

        data = load_json(
            daily_path,
            default=None,
        )

        complete = (
            is_daily_collection_complete(
                data
            )
        )

        return {

            "exists":
                True,

            "complete":
                complete,

            "data":
                data,

            "error":
                None,

        }

    except Exception as e:

        return {

            "exists":
                True,

            "complete":
                False,

            "data":
                None,

            "error":
                repr(e),

        }


# ===========================================================
# 進捗リスト正規化
# ===========================================================

def normalize_progress_lists(
    progress,
):
    """
    completed_dates / failed_datesを
    重複なし・日付順へ正規化
    """

    completed_dates = progress.get(
        "completed_dates"
    )

    if not isinstance(
        completed_dates,
        list,
    ):

        completed_dates = []

    failed_dates = progress.get(
        "failed_dates"
    )

    if not isinstance(
        failed_dates,
        list,
    ):

        failed_dates = []

    progress[
        "completed_dates"
    ] = sorted(
        set(
            str(x)
            for x in completed_dates
        )
    )

    progress[
        "failed_dates"
    ] = sorted(
        set(
            str(x)
            for x in failed_dates
        )
    )

    return progress


# ===========================================================
# 日付完了登録
# ===========================================================

def mark_date_completed(
    progress,
    kday,
):
    """
    日付を完了済みへ登録
    """

    completed_dates = set(
        progress.get(
            "completed_dates",
            [],
        )
    )

    failed_dates = set(
        progress.get(
            "failed_dates",
            [],
        )
    )

    completed_dates.add(
        kday
    )

    failed_dates.discard(
        kday
    )

    progress[
        "completed_dates"
    ] = sorted(
        completed_dates
    )

    progress[
        "failed_dates"
    ] = sorted(
        failed_dates
    )

    progress[
        "last_completed_date"
    ] = kday

    save_progress(
        progress
    )


# ===========================================================
# 日付失敗登録
# ===========================================================

def mark_date_failed(
    progress,
    kday,
):
    """
    日付を失敗日へ登録
    """

    completed_dates = set(
        progress.get(
            "completed_dates",
            [],
        )
    )

    failed_dates = set(
        progress.get(
            "failed_dates",
            [],
        )
    )

    completed_dates.discard(
        kday
    )

    failed_dates.add(
        kday
    )

    progress[
        "completed_dates"
    ] = sorted(
        completed_dates
    )

    progress[
        "failed_dates"
    ] = sorted(
        failed_dates
    )

    save_progress(
        progress
    )


# ===========================================================
# 失敗日ログ保存
# ===========================================================

def save_failed_dates_log(
    progress,
):
    """
    現在の失敗日一覧を保存
    """

    failed_dates = progress.get(
        "failed_dates",
        [],
    )

    failed_items = []

    for kday in failed_dates:

        daily_validation = (
            validate_saved_daily_raw(
                kday
            )
        )

        daily_data = (
            daily_validation.get(
                "data"
            )
        )

        item = {

            "kday":
                kday,

            "file_exists":
                daily_validation.get(
                    "exists"
                ),

            "daily_complete":
                daily_validation.get(
                    "complete"
                ),

            "load_error":
                daily_validation.get(
                    "error"
                ),

            "problem_count":
                None,

            "problems":
                [],

        }

        if isinstance(
            daily_data,
            dict,
        ):

            item[
                "problem_count"
            ] = daily_data.get(
                "problem_count"
            )

            item[
                "problems"
            ] = daily_data.get(
                "problems",
                [],
            )

        failed_items.append(
            item
        )

    save_json(
        FAILED_DATES_FILE,
        {

            "failed_date_count":
                len(
                    failed_dates
                ),

            "failed_dates":
                failed_dates,

            "items":
                failed_items,

        },
    )


# ===========================================================
# 1日収集
# ===========================================================

def collect_one_date(
    kday,
):
    """
    指定日1日分を正式収集

    レース地図
    ↓
    JSJ006 / JSJ012
    ↓
    日別RAW保存
    """

    print()
    print(
        "=" * 80
    )

    print(
        "収集日:",
        kday,
    )

    print(
        "  レース地図取得開始"
    )

    daily_race_map = (
        build_daily_race_map(
            kday
        )
    )

    print(
        "  開催会場数:",
        daily_race_map.get(
            "venue_count"
        ),
    )

    print(
        "  レース地図件数:",
        daily_race_map.get(
            "race_count"
        ),
    )

    print(
        "  全レースRAW取得開始"
    )

    daily_data = (
        fetch_daily_race_raw(
            daily_race_map
        )
    )

    daily_path = (
        build_daily_raw_path(
            kday
        )
    )

    save_json(
        daily_path,
        daily_data,
    )

    complete = (
        is_daily_collection_complete(
            daily_data
        )
    )

    print()
    print(
        "  === 日別結果 ==="
    )

    print(
        "  会場数:",
        daily_data.get(
            "venue_count"
        ),
    )

    print(
        "  レース数:",
        daily_data.get(
            "race_count"
        ),
    )

    print(
        "  完全取得:",
        daily_data.get(
            "complete_race_count"
        ),
    )

    print(
        "  問題件数:",
        daily_data.get(
            "problem_count"
        ),
    )

    print(
        "  日別完了判定:",
        complete,
    )

    print(
        "  保存:",
        daily_path,
    )

    return (
        daily_data,
        complete,
    )


# ===========================================================
# 取得済み日スキップ判定
# ===========================================================

def should_skip_date(
    kday,
    progress,
):
    """
    保存済みRAWを実体確認して
    正常完了ならスキップ

    progressだけを信用せず
    日別JSON本体も検証する
    """

    daily_validation = (
        validate_saved_daily_raw(
            kday
        )
    )

    if daily_validation[
        "complete"
    ]:

        completed_dates = set(
            progress.get(
                "completed_dates",
                [],
            )
        )

        if kday not in completed_dates:

            mark_date_completed(
                progress,
                kday,
            )

        return True

    return False


# ===========================================================
# 既存日別RAW再検証
# ===========================================================

def rebuild_progress_from_daily_files(
    target_dates,
    progress,
):
    """
    日別RAWファイル本体から
    進捗状態を再構築する

    progressファイル破損時や
    手動変更時にも復旧可能
    """

    completed_dates = []

    failed_dates = []

    for kday in target_dates:

        validation = (
            validate_saved_daily_raw(
                kday
            )
        )

        if validation[
            "complete"
        ]:

            completed_dates.append(
                kday
            )

        elif validation[
            "exists"
        ]:

            failed_dates.append(
                kday
            )

    progress[
        "completed_dates"
    ] = sorted(
        completed_dates
    )

    progress[
        "failed_dates"
    ] = sorted(
        failed_dates
    )

    if completed_dates:

        progress[
            "last_completed_date"
        ] = max(
            completed_dates
        )

    else:

        progress[
            "last_completed_date"
        ] = None

    progress[
        "start_date"
    ] = START_DATE

    progress[
        "end_date"
    ] = END_DATE

    save_progress(
        progress
    )

    return progress


# ===========================================================
# End Part 4
# ===========================================================


# ===========================================================
# Part 5
# 全日一括収集・最終検証・main
# ===========================================================


# ===========================================================
# 全日別RAW集計
# ===========================================================

def build_collection_validation(
    target_dates,
):
    """
    対象期間の日別RAWを再読込し
    最終検証レポートを生成
    """

    completed_dates = []

    failed_dates = []

    missing_dates = []

    total_venue_count = 0

    total_race_count = 0

    total_complete_race_count = 0

    race_key_counter = Counter()

    player_count_dist = Counter()

    result_count_dist = Counter()

    date_race_dist = {}

    date_venue_dist = {}

    problems = []

    for kday in target_dates:

        validation = (
            validate_saved_daily_raw(
                kday
            )
        )

        if not validation[
            "exists"
        ]:

            missing_dates.append(
                kday
            )

            continue

        daily_data = validation.get(
            "data"
        )

        if not isinstance(
            daily_data,
            dict,
        ):

            failed_dates.append(
                kday
            )

            problems.append({

                "date":
                    kday,

                "problem":
                    "DAILY_RAW_INVALID",

                "error":
                    validation.get(
                        "error"
                    ),

            })

            continue

        if validation[
            "complete"
        ]:

            completed_dates.append(
                kday
            )

        else:

            failed_dates.append(
                kday
            )

        venue_count = daily_data.get(
            "venue_count",
            0,
        )

        race_count = daily_data.get(
            "race_count",
            0,
        )

        complete_race_count = (
            daily_data.get(
                "complete_race_count",
                0,
            )
        )

        total_venue_count += venue_count

        total_race_count += race_count

        total_complete_race_count += (
            complete_race_count
        )

        date_venue_dist[
            kday
        ] = venue_count

        date_race_dist[
            kday
        ] = race_count

        for race in daily_data.get(
            "races",
            [],
        ):

            race_key = race.get(
                "race_key"
            )

            race_key_counter[
                race_key
            ] += 1

            player_count_dist[
                race.get(
                    "player_count"
                )
            ] += 1

            result_count_dist[
                race.get(
                    "result_count"
                )
            ] += 1

        for problem in daily_data.get(
            "problems",
            [],
        ):

            problems.append(
                problem
            )

    duplicate_race_keys = {

        race_key: count

        for race_key, count
        in race_key_counter.items()

        if count > 1

    }

    report = {

        "script":
            "004_collect_historical_raw.py",

        "start_date":
            START_DATE,

        "end_date":
            END_DATE,

        "target_date_count":
            len(
                target_dates
            ),

        "completed_date_count":
            len(
                completed_dates
            ),

        "failed_date_count":
            len(
                failed_dates
            ),

        "missing_date_count":
            len(
                missing_dates
            ),

        "completed_dates":
            completed_dates,

        "failed_dates":
            failed_dates,

        "missing_dates":
            missing_dates,

        "total_venue_count":
            total_venue_count,

        "total_race_count":
            total_race_count,

        "total_complete_race_count":
            total_complete_race_count,

        "date_venue_distribution":
            date_venue_dist,

        "date_race_distribution":
            date_race_dist,

        "player_count_distribution":
            dict(
                player_count_dist
            ),

        "result_count_distribution":
            dict(
                result_count_dist
            ),

        "unique_race_key_count":
            len(
                race_key_counter
            ),

        "duplicate_race_keys":
            duplicate_race_keys,

        "problem_count":
            len(
                problems
            ),

        "problems":
            problems,

    }

    return report


# ===========================================================
# 最終結果表示
# ===========================================================

def print_collection_result(
    report,
):
    """
    004最終結果表示
    """

    print()
    print(
        "=" * 80
    )

    print(
        "=== 004 最終結果 ==="
    )

    print(
        "対象日数:",
        report[
            "target_date_count"
        ],
    )

    print(
        "完了日数:",
        report[
            "completed_date_count"
        ],
    )

    print(
        "失敗日数:",
        report[
            "failed_date_count"
        ],
    )

    print(
        "未取得日数:",
        report[
            "missing_date_count"
        ],
    )

    print(
        "開催会場総数:",
        report[
            "total_venue_count"
        ],
    )

    print(
        "取得レース総数:",
        report[
            "total_race_count"
        ],
    )

    print(
        "完全取得レース数:",
        report[
            "total_complete_race_count"
        ],
    )

    print(
        "一意race_key数:",
        report[
            "unique_race_key_count"
        ],
    )

    print(
        "race_key重複:",
        report[
            "duplicate_race_keys"
        ],
    )

    print(
        "車立て分布:",
        report[
            "player_count_distribution"
        ],
    )

    print(
        "着順人数分布:",
        report[
            "result_count_distribution"
        ],
    )

    print(
        "問題件数:",
        report[
            "problem_count"
        ],
    )

    if report[
        "failed_dates"
    ]:

        print()
        print(
            "=== 失敗日一覧 ==="
        )

        for kday in report[
            "failed_dates"
        ]:

            print(
                kday
            )

    if report[
        "missing_dates"
    ]:

        print()
        print(
            "=== 未取得日一覧 ==="
        )

        for kday in report[
            "missing_dates"
        ]:

            print(
                kday
            )

    if report[
        "problems"
    ]:

        print()
        print(
            "=== 問題一覧 先頭100件 ==="
        )

        for problem in report[
            "problems"
        ][:100]:

            print(
                problem
            )


# ===========================================================
# main
# ===========================================================

def main():

    print(
        "=== 004 正式過去RAW大量自動収集 ==="
    )

    print(
        "対象期間:",
        START_DATE,
        "～",
        END_DATE,
    )

    target_dates = (
        build_target_dates(
            START_DATE,
            END_DATE,
        )
    )

    print(
        "対象日数:",
        len(
            target_dates
        ),
    )

    progress = load_progress()

    progress = normalize_progress_lists(
        progress
    )

    print()
    print(
        "既存日別RAWから進捗再構築中..."
    )

    progress = (
        rebuild_progress_from_daily_files(
            target_dates,
            progress,
        )
    )

    print(
        "既存完了日数:",
        len(
            progress.get(
                "completed_dates",
                [],
            )
        ),
    )

    print(
        "既存失敗日数:",
        len(
            progress.get(
                "failed_dates",
                [],
            )
        ),
    )

    for date_index, kday in enumerate(
        target_dates,
        1,
    ):

        print()
        print(
            "#" * 80
        )

        print(
            f"[日付 "
            f"{date_index}/"
            f"{len(target_dates)}] "
            f"{kday}"
        )

        if should_skip_date(
            kday,
            progress,
        ):

            print(
                "  SKIP: 正常取得済み"
            )

            continue

        try:

            daily_data, complete = (
                collect_one_date(
                    kday
                )
            )

            if complete:

                mark_date_completed(
                    progress,
                    kday,
                )

            else:

                mark_date_failed(
                    progress,
                    kday,
                )

        except KeyboardInterrupt:

            print()
            print(
                "手動停止を検出しました"
            )

            print(
                "現在までの進捗を保存して終了します"
            )

            save_progress(
                progress
            )

            save_failed_dates_log(
                progress
            )

            raise

        except Exception as e:

            print(
                "  日付収集ERROR:",
                repr(e),
            )

            mark_date_failed(
                progress,
                kday,
            )

        save_failed_dates_log(
            progress
        )

    print()
    print(
        "全日収集処理終了"
    )

    progress = (
        rebuild_progress_from_daily_files(
            target_dates,
            progress,
        )
    )

    save_failed_dates_log(
        progress
    )

    report = (
        build_collection_validation(
            target_dates
        )
    )

    save_json(
        VALIDATION_FILE,
        report,
    )

    print_collection_result(
        report
    )

    print()
    print(
        "進捗保存:"
    )

    print(
        PROGRESS_FILE
    )

    print()
    print(
        "失敗日ログ保存:"
    )

    print(
        FAILED_DATES_FILE
    )

    print()
    print(
        "最終検証保存:"
    )

    print(
        VALIDATION_FILE
    )

    print()
    print(
        "=== 004 完了 ==="
    )


if __name__ == "__main__":

    main()


# ===========================================================
# End Part 5
# ===========================================================