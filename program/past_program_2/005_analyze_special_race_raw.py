"""
===========================================================
競輪AI 正式版
005_analyze_special_race_raw.py

004で不完全判定されたレースを直接解析

目的:
・開催中止
・レース中止
・不成立
・特殊結果
・取得失敗

をRAW構造から分類するための材料を取得
===========================================================
"""

import json
from pathlib import Path
from collections import Counter


# ===========================================================
# 基本設定
# ===========================================================

BASE = Path(r"C:\競輪AI")

HISTORICAL_DIR = (
    BASE
    / "data_official"
    / "historical_raw"
)

DAILY_RAW_DIR = (
    HISTORICAL_DIR
    / "daily"
)

VALIDATION_FILE = (
    HISTORICAL_DIR
    / "004_collection_validation.json"
)

OUT_FILE = (
    HISTORICAL_DIR
    / "005_special_race_raw_analysis.json"
)


# ===========================================================
# JSON
# ===========================================================

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


# ===========================================================
# 全PATH探索
# ===========================================================

def walk_paths(
    obj,
    path="$",
    output=None,
):

    if output is None:

        output = []

    if isinstance(obj, dict):

        output.append({

            "path":
                path,

            "type":
                "dict",

            "keys":
                list(
                    obj.keys()
                ),

        })

        for key, value in obj.items():

            walk_paths(

                value,

                f"{path}.{key}",

                output,

            )

    elif isinstance(obj, list):

        output.append({

            "path":
                path,

            "type":
                "list",

            "count":
                len(obj),

        })

        for index, value in enumerate(obj):

            walk_paths(

                value,

                f"{path}[{index}]",

                output,

            )

    else:

        output.append({

            "path":
                path,

            "type":
                type(obj).__name__,

            "value":
                obj,

        })

    return output


# ===========================================================
# 特殊状態候補PATH抽出
# ===========================================================

def extract_special_candidates(
    path_items,
):

    keywords = [

        "cancel",
        "stop",
        "abort",
        "invalid",

        "chuushi",
        "tyuusi",
        "chushi",

        "fuseiritsu",
        "seiritsu",

        "status",
        "state",

        "flg",
        "flag",

        "reason",

        "message",
        "msg",

        "huseiritsu",

        "race",

        "kaisai",

        "harai",

        "tyaku",

    ]

    candidates = []

    for item in path_items:

        path = str(
            item.get(
                "path",
                ""
            )
        )

        path_lower = path.lower()

        if any(
            keyword in path_lower
            for keyword in keywords
        ):

            candidates.append(
                item
            )

    return candidates


# ===========================================================
# 値検索
# ===========================================================

def search_special_values(
    path_items,
):

    keywords = [

        "中止",
        "開催中止",
        "レース中止",
        "打切",
        "打ち切り",

        "不成立",
        "不成",

        "返還",
        "特払い",

        "欠場",
        "棄権",
        "落車",
        "失格",

        "未発売",

    ]

    matches = []

    for item in path_items:

        if "value" not in item:

            continue

        value = item.get(
            "value"
        )

        if value is None:

            continue

        text = str(value)

        if any(
            keyword in text
            for keyword in keywords
        ):

            matches.append(
                item
            )

    return matches


# ===========================================================
# race_key -> RAWレース取得
# ===========================================================

def find_race(
    daily_data,
    race_key,
):

    for race in daily_data.get(
        "races",
        [],
    ):

        if race.get(
            "race_key"
        ) == race_key:

            return race

    return None


# ===========================================================
# 問題race_key取得
# ===========================================================

def collect_problem_race_keys(
    validation,
):

    race_keys = []

    for problem in validation.get(
        "problems",
        [],
    ):

        race_key = problem.get(
            "race_key"
        )

        if race_key:

            race_keys.append(
                race_key
            )

    return sorted(
        set(
            race_keys
        )
    )


# ===========================================================
# race_keyから日付取得
# ===========================================================

def get_date_from_race_key(
    race_key,
):

    return str(
        race_key
    ).split(
        "_"
    )[0]


# ===========================================================
# RAW概要
# ===========================================================

def build_raw_summary(
    race,
):

    jsj006 = race.get(
        "jsj006"
    )

    jsj012 = race.get(
        "jsj012"
    )

    jsj001_race = race.get(
        "jsj001_race"
    )

    return {

        "player_count":
            race.get(
                "player_count"
            ),

        "result_count":
            race.get(
                "result_count"
            ),

        "has_trifecta_result":
            race.get(
                "has_trifecta_result"
            ),

        "complete":
            race.get(
                "complete"
            ),

        "problems":
            race.get(
                "problems"
            ),

        "jsj001_exists":
            isinstance(
                jsj001_race,
                dict,
            ),

        "jsj006_exists":
            isinstance(
                jsj006,
                dict,
            ),

        "jsj012_exists":
            isinstance(
                jsj012,
                dict,
            ),

        "jsj001_top_keys":
            (
                list(
                    jsj001_race.keys()
                )

                if isinstance(
                    jsj001_race,
                    dict,
                )

                else []
            ),

        "jsj006_top_keys":
            (
                list(
                    jsj006.keys()
                )

                if isinstance(
                    jsj006,
                    dict,
                )

                else []
            ),

        "jsj012_top_keys":
            (
                list(
                    jsj012.keys()
                )

                if isinstance(
                    jsj012,
                    dict,
                )

                else []
            ),

    }


# ===========================================================
# 1レース解析
# ===========================================================

