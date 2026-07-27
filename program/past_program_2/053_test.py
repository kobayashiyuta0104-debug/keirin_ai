from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
import json
import re


# ============================================================
# 053
#
# AI TRAINING SOURCE RACE KEY AUDIT
#
# 目的:
#
# 既存の
#
# 1. 選手能力データ
# 2. ライン予想データ
# 3. 確定結果データ
#
# を自動探索
#
# race_key
# 日付
# 開催場
# レース番号
#
# の保存形式を比較する
#
# 次の054で3データを正式合体するための調査
#
# Edge不要
# サイトアクセスなし
#
# ============================================================


BASE = Path(r"C:\競輪AI")


LINE_FILE = (
    BASE
    / "data_official"
    / "line_predictions"
    / "043_all_venues_official_lines.json"
)


OUT_DIR = (
    BASE
    / "data_ai"
    / "merge_research"
    / "053_training_source_race_key_audit"
)


OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


OUT_FILE = (
    OUT_DIR
    / "053_training_source_race_key_audit.json"
)


TARGET_DATE = "20260710"


# ============================================================
# JSON
# ============================================================


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


def save_json(path, data):

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


# ============================================================
# RACE KEY
# ============================================================


RACE_KEY_PATTERN = re.compile(

    r"(?P<date>20\d{6})"
    r"_"
    r"(?P<venue>.+?)"
    r"_"
    r"(?P<race_no>\d{1,2})R"

)


def parse_race_key(value):

    if value is None:

        return None


    text = str(
        value
    ).strip()


    match = RACE_KEY_PATTERN.fullmatch(
        text
    )


    if not match:

        return None


    return {

        "race_key":
            text,

        "date":
            match.group(
                "date"
            ),

        "venue":
            match.group(
                "venue"
            ),

        "race_no":
            int(
                match.group(
                    "race_no"
                )
            ),

    }


# ============================================================
# FILE SKIP
# ============================================================


SKIP_DIR_NAMES = {

    "__pycache__",
    ".git",
    ".vscode",
    "node_modules",

}


SKIP_FILE_NAMES = {

    OUT_FILE.name,

}


def should_skip_path(path):

    for part in path.parts:

        if part in SKIP_DIR_NAMES:

            return True


    if path.name in SKIP_FILE_NAMES:

        return True


    return False


# ============================================================
# SAFE LOAD
# ============================================================


def safe_load_json(path):

    try:

        return load_json(
            path
        )

    except Exception:

        return None


# ============================================================
# RECURSIVE WALK
# ============================================================


def walk_json(
    value,
    path="root",
    depth=0,
):

    if depth > 30:

        return


    if isinstance(
        value,
        dict,
    ):

        for key, child in value.items():

            child_path = (
                f"{path}.{key}"
            )


            yield {

                "path":
                    child_path,

                "key":
                    str(
                        key
                    ),

                "value":
                    child,

            }


            yield from walk_json(

                child,

                child_path,

                depth + 1,

            )


    elif isinstance(
        value,
        list,
    ):

        for index, child in enumerate(
            value
        ):

            child_path = (
                f"{path}[{index}]"
            )


            yield from walk_json(

                child,

                child_path,

                depth + 1,

            )


# ============================================================
# RACE KEY EXTRACT
# ============================================================


def extract_race_keys(data):

    found = []


    for item in walk_json(
        data
    ):

        key = item.get(
            "key"
        )


        value = item.get(
            "value"
        )


        # ----------------------------------------------------
        # race_key フィールド
        # ----------------------------------------------------

        if key == "race_key":

            parsed = parse_race_key(
                value
            )


            if parsed:

                found.append({

                    "race_key":
                        parsed.get(
                            "race_key"
                        ),

                    "json_path":
                        item.get(
                            "path"
                        ),

                    "method":
                        "RACE_KEY_FIELD",

                })


        # ----------------------------------------------------
        # 値そのものがrace_key
        # ----------------------------------------------------

        if isinstance(
            value,
            str,
        ):

            parsed = parse_race_key(
                value
            )


            if parsed:

                found.append({

                    "race_key":
                        parsed.get(
                            "race_key"
                        ),

                    "json_path":
                        item.get(
                            "path"
                        ),

                    "method":
                        "RACE_KEY_VALUE",

                })


    # ========================================================
    # DEDUP
    # ========================================================


    unique = {}


    for item in found:

        race_key = item.get(
            "race_key"
        )


        if race_key not in unique:

            unique[
                race_key
            ] = item


    return list(
        unique.values()
    )


# ============================================================
# FIELD NAME RESEARCH
# ============================================================


