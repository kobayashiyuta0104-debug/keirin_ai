import json
from pathlib import Path
from collections import defaultdict


BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_FILE = (
    BASE_DIR
    / "151_player_object_shapes.json"
)


PLAYER_ID_KEYS = {
    "numPlayer",
    "sensyuRegistNo",
}


def walk(
    obj,
    path="ROOT",
    found=None,
):

    if found is None:

        found = []

    if isinstance(obj, dict):

        player_id_key = None
        player_id = None

        for key in PLAYER_ID_KEYS:

            if key in obj:

                value = obj.get(key)

                if value is not None:

                    text = str(value).strip()

                    if (
                        text.isdigit()
                        and 5 <= len(text) <= 6
                    ):

                        player_id_key = key
                        player_id = text

                        break

        if player_id_key is not None:

            found.append({
                "path": path,
                "player_id_key": player_id_key,
                "player_id": player_id,
                "keys": sorted(
                    str(key)
                    for key in obj.keys()
                ),
                "raw": obj,
            })

        for key, value in obj.items():

            new_path = (
                f"{path}.{key}"
            )

            if isinstance(
                value,
                (dict, list),
            ):

                walk(
                    value,
                    new_path,
                    found,
                )

    elif isinstance(obj, list):

        for index, value in enumerate(obj):

            new_path = (
                f"{path}[{index}]"
            )

            if isinstance(
                value,
                (dict, list),
            ):

                walk(
                    value,
                    new_path,
                    found,
                )

    return found


def make_shape_key(keys):

    return " | ".join(keys)


def main():

    print("=" * 70)
    print(
        "🔥 151 選手OBJECT型 "
        "全JSON横断比較"
    )
    print("=" * 70)

    json_files = sorted(
        BASE_DIR.glob("*.json")
    )

    print()
    print(
        f"探索JSON数: "
        f"{len(json_files)}"
    )

    shape_groups = defaultdict(
        lambda: {
            "count": 0,
            "files": set(),
            "examples": [],
        }
    )

    total_player_objects = 0

    for file_path in json_files:

        if file_path.name.startswith(
            "151_"
        ):

            continue

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8",
            ) as f:

                data = json.load(f)

        except Exception:

            continue

        player_objects = walk(data)

        if not player_objects:

            continue

        for item in player_objects:

            total_player_objects += 1

            shape_key = make_shape_key(
                item["keys"]
            )

            group = shape_groups[
                shape_key
            ]

            group["count"] += 1

            group["files"].add(
                file_path.name
            )

            if len(
                group["examples"]
            ) < 3:

                group[
                    "examples"
                ].append({
                    "file": file_path.name,
                    "path": item["path"],
                    "player_id": (
                        item["player_id"]
                    ),
                    "raw": item["raw"],
                })

    sorted_shapes = sorted(
        shape_groups.items(),
        key=lambda x: x[1]["count"],
        reverse=True,
    )

    output_shapes = []

    print()
    print("=" * 70)
    print("🔥 選手OBJECT型一覧")
    print("=" * 70)

    for index, (
        shape_key,
        group,
    ) in enumerate(
        sorted_shapes,
        start=1,
    ):

        print()
        print("-" * 70)
        print(
            f"🔥 SHAPE #{index}"
        )
        print(
            f"OBJECT件数: "
            f"{group['count']}"
        )
        print(
            f"使用JSON数: "
            f"{len(group['files'])}"
        )

        print()
        print("🔥 KEYS")

        keys = (
            shape_key.split(" | ")
            if shape_key
            else []
        )

        for key in keys:

            print(f"- {key}")

        print()
        print("🔥 使用JSON")

        for file_name in sorted(
            group["files"]
        ):

            print(
                f"- {file_name}"
            )

        print()
        print("🔥 代表OBJECT")

        for example in group["examples"]:

            print()
            print(
                f"FILE: "
                f"{example['file']}"
            )
            print(
                f"PATH: "
                f"{example['path']}"
            )
            print(
                f"PLAYER ID: "
                f"{example['player_id']}"
            )

            print(
                json.dumps(
                    example["raw"],
                    ensure_ascii=False,
                    indent=2,
                )
            )

        output_shapes.append({
            "shape_no": index,
            "object_count": (
                group["count"]
            ),
            "file_count": len(
                group["files"]
            ),
            "keys": keys,
            "files": sorted(
                group["files"]
            ),
            "examples": (
                group["examples"]
            ),
        })

    output_data = {
        "total_player_objects": (
            total_player_objects
        ),
        "shape_count": len(
            sorted_shapes
        ),
        "shapes": output_shapes,
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            output_data,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print("=" * 70)
    print("🔥 151テスト終了")
    print("=" * 70)

    print(
        f"選手OBJECT総数: "
        f"{total_player_objects}"
    )

    print(
        f"選手OBJECT型数: "
        f"{len(sorted_shapes)}"
    )

    print()
    print("🔥 SHAPE要約")

    for index, (
        shape_key,
        group,
    ) in enumerate(
        sorted_shapes,
        start=1,
    ):

        keys = (
            shape_key.split(" | ")
            if shape_key
            else []
        )

        print()
        print(
            f"SHAPE #{index}"
        )
        print(
            f"件数: {group['count']}"
        )
        print(
            "KEYS: "
            + ", ".join(keys)
        )

    print()
    print(
        f"保存先: "
        f"{OUTPUT_FILE.name}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()