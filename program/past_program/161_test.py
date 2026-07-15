import json
import os
from collections import Counter, defaultdict


INPUT_FILE = "155_all_venues_jsj006.json"
OUTPUT_FILE = "161_jsj006_player_full_structure.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def walk(obj, path="ROOT"):

    yield path, obj

    if isinstance(obj, dict):

        for key, value in obj.items():

            child_path = f"{path}.{key}"

            yield from walk(
                value,
                child_path,
            )

    elif isinstance(obj, list):

        for index, value in enumerate(obj):

            child_path = f"{path}[{index}]"

            yield from walk(
                value,
                child_path,
            )


def is_player_object(obj):

    if not isinstance(obj, dict):
        return False

    id_keys = [
        "sensyuRegistNo",
        "numPlayer",
        "player_id",
        "playerId",
    ]

    name_keys = [
        "sensyuName",
        "namePlayerSei",
        "player_name",
    ]

    has_id = any(
        key in obj
        for key in id_keys
    )

    has_name = any(
        key in obj
        for key in name_keys
    )

    return has_id and has_name


def flatten_object(
    obj,
    path="PLAYER",
    result=None,
):

    if result is None:
        result = []

    if isinstance(obj, dict):

        for key, value in obj.items():

            child_path = f"{path}.{key}"

            result.append({
                "path": child_path,
                "key": key,
                "type": type(value).__name__,
                "value": (
                    value
                    if not isinstance(
                        value,
                        (dict, list),
                    )
                    else None
                ),
            })

            flatten_object(
                value,
                child_path,
                result,
            )

    elif isinstance(obj, list):

        for index, value in enumerate(obj):

            child_path = (
                f"{path}[{index}]"
            )

            result.append({
                "path": child_path,
                "key": f"[{index}]",
                "type": type(value).__name__,
                "value": (
                    value
                    if not isinstance(
                        value,
                        (dict, list),
                    )
                    else None
                ),
            })

            flatten_object(
                value,
                child_path,
                result,
            )

    return result


def main():

    print("=" * 70)
    print("🔥 161 JSJ006 選手能力OBJECT完全解析")
    print("=" * 70)

    if not os.path.exists(INPUT_FILE):

        print(
            f"❌ JSONなし: {INPUT_FILE}"
        )
        return

    data = load_json(
        INPUT_FILE
    )

    players = []

    for path, obj in walk(data):

        if is_player_object(obj):

            players.append({
                "path": path,
                "object": obj,
            })

    print()
    print(
        "🔥 選手OBJECT数:",
        len(players),
    )

    if not players:

        print("❌ 選手OBJECTなし")
        return

    print()
    print("=" * 70)
    print("🔥 PLAYER[0] 生JSON")
    print("=" * 70)

    first_player = players[0]

    print(
        "PATH:",
        first_player["path"],
    )

    print(
        json.dumps(
            first_player["object"],
            ensure_ascii=False,
            indent=2,
        )
    )

    print()
    print("=" * 70)
    print("🔥 PLAYER[0] 完全展開")
    print("=" * 70)

    expanded = flatten_object(
        first_player["object"]
    )

    for item in expanded:

        print(
            f'{item["path"]}'
            f' = {item["value"]}'
            f' [{item["type"]}]'
        )

    key_counter = Counter()

    key_values = defaultdict(list)

    shape_counter = Counter()

    shape_samples = {}

    for player in players:

        obj = player["object"]

        shape = tuple(
            sorted(obj.keys())
        )

        shape_counter[
            shape
        ] += 1

        if shape not in shape_samples:

            shape_samples[
                shape
            ] = player

        for item in flatten_object(obj):

            key = item["key"]

            key_counter[
                key
            ] += 1

            value = item["value"]

            if value not in [
                None,
                "",
            ]:

                if len(
                    key_values[key]
                ) < 20:

                    key_values[
                        key
                    ].append(value)

    print()
    print("=" * 70)
    print("🔥 全KEYランキング")
    print("=" * 70)

    for key, count in (
        key_counter.most_common()
    ):

        samples = key_values.get(
            key,
            [],
        )

        print()
        print(
            f"KEY: {key}"
        )

        print(
            f"COUNT: {count}"
        )

        print(
            "SAMPLE:",
            samples[:10],
        )

    print()
    print("=" * 70)
    print("🔥 選手OBJECT SHAPE")
    print("=" * 70)

    shape_output = []

    for index, (
        shape,
        count,
    ) in enumerate(
        shape_counter.most_common(),
        start=1,
    ):

        sample = shape_samples[
            shape
        ]

        print()
        print(
            f"🔥 SHAPE #{index}"
        )

        print(
            "件数:",
            count,
        )

        print(
            "KEY数:",
            len(shape),
        )

        print(
            "KEYS:",
            ", ".join(shape),
        )

        print(
            "SAMPLE PATH:",
            sample["path"],
        )

        print(
            json.dumps(
                sample["object"],
                ensure_ascii=False,
                indent=2,
            )
        )

        shape_output.append({
            "shape_no": index,
            "count": count,
            "keys": list(shape),
            "sample_path":
                sample["path"],
            "sample_object":
                sample["object"],
        })

    output = {
        "input_file":
            INPUT_FILE,

        "player_object_count":
            len(players),

        "first_player":
            first_player,

        "first_player_expanded":
            expanded,

        "key_ranking": [
            {
                "key": key,
                "count": count,
                "samples":
                    key_values.get(
                        key,
                        [],
                    ),
            }
            for key, count
            in key_counter.most_common()
        ],

        "shapes":
            shape_output,
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
    print("🔥 161テスト終了")
    print("=" * 70)

    print(
        "選手OBJECT数:",
        len(players),
    )

    print(
        "KEY種類数:",
        len(key_counter),
    )

    print(
        "SHAPE種類数:",
        len(shape_counter),
    )

    print()
    print(
        f"保存先: {OUTPUT_FILE}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()