ABILITY_KEYWORDS = [

    "heikinTokuten",
    "race_score",
    "syouritu",
    "win_rate",
    "rentairitu2",
    "top2_rate",
    "rentairitu3",
    "top3_rate",
    "nigeCnt",
    "nige_count",
    "makuriCnt",
    "makuri_count",
    "sasiCnt",
    "sashi_count",
    "markCnt",
    "mark_count",
    "backCnt",
    "back_count",
    "homeCnt",
    "home_count",
    "startCnt",
    "start_count",
    "kyuhan",
    "leg_type",
    "kyakushitsu",
    "sensyuName",
    "rider_name",

]


RESULT_KEYWORDS = [

    "rcvRefund",
    "refund",
    "rcvOdds",
    "odds",
    "tyakujyun",
    "raceResult1Syaban",
    "raceResult2Syaban",
    "raceResult3Syaban",
    "kimarite",
    "confirmed_result",

]


LINE_KEYWORDS = [

    "main_lines",
    "competition_rows",
    "prediction_type",
    "provider",
    "line_prediction",

]


def keyword_hit(
    key,
    keywords,
):

    normalized_key = str(
        key
    ).lower()


    for keyword in keywords:

        if str(
            keyword
        ).lower() in normalized_key:

            return True


    return False


def detect_file_categories(data):

    counters = {

        "ability":
            0,

        "result":
            0,

        "line":
            0,

    }


    hit_keys = {

        "ability":
            set(),

        "result":
            set(),

        "line":
            set(),

    }


    for item in walk_json(
        data
    ):

        key = item.get(
            "key"
        )


        if keyword_hit(
            key,
            ABILITY_KEYWORDS,
        ):

            counters[
                "ability"
            ] += 1

            hit_keys[
                "ability"
            ].add(
                key
            )


        if keyword_hit(
            key,
            RESULT_KEYWORDS,
        ):

            counters[
                "result"
            ] += 1

            hit_keys[
                "result"
            ].add(
                key
            )


        if keyword_hit(
            key,
            LINE_KEYWORDS,
        ):

            counters[
                "line"
            ] += 1

            hit_keys[
                "line"
            ].add(
                key
            )


    return {

        "scores":
            counters,

        "hit_keys": {

            key:
                sorted(
                    values
                )

            for key, values in hit_keys.items()

        },

    }


# ============================================================
# FILE DATE
# ============================================================


def target_date_race_keys(
    race_key_items,
):

    result = []


    for item in race_key_items:

        parsed = parse_race_key(
            item.get(
                "race_key"
            )
        )


        if not parsed:

            continue


        if parsed.get(
            "date"
        ) != TARGET_DATE:

            continue


        result.append(
            item
        )


    return result


# ============================================================
# LINE INDEX
# ============================================================


def load_line_race_keys():

    if not LINE_FILE.exists():

        return set()


    data = load_json(
        LINE_FILE
    )


    items = extract_race_keys(
        data
    )


    return {

        item.get(
            "race_key"
        )

        for item in items

        if parse_race_key(
            item.get(
                "race_key"
            )
        )
        and
        parse_race_key(
            item.get(
                "race_key"
            )
        ).get(
            "date"
        ) == TARGET_DATE

    }


# ============================================================
# MAIN
# ============================================================