def analyze_race(
    race,
):

    sources = {

        "jsj001_race":
            race.get(
                "jsj001_race"
            ),

        "jsj006":
            race.get(
                "jsj006"
            ),

        "jsj012":
            race.get(
                "jsj012"
            ),

    }

    source_analysis = {}

    all_value_matches = []

    for source_name, source_data in (
        sources.items()
    ):

        paths = walk_paths(
            source_data
        )

        special_candidates = (
            extract_special_candidates(
                paths
            )
        )

        value_matches = (
            search_special_values(
                paths
            )
        )

        source_analysis[
            source_name
        ] = {

            "path_count":
                len(paths),

            "special_candidate_count":
                len(
                    special_candidates
                ),

            "special_candidates":
                special_candidates,

            "special_value_match_count":
                len(
                    value_matches
                ),

            "special_value_matches":
                value_matches,

        }

        for item in value_matches:

            all_value_matches.append({

                "source":
                    source_name,

                **item,

            })

    return {

        "race_key":
            race.get(
                "race_key"
            ),

        "summary":
            build_raw_summary(
                race
            ),

        "special_value_matches":
            all_value_matches,

        "sources":
            source_analysis,

    }


# ===========================================================
# コンソール表示
# ===========================================================

def print_analysis(
    analysis,
):

    print()
    print(
        "=" * 100
    )

    print(
        "race_key:",
        analysis[
            "race_key"
        ],
    )

    summary = analysis[
        "summary"
    ]

    print(
        "player_count:",
        summary[
            "player_count"
        ],
    )

    print(
        "result_count:",
        summary[
            "result_count"
        ],
    )

    print(
        "has_trifecta_result:",
        summary[
            "has_trifecta_result"
        ],
    )

    print(
        "JSJ001:",
        summary[
            "jsj001_exists"
        ],
    )

    print(
        "JSJ006:",
        summary[
            "jsj006_exists"
        ],
    )

    print(
        "JSJ012:",
        summary[
            "jsj012_exists"
        ],
    )

    print(
        "問題:",
        [
            x.get(
                "problem"
            )
            for x
            in summary[
                "problems"
            ]
        ],
    )

    print()
    print(
        "特殊値候補:"
    )

    matches = analysis[
        "special_value_matches"
    ]

    if not matches:

        print(
            "  なし"
        )

    else:

        for item in matches:

            print(

                " ",

                item.get(
                    "source"
                ),

                item.get(
                    "path"
                ),

                "=",

                item.get(
                    "value"
                ),

            )

    print()
    print(
        "SOURCE別候補PATH:"
    )

    for source_name, source in (
        analysis[
            "sources"
        ].items()
    ):

        print()
        print(
            f"  [{source_name}]"
        )

        print(
            "    PATH数:",
            source[
                "path_count"
            ],
        )

        print(
            "    候補PATH数:",
            source[
                "special_candidate_count"
            ],
        )

        for item in source[
            "special_candidates"
        ][:30]:

            if "value" in item:

                print(

                    "     ",

                    item.get(
                        "path"
                    ),

                    "=",

                    item.get(
                        "value"
                    ),

                )

            elif item.get(
                "type"
            ) == "list":

                print(

                    "     ",

                    item.get(
                        "path"
                    ),

                    "/ list / 件数=",

                    item.get(
                        "count"
                    ),

                )

            else:

                print(

                    "     ",

                    item.get(
                        "path"
                    ),

                    "/ dict / KEYS=",

                    item.get(
                        "keys"
                    ),

                )


# ===========================================================
# main
# ===========================================================

def main():

    print(
        "=== 005 特殊・中止レース "
        "RAW構造解析 ==="
    )

    validation = load_json(
        VALIDATION_FILE
    )

    race_keys = (
        collect_problem_race_keys(
            validation
        )
    )

    print(
        "問題race_key数:",
        len(
            race_keys
        ),
    )

    analyses = []

    date_cache = {}

    not_found = []

    type_counter = Counter()

    for race_key in race_keys:

        kday = get_date_from_race_key(
            race_key
        )

        if kday not in date_cache:

            daily_path = (

                DAILY_RAW_DIR
                / f"{kday}_raw.json"

            )

            date_cache[
                kday
            ] = load_json(
                daily_path
            )

        race = find_race(

            date_cache[
                kday
            ],

            race_key,

        )

        if race is None:

            not_found.append(
                race_key
            )

            continue

        analysis = analyze_race(
            race
        )

        analyses.append(
            analysis
        )

        summary = analysis[
            "summary"
        ]

        pattern = (

            summary[
                "player_count"
            ],

            summary[
                "result_count"
            ],

            summary[
                "has_trifecta_result"
            ],

        )

        type_counter[
            str(pattern)
        ] += 1

        print_analysis(
            analysis
        )

    output = {

        "source_validation":
            str(
                VALIDATION_FILE
            ),

        "problem_race_key_count":
            len(
                race_keys
            ),

        "analyzed_race_count":
            len(
                analyses
            ),

        "not_found_count":
            len(
                not_found
            ),

        "not_found":
            not_found,

        "structure_pattern_distribution":
            dict(
                type_counter
            ),

        "analyses":
            analyses,

    }

    save_json(
        OUT_FILE,
        output,
    )

    print()
    print(
        "=" * 100
    )

    print(
        "=== 005 結果 ==="
    )

    print(
        "問題race_key数:",
        len(
            race_keys
        ),
    )

    print(
        "解析成功:",
        len(
            analyses
        ),
    )

    print(
        "RAW未発見:",
        len(
            not_found
        ),
    )

    print(
        "構造パターン分布:",
        dict(
            type_counter
        ),
    )

    print(
        "保存完了:",
        OUT_FILE,
    )

    print(
        "=== 005 完了 ==="
    )


if __name__ == "__main__":

    main()