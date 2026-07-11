from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
import json
import re


# ============================================================
# 052
#
# JSJ006 CONTENT IDENTITY RESEARCH
#
# 050で正しくrace_keyへ接続したJSJ006を解析
#
# 目的:
#
# ・JSJ006内部の全JSONパスを集計
# ・キー名を集計
# ・結果系フィールドを調査
# ・選手能力系フィールドを調査
# ・日付 / レース番号 / 車番らしい値を調査
# ・JSJ006が何のJSONなのか判定材料を作る
#
# Edge不要
# サイトアクセスなし
#
# ============================================================


BASE = Path(r"C:\競輪AI")


SOURCE_FILE = (
    BASE
    / "data_official"
    / "pre_race"
    / "050_jsj006_race_click_only"
    / "050_jsj006_race_click_only.json"
)


OUT_DIR = (
    BASE
    / "data_official"
    / "pre_race"
    / "052_jsj006_content_identity"
)


OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


OUT_FILE = (
    OUT_DIR
    / "052_jsj006_content_identity.json"
)


# ============================================================
# KEYWORD GROUP
# ============================================================


RESULT_KEYWORDS = [

    "result",
    "raceResult",
    "tyaku",
    "tyakujyun",
    "rank",
    "arrival",
    "refund",
    "払戻",
    "着順",
    "確定",

]


RIDER_KEYWORDS = [

    "sensyu",
    "rider",
    "player",
    "選手",

]


ABILITY_KEYWORDS = [

    "tokuten",
    "score",
    "point",
    "rating",
    "競走得点",

    "syoritu",
    "winrate",
    "win_rate",
    "勝率",

    "nirentai",
    "2rentai",
    "secondrate",
    "二連対",
    "2連対",

    "sanrentai",
    "3rentai",
    "thirdrate",
    "三連対",
    "3連対",

    "back",
    "バック",

    "kyakushitsu",
    "脚質",

    "kyuhan",
    "級班",

    "fuken",
    "prefecture",
    "府県",

    "age",
    "nenrei",
    "年齢",

    "kibetsu",
    "期別",

]


IDENTITY_KEYWORDS = [

    "race",
    "kaisai",
    "jo",
    "venue",
    "date",
    "day",
    "raceNo",
    "raceNum",
    "raceNumber",
    "syaban",
    "carNum",
    "lastUpdateTime",

]


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
# NORMALIZE
# ============================================================


def normalize_text(value):

    return str(
        value
    ).lower()


def keyword_hit(
    text,
    keywords,
):

    normalized = normalize_text(
        text
    )


    for keyword in keywords:

        if normalize_text(
            keyword
        ) in normalized:

            return True


    return False


# ============================================================
# RECURSIVE WALK
# ============================================================


def walk_json(
    value,
    path="root",
):

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

                "value_type":
                    type(
                        child
                    ).__name__,

            }


            yield from walk_json(
                child,
                child_path,
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
            )


# ============================================================
# PATH NORMALIZE
#
# [0], [1], [2] ...
#
# ↓
#
# []
#
# 同一構造として集計
# ============================================================


def normalize_path(path):

    return re.sub(
        r"\[\d+\]",
        "[]",
        path,
    )


# ============================================================
# SAFE SAMPLE
# ============================================================


def safe_sample(value):

    if isinstance(
        value,
        dict,
    ):

        keys = list(
            value.keys()
        )


        return {

            "type":
                "dict",

            "key_count":
                len(
                    keys
                ),

            "keys":
                keys[:30],

        }


    if isinstance(
        value,
        list,
    ):

        return {

            "type":
                "list",

            "length":
                len(
                    value
                ),

        }


    text = str(
        value
    )


    if len(
        text
    ) > 300:

        text = (
            text[:300]
            + "..."
        )


    return text


# ============================================================
# RESPONSE BODY EXTRACT
#
# 050の保存形式に多少差があっても探す
# ============================================================


def parse_json_string(value):

    if not isinstance(
        value,
        str,
    ):

        return None


    text = value.strip()


    if not text:

        return None


    if not (
        text.startswith(
            "{"
        )
        or
        text.startswith(
            "["
        )
    ):

        return None


    try:

        return json.loads(
            text
        )

    except Exception:

        return None


