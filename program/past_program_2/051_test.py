from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
import json


# ============================================================
# 051
#
# AI PRE-RACE DATA MERGE
#
# 043
# 公式ライン復元データ
#
# +
#
# 044
# AI学習対象監査
#
# +
#
# 050
# race_key付きJSJ006
#
# ↓
#
# race_key完全一致接続
#
#
# 目的:
#
# ・AI学習対象46件を基準にする
# ・ライン情報を接続
# ・JSJ006を接続
# ・READY FOR AI判定
#
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


AUDIT_FILE = (
    BASE
    / "data_official"
    / "line_research"
    / "044_line_audit"
    / "044_line_audit.json"
)


JSJ006_FILE = (
    BASE
    / "data_official"
    / "pre_race"
    / "050_jsj006_race_click_only"
    / "050_jsj006_race_click_only.json"
)


OUT_DIR = (
    BASE
    / "data_ai"
    / "pre_race_merged"
    / "051_ai_pre_race_candidate"
)


OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


OUT_FILE = (
    OUT_DIR
    / "051_ai_pre_race_candidate.json"
)


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
# RECURSIVE SEARCH
# ============================================================


def walk_objects(value):

    if isinstance(value, dict):

        yield value

        for child in value.values():

            yield from walk_objects(
                child
            )


    elif isinstance(value, list):

        for child in value:

            yield from walk_objects(
                child
            )


# ============================================================
# RACE KEY INDEX
# ============================================================


def build_race_key_index(data):

    index = defaultdict(
        list
    )


    for obj in walk_objects(
        data
    ):

        race_key = obj.get(
            "race_key"
        )


        if not isinstance(
            race_key,
            str,
        ):

            continue


        if not race_key:

            continue


        index[
            race_key
        ].append(
            obj
        )


    return index


# ============================================================
# BEST LINE RECORD
# ============================================================


def line_score(obj):

    score = 0


    if obj.get(
        "race_key"
    ):

        score += 1


    for key in [

        "main_lines",
        "main",
        "lines",
        "line",
    ]:

        value = obj.get(
            key
        )


        if isinstance(
            value,
            list,
        ) and value:

            score += 100

            score += len(
                value
            )


    for key in [

        "prediction_type",
        "type",

    ]:

        if obj.get(
            key
        ) is not None:

            score += 10


    for key in [

        "provider",
        "information_provider",

    ]:

        if obj.get(
            key
        ):

            score += 10


    for key in [

        "competition_rows",
        "competition",

    ]:

        if key in obj:

            score += 5


    return score


def choose_best_line_record(
    candidates
):

    if not candidates:

        return None


    return max(

        candidates,

        key=line_score,

    )


# ============================================================
# NORMALIZE LINE
# ============================================================


def first_existing(
    obj,
    keys,
    default=None,
):

    if not isinstance(
        obj,
        dict,
    ):

        return default


    for key in keys:

        if key in obj:

            return obj.get(
                key
            )


    return default


def normalize_line_record(obj):

    if not isinstance(
        obj,
        dict,
    ):

        return None


    main_lines = first_existing(

        obj,

        [
            "main_lines",
            "main",
            "lines",
            "line",
        ],

        None,

    )


    prediction_type = first_existing(

        obj,

        [
            "prediction_type",
            "type",
        ],

        None,

    )


    provider = first_existing(

        obj,

        [
            "provider",
            "information_provider",
        ],

        None,

    )


    competition = first_existing(

        obj,

        [
            "competition_rows",
            "competition",
        ],

        [],

    )


    return {

        "prediction_type":
            prediction_type,

        "provider":
            provider,

        "main_lines":
            main_lines,

        "competition":
            competition,

        "source_status":
            obj.get(
                "status"
            ),

        "raw_line_record":
            obj,

    }


# ============================================================
# 044 ELIGIBILITY
# ============================================================


def eligibility_score(obj):

    score = 0


    if obj.get(
        "race_key"
    ):

        score += 1


    for key in [

        "ai_learning_eligible",
        "learning_eligible",
        "eligible",

    ]:

        if key in obj:

            score += 100


    if "warnings" in obj:

        score += 20


    if "issues" in obj:

        score += 20


    if "issue" in obj:

        score += 20


    if obj.get(
        "audit_status"
    ):

        score += 10


    return score


def choose_best_audit_record(
    candidates
):

    if not candidates:

        return None


    return max(

        candidates,

        key=eligibility_score,

    )


