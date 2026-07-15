import json
from collections import defaultdict, Counter


def main():

    print("=== 132 categories直接解析テスト ===")

    input_file = "128_join_key_detail.json"
    output_file = "132_category_candidates.json"

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
    print("🔥 132 categories解析開始")
    print("=" * 70)

    category_items = defaultdict(list)

    total_files = 0
    total_items = 0

    for file_name, items in data.items():

        total_files += 1

        if not isinstance(items, list):
            continue

        for item in items:

            total_items += 1

            if not isinstance(item, dict):
                continue

            categories = item.get(
                "categories",
                []
            )

            if not isinstance(categories, list):
                continue

            for category in categories:

                if category not in target_categories:
                    continue

                category_items[category].append({
                    "file": file_name,
                    "path": item.get("path"),
                    "key": item.get("key"),
                    "value": item.get("value"),
                })

    result = {}

    for category in target_categories:

        print()
        print("=" * 70)
        print(
            "🔥 CATEGORY:",
            category
        )
        print("=" * 70)

        items = category_items.get(
            category,
            []
        )

        print(
            "候補ITEM数:",
            len(items)
        )

        key_counter = Counter(
            item["key"]
            for item in items
        )

        path_counter = Counter(
            item["path"]
            for item in items
        )

        value_counter = Counter(
            str(item["value"])
            for item in items
        )

        print()
        print("🔥 KEY TOP20")

        for key, count in key_counter.most_common(20):

            print(
                f"{count}件 | {repr(key)}"
            )

        print()
        print("🔥 PATH TOP20")

        for path, count in path_counter.most_common(20):

            print(
                f"{count}件 | {path}"
            )

        print()
        print("🔥 VALUE TOP20")

        for value, count in value_counter.most_common(20):

            print(
                f"{count}件 | {repr(value)}"
            )

        result[category] = {
            "item_count": len(items),
            "key_top": key_counter.most_common(),
            "path_top": path_counter.most_common(),
            "value_top": value_counter.most_common(),
            "items": items,
        }

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=2
        )

    print()
    print("=" * 70)
    print("🔥 132テスト終了")
    print("=" * 70)

    print(
        "調査ファイル数:",
        total_files
    )

    print(
        "総ITEM数:",
        total_items
    )

    print()

    for category in target_categories:

        print(
            f"{category}:",
            len(
                category_items.get(
                    category,
                    []
                )
            )
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