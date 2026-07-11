import json
from pathlib import Path
from collections import Counter, defaultdict


BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "142_joined_race_data.json"
OUTPUT_FILE = BASE_DIR / "143_joined_data_inventory.json"


def walk_json(obj, path="ROOT", rows=None):
    if rows is None:
        rows = []

    if isinstance(obj, dict):
        for key, value in obj.items():

            current_path = f"{path}.{key}"

            rows.append(
                {
                    "path": current_path,
                    "key": str(key),
                    "type": type(value).__name__,
                    "value": value
                    if isinstance(value, (str, int, float, bool))
                    or value is None
                    else None,
                }
            )

            walk_json(
                value,
                current_path,
                rows,
            )

    elif isinstance(obj, list):
        for index, value in enumerate(obj):

            current_path = f"{path}[{index}]"

            rows.append(
                {
                    "path": current_path,
                    "key": f"[{index}]",
                    "type": type(value).__name__,
                    "value": value
                    if isinstance(value, (str, int, float, bool))
                    or value is None
                    else None,
                }
            )

            walk_json(
                value,
                current_path,
                rows,
            )

    return rows


def short_value(value, limit=100):

    if value is None:
        return "None"

    text = str(value)

    if len(text) > limit:
        return text[:limit] + "..."

    return text


def main():

    print("=" * 70)
    print("🔥 143 結合JSON 完全棚卸しテスト")
    print("=" * 70)

    if not INPUT_FILE.exists():

        print()
        print("❌ 入力JSONが見つからない")
        print(f"検索先: {INPUT_FILE}")
        return

    print()
    print(f"入力JSON: {INPUT_FILE.name}")

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8",
    ) as f:

        data = json.load(f)

    print()
    print(f"ROOT TYPE: {type(data).__name__}")

    if isinstance(data, dict):

        print(f"ROOT KEY数: {len(data)}")

        print()
        print("🔥 ROOT KEYS")

        for key in data.keys():
            print(f"- {repr(key)}")

    elif isinstance(data, list):

        print(f"ROOT件数: {len(data)}")

    rows = walk_json(data)

    print()
    print("=" * 70)
    print("🔥 全ITEM統計")
    print("=" * 70)

    print()
    print(f"総ITEM数: {len(rows)}")

    type_counter = Counter(
        row["type"]
        for row in rows
    )

    print()
    print("🔥 TYPE別件数")

    for type_name, count in type_counter.most_common():

        print(
            f"{type_name}: {count}"
        )

    key_counter = Counter(
        row["key"]
        for row in rows
        if not row["key"].startswith("[")
    )

    print()
    print("=" * 70)
    print("🔥 KEY TOP100")
    print("=" * 70)

    for rank, (key, count) in enumerate(
        key_counter.most_common(100),
        start=1,
    ):

        print(
            f"{rank:03d}位 | "
            f"{count:4d}件 | "
            f"{repr(key)}"
        )

    print()
    print("=" * 70)
    print("🔥 VALUE入り PATH 全表示")
    print("=" * 70)

    value_rows = [
        row
        for row in rows
        if row["value"] is not None
    ]

    print()
    print(f"VALUE入りITEM数: {len(value_rows)}")

    for index, row in enumerate(
        value_rows,
        start=1,
    ):

        print()
        print("-" * 70)

        print(f"🔥 ITEM #{index}")

        print(
            f"PATH : {row['path']}"
        )

        print(
            f"KEY  : {repr(row['key'])}"
        )

        print(
            f"TYPE : {row['type']}"
        )

        print(
            f"VALUE: {short_value(row['value'])}"
        )

    keyword_groups = {
        "選手候補": [
            "player",
            "senshu",
            "name",
            "選手",
        ],
        "車番候補": [
            "car",
            "waku",
            "number",
            "車番",
            "枠",
        ],
        "ライン並び候補": [
            "line",
            "narabi",
            "並び",
        ],
        "オッズ候補": [
            "odds",
            "odd",
            "オッズ",
        ],
        "着順候補": [
            "rank",
            "order",
            "arrival",
            "着",
            "着順",
        ],
        "払戻候補": [
            "pay",
            "refund",
            "payout",
            "払戻",
        ],
        "3連単候補": [
            "sanrentan",
            "trifecta",
            "3連単",
        ],
        "タイム候補": [
            "time",
            "タイム",
        ],
        "決まり手候補": [
            "kimarite",
            "決まり手",
        ],
    }

    inventory = {
        "input_file": INPUT_FILE.name,
        "root_type": type(data).__name__,
        "total_items": len(rows),
        "type_counts": dict(type_counter),
        "key_counts": dict(key_counter),
        "keyword_groups": {},
        "items": rows,
    }

    print()
    print("=" * 70)
    print("🔥 AI学習項目 候補探索")
    print("=" * 70)

    for group_name, keywords in keyword_groups.items():

        matches = []

        for row in rows:

            search_text = (
                row["path"]
                + " "
                + row["key"]
            ).lower()

            if any(
                keyword.lower() in search_text
                for keyword in keywords
            ):

                matches.append(row)

        inventory["keyword_groups"][group_name] = matches

        print()
        print(f"🔥 {group_name}")
        print(f"候補数: {len(matches)}")

        for row in matches[:20]:

            print(
                f"{row['path']} "
                f"= "
                f"{short_value(row['value'])}"
            )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            inventory,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print("=" * 70)
    print("🔥 143テスト終了")
    print("=" * 70)

    print(f"総ITEM数: {len(rows)}")
    print(f"VALUE入りITEM数: {len(value_rows)}")
    print()

    for group_name in keyword_groups.keys():

        count = len(
            inventory["keyword_groups"][group_name]
        )

        print(
            f"{group_name}: {count}"
        )

    print()
    print(
        f"保存先: {OUTPUT_FILE.name}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()