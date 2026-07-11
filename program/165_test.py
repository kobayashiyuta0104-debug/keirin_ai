import json
import os


PRE_RACE_FILE = "163_dated_ai_pre_race_features.json"
RESULT_FILE = "145_ai_training_race.json"

OUTPUT_FILE = "165_direct_player_id_join.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_id(value):
    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    return text.zfill(6)


def get_pre_player_id(player):
    if not isinstance(player, dict):
        return None

    for key in [
        "player_id",
        "sensyuRegistNo",
        "numPlayer",
    ]:
        value = player.get(key)

        if value not in [None, ""]:
            return normalize_id(value)

    return None


def get_result_player_id(player):
    if not isinstance(player, dict):
        return None

    for key in [
        "player_id",
        "sensyuRegistNo",
        "numPlayer",
    ]:
        value = player.get(key)

        if value not in [None, ""]:
            return normalize_id(value)

    return None


def main():
    print("=" * 70)
    print("🔥 165 163予想データ × 145確定結果 直接ID照合")
    print("=" * 70)

    if not os.path.exists(PRE_RACE_FILE):
        print("❌ ファイルなし:", PRE_RACE_FILE)
        return

    if not os.path.exists(RESULT_FILE):
        print("❌ ファイルなし:", RESULT_FILE)
        return

    pre_data = load_json(PRE_RACE_FILE)
    result_data = load_json(RESULT_FILE)

    pre_races = pre_data.get("races", [])

    print()
    print("🔥 JSON読込成功")
    print("PRE :", PRE_RACE_FILE)
    print("RESULT:", RESULT_FILE)
    print("163レース数:", len(pre_races))

    print()
    print("=" * 70)
    print("🔥 163 選手IDセット作成")
    print("=" * 70)

    pre_index = {}

    for race in pre_races:
        if not isinstance(race, dict):
            continue

        race_key = race.get("race_key")

        players = race.get("players", [])

        ids = []

        for player in players:
            player_id = get_pre_player_id(player)

            if player_id:
                ids.append(player_id)

        id_set = frozenset(ids)

        if id_set:
            pre_index.setdefault(id_set, [])
            pre_index[id_set].append(race_key)

    print("IDセット数:", len(pre_index))

    print()
    print("🔥 163 IDセット SAMPLE")

    for index, (id_set, race_keys) in enumerate(
        pre_index.items()
    ):
        if index >= 10:
            break

        print()
        print("RACE KEY:", race_keys)
        print("ID数:", len(id_set))
        print("ID:", sorted(id_set))

    print()
    print("=" * 70)
    print("🔥 145確定結果探索")
    print("=" * 70)

    if isinstance(result_data, dict):
        result_races = [result_data]

    elif isinstance(result_data, list):
        result_races = result_data

    else:
        result_races = []

    print("145 ROOT件数:", len(result_races))

    result_candidates = []

    for index, race in enumerate(result_races):
        if not isinstance(race, dict):
            continue

        result = race.get("result")

        if not isinstance(result, dict):
            continue

        finish_order = result.get("finish_order")

        if not isinstance(finish_order, list):
            continue

        ids = []

        for player in finish_order:
            player_id = get_result_player_id(player)

            if player_id:
                ids.append(player_id)

        print()
        print("-" * 70)
        print("🔥 RESULT RACE", index)
        print("race_key:", race.get("race_key"))
        print("finish_order件数:", len(finish_order))
        print("選手ID数:", len(ids))
        print("ID:", ids)

        result_candidates.append(
            {
                "index": index,
                "race": race,
                "finish_order": finish_order,
                "ids": ids,
                "id_set": frozenset(ids),
            }
        )

    print()
    print("=" * 70)
    print("🔥 163 × 145 ID完全一致照合")
    print("=" * 70)

    joined = []

    for candidate in result_candidates:
        id_set = candidate["id_set"]

        if not id_set:
            continue

        matched_race_keys = pre_index.get(
            id_set,
            [],
        )

        print()
        print("RESULT INDEX:", candidate["index"])
        print("ID数:", len(id_set))
        print("一致race_key数:", len(matched_race_keys))

        if matched_race_keys:
            for race_key in matched_race_keys:
                print("🔥 完全一致:", race_key)

                joined.append(
                    {
                        "race_key": race_key,
                        "result_index": candidate["index"],
                        "player_ids": sorted(id_set),
                        "finish_order": candidate["finish_order"],
                    }
                )

    print()
    print("=" * 70)
    print("🔥 部分一致TOP探索")
    print("=" * 70)

    partial_matches = []

    for candidate in result_candidates:
        result_ids = candidate["id_set"]

        if not result_ids:
            continue

        for pre_ids, race_keys in pre_index.items():
            common = result_ids & pre_ids

            partial_matches.append(
                {
                    "result_index": candidate["index"],
                    "race_keys": race_keys,
                    "common_count": len(common),
                    "result_count": len(result_ids),
                    "pre_count": len(pre_ids),
                    "common_ids": sorted(common),
                }
            )

    partial_matches.sort(
        key=lambda x: x["common_count"],
        reverse=True,
    )

    for item in partial_matches[:20]:
        print()
        print("RESULT INDEX:", item["result_index"])
        print("RACE KEY:", item["race_keys"])
        print(
            "一致:",
            item["common_count"],
            "/",
            item["result_count"],
        )
        print("共通ID:", item["common_ids"])

    output = {
        "pre_race_count": len(pre_races),
        "pre_id_set_count": len(pre_index),
        "result_candidate_count": len(result_candidates),
        "joined_count": len(joined),
        "joined": joined,
        "partial_match_top20": partial_matches[:20],
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
    print("🔥 165テスト終了")
    print("=" * 70)

    print("163レース数:", len(pre_races))
    print("163 IDセット数:", len(pre_index))
    print(
        "145確定結果候補数:",
        len(result_candidates),
    )
    print(
        "🔥 完全一致結合数:",
        len(joined),
    )

    print()
    print("保存先:", OUTPUT_FILE)
    print("=" * 70)


if __name__ == "__main__":
    main()