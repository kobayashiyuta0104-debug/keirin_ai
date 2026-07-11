import json
import os
import re


PRE_RACE_FILE = "163_dated_ai_pre_race_features.json"
RESULT_FILES = [
    "142_joined_race_data.json",
    "145_ai_training_race.json",
    "125_extracted_results.json",
    "122_all_venues_jsj012.json",
]

OUTPUT_FILE = "164_result_join_probe.json"

TARGET_DATE = "20260707"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_text(value):
    if value is None:
        return ""

    value = str(value)

    value = value.replace("\u3000", " ")
    value = value.replace("&nbsp;", " ")
    value = re.sub(r"\s+", "", value)

    return value.strip()


def normalize_race_no(value):
    if value is None:
        return None

    text = str(value)

    m = re.search(r"(\d+)", text)

    if not m:
        return None

    return int(m.group(1))


def walk(obj, path="ROOT"):
    yield path, obj

    if isinstance(obj, dict):
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


def find_value(obj, keys):
    if not isinstance(obj, dict):
        return None

    for key in keys:
        if key in obj:
            value = obj.get(key)

            if value not in [None, ""]:
                return value

    return None


def extract_finish_order(obj):
    if not isinstance(obj, dict):
        return []

    if isinstance(obj.get("finish_order"), list):
        players = obj["finish_order"]

        valid = []

        for player in players:
            if not isinstance(player, dict):
                continue

            rank = find_value(
                player,
                [
                    "rank",
                    "tyaku",
                    "finish",
                ],
            )

            car_no = find_value(
                player,
                [
                    "car_no",
                    "carNum",
                    "syaban",
                ],
            )

            player_id = find_value(
                player,
                [
                    "player_id",
                    "numPlayer",
                    "sensyuRegistNo",
                ],
            )

            if rank is None:
                continue

            valid.append(
                {
                    "rank": rank,
                    "car_no": car_no,
                    "player_id": (
                        str(player_id).zfill(6)
                        if player_id is not None
                        else None
                    ),
                }
            )

        if len(valid) >= 5:
            return valid

    return []


def detect_result_objects(data):
    results = []

    for path, obj in walk(data):
        if not isinstance(obj, dict):
            continue

        finish_order = extract_finish_order(obj)

        if len(finish_order) < 5:
            continue

        results.append(
            {
                "path": path,
                "object": obj,
                "finish_order": finish_order,
            }
        )

    return results


def main():
    print("=" * 70)
    print("🔥 164 確定結果 × 163 race_key 結合準備テスト")
    print("=" * 70)

    if not os.path.exists(PRE_RACE_FILE):
        print(f"❌ 予想データなし: {PRE_RACE_FILE}")
        return

    pre_data = load_json(PRE_RACE_FILE)

    races = pre_data.get("races", [])

    pre_race_map = {}

    for race in races:
        if not isinstance(race, dict):
            continue

        race_key = race.get("race_key")

        if not race_key:
            continue

        pre_race_map[race_key] = race

    print()
    print("🔥 163読込成功")
    print("予想レース数:", len(pre_race_map))

    all_result_candidates = []

    print()
    print("=" * 70)
    print("🔥 既存確定結果JSON探索")
    print("=" * 70)

    for file_name in RESULT_FILES:
        if not os.path.exists(file_name):
            print(f"⚠ JSONなし: {file_name}")
            continue

        data = load_json(file_name)

        candidates = detect_result_objects(data)

        print(
            file_name,
            "→ 確定結果候補:",
            len(candidates),
        )

        for candidate in candidates:
            candidate["source_file"] = file_name
            all_result_candidates.append(candidate)

    print()
    print("確定結果候補総数:", len(all_result_candidates))

    print()
    print("=" * 70)
    print("🔥 確定結果候補 SAMPLE")
    print("=" * 70)

    for index, candidate in enumerate(
        all_result_candidates[:20],
        start=1,
    ):
        print()
        print(f"🔥 RESULT #{index}")
        print("FILE:", candidate["source_file"])
        print("PATH:", candidate["path"])
        print(
            "着順:",
            "-".join(
                str(player["car_no"])
                for player in sorted(
                    candidate["finish_order"],
                    key=lambda x: int(x["rank"])
                    if str(x["rank"]).isdigit()
                    else 999,
                )[:3]
            ),
        )

        ids = [
            player["player_id"]
            for player in candidate["finish_order"]
            if player["player_id"]
        ]

        print("選手ID数:", len(ids))
        print("ID:", ids)

    pre_player_index = {}

    for race_key, race in pre_race_map.items():
        players = race.get("players", [])

        player_ids = []

        for player in players:
            if not isinstance(player, dict):
                continue

            player_id = find_value(
                player,
                [
                    "player_id",
                    "sensyuRegistNo",
                    "numPlayer",
                ],
            )

            if player_id is None:
                continue

            player_ids.append(
                str(player_id).zfill(6)
            )

        player_id_set = frozenset(player_ids)

        if player_id_set:
            pre_player_index.setdefault(
                player_id_set,
                [],
            )

            pre_player_index[player_id_set].append(
                race_key
            )

    print()
    print("=" * 70)
    print("🔥 7選手ID完全一致照合")
    print("=" * 70)

    joined = []

    for candidate in all_result_candidates:
        result_ids = [
            player["player_id"]
            for player in candidate["finish_order"]
            if player["player_id"]
        ]

        result_id_set = frozenset(result_ids)

        matched_race_keys = pre_player_index.get(
            result_id_set,
            [],
        )

        if not matched_race_keys:
            continue

        for race_key in matched_race_keys:
            joined.append(
                {
                    "race_key": race_key,
                    "source_file": candidate["source_file"],
                    "result_path": candidate["path"],
                    "finish_order": candidate["finish_order"],
                }
            )

            print()
            print("🔥 結合成功")
            print("RACE KEY:", race_key)
            print("FILE:", candidate["source_file"])
            print("PATH:", candidate["path"])

            sorted_finish = sorted(
                candidate["finish_order"],
                key=lambda x: int(x["rank"])
                if str(x["rank"]).isdigit()
                else 999,
            )

            print(
                "3連単:",
                "-".join(
                    str(player["car_no"])
                    for player in sorted_finish[:3]
                ),
            )

    output = {
        "target_date": TARGET_DATE,
        "pre_race_count": len(pre_race_map),
        "result_candidate_count": len(
            all_result_candidates
        ),
        "joined_count": len(joined),
        "joined": joined,
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
    print("🔥 164テスト終了")
    print("=" * 70)

    print(
        "163予想レース数:",
        len(pre_race_map),
    )

    print(
        "確定結果候補数:",
        len(all_result_candidates),
    )

    print(
        "🔥 7選手ID完全一致結合数:",
        len(joined),
    )

    print()
    print(
        f"保存先: {OUTPUT_FILE}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()