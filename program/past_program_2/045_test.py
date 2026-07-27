from pathlib import Path
from datetime import datetime
from collections import Counter
import json
import re


# ============================================================
# 045
#
# race_key 自動接続テスト
#
# 目的:
#
# 043 当日ラインデータ
#        +
# 当日レース前能力データ
#
# を race_key で自動接続する
#
#
# 重要:
#
# ・043の日付を基準にする
# ・C:\競輪AI 内のJSONを自動探索
# ・同じ日付のrace_keyだけ対象
# ・古いデータを誤接続しない
# ・元データは変更しない
# ・ガールズ等は削除しない
# ・学習対象判定は別フィールドで保存
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
    / "pre_race_merged"
)


OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


OUT_FILE = (
    OUT_DIR
    / "045_pre_race_line_merged.json"
)


SEARCH_EXCLUDE_DIR_NAMES = {

    ".git",

    ".venv",

    "venv",

    "__pycache__",

    "node_modules",

}


SEARCH_EXCLUDE_FILE_NAMES = {

    LINE_FILE.name,

    OUT_FILE.name,

    "044_line_audit.json",

}


# ============================================================
# JSON読込
# ============================================================


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


# ============================================================
# JSON保存
# ============================================================


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
# race_key 正規化
# ============================================================


def normalize_race_key(value):

    if not isinstance(
        value,
        str,
    ):

        return None


    value = (
        value
        .strip()
        .replace("　", "")
    )


    # --------------------------------------------------------
    # 正式形式
    #
    # 20260710_函館_1R
    # --------------------------------------------------------


    match = re.fullmatch(
        r"(20\d{6})_([^_]+)_(\d{1,2})R",
        value,
    )


    if match:

        race_date = (
            match.group(1)
        )

        venue = (
            match.group(2)
            .strip()
        )

        race_no = int(
            match.group(3)
        )


        return (

            f"{race_date}_"
            f"{venue}_"
            f"{race_no}R"

        )


    # --------------------------------------------------------
    # Rなし形式
    #
    # 20260710_函館_1
    # --------------------------------------------------------


    match = re.fullmatch(
        r"(20\d{6})_([^_]+)_(\d{1,2})",
        value,
    )


    if match:

        race_date = (
            match.group(1)
        )

        venue = (
            match.group(2)
            .strip()
        )

        race_no = int(
            match.group(3)
        )


        return (

            f"{race_date}_"
            f"{venue}_"
            f"{race_no}R"

        )


    return None


# ============================================================
# 辞書から race_key 候補取得
# ============================================================


def extract_direct_race_key(obj):

    if not isinstance(
        obj,
        dict,
    ):

        return None


    key_names = [

        "race_key",

        "raceKey",

        "race_id",

        "raceId",

    ]


    for key_name in key_names:

        value = obj.get(
            key_name
        )


        normalized = (
            normalize_race_key(
                value
            )
        )


        if normalized:

            return normalized


    return None


# ============================================================
# date / venue / race_no から race_key生成
# ============================================================


def extract_built_race_key(obj):

    if not isinstance(
        obj,
        dict,
    ):

        return None


    date_keys = [

        "race_date",

        "raceDate",

        "date",

        "target_date",

        "targetDate",

    ]


    venue_keys = [

        "venue",

        "venue_name",

        "venueName",

        "jo_name",

        "joName",

        "place",

    ]


    race_no_keys = [

        "race_no",

        "raceNo",

        "race_number",

        "raceNumber",

    ]


    race_date = None

    venue = None

    race_no = None


    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------


    for key_name in date_keys:

        value = obj.get(
            key_name
        )


        if value is None:

            continue


        text = str(
            value
        )


        digits = re.sub(
            r"\D",
            "",
            text,
        )


        if re.fullmatch(
            r"20\d{6}",
            digits,
        ):

            race_date = digits

            break


    # --------------------------------------------------------
    # VENUE
    # --------------------------------------------------------


    for key_name in venue_keys:

        value = obj.get(
            key_name
        )


        if isinstance(
            value,
            str,
        ):

            value = (
                value
                .strip()
            )


            if value:

                venue = value

                break


    # --------------------------------------------------------
    # RACE NO
    # --------------------------------------------------------


    for key_name in race_no_keys:

        value = obj.get(
            key_name
        )


        if value is None:

            continue


        match = re.search(
            r"\d{1,2}",
            str(
                value
            ),
        )


        if match:

            race_no = int(
                match.group(0)
            )

            break


    if (
        race_date
        and
        venue
        and
        race_no is not None
    ):

        return (

            f"{race_date}_"
            f"{venue}_"
            f"{race_no}R"

        )


    return None


