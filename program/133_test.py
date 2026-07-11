import json
from collections import defaultdict, Counter


def safe_text(value):
    if value is None:
        return ""

    if isinstance(value, (dict, list)):
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True
        )

    return str(value)


def main():

    print("=== 133 結合KEY候補絞り込みテスト ===")

    input_file = "132_category_candidates.json"
    output_file = "133_join_key_rankings.json"

    target_categories = [
        "DATE_VALUE",
        "VENUE_VALUE",
        "RACE_NO_KEY",
        "RACE_NO_VALUE",
        "RACE_URL_PRM",
    ]

    try:
        with open(
            input_file,
            "r",
            encoding="utf-8"
        ) as f:
            data = json.load(f)

    except Exception as e:
        print("❌ JSON読込失敗:", e)
        return

    print()
    print("=" * 70)
    print("🔥 133 候補絞り込み開始")
    print("=" * 70)

    final_result = {}

    for category in target_categories:

        print()
        print()
        print("=" * 70)
        print("🔥🔥🔥 CATEGORY:", category)
        print("=" * 70)

        category_data = data.get(
            category,
            {}
        )

        items = category_data.get(
            "items",
            []
        )

        if not isinstance(items, list):
            items = []

        print("候補ITEM数:", len(items))

        groups = defaultdict(list)

        for item in items:

            if not isinstance(item, dict):
                continue

            file_name = safe_text(
                item.get("file")
            )

            path = safe_text(
                item.get("path")
            )

            key = safe_text(
                item.get("key")
            )

            value = item.get("value")

            group_key = (
                key,
                path
            )

            groups[group_key].append({
                "file": file_name,
                "path": path,
                "key": key,
                "value": value,
            })

        rankings = []

        for (
            key,
            path
        ), group_items in groups.items():

            file_counter = Counter(
                item["file"]
                for item in group_items
            )

            value_counter = Counter(
                safe_text(item["value"])
                for item in group_items
            )

            item_count = len(group_items)

            file_count = len(file_counter)

            value_count = len(value_counter)

            score = (
                file_count * 10000
                + item_count * 100
                + value_count
            )

            rankings.append({
                "score": score,
                "key": key,
                "path": path,
                "item_count": item_count,
                "file_count": file_count,
                "value_count": value_count,
                "files": [
                    {
                        "file": file_name,
                        "count": count,
                    }
                    for file_name, count
                    in file_counter.most_common()
                ],
                "values": [
                    {
                        "value": value,
                        "count": count,
                    }
                    for value, count
                    in value_counter.most_common(30)
                ],
                "items": group_items,
            })

        rankings.sort(
            key=lambda x: (
                x["score"],
                x["file_count"],
                x["item_count"],
                x["value_count"],
            ),
            reverse=True
        )

        print()
        print("🔥 TOP候補")

        for index, ranking in enumerate(
            rankings[:15],
            start=1
        ):

            print()
            print("-" * 70)

            print(
                f"🔥 候補 #{index}"
            )

            print(
                "SCORE:",
                ranking["score"]
            )

            print(
                "KEY:",
                repr(ranking["key"])
            )

            print(
                "PATH:",
                ranking["path"]
            )

            print(
                "ITEM数:",
                ranking["item_count"]
            )

            print(
                "FILE数:",
                ranking["file_count"]
            )

            print(
                "VALUE種類数:",
                ranking["value_count"]
            )

            print()
            print("🔥 FILE TOP10")

            for file_info in ranking["files"][:10]:

                print(
                    f"{file_info['count']}件 | "
                    f"{file_info['file']}"
                )

            print()
            print("🔥 VALUE TOP15")

            for value_info in ranking["values"][:15]:

                print(
                    f"{value_info['count']}件 | "
                    f"{repr(value_info['value'])}"
                )

        final_result[category] = {
            "candidate_count": len(rankings),
            "rankings": rankings,
        }

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            final_result,
            f,
            ensure_ascii=False,
            indent=2
        )

    print()
    print()
    print("=" * 70)
    print("🔥 133テスト終了")
    print("=" * 70)

    for category in target_categories:

        category_result = final_result.get(
            category,
            {}
        )

        rankings = category_result.get(
            "rankings",
            []
        )

        print()
        print("🔥", category)

        print(
            "候補GROUP数:",
            len(rankings)
        )

        if rankings:

            top = rankings[0]

            print(
                "TOP KEY:",
                repr(top["key"])
            )

            print(
                "TOP PATH:",
                top["path"]
            )

            print(
                "TOP FILE数:",
                top["file_count"]
            )

            print(
                "TOP ITEM数:",
                top["item_count"]
            )

            print(
                "TOP VALUE種類数:",
                top["value_count"]
            )

    print()
    print(
        "保存先:",
        output_file
    )

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()