import json
import os
from collections import defaultdict


INPUT_FILE = "155_all_venues_jsj006.json"
OUTPUT_FILE = "160_jsj006_kaisai_date_map.json"

TARGET_DATE = "20260703"

TARGET_IDS = {
    "015788",
    "014302",
    "014059",
    "015689",
    "015446",
    "013550",
    "015005",
}


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def walk(obj, path="ROOT", parents=None):
    if parents is None:
        parents = []

    if isinstance(obj, dict):

        current_parents = parents + [
            (path, obj)
        ]

        yield path, obj, current_parents

        for key, value in obj.items():
            child_path = f"{path}.{key}"

            yield from walk(
                value,
                child_path,
                current_parents,
            )

    elif isinstance(obj, list):

        for index, value in enumerate(obj):
            child_path = f"{path}[{index}]"

            yield from walk(
                value,
                child_path,
                parents,
            )


def normalize_id(value):
    if value is None:
        return ""

    text = str(value).strip()

    digits = "".join(
        c for c in text
        if c.isdigit()
    )

    if not digits:
        return ""

    return digits.zfill(6)


def get_player_id(obj):
    if not isinstance(obj, dict):
        return ""

    candidate_keys = [
        "numPlayer",
        "sensyuRegistNo",
        "player_id",
        "playerId",
        "sensyuNo",
        "registNo",
    ]

    for key in candidate_keys:

        if key not in obj:
            continue

        player_id = normalize_id(
            obj.get(key)
        )

        if player_id:
            return player_id

    return ""


def get_player_name(obj):
    if not isinstance(obj, dict):
        return ""

    candidate_keys = [
        "sensyuName",
        "player_name",
        "namePlayer",
        "namePlayerSei",
        "imgPlayerPictAlt",
    ]

    for key in candidate_keys:

        value = obj.get(key)

        if value not in [
            None,
            "",
        ]:
            return str(value)

    return ""


def find_parent_value(
    parents,
    candidate_keys,
):
    for path, obj in reversed(parents):

        if not isinstance(obj, dict):
            continue

        for key in candidate_keys:

            if key not in obj:
                continue

            value = obj.get(key)

            if value not in [
                None,
                "",
            ]:
                return {
                    "path": f"{path}.{key}",
                    "key": key,
                    "value": str(value),
                }

    return None


def main():

    print("=" * 70)
    print("🔥 160 JSJ006 kaisaiFirst 選手ID追跡")
    print("=" * 70)

    if not os.path.exists(INPUT_FILE):

        print(
            f"❌ JSONなし: {INPUT_FILE}"
        )
        return

    data = load_json(
        INPUT_FILE
    )

    player_objects = []

    for path, obj, parents in walk(data):

        if not isinstance(obj, dict):
            continue

        player_id = get_player_id(obj)

        if not player_id:
            continue

        date_info = find_parent_value(
            parents,
            [
                "kaisaiFirst",
                "kaisaiDate",
                "kaisai_date",
                "date",
            ],
        )

        venue_info = find_parent_value(
            parents,
            [
                "joName",
                "jo_name",
                "venue",
                "venueName",
                "joCode",
                "jo_code",
            ],
        )

        race_info = find_parent_value(
            parents,
            [
                "raceNo",
                "race_no",
                "selRaceNo",
                "raceNum",
            ],
        )

        item = {
            "path": path,
            "player_id": player_id,
            "player_name":
                get_player_name(obj),

            "date_info":
                date_info,

            "venue_info":
                venue_info,

            "race_info":
                race_info,

            "object":
                obj,
        }

        player_objects.append(item)

    print()
    print(
        "🔥 選手OBJECT数:",
        len(player_objects),
    )

    date_map = defaultdict(list)

    no_date_players = []

    for item in player_objects:

        date_info = item["date_info"]

        if date_info:
            date_value = date_info["value"]

            date_map[
                date_value
            ].append(item)

        else:
            no_date_players.append(item)

    print()
    print("=" * 70)
    print("🔥 kaisaiFirst 日付別選手数")
    print("=" * 70)

    for date_value in sorted(
        date_map.keys()
    ):

        players = date_map[
            date_value
        ]

        unique_ids = {
            item["player_id"]
            for item in players
        }

        print(
            f"{date_value}"
            f" → OBJECT:{len(players)}"
            f" 選手ID:{len(unique_ids)}"
        )

    print()
    print("=" * 70)
    print(
        f"🔥 TARGET DATE {TARGET_DATE} 選手"
    )
    print("=" * 70)

    target_date_players = date_map.get(
        TARGET_DATE,
        [],
    )

    print(
        "対象OBJECT数:",
        len(target_date_players),
    )

    for index, item in enumerate(
        target_date_players,
        start=1,
    ):

        print()
        print(
            f"🔥 PLAYER #{index}"
        )
        print(
            "PATH :",
            item["path"],
        )
        print(
            "ID   :",
            item["player_id"],
        )
        print(
            "NAME :",
            item["player_name"],
        )
        print(
            "DATE :",
            item["date_info"],
        )
        print(
            "VENUE:",
            item["venue_info"],
        )
        print(
            "RACE :",
            item["race_info"],
        )

    print()
    print("=" * 70)
    print("🔥 奈良7R 7選手 直接追跡")
    print("=" * 70)

    target_id_results = []

    for target_id in sorted(TARGET_IDS):

        matches = [
            item
            for item in player_objects
            if item["player_id"]
            == target_id
        ]

        print()
        print("-" * 70)
        print(
            "ID:",
            target_id,
        )
        print(
            "一致OBJECT数:",
            len(matches),
        )

        for item in matches[:20]:

            print()
            print(
                "PATH :",
                item["path"],
            )
            print(
                "NAME :",
                item["player_name"],
            )
            print(
                "DATE :",
                item["date_info"],
            )
            print(
                "VENUE:",
                item["venue_info"],
            )
            print(
                "RACE :",
                item["race_info"],
            )

        target_id_results.append({
            "player_id":
                target_id,

            "match_count":
                len(matches),

            "matches":
                matches,
        })

    print()
    print("=" * 70)
    print("🔥 日付なし選手OBJECT SAMPLE")
    print("=" * 70)

    print(
        "日付なしOBJECT数:",
        len(no_date_players),
    )

    for item in no_date_players[:10]:

        print()
        print(
            "PATH:",
            item["path"],
        )
        print(
            "ID:",
            item["player_id"],
        )
        print(
            "NAME:",
            item["player_name"],
        )

    output = {
        "input_file":
            INPUT_FILE,

        "target_date":
            TARGET_DATE,

        "summary": {
            "player_object_count":
                len(player_objects),

            "date_count":
                len(date_map),

            "target_date_object_count":
                len(target_date_players),

            "no_date_object_count":
                len(no_date_players),
        },

        "date_summary": {
            date_value: {
                "object_count":
                    len(players),

                "unique_player_ids":
                    len({
                        item["player_id"]
                        for item in players
                    }),
            }

            for date_value, players
            in date_map.items()
        },

        "target_date_players":
            target_date_players,

        "target_player_results":
            target_id_results,

        "no_date_players":
            no_date_players,
    }

    with open(
        OUTPUT_FILE,
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
    print("🔥 160テスト終了")
    print("=" * 70)

    print(
        "選手OBJECT数:",
        len(player_objects),
    )

    print(
        "kaisaiFirst日付数:",
        len(date_map),
    )

    print(
        f"{TARGET_DATE} OBJECT数:",
        len(target_date_players),
    )

    print(
        "日付なしOBJECT数:",
        len(no_date_players),
    )

    print()
    print(
        f"保存先: {OUTPUT_FILE}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()