def find_json_candidates(
    value,
    path="response",
    depth=0,
):

    found = []


    if depth > 8:

        return found


    if isinstance(
        value,
        dict,
    ):

        # ----------------------------------------------------
        # よくあるBODYキーを優先
        # ----------------------------------------------------

        priority_keys = [

            "json",
            "body_json",
            "response_json",
            "data",
            "body",
            "text",
            "response_body",
            "raw_body",

        ]


        for key in priority_keys:

            if key not in value:

                continue


            child = value.get(
                key
            )


            child_path = (
                f"{path}.{key}"
            )


            if isinstance(
                child,
                (
                    dict,
                    list,
                ),
            ):

                found.append({

                    "path":
                        child_path,

                    "data":
                        child,

                })


            else:

                parsed = parse_json_string(
                    child
                )


                if parsed is not None:

                    found.append({

                        "path":
                            child_path,

                        "data":
                            parsed,

                    })


        # ----------------------------------------------------
        # 再帰探索
        # ----------------------------------------------------

        for key, child in value.items():

            if key in priority_keys:

                continue


            if isinstance(
                child,
                (
                    dict,
                    list,
                ),
            ):

                found.extend(

                    find_json_candidates(

                        child,

                        f"{path}.{key}",

                        depth + 1,

                    )

                )


            elif isinstance(
                child,
                str,
            ):

                parsed = parse_json_string(
                    child
                )


                if parsed is not None:

                    found.append({

                        "path":
                            f"{path}.{key}",

                        "data":
                            parsed,

                    })


    elif isinstance(
        value,
        list,
    ):

        for index, child in enumerate(
            value
        ):

            found.extend(

                find_json_candidates(

                    child,

                    f"{path}[{index}]",

                    depth + 1,

                )

            )


    return found


def candidate_score(candidate):

    data = candidate.get(
        "data"
    )


    score = 0


    if isinstance(
        data,
        dict,
    ):

        score += 100

        score += len(
            data
        )


    elif isinstance(
        data,
        list,
    ):

        score += 50

        score += len(
            data
        )


    for item in walk_json(
        data
    ):

        score += 1


        if keyword_hit(

            item.get(
                "key",
                ""
            ),

            RESULT_KEYWORDS
            + RIDER_KEYWORDS
            + ABILITY_KEYWORDS,

        ):

            score += 10


    return score


def extract_response_json(response):

    candidates = find_json_candidates(
        response
    )


    if not candidates:

        # response自体がJSON本体の可能性
        if isinstance(
            response,
            (
                dict,
                list,
            ),
        ):

            return {

                "path":
                    "response",

                "data":
                    response,

                "candidate_count":
                    0,

            }


        return None


    best = max(

        candidates,

        key=candidate_score,

    )


    return {

        "path":
            best.get(
                "path"
            ),

        "data":
            best.get(
                "data"
            ),

        "candidate_count":
            len(
                candidates
            ),

    }


# ============================================================
# DATE VALUE
# ============================================================


def is_date_like(value):

    text = str(
        value
    )


    if re.fullmatch(
        r"20\d{6}",
        text,
    ):

        return True


    if re.fullmatch(
        r"20\d{2}[-/]\d{1,2}[-/]\d{1,2}",
        text,
    ):

        return True


    return False


# ============================================================
# RACE NUMBER VALUE
# ============================================================


