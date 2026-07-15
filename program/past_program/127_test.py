import json
import glob
import os


# --------------------------------------------------
# 調査したいキーワード
# --------------------------------------------------

DATE_WORDS = [
    "date",
    "ymd",
    "day",
    "kaisaiDate",
    "raceDate",
    "targetDate"
]

VENUE_WORDS = [
    "venue",
    "jo",
    "jyo",
    "keirinjo",
    "keirinJo",
    "place",
    "jocode",
    "joCode",
    "keirinjoCode"
]

RACE_WORDS = [
    "race",
    "raceNo",
    "race_no",
    "raceNum",
    "raceNumber",
    "rno"
]


def is_candidate_key(key):

    key_lower = str(key).lower()

    words = (
        DATE_WORDS
        + VENUE_WORDS
        + RACE_WORDS
    )

    for word in words:

        if word.lower() in key_lower:
            return True

    return False


def search_keys(
    data,
    path="ROOT",
    results=None,
    depth=0
):

    if results is None:
        results = []

    # 深すぎる場所は止める
    if depth > 15:
        return results

    if isinstance(data, dict):

        for key, value in data.items():

            current_path = (
                f"{path}.{key}"
            )

            if is_candidate_key(key):

                # 巨大DATAは短縮表示
                value_text = repr(value)

                if len(value_text) > 300:

                    value_text = (
                        value_text[:300]
                        + "..."
                    )

                results.append(
                    {
                        "path": current_path,
                        "key": key,
                        "value": value_text,
                        "type": type(
                            value
                        ).__name__
                    }
                )

            search_keys(
                value,
                current_path,
                results,
                depth + 1
            )

    elif isinstance(data, list):

        # 全件見ると同じ構造が大量に出るため
        # 最初の3件だけ調査
        for index, value in enumerate(
            data[:3]
        ):

            current_path = (
                f"{path}[{index}]"
            )

            search_keys(
                value,
                current_path,
                results,
                depth + 1
            )

    return results


def main():

    print(
        "=== 127 レース前JSON "
        "結合キー候補 自動調査 ==="
    )

    # --------------------------------------------------
    # JSONファイル検索
    # --------------------------------------------------

    json_files = []

    json_files.extend(
        glob.glob("*.json")
    )

    json_files.extend(
        glob.glob(
            "result/*.json"
        )
    )

    json_files = sorted(
        set(json_files)
    )

    # 今回作った結果系は除外
    exclude_words = [
        "122_all_venues_jsj012",
        "123_jsj012_structure",
        "125_extracted_results"
    ]

    target_files = []

    for file_path in json_files:

        file_name = os.path.basename(
            file_path
        )

        excluded = False

        for word in exclude_words:

            if word in file_name:

                excluded = True
                break

        if excluded:
            continue

        target_files.append(
            file_path
        )

    print()
    print(
        "🔥 調査対象JSON数:",
        len(target_files)
    )

    print()

    for file_path in target_files:

        print(
            "-",
            file_path
        )

    # --------------------------------------------------
    # 全JSON調査
    # --------------------------------------------------

    all_findings = {}

    files_with_candidates = 0
    total_candidates = 0

    for file_path in target_files:

        print()
        print("=" * 80)
        print(
            "🔥 調査:",
            file_path
        )
        print("=" * 80)

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

        except Exception as e:

            print(
                "❌ 読み込み失敗:",
                e
            )

            continue

        findings = search_keys(data)

        # 同じPATHを除去
        unique_findings = []

        seen_paths = set()

        for item in findings:

            path = item["path"]

            if path in seen_paths:
                continue

            seen_paths.add(path)

            unique_findings.append(item)

        all_findings[
            file_path
        ] = unique_findings

        print(
            "候補KEY数:",
            len(unique_findings)
        )

        if len(unique_findings) > 0:

            files_with_candidates += 1

        total_candidates += len(
            unique_findings
        )

        # 最大50件表示
        for item in unique_findings[:50]:

            print()
            print(
                "🔥 PATH:",
                item["path"]
            )

            print(
                "KEY:",
                item["key"]
            )

            print(
                "TYPE:",
                item["type"]
            )

            print(
                "VALUE:",
                item["value"]
            )

        if len(unique_findings) > 50:

            print()
            print(
                "⚠️ 残り",
                len(unique_findings) - 50,
                "件は画面表示省略"
            )

    # --------------------------------------------------
    # 調査結果保存
    # --------------------------------------------------

    save_file = (
        "127_join_key_candidates.json"
    )

    with open(
        save_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            all_findings,
            f,
            ensure_ascii=False,
            indent=2
        )

    # --------------------------------------------------
    # 最終結果
    # --------------------------------------------------

    print()
    print("=" * 80)
    print("🔥 127テスト終了")
    print("=" * 80)

    print(
        "調査JSON数:",
        len(target_files)
    )

    print(
        "候補ありJSON数:",
        files_with_candidates
    )

    print(
        "候補KEY総数:",
        total_candidates
    )

    print()
    print(
        "保存先:",
        save_file
    )

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()