# ============================================================
# JSON内を再帰探索
#
# race_keyを持つ辞書をレース候補として収集
# ============================================================


def collect_race_objects(
    obj,
    source_file,
    json_path="$",
    results=None,
):

    if results is None:

        results = []


    if isinstance(
        obj,
        dict,
    ):

        race_key = (
            extract_direct_race_key(
                obj
            )
        )


        race_key_method = None


        if race_key:

            race_key_method = (
                "DIRECT_RACE_KEY"
            )


        if not race_key:

            race_key = (
                extract_built_race_key(
                    obj
                )
            )


            if race_key:

                race_key_method = (
                    "BUILT_FROM_FIELDS"
                )


        if race_key:

            results.append({

                "race_key":
                    race_key,

                "race_key_method":
                    race_key_method,

                "source_file":
                    str(
                        source_file
                    ),

                "json_path":
                    json_path,

                "data":
                    obj,

            })


        for key, value in obj.items():

            child_path = (

                f"{json_path}."
                f"{key}"

            )


            collect_race_objects(

                value,

                source_file,

                child_path,

                results,

            )


    elif isinstance(
        obj,
        list,
    ):

        for index, value in enumerate(
            obj
        ):

            child_path = (

                f"{json_path}"
                f"[{index}]"

            )


            collect_race_objects(

                value,

                source_file,

                child_path,

                results,

            )


    return results


# ============================================================
# JSONファイル探索
# ============================================================


def find_json_files():

    json_files = []


    for path in BASE.rglob(
        "*.json"
    ):

        try:

            relative_parts = (
                path.relative_to(
                    BASE
                ).parts
            )


            if any(

                part
                in
                SEARCH_EXCLUDE_DIR_NAMES

                for part
                in relative_parts

            ):

                continue


            if (
                path.name
                in
                SEARCH_EXCLUDE_FILE_NAMES
            ):

                continue


            json_files.append(
                path
            )


        except Exception:

            continue


    return sorted(
        json_files
    )


# ============================================================
# 043ラインレース平坦化
# ============================================================


def flatten_line_races(line_data):

    races = []


    for venue_data in line_data.get(
        "venues",
        []
    ):

        for race in venue_data.get(
            "races",
            []
        ):

            races.append(
                race
            )


    return races


# ============================================================
# 学習対象判定
#
# 現段階:
#
# ・ライン取得成功
# ・TYPEあり
# ・main_linesあり
#
# TYPE None の全員単騎等は一旦除外
# ============================================================


