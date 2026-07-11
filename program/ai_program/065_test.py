import json
from pathlib import Path
from collections import Counter


print("=== 065 JSJ005 ichi復元ライン本数 × lineKeitai 全件監査テスト ===")


# ============================================================
# 基本設定
# ============================================================

BASE = Path(r"C:\競輪AI")

SRC_FILE = (
    BASE
    / "data_official"
    / "line_research"
    / "064_jsj005_direct_live"
    / "064_jsj005_direct_live.json"
)

OUT_DIR = (
    BASE
    / "data_official"
    / "line_research"
    / "065_jsj005_line_count_audit"
)

OUT_FILE = (
    OUT_DIR
    / "065_jsj005_line_count_audit.json"
)

OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
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
# lineKeitai期待ライン本数
# ============================================================

def get_expected_line_count(
    line_keitai,
):

    mapping = {
        "二分戦": 2,
        "三分戦": 3,
        "四分戦": 4,
        "五分戦": 5,
        "六分戦": 6,
        "ライン無し": 0,
    }

    return mapping.get(
        line_keitai
    )


# ============================================================
# main_lines正規化
# ============================================================

def normalize_groups(
    main_lines,
):

    groups = []

    if not isinstance(
        main_lines,
        list,
    ):

        return groups

    for group in main_lines:

        if not isinstance(
            group,
            list,
        ):

            continue

        nums = []

        for value in group:

            try:

                num = int(
                    value
                )

            except Exception:

                continue

            if 1 <= num <= 9:

                nums.append(
                    num
                )

        if nums:

            groups.append(
                nums
            )

    return groups


# ============================================================
# メイン
# ============================================================

def main():

    print()
    print("[1] 064保存JSON読込")

    if not SRC_FILE.exists():

        print(
            "ERROR: 064保存JSONがありません"
        )

        print(
            SRC_FILE
        )

        return

    root = load_json(
        SRC_FILE
    )

    results_064 = root.get(
        "results"
    )

    if not isinstance(
        results_064,
        list,
    ):

        print(
            "ERROR: 064 resultsがありません"
        )

        return

    found_rows = [
        item
        for item in results_064
        if isinstance(item, dict)
        and item.get("status")
        == "JSJ005_DIRECT_FOUND"
    ]

    print(
        "064 TOTAL RESULTS:",
        len(results_064),
    )

    print(
        "JSJ005 DIRECT FOUND:",
        len(found_rows),
    )

    print()
    print(
        "[2] 2車以上ライン本数 × "
        "lineKeitai監査開始"
    )

    audit_results = []

    status_counter = Counter()

    type_counter = Counter()

    for index, item in enumerate(
        found_rows,
        1,
    ):

        race_key = item.get(
            "race_key"
        )

        line_keitai = item.get(
            "lineKeitai"
        )

        main_lines = normalize_groups(
            item.get("main_lines")
        )

        actual_lines = [
            group
            for group in main_lines
            if len(group) >= 2
        ]

        solo_riders = [
            group[0]
            for group in main_lines
            if len(group) == 1
        ]

        expected_line_count = (
            get_expected_line_count(
                line_keitai
            )
        )

        actual_line_count = len(
            actual_lines
        )

        type_counter[
            str(line_keitai)
        ] += 1

        if expected_line_count is None:

            status = "UNKNOWN_LINE_KEITAI"

        elif (
            actual_line_count
            == expected_line_count
        ):

            status = "MATCH"

        else:

            status = "MISMATCH"

        status_counter[
            status
        ] += 1

        print()
        print("-" * 100)

        print(
            f"[{index}/{len(found_rows)}] "
            f"{race_key}"
        )

        print(
            "TYPE:",
            line_keitai,
        )

        print(
            "GROUPS:",
            main_lines,
        )

        print(
            "LINES:",
            actual_lines,
        )

        print(
            "SOLO:",
            solo_riders,
        )

        print(
            "EXPECTED LINE COUNT:",
            expected_line_count,
        )

        print(
            "ACTUAL LINE COUNT:",
            actual_line_count,
        )

        print(
            "STATUS:",
            status,
        )

        audit_results.append({
            "race_key": race_key,
            "lineKeitai": line_keitai,
            "groups": main_lines,
            "lines": actual_lines,
            "solo_riders": solo_riders,
            "expected_line_count": (
                expected_line_count
            ),
            "actual_line_count": (
                actual_line_count
            ),
            "status": status,
            "ichi": item.get("ichi"),
            "teikyo": item.get("teikyo"),
            "encp": item.get("encp"),
        })

    mismatch_rows = [
        item
        for item in audit_results
        if item["status"]
        == "MISMATCH"
    ]

    unknown_rows = [
        item
        for item in audit_results
        if item["status"]
        == "UNKNOWN_LINE_KEITAI"
    ]

    output = {
        "program": "065_test.py",
        "purpose": (
            "064でJSJ005直接取得に成功した"
            "全レースについて、"
            "ichi連続位置から復元したグループのうち"
            "2車以上を正式ラインとして数え、"
            "lineKeitaiの二分戦・三分戦・四分戦等と"
            "ライン本数が一致するか全件監査する。"
        ),
        "source_file": str(
            SRC_FILE
        ),
        "source_total_count": len(
            results_064
        ),
        "direct_found_count": len(
            found_rows
        ),
        "status_summary": dict(
            status_counter
        ),
        "line_keitai_summary": dict(
            type_counter
        ),
        "mismatch_count": len(
            mismatch_rows
        ),
        "unknown_count": len(
            unknown_rows
        ),
        "audit_results": audit_results,
    }

    save_json(
        OUT_FILE,
        output,
    )

    print()
    print("=" * 100)
    print("065 最終結果")
    print("=" * 100)

    print()
    print(
        "AUDIT TARGET:",
        len(found_rows),
    )

    print()
    print("★ STATUS SUMMARY ★")

    for key, value in (
        status_counter.most_common()
    ):

        print(
            key,
            ":",
            value,
        )

    print()
    print("★ LINE KEITAI SUMMARY ★")

    for key, value in (
        type_counter.most_common()
    ):

        print(
            key,
            ":",
            value,
        )

    print()
    print(
        "MATCH:",
        status_counter["MATCH"],
    )

    print(
        "MISMATCH:",
        len(mismatch_rows),
    )

    print(
        "UNKNOWN:",
        len(unknown_rows),
    )

    print()
    print("★ MISMATCH一覧 ★")

    if not mismatch_rows:

        print("なし")

    else:

        for item in mismatch_rows:

            print()
            print(
                item["race_key"]
            )

            print(
                "TYPE:",
                item["lineKeitai"],
            )

            print(
                "GROUPS:",
                item["groups"],
            )

            print(
                "LINES:",
                item["lines"],
            )

            print(
                "SOLO:",
                item["solo_riders"],
            )

            print(
                "EXPECTED:",
                item[
                    "expected_line_count"
                ],
            )

            print(
                "ACTUAL:",
                item[
                    "actual_line_count"
                ],
            )

    print()
    print("★ UNKNOWN LINE KEITAI一覧 ★")

    if not unknown_rows:

        print("なし")

    else:

        for item in unknown_rows:

            print()
            print(
                item["race_key"]
            )

            print(
                "TYPE:",
                item["lineKeitai"],
            )

            print(
                "GROUPS:",
                item["groups"],
            )

    print()
    print("保存先:")

    print(
        OUT_FILE
    )

    print()
    print("=== 065 完了 ===")


if __name__ == "__main__":

    main()