def main():

    print()

    print(
        "="
        * 100
    )

    print(
        "053 AI TRAINING SOURCE RACE KEY AUDIT"
    )

    print(
        "="
        * 100
    )

    print()

    print(
        "TARGET DATE:",
        TARGET_DATE
    )

    print()

    print(
        "LINE FILE:",
        LINE_FILE
    )


    # ========================================================
    # LINE
    # ========================================================


    line_race_keys = load_line_race_keys()


    print()

    print(
        "LINE RACE KEYS:",
        len(
            line_race_keys
        )
    )


    # ========================================================
    # SCAN
    # ========================================================


    json_files = []


    for path in BASE.rglob(
        "*.json"
    ):

        if should_skip_path(
            path
        ):

            continue


        json_files.append(
            path
        )


    print()

    print(
        "JSON FILES:",
        len(
            json_files
        )
    )


    file_results = []


    ability_candidate_files = []

    result_candidate_files = []

    line_candidate_files = []


    ability_race_keys = set()

    result_race_keys = set()


    ability_key_sources = defaultdict(
        list
    )

    result_key_sources = defaultdict(
        list
    )


    load_error_count = 0


    for file_index, path in enumerate(
        json_files,
        start=1,
    ):

        if (
            file_index == 1
            or
            file_index % 100 == 0
            or
            file_index == len(
                json_files
            )
        ):

            print(

                f"[SCAN] "
                f"{file_index}"
                f"/"
                f"{len(json_files)} "
                f"{path.name}"

            )


        data = safe_load_json(
            path
        )


        if data is None:

            load_error_count += 1

            continue


        race_key_items = extract_race_keys(
            data
        )


        target_items = target_date_race_keys(
            race_key_items
        )


        if not target_items:

            continue


        category = detect_file_categories(
            data
        )


        scores = category.get(
            "scores",
            {}
        )


        hit_keys = category.get(
            "hit_keys",
            {}
        )


        target_keys = sorted({

            item.get(
                "race_key"
            )

            for item in target_items

        })


        file_result = {

            "file":
                str(
                    path
                ),

            "file_name":
                path.name,

            "target_race_key_count":
                len(
                    target_keys
                ),

            "target_race_keys":
                target_keys,

            "category_scores":
                scores,

            "category_hit_keys":
                hit_keys,

        }


        file_results.append(
            file_result
        )


        # ====================================================
        # ABILITY
        # ====================================================


        if scores.get(
            "ability",
            0
        ) > 0:

            ability_candidate_files.append(
                file_result
            )


            for race_key in target_keys:

                ability_race_keys.add(
                    race_key
                )


                ability_key_sources[
                    race_key
                ].append(
                    str(
                        path
                    )
                )


        # ====================================================
        # RESULT
        # ====================================================


        if scores.get(
            "result",
            0
        ) > 0:

            result_candidate_files.append(
                file_result
            )


            for race_key in target_keys:

                result_race_keys.add(
                    race_key
                )


                result_key_sources[
                    race_key
                ].append(
                    str(
                        path
                    )
                )


        # ====================================================
        # LINE
        # ====================================================


        if scores.get(
            "line",
            0
        ) > 0:

            line_candidate_files.append(
                file_result
            )


    # ========================================================
    # INTERSECTION
    # ========================================================


    ability_and_line = (
        ability_race_keys
        &
        line_race_keys
    )


    line_and_result = (
        line_race_keys
        &
        result_race_keys
    )


    all_three = (

        ability_race_keys
        &
        line_race_keys
        &
        result_race_keys

    )


    line_without_ability = (

        line_race_keys
        -
        ability_race_keys

    )


    line_without_result = (

        line_race_keys
        -
        result_race_keys

    )


    # ========================================================
    # RACE KEY SOURCE MAP
    # ========================================================


    race_key_source_map = []


    all_race_keys = sorted(

        ability_race_keys
        |
        line_race_keys
        |
        result_race_keys

    )


    for race_key in all_race_keys:

        race_key_source_map.append({

            "race_key":
                race_key,

            "ability_found":
                race_key
                in ability_race_keys,

            "line_found":
                race_key
                in line_race_keys,

            "result_found":
                race_key
                in result_race_keys,

            "ability_source_files":
                ability_key_sources.get(
                    race_key,
                    []
                ),

            "result_source_files":
                result_key_sources.get(
                    race_key,
                    []
                ),

        })


    # ========================================================
    # SORT CANDIDATES
    # ========================================================


    ability_candidate_files = sorted(

        ability_candidate_files,

        key=lambda x: (

            x.get(
                "category_scores",
                {}
            ).get(
                "ability",
                0
            ),

            x.get(
                "target_race_key_count",
                0
            ),

        ),

        reverse=True,

    )


    result_candidate_files = sorted(

        result_candidate_files,

        key=lambda x: (

            x.get(
                "category_scores",
                {}
            ).get(
                "result",
                0
            ),

            x.get(
                "target_race_key_count",
                0
            ),

        ),

        reverse=True,

    )


    line_candidate_files = sorted(

        line_candidate_files,

        key=lambda x: (

            x.get(
                "category_scores",
                {}
            ).get(
                "line",
                0
            ),

            x.get(
                "target_race_key_count",
                0
            ),

        ),

        reverse=True,

    )


    # ========================================================
    # OUTPUT
    # ========================================================


    output = {

        "program":
            "053_test.py",

        "created_at":
            datetime.now().isoformat(),

        "target_date":
            TARGET_DATE,

        "line_file":
            str(
                LINE_FILE
            ),

        "json_scan_files":
            len(
                json_files
            ),

        "json_load_errors":
            load_error_count,

        "target_date_files":
            len(
                file_results
            ),

        "race_key_counts": {

            "ability":
                len(
                    ability_race_keys
                ),

            "line":
                len(
                    line_race_keys
                ),

            "result":
                len(
                    result_race_keys
                ),

            "ability_and_line":
                len(
                    ability_and_line
                ),

            "line_and_result":
                len(
                    line_and_result
                ),

            "all_three":
                len(
                    all_three
                ),

        },

        "line_without_ability":
            sorted(
                line_without_ability
            ),

        "line_without_result":
            sorted(
                line_without_result
            ),

        "all_three_race_keys":
            sorted(
                all_three
            ),

        "ability_candidate_files":
            ability_candidate_files,

        "result_candidate_files":
            result_candidate_files,

        "line_candidate_files":
            line_candidate_files,

        "race_key_source_map":
            race_key_source_map,

        "target_date_file_results":
            file_results,

    }


    save_json(
        OUT_FILE,
        output
    )


    # ========================================================
    # FINAL
    # ========================================================


    print()

    print(
        "#"
        * 100
    )

    print(
        "053 最終結果"
    )

    print(
        "#"
        * 100
    )

    print()

    print(
        "TARGET DATE:",
        TARGET_DATE
    )

    print(
        "JSON SCAN FILES:",
        len(
            json_files
        )
    )

    print(
        "TARGET DATE FILES:",
        len(
            file_results
        )
    )

    print(
        "LOAD ERROR:",
        load_error_count
    )

    print()

    print(
        "ABILITY RACE KEYS:",
        len(
            ability_race_keys
        )
    )

    print(
        "LINE RACE KEYS:",
        len(
            line_race_keys
        )
    )

    print(
        "RESULT RACE KEYS:",
        len(
            result_race_keys
        )
    )

    print()

    print(
        "ABILITY + LINE:",
        len(
            ability_and_line
        )
    )

    print(
        "LINE + RESULT:",
        len(
            line_and_result
        )
    )

    print(
        "ALL THREE:",
        len(
            all_three
        )
    )


    # ========================================================
    # ABILITY FILE
    # ========================================================


    print()

    print(
        "★ ABILITY CANDIDATE FILE TOP20 ★"
    )


    if not ability_candidate_files:

        print(
            "なし"
        )


    for item in ability_candidate_files[:20]:

        print()

        print(
            item.get(
                "file"
            )
        )

        print(
            "RACE KEYS:",
            item.get(
                "target_race_key_count"
            )
        )

        print(
            "ABILITY SCORE:",
            item.get(
                "category_scores",
                {}
            ).get(
                "ability"
            )
        )

        print(
            "ABILITY KEYS:",
            item.get(
                "category_hit_keys",
                {}
            ).get(
                "ability"
            )
        )


    # ========================================================
    # RESULT FILE
    # ========================================================


    print()

    print(
        "★ RESULT CANDIDATE FILE TOP20 ★"
    )


    if not result_candidate_files:

        print(
            "なし"
        )


    for item in result_candidate_files[:20]:

        print()

        print(
            item.get(
                "file"
            )
        )

        print(
            "RACE KEYS:",
            item.get(
                "target_race_key_count"
            )
        )

        print(
            "RESULT SCORE:",
            item.get(
                "category_scores",
                {}
            ).get(
                "result"
            )
        )

        print(
            "RESULT KEYS:",
            item.get(
                "category_hit_keys",
                {}
            ).get(
                "result"
            )
        )


    # ========================================================
    # LINE FILE
    # ========================================================


    print()

    print(
        "★ LINE CANDIDATE FILE TOP10 ★"
    )


    if not line_candidate_files:

        print(
            "なし"
        )


    for item in line_candidate_files[:10]:

        print()

        print(
            item.get(
                "file"
            )
        )

        print(
            "RACE KEYS:",
            item.get(
                "target_race_key_count"
            )
        )

        print(
            "LINE SCORE:",
            item.get(
                "category_scores",
                {}
            ).get(
                "line"
            )
        )

        print(
            "LINE KEYS:",
            item.get(
                "category_hit_keys",
                {}
            ).get(
                "line"
            )
        )


    # ========================================================
    # ALL THREE
    # ========================================================


    print()

    print(
        "★ ALL THREE RACE KEY ★"
    )


    if not all_three:

        print(
            "なし"
        )


    for race_key in sorted(
        all_three
    ):

        print(
            race_key
        )


    # ========================================================
    # LINE WITHOUT ABILITY
    # ========================================================


    print()

    print(
        "★ LINE WITHOUT ABILITY TOP50 ★"
    )


    if not line_without_ability:

        print(
            "なし"
        )


    for race_key in sorted(
        line_without_ability
    )[:50]:

        print(
            race_key
        )


    # ========================================================
    # LINE WITHOUT RESULT
    # ========================================================


    print()

    print(
        "★ LINE WITHOUT RESULT TOP50 ★"
    )


    if not line_without_result:

        print(
            "なし"
        )


    for race_key in sorted(
        line_without_result
    )[:50]:

        print(
            race_key
        )


    print()

    print(
        "保存先:"
    )

    print(
        OUT_FILE
    )

    print()

    print(
        "=== 053 完了 ==="
    )


if __name__ == "__main__":

    main()