def judge_ai_learning_eligible(
    line_race,
):

    status = line_race.get(
        "status"
    )


    prediction_type = line_race.get(
        "prediction_type"
    )


    main_lines = line_race.get(
        "main_lines",
        []
    )


    if (
        status
        !=
        "LINE_FOUND"
    ):

        return (
            False,
            "LINE_NOT_AVAILABLE",
        )


    if (
        prediction_type
        is None
    ):

        return (
            False,
            "NO_LINE_RACE",
        )


    if not main_lines:

        return (
            False,
            "MAIN_LINES_EMPTY",
        )


    return (
        True,
        None,
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
        "045 race_key レース前能力 × ライン 自動接続テスト"
    )

    print(
        "="
        * 100
    )

    print()


    # ========================================================
    # 043確認
    # ========================================================


    print(
        "[1] 043ラインデータ確認"
    )

    print()

    print(
        LINE_FILE
    )


    if not LINE_FILE.exists():

        print()

        print(
            "ERROR: 043 JSONがありません"
        )

        return


    line_data = load_json(
        LINE_FILE
    )


    race_date = line_data.get(
        "race_date"
    )


    line_races = (
        flatten_line_races(
            line_data
        )
    )


    line_found_races = [

        race

        for race in line_races

        if (
            race.get(
                "status"
            )
            ==
            "LINE_FOUND"
        )

    ]


    print()

    print(
        "TARGET DATE:",
        race_date
    )

    print(
        "LINE RACES:",
        len(
            line_races
        )
    )

    print(
        "LINE FOUND:",
        len(
            line_found_races
        )
    )


    # ========================================================
    # JSON探索
    # ========================================================


    print()

    print(
        "[2] C:\\競輪AI JSON自動探索"
    )


    json_files = (
        find_json_files()
    )


    print()

    print(
        "JSON FILE COUNT:",
        len(
            json_files
        )
    )


    # ========================================================
    # race_key候補収集
    # ========================================================


    print()

    print(
        "[3] race_key候補収集"
    )


    candidate_objects = []

    file_scan_results = []


    for index, path in enumerate(
        json_files,
        start=1,
    ):

        file_record = {

            "file":
                str(
                    path
                ),

            "status":
                None,

            "race_object_count":
                0,

            "target_date_count":
                0,

            "error":
                None,

        }


        try:

            data = load_json(
                path
            )


            race_objects = (
                collect_race_objects(
                    data,
                    path,
                )
            )


            target_date_objects = [

                item

                for item in race_objects

                if (
                    isinstance(
                        item.get(
                            "race_key"
                        ),
                        str,
                    )
                    and
                    item[
                        "race_key"
                    ].startswith(
                        str(
                            race_date
                        )
                        +
                        "_"
                    )
                )

            ]


            file_record[
                "status"
            ] = (
                "SCAN_OK"
            )


            file_record[
                "race_object_count"
            ] = (
                len(
                    race_objects
                )
            )


            file_record[
                "target_date_count"
            ] = (
                len(
                    target_date_objects
                )
            )


            candidate_objects.extend(
                target_date_objects
            )


            if target_date_objects:

                print()

                print(
                    f"[{index}/"
                    f"{len(json_files)}]"
                )

                print(
                    "MATCH FILE:"
                )

                print(
                    path
                )

                print(
                    "TARGET DATE OBJECTS:",
                    len(
                        target_date_objects
                    )
                )


        except Exception as e:

            file_record[
                "status"
            ] = (
                "SCAN_ERROR"
            )


            file_record[
                "error"
            ] = (
                repr(
                    e
                )
            )


        file_scan_results.append(
            file_record
        )


    print()

    print(
        "TARGET DATE CANDIDATES:",
        len(
            candidate_objects
        )
    )


    # ========================================================
    # race_key別候補MAP
    # ========================================================


    candidate_map = {}


    for item in candidate_objects:

        race_key = item.get(
            "race_key"
        )


        if race_key not in candidate_map:

            candidate_map[
                race_key
            ] = []


        candidate_map[
            race_key
        ].append(
            item
        )


    # ========================================================
    # ラインデータと照合
    # ========================================================


    print()

    print(
        "[4] race_key照合"
    )


    merged_races = []

    matched_count = 0

    unmatched_count = 0

    multiple_candidate_count = 0


    for line_race in line_races:

        race_key = (
            normalize_race_key(
                line_race.get(
                    "race_key"
                )
            )
        )


        candidates = (
            candidate_map.get(
                race_key,
                []
            )
        )


        # ----------------------------------------------------
        # 043自身に近いデータを除外
        #
        # line_predictions由来の候補は
        # レース前能力データとして採用しない
        # ----------------------------------------------------


        filtered_candidates = []


        for candidate in candidates:

            source_file = (
                candidate.get(
                    "source_file",
                    ""
                )
            )


            source_lower = (
                source_file.lower()
            )


            if (
                "line_predictions"
                in
                source_lower
            ):

                continue


            if (
                "line_research"
                in
                source_lower
            ):

                continue


            filtered_candidates.append(
                candidate
            )


        candidates = (
            filtered_candidates
        )


        eligible, exclude_reason = (
            judge_ai_learning_eligible(
                line_race
            )
        )


        merged_record = {

            "race_key":
                race_key,

            "race_date":
                line_race.get(
                    "race_date"
                ),

            "venue":
                line_race.get(
                    "venue"
                ),

            "race_no":
                line_race.get(
                    "race_no"
                ),

            "merge_status":
                None,

            "pre_race_candidate_count":
                len(
                    candidates
                ),

            "pre_race_source_file":
                None,

            "pre_race_json_path":
                None,

            "pre_race_race_key_method":
                None,

            "pre_race_data":
                None,

            "line_data": {

                "status":
                    line_race.get(
                        "status"
                    ),

                "prediction_type":
                    line_race.get(
                        "prediction_type"
                    ),

                "provider":
                    line_race.get(
                        "provider"
                    ),

                "main_lines":
                    line_race.get(
                        "main_lines",
                        []
                    ),

                "has_competition":
                    line_race.get(
                        "has_competition"
                    ),

                "competition_rows":
                    line_race.get(
                        "competition_rows",
                        []
                    ),

            },

            "ai_learning_eligible":
                eligible,

            "exclude_reason":
                exclude_reason,

        }


        if len(
            candidates
        ) == 0:

            merged_record[
                "merge_status"
            ] = (
                "PRE_RACE_NOT_FOUND"
            )


            unmatched_count += 1


        else:

            # ------------------------------------------------
            # 候補が複数でも今回は最初を保存
            #
            # ただし MULTIPLE を明示
            # 次のテストで正しい能力ファイルを固定できる
            # ------------------------------------------------


            selected = (
                candidates[0]
            )


            merged_record[
                "pre_race_source_file"
            ] = (
                selected.get(
                    "source_file"
                )
            )


            merged_record[
                "pre_race_json_path"
            ] = (
                selected.get(
                    "json_path"
                )
            )


            merged_record[
                "pre_race_race_key_method"
            ] = (
                selected.get(
                    "race_key_method"
                )
            )


            merged_record[
                "pre_race_data"
            ] = (
                selected.get(
                    "data"
                )
            )


            if len(
                candidates
            ) == 1:

                merged_record[
                    "merge_status"
                ] = (
                    "MATCHED"
                )


            else:

                merged_record[
                    "merge_status"
                ] = (
                    "MATCHED_MULTIPLE_CANDIDATES"
                )


                multiple_candidate_count += 1


            matched_count += 1


        merged_races.append(
            merged_record
        )


    # ========================================================
    # 集計
    # ========================================================


    merge_status_counter = Counter(

        item.get(
            "merge_status"
        )

        for item in merged_races

    )


    matched_source_counter = Counter(

        item.get(
            "pre_race_source_file"
        )

        for item in merged_races

        if item.get(
            "pre_race_source_file"
        )

    )


    eligible_count = len([

        item

        for item in merged_races

        if (
            item.get(
                "ai_learning_eligible"
            )
            is True
        )

    ])


    excluded_count = (

        len(
            merged_races
        )
        -
        eligible_count

    )


    # ========================================================
    # 保存
    # ========================================================


    output = {

        "program":
            "045_test.py",

        "created_at":
            datetime.now().isoformat(),

        "target_date":
            race_date,

        "line_source_file":
            str(
                LINE_FILE
            ),

        "json_scan_file_count":
            len(
                json_files
            ),

        "target_date_candidate_count":
            len(
                candidate_objects
            ),

        "line_race_count":
            len(
                line_races
            ),

        "matched_count":
            matched_count,

        "unmatched_count":
            unmatched_count,

        "multiple_candidate_count":
            multiple_candidate_count,

        "ai_learning_eligible_count":
            eligible_count,

        "ai_learning_excluded_count":
            excluded_count,

        "merge_status_summary":
            dict(
                merge_status_counter
            ),

        "matched_source_summary":
            dict(
                matched_source_counter
            ),

        "file_scan_results":
            file_scan_results,

        "races":
            merged_races,

    }


    save_json(
        OUT_FILE,
        output,
    )


    # ========================================================
    # 最終結果
    # ========================================================


    print()

    print(
        "#"
        * 100
    )

    print(
        "045 最終結果"
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
        "JSON SCAN FILES:",
        output[
            "json_scan_file_count"
        ]
    )

    print(
        "TARGET DATE CANDIDATES:",
        output[
            "target_date_candidate_count"
        ]
    )

    print(
        "LINE RACES:",
        output[
            "line_race_count"
        ]
    )

    print(
        "MATCHED:",
        output[
            "matched_count"
        ]
    )

    print(
        "UNMATCHED:",
        output[
            "unmatched_count"
        ]
    )

    print(
        "MULTIPLE CANDIDATES:",
        output[
            "multiple_candidate_count"
        ]
    )

    print(
        "AI LEARNING ELIGIBLE:",
        output[
            "ai_learning_eligible_count"
        ]
    )

    print(
        "AI LEARNING EXCLUDED:",
        output[
            "ai_learning_excluded_count"
        ]
    )


    print()

    print(
        "★ MERGE STATUS ★"
    )


    for key, value in (
        merge_status_counter.items()
    ):

        print(
            key,
            ":",
            value
        )


    print()

    print(
        "★ MATCHED SOURCE FILE ★"
    )


    if not matched_source_counter:

        print(
            "なし"
        )


    for key, value in (
        matched_source_counter.most_common()
    ):

        print()

        print(
            key
        )

        print(
            "MATCH:",
            value
        )


    print()

    print(
        "★ MATCHED SAMPLE TOP10 ★"
    )


    matched_samples = [

        item

        for item in merged_races

        if item.get(
            "merge_status"
        )
        in {

            "MATCHED",

            "MATCHED_MULTIPLE_CANDIDATES",

        }

    ]


    if not matched_samples:

        print(
            "なし"
        )


    for item in matched_samples[:10]:

        print()

        print(
            item.get(
                "race_key"
            )
        )

        print(
            "STATUS:",
            item.get(
                "merge_status"
            )
        )

        print(
            "CANDIDATES:",
            item.get(
                "pre_race_candidate_count"
            )
        )

        print(
            "SOURCE:",
            item.get(
                "pre_race_source_file"
            )
        )

        print(
            "JSON PATH:",
            item.get(
                "pre_race_json_path"
            )
        )

        print(
            "TYPE:",
            item.get(
                "line_data",
                {}
            ).get(
                "prediction_type"
            )
        )

        print(
            "LINES:",
            item.get(
                "line_data",
                {}
            ).get(
                "main_lines"
            )
        )

        print(
            "AI ELIGIBLE:",
            item.get(
                "ai_learning_eligible"
            )
        )


    print()

    print(
        "★ UNMATCHED SAMPLE TOP20 ★"
    )


    unmatched_samples = [

        item

        for item in merged_races

        if (
            item.get(
                "merge_status"
            )
            ==
            "PRE_RACE_NOT_FOUND"
        )

    ]


    if not unmatched_samples:

        print(
            "なし"
        )


    for item in unmatched_samples[:20]:

        print(

            item.get(
                "race_key"
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
        "=== 045 完了 ==="
    )


if __name__ == "__main__":

    main()