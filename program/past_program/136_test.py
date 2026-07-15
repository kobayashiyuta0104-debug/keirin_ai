import json
from pathlib import Path
from collections import defaultdict


BASE_DIR = Path(__file__).resolve().parent.parent

FILE_A = BASE_DIR / "054_all_results.json"
FILE_B = BASE_DIR / "055_all_races.json"


VENUE_NAMES = [
    "函館", "青森", "いわき平", "弥彦", "前橋", "取手",
    "宇都宮", "大宮", "西武園", "京王閣", "立川", "松戸",
    "千葉", "川崎", "平塚", "小田原", "伊東", "静岡",
    "名古屋", "岐阜", "大垣", "豊橋", "富山", "松阪",
    "四日市", "福井", "奈良", "向日町", "和歌山", "岸和田",
    "玉野", "広島", "防府", "高松", "小松島", "高知",
    "松山", "小倉", "久留米", "武雄", "佐世保", "別府",
    "熊本"
]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def walk_json(obj, path="ROOT"):
    items = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = f"{path}.{key}"

            if not isinstance(value, (dict, list)):
                items.append({
                    "path": current_path,
                    "key": str(key),
                    "value": value,
                })

            items.extend(
                walk_json(value, current_path)
            )

    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            current_path = f"{path}[{index}]"

            items.extend(
                walk_json(value, current_path)
            )

    return items


def normalize(value):
    if value is None:
        return ""

    return str(value).strip()


def find_venue_name_items(items):
    results = []

    for item in items:
        value = normalize(item["value"])

        for venue in VENUE_NAMES:
            if venue in value:
                result = dict(item)
                result["venue"] = venue
                results.append(result)
                break

    return results


def build_key_map(items):
    result = defaultdict(list)

    for item in items:
        key = item["key"]
        value = normalize(item["value"])

        result[key].append({
            "path": item["path"],
            "value": value,
        })

    return result


def find_common_keys(items_a, items_b):
    map_a = build_key_map(items_a)
    map_b = build_key_map(items_b)

    common_keys = sorted(
        set(map_a.keys()) & set(map_b.keys())
    )

    results = []

    for key in common_keys:
        values_a = {
            x["value"]
            for x in map_a[key]
            if x["value"]
        }

        values_b = {
            x["value"]
            for x in map_b[key]
            if x["value"]
        }

        common_values = values_a & values_b

        if not common_values:
            continue

        venue_like_values = []

        for value in common_values:
            for venue in VENUE_NAMES:
                if venue in value:
                    venue_like_values.append(value)
                    break

        key_lower = key.lower()

        venue_key_score = 0

        venue_words = [
            "venue",
            "jyo",
            "jo",
            "place",
            "race_name",
            "kaisai",
            "stadium",
        ]

        for word in venue_words:
            if word in key_lower:
                venue_key_score += 100

        if venue_like_values:
            venue_key_score += 500

        if venue_key_score == 0:
            continue

        results.append({
            "key": key,
            "score": venue_key_score,
            "common_values": sorted(common_values)[:50],
            "venue_like_values": sorted(
                set(venue_like_values)
            ),
            "a_examples": map_a[key][:10],
            "b_examples": map_b[key][:10],
        })

    results.sort(
        key=lambda x: (
            x["score"],
            len(x["venue_like_values"]),
            len(x["common_values"]),
        ),
        reverse=True,
    )

    return results


def find_same_value_different_key(items_a, items_b):
    value_map_a = defaultdict(list)
    value_map_b = defaultdict(list)

    for item in items_a:
        value = normalize(item["value"])

        if value:
            value_map_a[value].append(item)

    for item in items_b:
        value = normalize(item["value"])

        if value:
            value_map_b[value].append(item)

    common_values = (
        set(value_map_a.keys())
        & set(value_map_b.keys())
    )

    results = []

    for value in common_values:
        detected_venue = None

        for venue in VENUE_NAMES:
            if venue in value:
                detected_venue = venue
                break

        if detected_venue is None:
            continue

        results.append({
            "value": value,
            "venue": detected_venue,
            "a_items": value_map_a[value][:10],
            "b_items": value_map_b[value][:10],
        })

    results.sort(
        key=lambda x: x["venue"]
    )

    return results


