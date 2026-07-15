import json
from collections import defaultdict, Counter


def load_json(file_name):

    with open(
        file_name,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def normalize_item(item):

    if not isinstance(item, dict):
        return None

    path = (
        item.get("path")
        or item.get("PATH")
        or item.get("Path")
        or ""
    )

    key = (
        item.get("key")
        or item.get("KEY")
        or item.get("Key")
        or ""
    )

    value = None

    for value_key in [
        "value",
        "VALUE",
        "Value"
    ]:

        if value_key in item:

            value = item[value_key]
            break

    category = (
        item.get("category")
        or item.get("CATEGORY")
        or item.get("Category")
        or ""
    )

    source = (
        item.get("source")
        or item.get("SOURCE")
        or item.get("file")
        or item.get("FILE")
        or item.get("json_file")
        or ""
    )

    return {
        "path": str(path),
        "key": str(key),
        "value": value,
        "category": str(category),
        "source": str(source)
    }


def collect_items(data):

    items = []

    def walk(obj):

        if isinstance(obj, dict):

            normalized = normalize_item(obj)

            if (
                normalized
                and normalized["path"]
                and normalized["key"]
            ):

                items.append(normalized)

            for value in obj.values():

                walk(value)

        elif isinstance(obj, list):

            for value in obj:

                walk(value)

    walk(data)

    return items


def detect_category(item):

    category = (
        item["category"]
        .upper()
        .strip()
    )

    if category:
        return category

    text = (
        item["path"]
        + " "
        + item["key"]
    ).lower()

    if (
        "date" in text
        or "day" in text
        or "update" in text
    ):

        return "DATE"

    if (
        "venue" in text
        or "keirinjo" in text
        or "jyo" in text
        or "jo" in text
    ):

        return "VENUE"

    if (
        "raceurl" in text
        or "race_url" in text
        or "urlprm" in text
    ):

        return "RACE_URL_PRM"

    if (
        "race" in text
        or "rceno" in text
        or "raceno" in text
    ):

        return "RACE_NO"

    return "OTHER"


def value_to_text(value):

    if isinstance(
        value,
        (dict, list)
    ):

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
        "=== 129 結合キー候補 PATH・KEY・VALUE集約テスト ==="
    )

    input_file = (
        "128_join_key_detail.json"
    )

    output_file = (
        "129_join_key_summary.json"
    )

    print()
    print("=" * 70)
    print("🔥 JSON読込")
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

    items = collect_items(
        data
    )

    print()
    print(
        "🔥 候補ITEM数:",
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

        category = detect_category(
            item
        )

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

    summary = {}

    category_order = [
        "DATE",
        "DATE_KEY",
        "DATE_VALUE",
        "VENUE",
        "VENUE_KEY",
        "VENUE_VALUE",
        "RACE_NO",
        "RACE_NO_KEY",
        "RACE_NO_VALUE",
        "RACE_URL_PRM",
        "OTHER"
    ]

    all_categories = list(
        grouped.keys()
    )

    ordered_categories = []

    for category in category_order:

        if category in all_categories:

            ordered_categories.append(
                category
            )

    for category in all_categories:

        if (
            category
            not in ordered_categories
        ):

            ordered_categories.append(
                category
            )

    for category in ordered_categories:

        print()
        print("=" * 70)
        print(
            f"🔥 CATEGORY: {category}"
        )
        print("=" * 70)

        key_data = grouped[
            category
        ]

        sorted_keys = sorted(
            key_data.items(),
            key=lambda x: (
                -x[1]["count"],
                x[0]
            )
        )

        summary[
            category
        ] = []

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
                key
            )

            print(
                "件数:",
                info["count"]
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
                    f"  {count}件 | {path}"
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

            summary[
                category
            ].append(
                {
                    "rank": rank,
                    "key": key,
                    "count": info["count"],
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
            summary,
            f,
            ensure_ascii=False,
            indent=2
        )

    print()
    print("=" * 70)
    print("🔥 129テスト終了")
    print("=" * 70)

    print(
        "候補ITEM数:",
        len(items)
    )

    print(
        "CATEGORY数:",
        len(summary)
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