def is_small_race_number(value):

    if isinstance(
        value,
        bool,
    ):

        return False


    try:

        number = int(
            value
        )

    except Exception:

        return False


    return (
        1
        <= number
        <= 12
    )


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
        "052 JSJ006 CONTENT IDENTITY RESEARCH"
    )

    print(
        "="
        * 100
    )

    print()


    print(
        "SOURCE:",
        SOURCE_FILE
    )


    if not SOURCE_FILE.exists():

        print()

        print(
            "ERROR: 050ファイルがありません"
        )

        print(
            SOURCE_FILE
        )

        return


    source_data = load_json(
        SOURCE_FILE
    )


    # ========================================================
    # COUNTERS
    # ========================================================


    key_counter = Counter()

    path_counter = Counter()

    path_type_counter = defaultdict(
        Counter
    )


    result_key_counter = Counter()

    rider_key_counter = Counter()

    ability_key_counter = Counter()

    identity_key_counter = Counter()


    result_path_counter = Counter()

    rider_path_counter = Counter()

    ability_path_counter = Counter()

    identity_path_counter = Counter()


    result_samples = defaultdict(
        list
    )

    rider_samples = defaultdict(
        list
    )

    ability_samples = defaultdict(
        list
    )

    identity_samples = defaultdict(
        list
    )


    date_value_counter = Counter()

    small_number_counter = Counter()


    race_results = []


    response_total = 0

    response_json_found = 0

    response_json_not_found = 0


    race_with_result_key = set()

    race_with_rider_key = set()

    race_with_ability_key = set()

    race_with_identity_key = set()


    # ========================================================
    # RACES
    # ========================================================


    races = source_data.get(
        "races",
        []
    )


    for race in races:

        if race.get(
            "status"
        ) != "JSJ006_FOUND":

            continue


        race_key = race.get(
            "race_key"
        )


        responses = race.get(
            "jsj006_responses",
            []
        )


        race_summary = {

            "race_key":
                race_key,

            "response_count":
                len(
                    responses
                ),

            "responses":
                [],

        }


        for response_index, response in enumerate(
            responses
        ):

            response_total += 1


            extracted = extract_response_json(
                response
            )


            if extracted is None:

                response_json_not_found += 1


                race_summary[
                    "responses"
                ].append({

                    "response_index":
                        response_index,

                    "status":
                        "JSON_BODY_NOT_FOUND",

                })


                continue


            response_json_found += 1


            body = extracted.get(
                "data"
            )


            local_result_keys = []

            local_rider_keys = []

            local_ability_keys = []

            local_identity_keys = []


            local_paths = 0


            for item in walk_json(
                body
            ):

                local_paths += 1


                path = item.get(
                    "path"
                )


                normalized_path = normalize_path(
                    path
                )


                key = item.get(
                    "key"
                )


                value = item.get(
                    "value"
                )


                value_type = item.get(
                    "value_type"
                )


                key_counter[
                    key
                ] += 1


                path_counter[
                    normalized_path
                ] += 1


                path_type_counter[
                    normalized_path
                ][
                    value_type
                ] += 1


                # ============================================
                # RESULT
                # ============================================


                if keyword_hit(
                    key,
                    RESULT_KEYWORDS,
                ):

                    result_key_counter[
                        key
                    ] += 1


                    result_path_counter[
                        normalized_path
                    ] += 1


                    local_result_keys.append(
                        key
                    )


                    race_with_result_key.add(
                        race_key
                    )


                    if len(
                        result_samples[
                            normalized_path
                        ]
                    ) < 5:

                        result_samples[
                            normalized_path
                        ].append({

                            "race_key":
                                race_key,

                            "value":
                                safe_sample(
                                    value
                                ),

                        })


                # ============================================
                # RIDER
                # ============================================


                if keyword_hit(
                    key,
                    RIDER_KEYWORDS,
                ):

                    rider_key_counter[
                        key
                    ] += 1


                    rider_path_counter[
                        normalized_path
                    ] += 1


                    local_rider_keys.append(
                        key
                    )


                    race_with_rider_key.add(
                        race_key
                    )


                    if len(
                        rider_samples[
                            normalized_path
                        ]
                    ) < 5:

                        rider_samples[
                            normalized_path
                        ].append({

                            "race_key":
                                race_key,

                            "value":
                                safe_sample(
                                    value
                                ),

                        })


                # ============================================
                # ABILITY
                # ============================================


                if keyword_hit(
                    key,
                    ABILITY_KEYWORDS,
                ):

                    ability_key_counter[
                        key
                    ] += 1


                    ability_path_counter[
                        normalized_path
                    ] += 1


                    local_ability_keys.append(
                        key
                    )


                    race_with_ability_key.add(
                        race_key
                    )


                    if len(
                        ability_samples[
                            normalized_path
                        ]
                    ) < 5:

                        ability_samples[
                            normalized_path
                        ].append({

                            "race_key":
                                race_key,

                            "value":
                                safe_sample(
                                    value
                                ),

                        })


                # ============================================
                # IDENTITY
                # ============================================


                if keyword_hit(
                    key,
                    IDENTITY_KEYWORDS,
                ):

                    identity_key_counter[
                        key
                    ] += 1


                    identity_path_counter[
                        normalized_path
                    ] += 1


                    local_identity_keys.append(
                        key
                    )


                    race_with_identity_key.add(
                        race_key
                    )


                    if len(
                        identity_samples[
                            normalized_path
                        ]
                    ) < 5:

                        identity_samples[
                            normalized_path
                        ].append({

                            "race_key":
                                race_key,

                            "value":
                                safe_sample(
                                    value
                                ),

                        })


                # ============================================
                # DATE VALUE
                # ============================================


                if not isinstance(
                    value,
                    (
                        dict,
                        list,
                    ),
                ):

                    if is_date_like(
                        value
                    ):

                        date_value_counter[
                            str(
                                value
                            )
                        ] += 1


                    if is_small_race_number(
                        value
                    ):

                        small_number_counter[
                            str(
                                value
                            )
                        ] += 1


            race_summary[
                "responses"
            ].append({

                "response_index":
                    response_index,

                "status":
                    "RESEARCHED",

                "json_source_path":
                    extracted.get(
                        "path"
                    ),

                "json_candidate_count":
                    extracted.get(
                        "candidate_count"
                    ),

                "walked_path_count":
                    local_paths,

                "result_keys":
                    sorted(
                        set(
                            local_result_keys
                        )
                    ),

                "rider_keys":
                    sorted(
                        set(
                            local_rider_keys
                        )
                    ),

                "ability_keys":
                    sorted(
                        set(
                            local_ability_keys
                        )
                    ),

                "identity_keys":
                    sorted(
                        set(
                            local_identity_keys
                        )
                    ),

            })


        race_results.append(
            race_summary
        )


    # ========================================================
    # PATH OUTPUT
    # ========================================================


    def make_path_output(
        counter,
        samples,
        limit=200,
    ):

        output = []


        for path, count in counter.most_common(
            limit
        ):

            output.append({

                "path":
                    path,

                "count":
                    count,

                "value_types":
                    dict(
                        path_type_counter.get(
                            path,
                            {}
                        )
                    ),

                "samples":
                    samples.get(
                        path,
                        []
                    ),

            })


        return output


    # ========================================================
    # ROUGH JUDGEMENT
    # ========================================================


    result_race_count = len(
        race_with_result_key
    )


    rider_race_count = len(
        race_with_rider_key
    )


    ability_race_count = len(
        race_with_ability_key
    )


    if (
        ability_race_count > 0
        and
        result_race_count > 0
    ):

        rough_judgement = (
            "RESULT_AND_PRE_RACE_LIKE_DATA_MIXED"
        )


    elif ability_race_count > 0:

        rough_judgement = (
            "PRE_RACE_ABILITY_LIKE_DATA"
        )


    elif result_race_count > 0:

        rough_judgement = (
            "RESULT_OR_RACE_STATUS_LIKE_DATA"
        )


    elif rider_race_count > 0:

        rough_judgement = (
            "RIDER_RELATED_DATA"
        )


    else:

        rough_judgement = (
            "UNKNOWN"
        )


    # ========================================================
    # OUTPUT
    # ========================================================


    output = {

        "program":
            "052_test.py",

        "created_at":
            datetime.now().isoformat(),

        "source_file":
            str(
                SOURCE_FILE
            ),

        "target_date":
            source_data.get(
                "target_date"
            ),

        "found_race_count":
            len(
                race_results
            ),

        "response_total":
            response_total,

        "response_json_found":
            response_json_found,

        "response_json_not_found":
            response_json_not_found,

        "race_category_counts": {

            "result_key_races":
                result_race_count,

            "rider_key_races":
                rider_race_count,

            "ability_key_races":
                ability_race_count,

            "identity_key_races":
                len(
                    race_with_identity_key
                ),

        },

        "rough_judgement":
            rough_judgement,

        "key_top_300":
            key_counter.most_common(
                300
            ),

        "result_key_summary":
            result_key_counter.most_common(),

        "rider_key_summary":
            rider_key_counter.most_common(),

        "ability_key_summary":
            ability_key_counter.most_common(),

        "identity_key_summary":
            identity_key_counter.most_common(),

        "result_paths":
            make_path_output(
                result_path_counter,
                result_samples,
            ),

        "rider_paths":
            make_path_output(
                rider_path_counter,
                rider_samples,
            ),

        "ability_paths":
            make_path_output(
                ability_path_counter,
                ability_samples,
            ),

        "identity_paths":
            make_path_output(
                identity_path_counter,
                identity_samples,
            ),

        "all_path_top_500": [

            {

                "path":
                    path,

                "count":
                    count,

                "value_types":
                    dict(
                        path_type_counter[
                            path
                        ]
                    ),

            }

            for path, count in path_counter.most_common(
                500
            )

        ],

        "date_value_summary":
            date_value_counter.most_common(
                100
            ),

        "small_number_value_summary":
            small_number_counter.most_common(
                20
            ),

        "race_with_result_key":
            sorted(
                race_with_result_key
            ),

        "race_with_rider_key":
            sorted(
                race_with_rider_key
            ),

        "race_with_ability_key":
            sorted(
                race_with_ability_key
            ),

        "races":
            race_results,

    }


    save_json(
        OUT_FILE,
        output
    )


    # ========================================================
    # FINAL RESULT
    # ========================================================


    print()

    print(
        "#"
        * 100
    )

    print(
        "052 最終結果"
    )

    print(
        "#"
        * 100
    )

    print()

    print(
        "TARGET DATE:",
        output.get(
            "target_date"
        )
    )

    print(
        "FOUND RACES:",
        output.get(
            "found_race_count"
        )
    )

    print(
        "RESPONSE TOTAL:",
        response_total
    )

    print(
        "RESPONSE JSON FOUND:",
        response_json_found
    )

    print(
        "RESPONSE JSON NOT FOUND:",
        response_json_not_found
    )

    print()

    print(
        "RESULT KEY RACES:",
        result_race_count
    )

    print(
        "RIDER KEY RACES:",
        rider_race_count
    )

    print(
        "ABILITY KEY RACES:",
        ability_race_count
    )

    print(
        "IDENTITY KEY RACES:",
        len(
            race_with_identity_key
        )
    )

    print()

    print(
        "ROUGH JUDGEMENT:",
        rough_judgement
    )


    # ========================================================
    # RESULT KEYS
    # ========================================================


    print()

    print(
        "★ RESULT KEY TOP50 ★"
    )


    if not result_key_counter:

        print(
            "なし"
        )


    for key, count in result_key_counter.most_common(
        50
    ):

        print(
            key,
            ":",
            count
        )


    # ========================================================
    # RIDER KEYS
    # ========================================================


    print()

    print(
        "★ RIDER KEY TOP50 ★"
    )


    if not rider_key_counter:

        print(
            "なし"
        )


    for key, count in rider_key_counter.most_common(
        50
    ):

        print(
            key,
            ":",
            count
        )


    # ========================================================
    # ABILITY KEYS
    # ========================================================


    print()

    print(
        "★ ABILITY KEY TOP100 ★"
    )


    if not ability_key_counter:

        print(
            "なし"
        )


    for key, count in ability_key_counter.most_common(
        100
    ):

        print(
            key,
            ":",
            count
        )


    # ========================================================
    # RESULT PATH
    # ========================================================


    print()

    print(
        "★ RESULT PATH TOP50 ★"
    )


    if not result_path_counter:

        print(
            "なし"
        )


    for path, count in result_path_counter.most_common(
        50
    ):

        print()

        print(
            path,
            ":",
            count
        )


        samples = result_samples.get(
            path,
            []
        )


        for sample in samples[:3]:

            print(
                "  ",
                sample.get(
                    "race_key"
                ),
                "=>",
                sample.get(
                    "value"
                ),
            )


    # ========================================================
    # ABILITY PATH
    # ========================================================


    print()

    print(
        "★ ABILITY PATH TOP100 ★"
    )


    if not ability_path_counter:

        print(
            "なし"
        )


    for path, count in ability_path_counter.most_common(
        100
    ):

        print()

        print(
            path,
            ":",
            count
        )


        samples = ability_samples.get(
            path,
            []
        )


        for sample in samples[:3]:

            print(
                "  ",
                sample.get(
                    "race_key"
                ),
                "=>",
                sample.get(
                    "value"
                ),
            )


    # ========================================================
    # DATE VALUES
    # ========================================================


    print()

    print(
        "★ DATE VALUE TOP50 ★"
    )


    if not date_value_counter:

        print(
            "なし"
        )


    for value, count in date_value_counter.most_common(
        50
    ):

        print(
            value,
            ":",
            count
        )


    # ========================================================
    # PER RACE
    # ========================================================


    print()

    print(
        "★ RESPONSE SUMMARY TOP20 ★"
    )


    for race in race_results[:20]:

        print()

        print(
            race.get(
                "race_key"
            )
        )


        for response in race.get(
            "responses",
            []
        ):

            print(
                "RESPONSE:",
                response.get(
                    "response_index"
                )
            )

            print(
                "STATUS:",
                response.get(
                    "status"
                )
            )

            print(
                "JSON SOURCE:",
                response.get(
                    "json_source_path"
                )
            )

            print(
                "PATH COUNT:",
                response.get(
                    "walked_path_count"
                )
            )

            print(
                "RESULT KEYS:",
                response.get(
                    "result_keys"
                )
            )

            print(
                "RIDER KEYS:",
                response.get(
                    "rider_keys"
                )
            )

            print(
                "ABILITY KEYS:",
                response.get(
                    "ability_keys"
                )
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
        "=== 052 完了 ==="
    )


if __name__ == "__main__":

    main()