def main():
    print("=" * 70)
    print("🔥 136 競輪場共通識別子探索テスト")
    print("=" * 70)

    print(f"A: {FILE_A.name}")
    print(f"B: {FILE_B.name}")

    data_a = load_json(FILE_A)
    data_b = load_json(FILE_B)

    items_a = walk_json(data_a)
    items_b = walk_json(data_b)

    print()
    print(f"A ITEM数: {len(items_a)}")
    print(f"B ITEM数: {len(items_b)}")

    venue_a = find_venue_name_items(items_a)
    venue_b = find_venue_name_items(items_b)

    print()
    print("=" * 70)
    print("🔥 A 競輪場名VALUE候補")
    print("=" * 70)

    for item in venue_a[:50]:
        print()
        print(f"VENUE: {item['venue']}")
        print(f"KEY: {item['key']}")
        print(f"PATH: {item['path']}")
        print(f"VALUE: {repr(item['value'])}")

    print()
    print("=" * 70)
    print("🔥 B 競輪場名VALUE候補")
    print("=" * 70)

    for item in venue_b[:50]:
        print()
        print(f"VENUE: {item['venue']}")
        print(f"KEY: {item['key']}")
        print(f"PATH: {item['path']}")
        print(f"VALUE: {repr(item['value'])}")

    common_key_results = find_common_keys(
        items_a,
        items_b,
    )

    print()
    print("=" * 70)
    print("🔥 共通KEY＋共通VALUE 競輪場候補")
    print("=" * 70)

    if not common_key_results:
        print("❌ 候補なし")

    for index, result in enumerate(
        common_key_results[:30],
        start=1,
    ):
        print()
        print("-" * 70)
        print(f"🔥 候補 #{index}")
        print(f"SCORE: {result['score']}")
        print(f"KEY: {result['key']}")
        print(
            "VENUE LIKE VALUES:",
            result["venue_like_values"],
        )
        print(
            "COMMON VALUES:",
            result["common_values"],
        )

        print("A EXAMPLES:")

        for example in result["a_examples"][:5]:
            print(
                " ",
                example["path"],
                "=",
                repr(example["value"]),
            )

        print("B EXAMPLES:")

        for example in result["b_examples"][:5]:
            print(
                " ",
                example["path"],
                "=",
                repr(example["value"]),
            )

    different_key_results = (
        find_same_value_different_key(
            items_a,
            items_b,
        )
    )

    print()
    print("=" * 70)
    print("🔥 KEY違い・VALUE同一 競輪場候補")
    print("=" * 70)

    if not different_key_results:
        print("❌ 候補なし")

    for index, result in enumerate(
        different_key_results[:30],
        start=1,
    ):
        print()
        print("-" * 70)
        print(f"🔥 候補 #{index}")
        print(f"VENUE: {result['venue']}")
        print(f"VALUE: {repr(result['value'])}")

        print("A:")

        for item in result["a_items"][:5]:
            print(
                " ",
                item["key"],
                item["path"],
            )

        print("B:")

        for item in result["b_items"][:5]:
            print(
                " ",
                item["key"],
                item["path"],
            )

    output = {
        "file_a": FILE_A.name,
        "file_b": FILE_B.name,
        "a_venue_items": venue_a,
        "b_venue_items": venue_b,
        "common_key_results": common_key_results,
        "same_value_different_key": different_key_results,
    }

    output_path = (
        BASE_DIR
        / "136_venue_identifier_candidates.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            output,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print("=" * 70)
    print("🔥 136テスト終了")
    print("=" * 70)
    print(f"A 競輪場名候補数: {len(venue_a)}")
    print(f"B 競輪場名候補数: {len(venue_b)}")
    print(
        "共通KEY候補数:",
        len(common_key_results),
    )
    print(
        "KEY違いVALUE同一候補数:",
        len(different_key_results),
    )
    print()
    print(f"保存先: {output_path.name}")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()