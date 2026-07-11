import json
import os


JSJ006_FILE = "155_all_venues_jsj006.json"
RESULT_FILE = "145_ai_training_race.json"
OUTPUT_FILE = "158_player_id_compare.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_id(value):
    if value is None:
        return ""

    value = str(value).strip()

    if not value:
        return ""

    return value.zfill(6)


def walk(obj, path="ROOT"):
    if isinstance(obj, dict):
        yield path, obj

        for key, value in obj.items():
            yield from walk(
                value,
                f"{path}.{key}",
            )

    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            yield from walk(
                value,
                f"{path}[{index}]",
            )


def collect_all_ids(data):
    id_keys = [
        "sensyuRegistNo",
        "numPlayer",
        "player_id",
        "playerId",
        "registration_no",
    ]

    found = []

    for path, obj in walk(data):
        if not isinstance(obj, dict):
            continue

        for key in id_keys:
            if key not in obj:
                continue

            player_id = normalize_id(
                obj.get(key)
            )

            if not player_id:
                continue

            found.append({
                "player_id": player_id,
                "key": key,
                "path": path,
                "object": obj,
            })

    return found


def main():
    print("=" * 70)
    print("🔥 158 JSJ006 × 奈良7R 登録番号直接照合")
    print("=" * 70)

    if not os.path.exists(JSJ006_FILE):
        print(
            f"❌ ファイル無し: {JSJ006_FILE}"
        )
        return

    if not os.path.exists(RESULT_FILE):
        print(
            f"❌ ファイル無し: {RESULT_FILE}"
        )
        return

    jsj006_data = load_json(JSJ006_FILE)
    result_data = load_json(RESULT_FILE)

    jsj006_ids = collect_all_ids(
        jsj006_data
    )

    result_ids = collect_all_ids(
        result_data
    )

    jsj006_index = {}

    for item in jsj006_ids:
        player_id = item["player_id"]

        jsj006_index.setdefault(
            player_id,
            []
        ).append(item)

    result_unique = {}

    for item in result_ids:
        player_id = item["player_id"]

        if player_id not in result_unique:
            result_unique[player_id] = item

    print()
    print("🔥 ID取得結果")
    print(
        "JSJ006 ID OBJECT数:",
        len(jsj006_ids),
    )
    print(
        "JSJ006 IDユニーク数:",
        len(jsj006_index),
    )
    print(
        "RESULT IDユニーク数:",
        len(result_unique),
    )

    print()
    print("=" * 70)
    print("🔥 奈良7R 7選手 直接照合")
    print("=" * 70)

    compare_results = []

    match_count = 0

    for player_id, result_item in result_unique.items():

        result_obj = result_item["object"]

        player_name = (
            result_obj.get("player_name")
            or result_obj.get("sensyuName")
            or result_obj.get("namePlayerSei")
            or ""
        )

        matches = jsj006_index.get(
            player_id,
            []
        )

        exists = len(matches) > 0

        if exists:
            match_count += 1

        print()
        print("-" * 70)
        print("ID   :", player_id)
        print("選手 :", player_name)
        print(
            "JSJ006存在:",
            "🔥 YES" if exists else "❌ NO",
        )

        if exists:
            print(
                "一致OBJECT数:",
                len(matches),
            )

            for index, match in enumerate(
                matches[:3],
                start=1,
            ):
                print()
                print(
                    f"🔥 MATCH #{index}"
                )
                print(
                    "KEY :",
                    match["key"],
                )
                print(
                    "PATH:",
                    match["path"],
                )
                print(
                    json.dumps(
                        match["object"],
                        ensure_ascii=False,
                        indent=2,
                    )
                )

        compare_results.append({
            "player_id": player_id,
            "player_name": player_name,
            "exists_in_jsj006": exists,
            "match_count": len(matches),
            "result_path": result_item["path"],
            "jsj006_matches": [
                {
                    "key": x["key"],
                    "path": x["path"],
                }
                for x in matches
            ],
        })

    output = {
        "summary": {
            "jsj006_id_objects":
                len(jsj006_ids),

            "jsj006_unique_ids":
                len(jsj006_index),

            "result_unique_ids":
                len(result_unique),

            "matched_ids":
                match_count,
        },

        "compare_results":
            compare_results,
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
    print("🔥 158テスト終了")
    print("=" * 70)
    print(
        "JSJ006 IDユニーク数:",
        len(jsj006_index),
    )
    print(
        "奈良7R 選手ID数:",
        len(result_unique),
    )
    print(
        "🔥 登録番号一致数:",
        match_count,
    )
    print()
    print(
        f"保存先: {OUTPUT_FILE}"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()