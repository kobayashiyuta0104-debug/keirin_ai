import json
from collections import defaultdict, Counter


def load_json(file_name):

    with open(
        file_name,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def find_category_items(obj, target_categories):

    found = []

    def walk(data):

        if isinstance(data, dict):

            category = (
                data.get("category")
                or data.get("CATEGORY")
                or data.get("Category")
            )

            if category in target_categories:

                path = (
                    data.get("path")
                    or data.get("PATH")
                    or data.get("Path")
                    or ""
                )

                key = (
                    data.get("key")
                    or data.get("KEY")
                    or data.get("Key")
                    or ""
                )

                value = None

                for value_key in [
                    "value",
                    "VALUE",
                    "Value"
                ]:

                    if value_key in data:

                        value = data[value_key]
                        break

                source = (
                    data.get("source")
                    or data.get("SOURCE")
                    or data.get("file")
                    or data.get("FILE")
                    or data.get("json_file")
                    or ""
                )

                found.append(
                    {
                        "category": category,
                        "path": str(path),
                        "key": str(key),
                        "value": value,
                        "source": str(source)
                    }
                )

            for value in data.values():

                walk(value)

        elif isinstance(data, list):

            for value in data:

                walk(value)

    walk(obj)

    return found


def value_to_text(value):

    if isinstance(value, (dict, list)):

        try:

            return json.dumps(
                value,
                ensure_ascii=False,
                sort_keys=True
            )

        except:

            return repr(value)

    return str(value)


def main():

    print(
        "=== 130 重要5分類 結合キー本命特定テスト ==="
    )

    input_file = (
        "128_join_key_detail.json"
    )

    output_file = (
        "130_join_key_final_candidates.json"
    )

    target_categories = [
        "DATE_VALUE",
        "VENUE_VALUE",
        "RACE_NO_KEY",
        "RACE_NO_VALUE",
        "RACE_URL_PRM"
    ]

    print()
    print("=" * 70)
    print("🔥 128詳細JSON読込")
    print("=" * 70)

    try:

        data = load_json(
            input_file
        )

    except Exception as e:

        print()
        print(
            "❌ JSON読込失敗:",
            e
        )

        return

    items = find_category_items(
        data,
        target_categories
    )

    print()
    print(
        "🔥 重要候補ITEM数:",
        len(items)
    )

    grouped = defaultdict(
        lambda: defaultdict(
            lambda: {
                "count": 0,
                "paths": Counter(),
                "values": Counter(),
                "sources": Counter()
            }
        )
    )

    for item in items:

        category = item["category"]
        key = item["key"]

        value_text = value_to_text(
            item["value"]
        )

        info = grouped[
            category
        ][
            key
        ]

        info["count"] += 1

        info["paths"][
            item["path"]
        ] += 1

        info["values"][
            value_text
        ] += 1

        if item["source"]:

            info["sources"][
                item["source"]
            ] += 1

    output = {}

    for category in target_categories:

        print()
        print()
        print("=" * 70)
        print(
            f"🔥🔥🔥 CATEGORY: {category}"
        )
        print("=" * 70)

        key_data = grouped.get(
            category,
            {}
        )

        if not key_data:

            print()
            print(
                "❌ 候補なし"
            )

            output[category] = []

            continue

        sorted_keys = sorted(
            key_data.items(),
            key=lambda x: (
                -len(x[1]["sources"]),
                -x[1]["count"],
                x[0]
            )
        )

        output[category] = []

        for rank, (
            key,
            info
        ) in enumerate(
            sorted_keys,
            start=1
        ):

            print()
            print("-" * 70)

            print(
                f"🔥 候補 #{rank}"
            )

            print(
                "KEY:",
                repr(key)
            )

            print(
                "総出現数:",
                info["count"]
            )

            print(
                "JSON種類数:",
                len(
                    info["sources"]
                )
            )

            print(
                "PATH種類数:",
                len(
                    info["paths"]
                )
            )

            print(
                "VALUE種類数:",
                len(
                    info["values"]
                )
            )

            print()
            print("🔥 PATH TOP10")

            for path, count in (
                info["paths"]
                .most_common(10)
            ):

                print(
                    f"  {count}件 | "
                    f"{path}"
                )

            print()
            print("🔥 VALUE TOP20")

            for value, count in (
                info["values"]
                .most_common(20)
            ):

                print(
                    f"  {count}件 | "
                    f"{repr(value)}"
                )

            if info["sources"]:

                print()
                print("🔥 SOURCE TOP10")

                for source, count in (
                    info["sources"]
                    .most_common(10)
                ):

                    print(
                        f"  {count}件 | "
                        f"{source}"
                    )

            output[
                category
            ].append(
                {
                    "rank": rank,
                    "key": key,
                    "total_count": info["count"],
                    "json_count": len(
                        info["sources"]
                    ),
                    "path_count": len(
                        info["paths"]
                    ),
                    "value_count": len(
                        info["values"]
                    ),
                    "paths": [
                        {
                            "path": path,
                            "count": count
                        }
                        for path, count
                        in info[
                            "paths"
                        ].most_common()
                    ],
                    "values": [
                        {
                            "value": value,
                            "count": count
                        }
                        for value, count
                        in info[
                            "values"
                        ].most_common()
                    ],
                    "sources": [
                        {
                            "source": source,
                            "count": count
                        }
                        for source, count
                        in info[
                            "sources"
                        ].most_common()
                    ]
                }
            )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            output,
            f,
            ensure_ascii=False,
            indent=2
        )

    print()
    print()
    print("=" * 70)
    print("🔥 130テスト終了")
    print("=" * 70)

    print(
        "重要候補ITEM数:",
        len(items)
    )

    print()

    for category in target_categories:

        print(
            category,
            "KEY候補数:",
            len(
                output.get(
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