"""
===========================================================
競輪AI 正式版
001_build_official_dataset.py

Part 1
・基本設定
・共通関数
・JSON探索関数
===========================================================
"""

import json
import re
from pathlib import Path
from collections import Counter


# ===========================================================
# ファイル設定
# ===========================================================

BASE = Path(r"C:\競輪AI")

INPUT_FILE = BASE / "239_historical_multi_date_raw_capture_fixed.json"

OUTPUT_FILE = BASE / "data_official" / "001_official_dataset.json"

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)


# ===========================================================
# 共通変換
# ===========================================================

def normalize_space(value):
    """
    全角スペース除去
    """

    if not isinstance(value, str):
        return value

    return " ".join(value.replace("\u3000", " ").split())


def to_int(value):

    if value in ("", None):
        return None

    try:
        return int(float(str(value).replace(",", "").replace("%", "")))
    except Exception:
        return None


def to_float(value):

    if value in ("", None):
        return None

    try:
        return float(str(value).replace(",", "").replace("%", ""))
    except Exception:
        return None


def money_to_int(value):

    if value in ("", None):
        return None

    try:
        return int(str(value).replace(",", ""))
    except Exception:
        return None


# ===========================================================
# race_key解析
# ===========================================================

RACE_PATTERN = re.compile(
    r"^(\d{8})_(.+)_(\d+)R$"
)


def split_race_key(race_key):

    m = RACE_PATTERN.match(race_key)

    if not m:
        return None

    return {
        "race_date": m.group(1),
        "venue": m.group(2),
        "race_no": int(m.group(3)),
    }


# ===========================================================
# JSON探索
# ===========================================================

def find_jsj006(obj):
    """
    JSJ006を再帰探索
    """

    if isinstance(obj, dict):

        if isinstance(obj.get("sensyuTypeInfo"), list):
            return obj

        for value in obj.values():

            result = find_jsj006(value)

            if result is not None:
                return result

    elif isinstance(obj, list):

        for value in obj:

            result = find_jsj006(value)

            if result is not None:
                return result

    return None


def find_jsj012(obj):
    """
    JSJ012を再帰探索
    """

    if isinstance(obj, dict):

        if (
            "tyakujyunItemSubData" in obj
            and "haraiGakuSubData" in obj
        ):
            return obj

        for value in obj.values():

            result = find_jsj012(value)

            if result is not None:
                return result

    elif isinstance(obj, list):

        for value in obj:

            result = find_jsj012(value)

            if result is not None:
                return result

    return None


# ===========================================================
# race_key取得
# ===========================================================

def get_race_key(obj):

    if not isinstance(obj, dict):
        return None

    if obj.get("race_key"):
        return obj["race_key"]

    if obj.get("raceKey"):
        return obj["raceKey"]

    return None


# ===========================================================
# RAWレース収集
# ===========================================================

def collect_raw_races(raw):

    races = []

    for date_data in raw.get("dates", []):

        kday = date_data.get("kday")

        for venue in date_data.get("venues", []):

            venue_name = venue.get("venue")

            for race in venue.get("races", []):

                race_key = get_race_key(race)

                if not race_key:
                    continue

                jsj006 = find_jsj006(race)

                jsj012 = find_jsj012(race)

                if jsj006 is None:
                    continue

                if jsj012 is None:
                    continue

                races.append({

                    "race_key": race_key,

                    "race_date": kday,

                    "venue": venue_name,

                    "jsj006": jsj006,

                    "jsj012": jsj012,

                })

    return races


# ===========================================================
# 検証
# ===========================================================

def validate_unique_race_keys(races):

    counter = Counter()

    for race in races:
        counter[race["race_key"]] += 1

    duplicates = {
        k: v
        for k, v in counter.items()
        if v > 1
    }

    return duplicates

# ===========================================================
# End Part 1
# ===========================================================


# ===========================================================
# Part 2
# 選手データ解析
# ===========================================================

def parse_recent_meeting(player):
    """
    JSJ006の過去開催成績を正式形式へ変換
    """

    tyo4 = player.get("tyo4InfoSubData")

    if not isinstance(tyo4, dict):
        tyo4 = {}

    rows = tyo4.get("resultInfoSubData")

    if not isinstance(rows, list):
        rows = []

    recent_results = []

    for row in rows:

        finish = row.get("imgTyakuiName")

        try:
            finish = int(finish)
        except Exception:
            finish = None

        recent_results.append({

            "finish": finish,

            "back": to_int(
                row.get("backTori")
            )

        })

    recent_meeting = {

        "venue_code":
            tyo4.get("bKeirinjyoCd"),

        "venue_name":
            normalize_space(
                tyo4.get("kerinjyoName")
            ),

        "meeting_start_date":
            tyo4.get("kaisaiFirst"),

        "grade":
            tyo4.get("gaiTeiGrade"),

    }

    return recent_results, recent_meeting


