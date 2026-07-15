import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "142_joined_race_data.json"
OUTPUT_FILE = BASE_DIR / "146_pre_race_ai_inventory.json"


TARGETS = {
    "選手": [
        "sensyu",
        "player",
        "nameplayer",
        "regist",
    ],
    "車番": [
        "carnum",
        "syaban",
        "shaban",
    ],
    "競走得点": [
        "tokuten",
        "score",
        "point",
        "kyousoutokuten",
        "kyosotokuten",
    ],
    "脚質": [
        "kyakushitsu",
        "kyakusitu",
        "style",
    ],
    "勝率": [
        "syouritsu",
        "shoritsu",
        "winrate",
        "win_rate",
    ],
    "2連対率": [
        "nirentai",
        "rentai",
        "2rentai",
    ],
    "3連対率": [
        "sanrentai",
        "3rentai",
    ],
    "バック": [
        "back",
        "backnum",
        "bcount",
    ],
    "S回数": [
        "scount",
        "startcount",
    ],
    "H回数": [
        "hcount",
        "homecount",
    ],
    "B回数": [
        "bcount",
        "backcount",
    ],
    "逃げ": [
        "nige",
    ],
    "捲り": [
        "makuri",
        "捲",
    ],
    "差し": [
        "sashi",
        "差",
    ],
    "マーク": [
        "mark",
        "マーク",
    ],
    "ライン": [
        "line",
        "並び",
        "narabi",
        "inLine",
    ],
    "級班": [
        "kyuhan",
        "class",
        "grade",
    ],
    "年齢": [
        "age",
        "nenrei",
    ],
    "府県": [
        "fuken",
        "pref",
        "ken",
    ],
    "期別": [
        "kibetsu",
        "kibetu",
        "term",
    ],
    "ギア": [
        "gear",
        "gearRatio",
    ],
    "直近成績": [
        "recent",
        "past",
        "history",
        "seiseki",
        "racehistory",
    ],
}


def normalize_text(value):
    if value is None:
        return ""

    return str(value).replace("　", " ").strip()


def flatten_json(obj, path="ROOT"):

    items = []

    if isinstance(obj, dict):

        for key, value in obj.items():

            new_path = f"{path}.{key}"

            items.append(
                {
                    "path": new_path,
                    "key": str(key),
                    "value": value,
                    "value_type": type(value).__name__,
                }
            )

            items.extend(
                flatten_json(
                    value,
                    new_path,
                )
            )

    elif isinstance(obj, list):

        for index, value in enumerate(obj):

            new_path = f"{path}[{index}]"

            items.extend(
                flatten_json(
                    value,
                    new_path,
                )
            )

    return items


def is_simple_value(value):

    return isinstance(
        value,
        (
            str,
            int,
            float,
            bool,
        ),
    ) or value is None


def match_target(item, words):

    key = item["key"].lower()
    path = item["path"].lower()

    for word in words:

        word = str(word).lower()

        if word in key:
            return True

        if word in path:
            return True

    return False


def main():

    print("=" * 70)
    print("🔥 146 レース前AI学習項目 徹底探索")
    print("=" * 70)

    if not INPUT_FILE.exists():

        print()
        print("❌ 入力JSONがありません")
        print(f"INPUT: {INPUT_FILE}")

        return

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8",
    ) as f:

        data = json.load(f)

    if not isinstance(data, list):

        print("❌ ROOTがlistではありません")
        return

    print()
    print(f"INPUT: {INPUT_FILE.name}")
    print(f"レース件数: {len(data)}")

    inventory = []

    for race_index, joined in enumerate(data):

        if not isinstance(joined, dict):
            continue

        race_key = normalize_text(
            joined.get("race_key")
        )

        date = normalize_text(
            joined.get("date")
        )

        venue = normalize_text(
            joined.get("venue")
        )

        race_no = normalize_text(
            joined.get("race_no")
        )

        pre_race_data = joined.get(
            "pre_race_data"
        )

        if not isinstance(
            pre_race_data,
            dict,
        ):

            print()
            print(
                f"⚠️ RACE #{race_index + 1} "
                "pre_race_dataなし"
            )

            continue

        print()
        print("-" * 70)
        print(f"🔥 RACE #{race_index + 1}")
        print(f"RACE KEY: {race_key}")
        print(f"開催日: {date}")
        print(f"競輪場: {venue}")
        print(f"レース番号: {race_no}")

        items = flatten_json(
            pre_race_data,
            "PRE_RACE",
        )

        simple_items = [
            item
            for item in items
            if is_simple_value(
                item["value"]
            )
        ]

        print(
            f"レース前 総ITEM数: "
            f"{len(items)}"
        )

        print(
            f"VALUE ITEM数: "
            f"{len(simple_items)}"
        )

        race_inventory = {
            "race_key": race_key,
            "date": date,
            "venue": venue,
            "race_no": race_no,
            "categories": {},
        }

        for category, words in TARGETS.items():

            candidates = []

            for item in simple_items:

                if not match_target(
                    item,
                    words,
                ):
                    continue

                candidates.append(
                    {
                        "path": item["path"],
                        "key": item["key"],
                        "value": item["value"],
                        "value_type": item[
                            "value_type"
                        ],
                    }
                )

            race_inventory[
                "categories"
            ][category] = candidates

        inventory.append(
            race_inventory
        )

        print()
        print("=" * 70)
        print("🔥 AI予想項目 候補探索")
        print("=" * 70)

        for category in TARGETS:

            candidates = race_inventory[
                "categories"
            ][category]

            print()
            print(f"🔥 {category}候補")
            print(
                f"候補数: "
                f"{len(candidates)}"
            )

            for candidate in candidates[:25]:

                value = candidate["value"]

                print(
                    f"{candidate['path']} "
                    f"= {value}"
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
    print("🔥 146テスト終了")
    print("=" * 70)

    print(
        f"探索レース件数: "
        f"{len(inventory)}"
    )

    if inventory:

        categories = inventory[0][
            "categories"
        ]

        print()

        for category in TARGETS:

            count = len(
                categories.get(
                    category,
                    [],
                )
            )

            print(
                f"{category}候補: "
                f"{count}"
            )

    print()
    print(
        f"保存先: "
        f"{OUTPUT_FILE.name}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()