def get_explicit_eligibility(obj):

    if not isinstance(
        obj,
        dict,
    ):

        return None


    for key in [

        "ai_learning_eligible",
        "learning_eligible",
        "eligible",

    ]:

        if key in obj:

            value = obj.get(
                key
            )


            if isinstance(
                value,
                bool,
            ):

                return value


            if isinstance(
                value,
                int,
            ):

                return bool(
                    value
                )


            if isinstance(
                value,
                str,
            ):

                upper = value.upper()


                if upper in {

                    "TRUE",
                    "YES",
                    "ELIGIBLE",
                    "AI_LEARNING_ELIGIBLE",

                }:

                    return True


                if upper in {

                    "FALSE",
                    "NO",
                    "EXCLUDED",
                    "AI_LEARNING_EXCLUDED",

                }:

                    return False


    return None


# ============================================================
# TOP LEVEL ELIGIBLE KEY SEARCH
# ============================================================


def collect_string_race_keys(
    value
):

    found = set()


    if isinstance(
        value,
        str,
    ):

        if (
            value.count(
                "_"
            )
            >= 2
            and
            value.endswith(
                "R"
            )
        ):

            found.add(
                value
            )


    elif isinstance(
        value,
        dict,
    ):

        race_key = value.get(
            "race_key"
        )


        if isinstance(
            race_key,
            str,
        ):

            found.add(
                race_key
            )


        for child in value.values():

            found.update(

                collect_string_race_keys(
                    child
                )

            )


    elif isinstance(
        value,
        list,
    ):

        for child in value:

            found.update(

                collect_string_race_keys(
                    child
                )

            )


    return found


def find_named_eligible_keys(data):

    eligible_keys = set()

    source_fields = []


    if not isinstance(
        data,
        dict,
    ):

        return (
            eligible_keys,
            source_fields,
        )


    for key, value in data.items():

        key_upper = str(
            key
        ).upper()


        if (
            "ELIGIBLE"
            in key_upper
            and
            "COUNT"
            not in key_upper
        ):

            keys = collect_string_race_keys(
                value
            )


            if keys:

                eligible_keys.update(
                    keys
                )


                source_fields.append({

                    "field":
                        key,

                    "race_key_count":
                        len(
                            keys
                        ),

                })


    return (
        eligible_keys,
        source_fields,
    )


# ============================================================
# JSJ006 INDEX
# ============================================================


def build_jsj006_index(data):

    index = {}


    for race in data.get(
        "races",
        []
    ):

        race_key = race.get(
            "race_key"
        )


        if not race_key:

            continue


        if race.get(
            "status"
        ) != "JSJ006_FOUND":

            continue


        responses = race.get(
            "jsj006_responses",
            []
        )


        if not responses:

            continue


        index[
            race_key
        ] = race


    return index


# ============================================================
# ELIGIBLE DETECTION
# ============================================================