# -----------------------------------------------------------

def parse_player(player):
    """
    JSJ006選手1人を正式形式へ変換
    """

    recent_results, recent_meeting = parse_recent_meeting(player)

    return {

        "car_no":
            to_int(player.get("syaban")),

        "player_id":
            str(
                player.get("sensyuRegistNo", "")
            ).zfill(6),

        "player_name":
            normalize_space(
                player.get("sensyuName")
            ),

        "prefecture":
            normalize_space(
                player.get("huKen")
            ),

        "previous_class":
            player.get("prevKyuhan"),

        "class":
            player.get("kyuhan"),

        "riding_style":
            player.get("kyakusitu"),

        "graduation_term":
            to_int(player.get("sotugyouki")),

        "age":
            to_int(player.get("age")),

        "race_score":
            to_float(player.get("heikinTokuten")),

        "nige_count":
            to_int(player.get("nigeCnt")),

        "makuri_count":
            to_int(player.get("makuriCnt")),

        "sashi_count":
            to_int(player.get("sasiCnt")),

        "mark_count":
            to_int(player.get("markCnt")),

        "back_count":
            to_int(player.get("backCnt")),

        "home_count":
            to_int(player.get("homeTori")),

        "start_count":
            to_int(player.get("stTori")),

        "win_rate":
            to_float(player.get("syouritu")),

        "top2_rate":
            to_float(player.get("rentairitu2")),

        "top3_rate":
            to_float(player.get("rentairitu3")),

        "current_meeting_results": [],

        "recent_meeting_results":
            recent_results,

        "recent_meeting":
            recent_meeting,

    }


# -----------------------------------------------------------

def build_players(jsj006):
    """
    JSJ006から正式players生成
    """

    players_raw = jsj006.get("sensyuTypeInfo")

    if not isinstance(players_raw, list):
        players_raw = []

    players = []

    for player in players_raw:

        players.append(
            parse_player(player)
        )

    players.sort(
        key=lambda x: (
            x["car_no"]
            if x["car_no"] is not None
            else 99
        )
    )

    return players


# -----------------------------------------------------------

def validate_players(players):
    """
    player整合性チェック
    """

    problems = []

    ids = []

    for player in players:

        pid = player.get("player_id")

        ids.append(pid)

        if not pid:

            problems.append(
                "EMPTY_PLAYER_ID"
            )

    if len(ids) != len(set(ids)):

        problems.append(
            "DUPLICATE_PLAYER_ID"
        )

    return problems


# -----------------------------------------------------------

def get_player_count(players):
    """
    車立て取得
    """

    return len(players)


# ===========================================================
# End Part 2
# ===========================================================


# ===========================================================
# Part 3
# 結果データ解析（JSJ012）
# ===========================================================

def parse_finish_results(jsj012):
    """
    JSJ012着順を正式形式へ変換
    """

    rows = jsj012.get("tyakujyunItemSubData")

    if not isinstance(rows, list):
        rows = []

    results = []

    for row in rows:

        car_no = to_int(
            row.get("syaban")
        )

        finish_rank = to_int(
            row.get("tyakujyun")
        )

        player_id = str(
            row.get("sensyuRegistNo", "")
        ).zfill(6)

        status = "NORMAL"

        text = (
            str(row.get("kikaku", ""))
            + str(row.get("jyoutai", ""))
            + str(row.get("tyakusa", ""))
        )

        if "落" in text:
            status = "落車"

        elif "失" in text:
            status = "失格"

        elif "棄" in text:
            status = "棄権"

        elif "欠" in text:
            status = "欠場"

        results.append({

            "car_no": car_no,

            "player_id": player_id,

            "finish_rank": finish_rank,

            "result_status": status,

        })

    results.sort(
        key=lambda x: (
            x["car_no"]
            if x["car_no"] is not None
            else 99
        )
    )

    return results


# -----------------------------------------------------------

