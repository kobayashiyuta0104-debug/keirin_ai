import json
import shutil
from pathlib import Path
from datetime import datetime
from collections import Counter


# ============================================================
# 059
#
# 本番用 日付別データ保存基盤
#
# 既存の成功済みデータを
#
# C:\競輪AI\data_daily\YYYYMMDD
#
# へ整理する
#
# 出力:
# pre_race.json
# line_prediction.json
# confirmed_result.json
# merged_training.json
# daily_manifest.json
# ============================================================


BASE = Path(r"C:\競輪AI")

TARGET_DATE = "20260710"


# ============================================================
# SOURCE
# ============================================================


PRE_RACE_SOURCE = (
    BASE
    / "data_official"
    / "pre_race"
    / "046_jsj006_by_race_key"
    / "046_jsj006_by_race_key.json"
)


LINE_SOURCE = (
    BASE
    / "data_official"
    / "line_predictions"
    / "043_all_venues_official_lines.json"
)


RESULT_SOURCE = (
    BASE
    / "data_official"
    / "confirmed_results"
    / "056_jsj012_confirmed_results"
    / "056_jsj012_confirmed_results.json"
)


MERGED_SOURCE = (
    BASE
    / "data_ai"
    / "training_dataset"
    / "057_merged_training_dataset"
    / "057_merged_training_dataset.json"
)


# ============================================================
# DAILY DIRECTORY
# ============================================================


DAILY_ROOT = (
    BASE
    / "data_daily"
)


DATE_DIR = (
    DAILY_ROOT
    / TARGET_DATE
)


DATE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


PRE_RACE_OUT = (
    DATE_DIR
    / "pre_race.json"
)


LINE_OUT = (
    DATE_DIR
    / "line_prediction.json"
)


RESULT_OUT = (
    DATE_DIR
    / "confirmed_result.json"
)


MERGED_OUT = (
    DATE_DIR
    / "merged_training.json"
)


MANIFEST_OUT = (
    DATE_DIR
    / "daily_manifest.json"
)