def detect_eligible_race_keys(
    audit_data,
    audit_index,
):

    # ========================================================
    # METHOD 1
    # 名前付きELIGIBLE一覧
    # ========================================================


    named_keys, source_fields = (
        find_named_eligible_keys(
            audit_data
        )
    )


    if named_keys:

        return {

            "method":
                "NAMED_ELIGIBLE_FIELD",

            "race_keys":
                named_keys,

            "source_fields":
                source_fields,

        }


    # ========================================================
    # METHOD 2
    # race record explicit boolean
    # ========================================================


    explicit_true = set()

    explicit_false = set()


    for race_key, candidates in (
        audit_index.items()
    ):

        record = choose_best_audit_record(
            candidates
        )


        eligibility = get_explicit_eligibility(
            record
        )


        if eligibility is True:

            explicit_true.add(
                race_key
            )


        elif eligibility is False:

            explicit_false.add(
                race_key
            )


    if explicit_true:

        return {

            "method":
                "EXPLICIT_RACE_ELIGIBILITY",

            "race_keys":
                explicit_true,

            "source_fields": [],

            "explicit_false_count":
                len(
                    explicit_false
                ),

        }


    # ========================================================
    # METHOD 3
    # 044仕様から除外判定
    #
    # PREDICTION_TYPE_NONE
    # = ガールズ等
    #
    # その他ISSUEあり
    # = 除外
    # ========================================================


    inferred = set()


    for race_key, candidates in (
        audit_index.items()
    ):

        record = choose_best_audit_record(
            candidates
        )


        if not record:

            continue


        warnings = record.get(
            "warnings",
            []
        )


        issues = first_existing(

            record,

            [
                "issues",
                "issue",
            ],

            [],

        )


        if warnings is None:

            warnings = []


        if issues is None:

            issues = []


        if isinstance(
            warnings,
            str,
        ):

            warnings = [
                warnings
            ]


        if isinstance(
            issues,
            str,
        ):

            issues = [
                issues
            ]


        prediction_type = first_existing(

            record,

            [
                "prediction_type",
                "type",
            ],

            None,

        )


        if (
            prediction_type is None
            or
            "PREDICTION_TYPE_NONE"
            in warnings
        ):

            continue


        if issues:

            continue


        inferred.add(
            race_key
        )


    return {

        "method":
            "INFERRED_FROM_044_AUDIT",

        "race_keys":
            inferred,

        "source_fields": [],

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
        "051 043 + 044 + 050 AI PRE-RACE MERGE"
    )

    print(
        "="
        * 100
    )

    print()


    required_files = [

        LINE_FILE,
        AUDIT_FILE,
        JSJ006_FILE,

    ]


    for path in required_files:

        print(
            "INPUT:",
            path
        )


        if not path.exists():

            print()

            print(
                "ERROR: 必要ファイルがありません"
            )

            print(
                path
            )

            return


    # ========================================================
    # LOAD
    # ========================================================


    line_data = load_json(
        LINE_FILE
    )


    audit_data = load_json(
        AUDIT_FILE
    )


    jsj006_data = load_json(
        JSJ006_FILE
    )


    # ========================================================
    # INDEX
    # ========================================================


    line_index = build_race_key_index(
        line_data
    )


    audit_index = build_race_key_index(
        audit_data
    )


    jsj006_index = build_jsj006_index(
        jsj006_data
    )


    # ========================================================
    # ELIGIBLE
    # ========================================================


    eligibility_result = (
        detect_eligible_race_keys(

            audit_data,

            audit_index,

        )
    )


    eligible_race_keys = sorted(

        eligibility_result[
            "race_keys"
        ]

    )


    print()

    print(
        "ELIGIBILITY METHOD:",
        eligibility_result[
            "method"
        ]
    )

    print(
        "ELIGIBLE RACE KEYS:",
        len(
            eligible_race_keys
        )
    )

    print(
        "LINE INDEX RACE KEYS:",
        len(
            line_index
        )
    )

    print(
        "AUDIT INDEX RACE KEYS:",
        len(
            audit_index
        )
    )

    print(
        "JSJ006 FOUND INDEX:",
        len(
            jsj006_index
        )
    )


    # ========================================================
    # MERGE
    # ========================================================


    merged_races = []

    merge_status_counter = Counter()

    ready_count = 0


    for race_key in eligible_race_keys:

        line_candidates = line_index.get(
            race_key,
            []
        )


        audit_candidates = audit_index.get(
            race_key,
            []
        )


        line_record = choose_best_line_record(
            line_candidates
        )


        audit_record = choose_best_audit_record(
            audit_candidates
        )


        jsj006_record = jsj006_index.get(
            race_key
        )


        normalized_line = normalize_line_record(
            line_record
        )


        line_found = (

            normalized_line is not None

            and

            isinstance(
                normalized_line.get(
                    "main_lines"
                ),
                list,
            )

            and

            bool(
                normalized_line.get(
                    "main_lines"
                )
            )

        )


        jsj006_found = (

            jsj006_record is not None

            and

            bool(
                jsj006_record.get(
                    "jsj006_responses"
                )
            )

        )


        if (
            line_found
            and
            jsj006_found
        ):

            merge_status = (
                "READY_FOR_AI"
            )


            ready_for_ai = True

            ready_count += 1


        elif (
            line_found
            and
            not jsj006_found
        ):

            merge_status = (
                "JSJ006_NOT_FOUND"
            )


            ready_for_ai = False


        elif (
            not line_found
            and
            jsj006_found
        ):

            merge_status = (
                "LINE_NOT_FOUND"
            )


            ready_for_ai = False


        else:

            merge_status = (
                "LINE_AND_JSJ006_NOT_FOUND"
            )


            ready_for_ai = False


        merge_status_counter[
            merge_status
        ] += 1


        merged_races.append({

            "race_key":
                race_key,

            "ai_learning_eligible":
                True,

            "ready_for_ai":
                ready_for_ai,

            "merge_status":
                merge_status,

            "line_found":
                line_found,

            "jsj006_found":
                jsj006_found,

            "line_data":
                normalized_line,

            "jsj006_response_count":
                (
                    jsj006_record.get(
                        "jsj006_response_count",
                        0
                    )

                    if jsj006_record

                    else 0
                ),

            "jsj006_raw":
                (
                    jsj006_record.get(
                        "jsj006_responses",
                        []
                    )

                    if jsj006_record

                    else []
                ),

            "audit_record":
                audit_record,

        })


    # ========================================================
    # JSJ006 FOUND BUT NOT ELIGIBLE
    # ========================================================


    eligible_set = set(
        eligible_race_keys
    )


    jsj006_not_eligible = sorted(

        set(
            jsj006_index.keys()
        )

        -
        eligible_set

    )


    # ========================================================
    # OUTPUT
    # ========================================================


    output = {

        "program":
            "051_test.py",

        "created_at":
            datetime.now().isoformat(),

        "source_files": {

            "line":
                str(
                    LINE_FILE
                ),

            "audit":
                str(
                    AUDIT_FILE
                ),

            "jsj006":
                str(
                    JSJ006_FILE
                ),

        },

        "target_date":
            jsj006_data.get(
                "target_date"
            ),

        "eligibility_detection": {

            **eligibility_result,

            "race_keys":
                sorted(
                    eligibility_result.get(
                        "race_keys",
                        []
                    )
                ),

        },

        "ai_learning_eligible_count":
            len(
                eligible_race_keys
            ),

        "jsj006_found_total_count":
            len(
                jsj006_index
            ),

        "ready_for_ai_count":
            ready_count,

        "merge_status_summary":
            dict(
                merge_status_counter
            ),

        "jsj006_found_but_not_eligible_count":
            len(
                jsj006_not_eligible
            ),

        "jsj006_found_but_not_eligible":
            jsj006_not_eligible,

        "races":
            merged_races,

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
        "051 最終結果"
    )

    print(
        "#"
        * 100
    )

    print()

    print(
        "TARGET DATE:",
        output[
            "target_date"
        ]
    )

    print(
        "ELIGIBILITY METHOD:",
        eligibility_result[
            "method"
        ]
    )

    print(
        "AI LEARNING ELIGIBLE:",
        output[
            "ai_learning_eligible_count"
        ]
    )

    print(
        "JSJ006 FOUND TOTAL:",
        output[
            "jsj006_found_total_count"
        ]
    )

    print(
        "READY FOR AI:",
        output[
            "ready_for_ai_count"
        ]
    )

    print(
        "JSJ006 FOUND BUT NOT ELIGIBLE:",
        output[
            "jsj006_found_but_not_eligible_count"
        ]
    )


    print()

    print(
        "★ MERGE STATUS ★"
    )


    for status, count in (
        merge_status_counter.items()
    ):

        print(
            status,
            ":",
            count
        )


    print()

    print(
        "★ READY FOR AI RACE KEY ★"
    )


    ready_races = [

        race

        for race in merged_races

        if race.get(
            "ready_for_ai"
        )

    ]


    if not ready_races:

        print(
            "なし"
        )


    for race in ready_races:

        line_data_record = race.get(
            "line_data"
        ) or {}


        print()

        print(
            race.get(
                "race_key"
            )
        )

        print(
            "TYPE:",
            line_data_record.get(
                "prediction_type"
            )
        )

        print(
            "PROVIDER:",
            line_data_record.get(
                "provider"
            )
        )

        print(
            "MAIN LINES:",
            line_data_record.get(
                "main_lines"
            )
        )

        print(
            "COMPETITION:",
            line_data_record.get(
                "competition"
            )
        )

        print(
            "JSJ006 RESPONSE COUNT:",
            race.get(
                "jsj006_response_count"
            )
        )


    print()

    print(
        "★ JSJ006 NOT FOUND IN ELIGIBLE ★"
    )


    missing_jsj006 = [

        race

        for race in merged_races

        if (
            race.get(
                "ai_learning_eligible"
            )
            and
            not race.get(
                "jsj006_found"
            )
        )

    ]


    if not missing_jsj006:

        print(
            "なし"
        )


    for race in missing_jsj006:

        print(
            race.get(
                "race_key"
            )
        )


    print()

    print(
        "★ JSJ006 FOUND BUT NOT ELIGIBLE ★"
    )


    if not jsj006_not_eligible:

        print(
            "なし"
        )


    for race_key in jsj006_not_eligible:

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
        "=== 051 完了 ==="
    )


if __name__ == "__main__":

    main()