"""
===========================================================
競輪AI 正式版
007_build_historical_features.py

006 NORMAL historical races
↓
001 Official Dataset形式へ変換
↓
002正式181特徴量生成ロジックを完全再利用
↓
Historical Feature Dataset生成
===========================================================
"""

import json
import importlib.util
from pathlib import Path
from collections import Counter


# ===========================================================
# 基本設定
# ===========================================================

BASE = Path(r"C:\競輪AI")

CLASSIFIED_FILE = (
    BASE
    / "data_official"
    / "historical_raw"
    / "006_classified_historical_races.json"
)

RAW_DIR = (
    BASE
    / "data_official"
    / "historical_raw"
)

OUTPUT_FILE = (
    BASE
    / "data_official"
    / "007_historical_feature_dataset.json"
)

VALIDATION_FILE = (
    BASE
    / "data_official"
    / "007_historical_feature_validation.json"
)

FEATURE_BUILDER_FILE = (
    BASE
    / "ai_program"
    / "002_build_features.py"
)


# ===========================================================
# 002正式特徴量モジュール読込
# ===========================================================

def load_feature_builder():

    spec = importlib.util.spec_from_file_location(
        "official_feature_builder",
        FEATURE_BUILDER_FILE,
    )

    if spec is None or spec.loader is None:

        raise RuntimeError(
            "002_build_features.pyを読込できません"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    spec.loader.exec_module(
        module
    )

    return module


# ===========================================================
# JSON読込
# ===========================================================

def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


# ===========================================================
# RAWファイル判定
# ===========================================================

def is_raw_collection_file(path):

    name = path.name

    if not name.endswith(".json"):
        return False

    excluded_prefixes = (
        "004_collection_progress",
        "004_collection_validation",
        "005_",
        "006_",
        "007_",
    )

    if name.startswith(
        excluded_prefixes
    ):
        return False

    return True


# ===========================================================
# race_key取得
# ===========================================================

def get_race_key(obj):

    if not isinstance(
        obj,
        dict,
    ):
        return None

    race_key = obj.get(
        "race_key"
    )

    if race_key:

        return str(
            race_key
        )

    return None


# ===========================================================
# JSJ006探索
# ===========================================================

def find_jsj006(obj):

    if isinstance(
        obj,
        dict,
    ):

        sensyu = obj.get(
            "sensyuTypeInfo"
        )

        if isinstance(
            sensyu,
            list,
        ):

            return obj

        for value in obj.values():

            result = find_jsj006(
                value
            )

            if result is not None:

                return result

    elif isinstance(
        obj,
        list,
    ):

        for value in obj:

            result = find_jsj006(
                value
            )

            if result is not None:

                return result

    return None


# ===========================================================
# JSJ012探索
# ===========================================================

def find_jsj012(obj):

    if isinstance(
        obj,
        dict,
    ):

        if (
            "tyakujyunItemSubData" in obj
            and
            "haraiGakuSubData" in obj
        ):

            return obj

        for value in obj.values():

            result = find_jsj012(
                value
            )

            if result is not None:

                return result

    elif isinstance(
        obj,
        list,
    ):

        for value in obj:

            result = find_jsj012(
                value
            )

            if result is not None:

                return result

    return None


# ===========================================================
# RAWレース探索
# ===========================================================

def collect_raw_races(
    obj,
    output,
):

    if isinstance(
        obj,
        dict,
    ):

        race_key = get_race_key(
            obj
        )

        if race_key:

            jsj006 = find_jsj006(
                obj
            )

            jsj012 = find_jsj012(
                obj
            )

            if (
                jsj006 is not None
                or
                jsj012 is not None
            ):

                if race_key not in output:

                    output[
                        race_key
                    ] = obj

                return

        for value in obj.values():

            collect_raw_races(
                value,
                output,
            )

    elif isinstance(
        obj,
        list,
    ):

        for value in obj:

            collect_raw_races(
                value,
                output,
            )


# ===========================================================
# 全RAWレース地図生成
# ===========================================================

def build_raw_map():

    raw_map = {}

    raw_files = []

    for path in sorted(
        RAW_DIR.rglob("*.json")
    ):

        if not is_raw_collection_file(
            path
        ):

            continue

        raw_files.append(
            path
        )

        try:

            data = load_json(
                path
            )

            collect_raw_races(
                data,
                raw_map,
            )

        except Exception as e:

            print(
                "RAW読込失敗:",
                path,
                repr(e),
            )

    return (
        raw_map,
        raw_files,
    )


# ===========================================================
# 数値変換
# ===========================================================

def to_int(value):

    if value in (
        None,
        "",
    ):
        return None

    try:

        return int(
            float(
                str(value)
                .replace(",", "")
                .replace("%", "")
                .strip()
            )
        )

    except Exception:

        return None


def to_float(value):

    if value in (
        None,
        "",
    ):
        return None

    try:

        return float(
            str(value)
            .replace(",", "")
            .replace("%", "")
            .strip()
        )

    except Exception:

        return None


def norm_space(value):

    if not isinstance(
        value,
        str,
    ):

        return value

    return " ".join(
        value
        .replace("\u3000", " ")
        .split()
    )


# ===========================================================
# recent meeting解析
# ===========================================================

def parse_recent(player):

    tyo4 = player.get(
        "tyo4InfoSubData"
    )

    if not isinstance(
        tyo4,
        dict,
    ):

        tyo4 = {}

    rows = tyo4.get(
        "resultInfoSubData"
    )

    if not isinstance(
        rows,
        list,
    ):

        rows = []

    results = []

    for row in rows:

        if not isinstance(
            row,
            dict,
        ):

            continue

        finish = to_int(
            row.get(
                "imgTyakuiName"
            )
        )

        results.append({

            "finish":
                finish,

            "back":
                to_int(
                    row.get(
                        "backTori"
                    )
                ),

        })

    recent_meeting = {

        "venue_code":
            tyo4.get(
                "bKeirinjyoCd"
            ),

        "venue_name":
            tyo4.get(
                "kerinjyoName"
            ),

        "meeting_start_date":
            tyo4.get(
                "kaisaiFirst"
            ),

        "grade":
            tyo4.get(
                "gaiTeiGrade"
            ),

    }

    return (
        results,
        recent_meeting,
    )


# ===========================================================
# 選手変換
# ===========================================================

def parse_player(player):

    recent_results, recent_meeting = (
        parse_recent(
            player
        )
    )

    player_id = str(
        player.get(
            "sensyuRegistNo",
            "",
        )
    ).strip()

    if player_id:

        player_id = (
            player_id.zfill(6)
        )

    return {

        "car_no":
            to_int(
                player.get(
                    "syaban"
                )
            ),

        "player_id":
            player_id,

        "player_name":
            norm_space(
                player.get(
                    "sensyuName"
                )
            ),

        "prefecture":
            norm_space(
                player.get(
                    "huKen"
                )
            ),

        "previous_class":
            player.get(
                "prevKyuhan"
            ),

        "class":
            player.get(
                "kyuhan"
            ),

        "riding_style":
            player.get(
                "kyakusitu"
            ),

        "graduation_term":
            to_int(
                player.get(
                    "sotugyouki"
                )
            ),

        "age":
            to_int(
                player.get(
                    "age"
                )
            ),

        "race_score":
            to_float(
                player.get(
                    "heikinTokuten"
                )
            ),

        "nige_count":
            to_int(
                player.get(
                    "nigeCnt"
                )
            ),

        "makuri_count":
            to_int(
                player.get(
                    "makuriCnt"
                )
            ),

        "sashi_count":
            to_int(
                player.get(
                    "sasiCnt"
                )
            ),

        "mark_count":
            to_int(
                player.get(
                    "markCnt"
                )
            ),

        "back_count":
            to_int(
                player.get(
                    "backCnt"
                )
            ),

        "home_count":
            to_int(
                player.get(
                    "homeTori"
                )
            ),

        "start_count":
            to_int(
                player.get(
                    "stTori"
                )
            ),

        "win_rate":
            to_float(
                player.get(
                    "syouritu"
                )
            ),

        "top2_rate":
            to_float(
                player.get(
                    "rentairitu2"
                )
            ),

        "top3_rate":
            to_float(
                player.get(
                    "rentairitu3"
                )
            ),

        "current_meeting_results":
            [],

        "recent_meeting_results":
            recent_results,

        "recent_meeting":
            recent_meeting,

    }


# ===========================================================
# 3連単結果取得
# ===========================================================

def extract_trifecta(
    jsj012,
):

    if not isinstance(
        jsj012,
        dict,
    ):

        return None

    harai = jsj012.get(
        "haraiGakuSubData"
    )

    if not isinstance(
        harai,
        dict,
    ):

        return None

    items = harai.get(
        "RT3HaraiGakuDispItemSubData"
    )

    if not isinstance(
        items,
        list,
    ):

        return None

    for item in items:

        if not isinstance(
            item,
            dict,
        ):

            continue

        combination = item.get(
            "kumiBan"
        )

        payout = to_int(
            item.get(
                "haraiGaku"
            )
        )

        if (
            combination
            and
            payout is not None
        ):

            return {

                "trifecta_combination":
                    combination,

                "trifecta_payout":
                    payout,

                "trifecta_popularity":
                    item.get(
                        "ninki"
                    ),

            }

    return None


# ===========================================================
# 払戻分類
# ===========================================================

def build_labels(
    trifecta,
):

    payout = trifecta[
        "trifecta_payout"
    ]

    if payout < 10000:

        payout_class = (
            "UNDER_10000"
        )

    elif payout < 20000:

        payout_class = (
            "10000_TO_19999"
        )

    elif payout < 50000:

        payout_class = (
            "20000_TO_49999"
        )

    else:

        payout_class = (
            "50000_PLUS"
        )

    return {

        "trifecta_combination":
            trifecta[
                "trifecta_combination"
            ],

        "trifecta_payout":
            payout,

        "trifecta_popularity":
            trifecta.get(
                "trifecta_popularity"
            ),

        "payout_class_4":
            payout_class,

        "is_20000_plus":
            int(
                payout >= 20000
            ),

        "is_50000_plus":
            int(
                payout >= 50000
            ),

    }


# ===========================================================
# 001形式レース生成
# ===========================================================

def build_official_race(
    race_key,
    raw_race,
):

    jsj006 = find_jsj006(
        raw_race
    )

    jsj012 = find_jsj012(
        raw_race
    )

    if jsj006 is None:

        return (
            None,
            "JSJ006_MISSING",
        )

    if jsj012 is None:

        return (
            None,
            "JSJ012_MISSING",
        )

    players_raw = jsj006.get(
        "sensyuTypeInfo"
    )

    if not isinstance(
        players_raw,
        list,
    ):

        return (
            None,
            "PLAYER_STRUCTURE_MISSING",
        )

    players = [

        parse_player(
            player
        )

        for player in players_raw

        if isinstance(
            player,
            dict,
        )

    ]

    players.sort(
        key=lambda player:
            player.get("car_no")
            if player.get("car_no") is not None
            else 99
    )

    trifecta = extract_trifecta(
        jsj012
    )

    if trifecta is None:

        return (
            None,
            "TRIFECTA_MISSING",
        )

    parts = race_key.split(
        "_"
    )

    if len(parts) < 3:

        return (
            None,
            "INVALID_RACE_KEY",
        )

    race_date = parts[0]

    venue = parts[1]

    race_no = to_int(
        parts[2].replace(
            "R",
            "",
        )
    )

    race = {

        "venue":
            venue,

        "race_no":
            race_no,

        "race_key":
            race_key,

        "player_count":
            len(players),

        "players":
            players,

        "race_date":
            race_date,

        "labels":
            build_labels(
                trifecta
            ),

    }

    return (
        race,
        None,
    )


# ===========================================================
# 006 NORMAL一覧取得
# ===========================================================

def extract_normal_races(
    classified_data,
):

    normal_races = []

    def walk(obj):

        if isinstance(
            obj,
            dict,
        ):

            race_key = obj.get(
                "race_key"
            )

            status = obj.get(
                "status"
            )

            if (
                race_key
                and
                status == "NORMAL"
            ):

                normal_races.append(
                    obj
                )

                return

            for value in obj.values():

                walk(
                    value
                )

        elif isinstance(
            obj,
            list,
        ):

            for value in obj:

                walk(
                    value
                )

    walk(
        classified_data
    )

    return normal_races


# ===========================================================
# main
# ===========================================================

def main():

    print(
        "=== 007 Historical Feature Dataset "
        "正式修正版 ==="
    )

    feature_builder = (
        load_feature_builder()
    )

    official_feature_names = (
        feature_builder
        .build_official_feature_names()
    )

    classified_data = load_json(
        CLASSIFIED_FILE
    )

    normal_races = extract_normal_races(
        classified_data
    )

    raw_map, raw_files = (
        build_raw_map()
    )

    print(
        "006 NORMALレース数:",
        len(normal_races),
    )

    print(
        "RAW対象ファイル数:",
        len(raw_files),
    )

    print(
        "RAW race_key地図数:",
        len(raw_map),
    )

    print(
        "正式特徴量数:",
        len(
            official_feature_names
        ),
    )

    dataset = []

    problems = []

    feature_count_dist = Counter()

    player_count_dist = Counter()

    payout_class_dist = Counter()

    exact_feature_order_count = 0

    normal_raw_missing = 0

    for index, classified_race in enumerate(
        normal_races,
        1,
    ):

        race_key = classified_race.get(
            "race_key"
        )

        raw_race = raw_map.get(
            race_key
        )

        if raw_race is None:

            normal_raw_missing += 1

            problems.append({

                "race_key":
                    race_key,

                "problem":
                    "NORMAL_RAW_MISSING",

            })

            continue

        official_race, convert_problem = (
            build_official_race(
                race_key,
                raw_race,
            )
        )

        if convert_problem:

            problems.append({

                "race_key":
                    race_key,

                "problem":
                    convert_problem,

            })

            continue

        # ===================================================
        # 002正式181特徴量生成ロジックを完全再利用
        # ===================================================

        feature_record, build_problems = (
            feature_builder
            .build_race_feature_record(
                official_race
            )
        )

        feature_record["features"] = (
            feature_builder
            .order_features(
                feature_record[
                    "features"
                ],
                official_feature_names,
            )
        )

        for problem in build_problems:

            problems.append({

                "race_key":
                    race_key,

                "problem":
                    problem,

            })

        validation_problems = (
            feature_builder
            .validate_race_feature_record(
                official_race,
                feature_record,
                official_feature_names,
            )
        )

        for problem in validation_problems:

            problems.append({

                "race_key":
                    race_key,

                "problem":
                    problem,

            })

        feature_count = len(
            feature_record.get(
                "features",
                {},
            )
        )

        feature_count_dist[
            feature_count
        ] += 1

        player_count = feature_record.get(
            "player_count"
        )

        player_count_dist[
            player_count
        ] += 1

        payout_class = (
            feature_record
            .get(
                "labels",
                {},
            )
            .get(
                "payout_class_4"
            )
        )

        payout_class_dist[
            payout_class
        ] += 1

        if list(
            feature_record.get(
                "features",
                {},
            ).keys()
        ) == official_feature_names:

            exact_feature_order_count += 1

        dataset.append(
            feature_record
        )

        if (
            index % 250 == 0
            or
            index == len(
                normal_races
            )
        ):

            print(
                f"[{index}/{len(normal_races)}] "
                f"生成={len(dataset)} "
                f"問題={len(problems)}"
            )

    race_key_counter = Counter(

        race.get(
            "race_key"
        )

        for race in dataset

    )

    duplicate_race_keys = {

        race_key: count

        for race_key, count
        in race_key_counter.items()

        if count > 1

    }

    nine_player_races = [

        race

        for race in dataset

        if race.get(
            "player_count"
        )
        == 9

    ]

    validation = {

        "normal_race_count":
            len(normal_races),

        "generated_race_count":
            len(dataset),

        "official_feature_count":
            len(
                official_feature_names
            ),

        "feature_count_distribution":
            dict(
                feature_count_dist
            ),

        "player_count_distribution":
            dict(
                player_count_dist
            ),

        "payout_class_distribution":
            dict(
                payout_class_dist
            ),

        "exact_feature_order_count":
            exact_feature_order_count,

        "duplicate_race_keys":
            duplicate_race_keys,

        "normal_raw_missing":
            normal_raw_missing,

        "nine_player_race_count":
            len(
                nine_player_races
            ),

        "problem_count":
            len(problems),

        "problems":
            problems,

    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            dataset,
            f,
            ensure_ascii=False,
            indent=2,
        )

    with open(
        VALIDATION_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            validation,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print(
        "=== 007 結果 ==="
    )

    print(
        "006 NORMALレース数:",
        len(normal_races),
    )

    print(
        "生成レース数:",
        len(dataset),
    )

    print(
        "正式特徴量数:",
        len(
            official_feature_names
        ),
    )

    print(
        "特徴量数分布:",
        dict(
            feature_count_dist
        ),
    )

    print(
        "車立て分布:",
        dict(
            player_count_dist
        ),
    )

    print(
        "4分類分布:",
        dict(
            payout_class_dist
        ),
    )

    print(
        "特徴量順完全一致:",
        exact_feature_order_count,
    )

    print(
        "race_key重複:",
        duplicate_race_keys,
    )

    print(
        "NORMAL RAW未発見:",
        normal_raw_missing,
    )

    print(
        "問題件数:",
        len(problems),
    )

    print(
        "9車立てレース数:",
        len(
            nine_player_races
        ),
    )

    if nine_player_races:

        sample = nine_player_races[0]

        print()
        print(
            "=== 9車立てサンプル確認 ==="
        )

        print(
            "race_key:",
            sample.get(
                "race_key"
            ),
        )

        print(
            "player_count:",
            sample.get(
                "player_count"
            ),
        )

        features = sample.get(
            "features",
            {},
        )

        for slot in range(
            1,
            10,
        ):

            print(
                f"p{slot}:",
                "race_score=",
                features.get(
                    f"p{slot}_race_score"
                ),
                "/ recent=",
                [
                    features.get(
                        f"p{slot}_recent_finish_{n}"
                    )
                    for n in range(
                        1,
                        4,
                    )
                ],
            )

    if problems:

        print()
        print(
            "=== 問題一覧 先頭100件 ==="
        )

        for problem in problems[:100]:

            print(
                problem
            )

    print()
    print(
        "Historical Feature Dataset保存:"
    )

    print(
        OUTPUT_FILE
    )

    print()
    print(
        "検証レポート保存:"
    )

    print(
        VALIDATION_FILE
    )

    print()
    print(
        "=== 007 完了 ==="
    )


if __name__ == "__main__":

    main()