print(
    "=== 059 本番用 日付別データ保存基盤 ==="
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
# WALK
# ============================================================


def walk(value):

    yield value

    if isinstance(
        value,
        dict,
    ):

        for child in value.values():

            yield from walk(
                child
            )

    elif isinstance(
        value,
        list,
    ):

        for child in value:

            yield from walk(
                child
            )


# ============================================================
# RACE KEY
# ============================================================


def collect_race_keys(data):

    race_keys = set()

    for obj in walk(
        data
    ):

        if not isinstance(
            obj,
            dict,
        ):

            continue

        race_key = obj.get(
            "race_key"
        )

        if not race_key:

            continue

        race_key = str(
            race_key
        ).strip()

        if not race_key.startswith(
            TARGET_DATE + "_"
        ):

            continue

        race_keys.add(
            race_key
        )

    return race_keys


# ============================================================
# STATUS COUNT
# ============================================================


def collect_statuses(data):

    counter = Counter()

    for obj in walk(
        data
    ):

        if not isinstance(
            obj,
            dict,
        ):

            continue

        status = obj.get(
            "status"
        )

        if status not in (
            None,
            "",
        ):

            counter[
                str(status)
            ] += 1

    return dict(
        counter
    )


# ============================================================
# MERGED READY COUNT
# ============================================================


def get_ready_count(data):

    races = data.get(
        "races"
    )

    if isinstance(
        races,
        list,
    ):

        return len(
            races
        )

    return 0


# ============================================================
# SOURCE CHECK
# ============================================================


def check_source(
    name,
    path,
):

    if not path.exists():

        return {
            "name": name,
            "path": str(path),
            "exists": False,
            "size_bytes": None,
        }

    return {
        "name": name,
        "path": str(path),
        "exists": True,
        "size_bytes": path.stat().st_size,
    }


# ============================================================
# COPY
# ============================================================


def copy_json(
    source,
    destination,
):

    data = load_json(
        source
    )

    save_json(
        destination,
        data,
    )

    return data


# ============================================================
# MAIN
# ============================================================


def main():

    print()

    print(
        "TARGET DATE:",
        TARGET_DATE
    )

    print()

    print(
        "DATE DIRECTORY:"
    )

    print(
        DATE_DIR
    )

    print()


    # ========================================================
    # SOURCE CHECK
    # ========================================================


    source_checks = [
        check_source(
            "pre_race",
            PRE_RACE_SOURCE,
        ),
        check_source(
            "line_prediction",
            LINE_SOURCE,
        ),
        check_source(
            "confirmed_result",
            RESULT_SOURCE,
        ),
        check_source(
            "merged_training",
            MERGED_SOURCE,
        ),
    ]


    missing_sources = [
        item
        for item in source_checks
        if not item[
            "exists"
        ]
    ]


    if missing_sources:

        print(
            "SOURCE FILE ERROR"
        )

        print()

        for item in missing_sources:

            print(
                "NOT FOUND:"
            )

            print(
                item["path"]
            )

            print()

        print(
            "=== 059 中止 ==="
        )

        return


    # ========================================================
    # COPY DATA
    # ========================================================


    print(
        "既存成功データを日付フォルダへ整理します"
    )

    print()


    pre_race_data = copy_json(
        PRE_RACE_SOURCE,
        PRE_RACE_OUT,
    )


    line_data = copy_json(
        LINE_SOURCE,
        LINE_OUT,
    )


    result_data = copy_json(
        RESULT_SOURCE,
        RESULT_OUT,
    )


    merged_data = copy_json(
        MERGED_SOURCE,
        MERGED_OUT,
    )


    # ========================================================
    # RACE KEY
    # ========================================================


    pre_race_keys = collect_race_keys(
        pre_race_data
    )


    line_keys = collect_race_keys(
        line_data
    )


    result_keys = collect_race_keys(
        result_data
    )


    merged_keys = collect_race_keys(
        merged_data
    )


    all_keys = (
        pre_race_keys
        | line_keys
        | result_keys
        | merged_keys
    )


    # ========================================================
    # INTERSECTION
    # ========================================================


    ability_line_keys = (
        pre_race_keys
        & line_keys
    )


    line_result_keys = (
        line_keys
        & result_keys
    )


    all_three_keys = (
        pre_race_keys
        & line_keys
        & result_keys
    )


    # ========================================================
    # MISSING
    # ========================================================


    missing_pre_race = sorted(
        all_keys
        - pre_race_keys
    )


    missing_line = sorted(
        all_keys
        - line_keys
    )


    missing_result = sorted(
        all_keys
        - result_keys
    )


    # ========================================================
    # STATUS
    # ========================================================


    result_status_summary = (
        collect_statuses(
            result_data
        )
    )


    ready_count = get_ready_count(
        merged_data
    )


    # ========================================================
    # DAILY STATUS
    # ========================================================


    if (
        len(pre_race_keys) > 0
        and len(line_keys) > 0
        and len(result_keys) > 0
        and ready_count > 0
    ):

        daily_status = (
            "TRAINING_DATA_AVAILABLE"
        )

    elif (
        len(pre_race_keys) > 0
        and len(line_keys) > 0
    ):

        daily_status = (
            "WAITING_FOR_RESULTS"
        )

    else:

        daily_status = (
            "DATA_INCOMPLETE"
        )


    # ========================================================
    # MANIFEST
    # ========================================================


    manifest = {
        "program": "059_test.py",
        "created_at": datetime.now().isoformat(),
        "target_date": TARGET_DATE,
        "daily_status": daily_status,

        "directory": str(
            DATE_DIR
        ),

        "files": {
            "pre_race": {
                "filename": PRE_RACE_OUT.name,
                "path": str(
                    PRE_RACE_OUT
                ),
                "source": str(
                    PRE_RACE_SOURCE
                ),
                "race_key_count": len(
                    pre_race_keys
                ),
            },

            "line_prediction": {
                "filename": LINE_OUT.name,
                "path": str(
                    LINE_OUT
                ),
                "source": str(
                    LINE_SOURCE
                ),
                "race_key_count": len(
                    line_keys
                ),
            },

            "confirmed_result": {
                "filename": RESULT_OUT.name,
                "path": str(
                    RESULT_OUT
                ),
                "source": str(
                    RESULT_SOURCE
                ),
                "race_key_count": len(
                    result_keys
                ),
                "status_summary": (
                    result_status_summary
                ),
            },

            "merged_training": {
                "filename": MERGED_OUT.name,
                "path": str(
                    MERGED_OUT
                ),
                "source": str(
                    MERGED_SOURCE
                ),
                "race_key_count": len(
                    merged_keys
                ),
                "ready_for_ai_count": (
                    ready_count
                ),
            },
        },

        "race_key_summary": {
            "all": len(
                all_keys
            ),
            "pre_race": len(
                pre_race_keys
            ),
            "line_prediction": len(
                line_keys
            ),
            "confirmed_result": len(
                result_keys
            ),
            "merged_training": len(
                merged_keys
            ),
            "ability_plus_line": len(
                ability_line_keys
            ),
            "line_plus_result": len(
                line_result_keys
            ),
            "all_three": len(
                all_three_keys
            ),
        },

        "missing_summary": {
            "pre_race": len(
                missing_pre_race
            ),
            "line_prediction": len(
                missing_line
            ),
            "confirmed_result": len(
                missing_result
            ),
        },

        "missing_race_keys": {
            "pre_race": missing_pre_race,
            "line_prediction": missing_line,
            "confirmed_result": missing_result,
        },
    }


    save_json(
        MANIFEST_OUT,
        manifest,
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
        "059 最終結果"
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
        "DAILY STATUS:",
        daily_status
    )

    print()

    print(
        "PRE RACE:",
        len(pre_race_keys)
    )

    print(
        "LINE PREDICTION:",
        len(line_keys)
    )

    print(
        "CONFIRMED RESULT:",
        len(result_keys)
    )

    print(
        "MERGED TRAINING:",
        len(merged_keys)
    )

    print(
        "READY FOR AI:",
        ready_count
    )

    print()

    print(
        "ABILITY + LINE:",
        len(ability_line_keys)
    )

    print(
        "LINE + RESULT:",
        len(line_result_keys)
    )

    print(
        "ALL THREE:",
        len(all_three_keys)
    )

    print()

    print(
        "★ RESULT STATUS ★"
    )


    if not result_status_summary:

        print(
            "なし"
        )

    else:

        for key, count in (
            result_status_summary.items()
        ):

            print(
                key,
                ":",
                count,
            )


    print()

    print(
        "★ MISSING SUMMARY ★"
    )

    print(
        "PRE RACE:",
        len(missing_pre_race)
    )

    print(
        "LINE PREDICTION:",
        len(missing_line)
    )

    print(
        "CONFIRMED RESULT:",
        len(missing_result)
    )


    print()

    print(
        "★ 作成ファイル ★"
    )

    print(
        PRE_RACE_OUT
    )

    print(
        LINE_OUT
    )

    print(
        RESULT_OUT
    )

    print(
        MERGED_OUT
    )

    print(
        MANIFEST_OUT
    )


    print()

    print(
        "=== 059 完了 ==="
    )


if __name__ == "__main__":

    main()