def parse_labels(jsj012):
    """
    3連単払戻ラベル生成
    """

    harai = jsj012.get(
        "haraiGakuSubData"
    )

    if not isinstance(harai, dict):

        return {

            "trifecta_combination": None,

            "trifecta_payout": None,

            "trifecta_popularity": None,

            "payout_class_4": None,

            "is_20000_plus": None,

            "is_50000_plus": None,

        }

    rt3 = harai.get(
        "RT3HaraiGakuDispItemSubData"
    )

    if not isinstance(rt3, list):

        rt3 = []

    target = None

    for item in rt3:

        if (
            isinstance(item, dict)
            and item.get("kumiBan")
        ):

            target = item

            break

    if target is None:

        return {

            "trifecta_combination": None,

            "trifecta_payout": None,

            "trifecta_popularity": None,

            "payout_class_4": None,

            "is_20000_plus": None,

            "is_50000_plus": None,

        }

    payout = money_to_int(
        target.get("haraiGaku")
    )

    if payout is None:

        label = None

    elif payout < 10000:

        label = "UNDER_10000"

    elif payout < 20000:

        label = "10000_TO_19999"

    elif payout < 50000:

        label = "20000_TO_49999"

    else:

        label = "50000_PLUS"

    return {

        "trifecta_combination":
            target.get("kumiBan"),

        "trifecta_payout":
            payout,

        "trifecta_popularity":
            target.get("ninki"),

        "payout_class_4":
            label,

        "is_20000_plus":
            int(
                payout is not None
                and payout >= 20000
            ),

        "is_50000_plus":
            int(
                payout is not None
                and payout >= 50000
            ),

    }


# -----------------------------------------------------------

def validate_results(players, results):
    """
    JSJ006とJSJ012整合性確認
    """

    problems = []

    p_ids = sorted(
        p["player_id"]
        for p in players
    )

    r_ids = sorted(
        r["player_id"]
        for r in results
    )

    if p_ids != r_ids:

        problems.append(
            "PLAYER_ID_MISMATCH"
        )

    if len(players) != len(results):

        problems.append(
            "PLAYER_COUNT_MISMATCH"
        )

    return problems


# ===========================================================
# End Part 3
# ===========================================================


# ===========================================================
# Part 4
# Official Dataset生成・保存
# ===========================================================

def build_official_dataset(raw):

    raw_races = collect_raw_races(raw)

    duplicate_keys = validate_unique_race_keys(raw_races)

    official_dataset = []

    problems = []

    player_count_dist = Counter()
    payout_class_dist = Counter()

    for race in raw_races:

        info = split_race_key(
            race["race_key"]
        )

        if info is None:

            problems.append({
                "race_key": race["race_key"],
                "problem": "INVALID_RACE_KEY",
            })

            continue

        players = build_players(
            race["jsj006"]
        )

        results = parse_finish_results(
            race["jsj012"]
        )

        labels = parse_labels(
            race["jsj012"]
        )

        for p in validate_players(players):

            problems.append({

                "race_key":
                    race["race_key"],

                "problem":
                    p,

            })

        for p in validate_results(players, results):

            problems.append({

                "race_key":
                    race["race_key"],

                "problem":
                    p,

            })

        player_count = get_player_count(players)

        player_count_dist[player_count] += 1

        if labels["payout_class_4"]:

            payout_class_dist[
                labels["payout_class_4"]
            ] += 1

        official_dataset.append({

            "race_key":
                race["race_key"],

            "race_date":
                info["race_date"],

            "venue":
                info["venue"],

            "race_no":
                info["race_no"],

            "player_count":
                player_count,

            "players":
                players,

            "results":
                results,

            "labels":
                labels,

        })

    official_dataset.sort(

        key=lambda x: (

            x["race_date"],

            x["venue"],

            x["race_no"],

        )

    )

    return (

        official_dataset,

        duplicate_keys,

        player_count_dist,

        payout_class_dist,

        problems,

    )


# -----------------------------------------------------------

def save_dataset(dataset):

    OUTPUT_FILE.write_text(

        json.dumps(

            dataset,

            ensure_ascii=False,

            indent=2,

        ),

        encoding="utf-8",

    )


# ===========================================================
# main
# ===========================================================

def main():

    print("===" * 20)

    print("001 Official Dataset Builder")

    print("===" * 20)

    raw = json.loads(

        INPUT_FILE.read_text(

            encoding="utf-8"

        )

    )

    (

        dataset,

        duplicate_keys,

        player_count_dist,

        payout_class_dist,

        problems,

    ) = build_official_dataset(raw)

    save_dataset(dataset)

    print()

    print("=== 001 結果 ===")

    print("生成レース数:", len(dataset))

    print("車立て分布:", dict(player_count_dist))

    print("払戻分類:", dict(payout_class_dist))

    print("race_key重複:", duplicate_keys)

    print("問題件数:", len(problems))

    print()

    print("保存先:")

    print(OUTPUT_FILE)

    if dataset:

        r = dataset[0]

        print()

        print("=== 先頭レース ===")

        print("race_key:", r["race_key"])

        print("player_count:", r["player_count"])

        print(

            "3連単:",

            r["labels"]["trifecta_combination"],

        )

        print(

            "払戻:",

            r["labels"]["trifecta_payout"],

        )

    if problems:

        print()

        print("=== 問題一覧（先頭30件）===")

        for x in problems[:30]:

            print(x)

    print()

    print("=== 001 完了 ===")


if __name__ == "__main__":

    main()


# ===========================================================
# End Part 4
# ===========================================================