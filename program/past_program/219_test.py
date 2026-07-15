import json
from pathlib import Path
from collections import Counter


OLD_PATH = Path(
    r"C:\競輪AI\163_dated_ai_pre_race_features.json"
)

RAW_PATH = Path(
    r"C:\競輪AI\181_jsj006_full_capture.json"
)

OUTPUT_PATH = Path(
    r"C:\競輪AI\219_old_recent_vs_jsj006_raw_compare.json"
)


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def normalize_id(value):
    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    return text


def normalize_finish(value):
    if value is None:
        return None

    if isinstance(value, int):
        return value

    text = str(value).strip()

    if not text:
        return None

    try:
        return int(text)
    except ValueError:
        return text


def find_sensyu_lists(obj, path="$"):
    hits = []

    if isinstance(obj, dict):

        value = obj.get("sensyuTypeInfo")

        if isinstance(value, list):
            hits.append(
                {
                    "path": f"{path}.sensyuTypeInfo",
                    "list": value,
                }
            )

        for key, value in obj.items():
            hits.extend(
                find_sensyu_lists(
                    value,
                    f"{path}.{key}"
                )
            )

    elif isinstance(obj, list):

        for i, value in enumerate(obj):
            hits.extend(
                find_sensyu_lists(
                    value,
                    f"{path}[{i}]"
                )
            )

    return hits


def extract_raw_recent(player):
    tyo4 = player.get("tyo4InfoSubData")

    if not isinstance(tyo4, dict):
        return []

    result_list = tyo4.get("resultInfoSubData")

    if not isinstance(result_list, list):
        return []

    results = []

    for item in result_list:

        if not isinstance(item, dict):
            continue

        finish = normalize_finish(
            item.get("imgTyakuiName")
        )

        back = item.get("backCnt")

        if back is None:
            back = item.get("backCount")

        results.append(
            {
                "finish": finish,
                "back": back,
            }
        )

    return results


def extract_old_recent(player):
    results = player.get(
        "recent_meeting_results"
    )

    if not isinstance(results, list):
        return []

    output = []

    for item in results:

        if not isinstance(item, dict):
            continue

        output.append(
            {
                "finish": normalize_finish(
                    item.get("finish")
                ),
                "back": item.get("back"),
            }
        )

    return output


def main():

    print(
        "=== 219 163旧recent_meeting_results "
        "vs JSJ006生データ直接比較 ==="
    )

    old_data = load_json(OLD_PATH)
    raw_data = load_json(RAW_PATH)

    old_players = []

    for race in old_data.get("races", []):

        if not isinstance(race, dict):
            continue

        race_key = race.get("race_key")

        for player in race.get("players", []):

            if not isinstance(player, dict):
                continue

            player_id = normalize_id(
                player.get("player_id")
            )

            old_players.append(
                {
                    "race_key": race_key,
                    "player_id": player_id,
                    "player_name": player.get(
                        "player_name"
                    ),
                    "recent": extract_old_recent(
                        player
                    ),
                    "recent_meeting": player.get(
                        "recent_meeting"
                    ),
                }
            )

    print(
        "163旧選手行数:",
        len(old_players)
    )

    raw_lists = find_sensyu_lists(raw_data)

    print(
        "JSJ006 sensyuTypeInfo発見数:",
        len(raw_lists)
    )

    raw_by_player_id = {}

    raw_player_count = 0

    for hit in raw_lists:

        for player in hit["list"]:

            if not isinstance(player, dict):
                continue

            raw_player_count += 1

            player_id = normalize_id(
                player.get("sensyuRegistNo")
            )

            if player_id is None:
                continue

            raw_by_player_id.setdefault(
                player_id,
                []
            ).append(
                {
                    "path": hit["path"],
                    "player_name": player.get(
                        "sensyuName"
                    ),
                    "recent": extract_raw_recent(
                        player
                    ),
                }
            )

    print(
        "JSJ006生選手行数:",
        raw_player_count
    )

    print(
        "JSJ006選手ID種類数:",
        len(raw_by_player_id)
    )

    compared = 0
    exact_match = 0
    finish_match = 0
    mismatch = 0
    not_found = 0

    old_len_counter = Counter()
    raw_len_counter = Counter()

    samples = []
    mismatch_samples = []
    not_found_samples = []

    for old in old_players:

        player_id = old["player_id"]

        old_recent = old["recent"]

        old_len_counter[len(old_recent)] += 1

        candidates = raw_by_player_id.get(
            player_id,
            []
        )

        if not candidates:

            not_found += 1

            if len(not_found_samples) < 50:
                not_found_samples.append(old)

            continue

        best = None
        best_score = -1

        old_finish = [
            x.get("finish")
            for x in old_recent
        ]

        for candidate in candidates:

            raw_recent = candidate["recent"]

            raw_finish = [
                x.get("finish")
                for x in raw_recent
            ]

            score = 0

            compare_len = min(
                len(old_finish),
                len(raw_finish)
            )

            for i in range(compare_len):

                if old_finish[i] == raw_finish[i]:
                    score += 1

            if (
                len(old_finish)
                == len(raw_finish)
            ):
                score += 10

            if score > best_score:
                best_score = score
                best = candidate

        if best is None:
            not_found += 1
            continue

        raw_recent = best["recent"]

        raw_len_counter[len(raw_recent)] += 1

        raw_finish = [
            x.get("finish")
            for x in raw_recent
        ]

        compared += 1

        is_finish_match = (
            old_finish == raw_finish
        )

        is_exact_match = (
            old_recent == raw_recent
        )

        if is_finish_match:
            finish_match += 1

        if is_exact_match:
            exact_match += 1
        else:
            mismatch += 1

        sample = {
            "race_key": old["race_key"],
            "player_id": player_id,
            "player_name": old["player_name"],
            "old_recent": old_recent,
            "raw_recent": raw_recent,
            "old_finish": old_finish,
            "raw_finish": raw_finish,
            "finish_match": is_finish_match,
            "exact_match": is_exact_match,
            "raw_path": best["path"],
            "recent_meeting": old[
                "recent_meeting"
            ],
        }

        if len(samples) < 50:
            samples.append(sample)

        if (
            not is_exact_match
            and len(mismatch_samples) < 100
        ):
            mismatch_samples.append(sample)

    print("\n=== 219 結果 ===")
    print("比較対象旧選手数:", len(old_players))
    print("比較成功:", compared)
    print("finish完全一致:", finish_match)
    print("finish+back完全一致:", exact_match)
    print("不一致:", mismatch)
    print("JSJ006選手ID未発見:", not_found)

    print(
        "\n旧recent件数分布:",
        dict(old_len_counter)
    )

    print(
        "RAW recent件数分布:",
        dict(raw_len_counter)
    )

    print(
        "\n=== 不一致サンプル 先頭100 ==="
    )

    for i, item in enumerate(
        mismatch_samples,
        start=1
    ):

        print("\n" + "-" * 70)

        print(
            f"[{i}]",
            item["race_key"],
            "/",
            item["player_id"],
            "/",
            item["player_name"]
        )

        print(
            "OLD:",
            item["old_recent"]
        )

        print(
            "RAW:",
            item["raw_recent"]
        )

        print(
            "FINISH MATCH:",
            item["finish_match"]
        )

        print(
            "RAW PATH:",
            item["raw_path"]
        )

    print(
        "\n=== JSJ006未発見サンプル 先頭50 ==="
    )

    for i, item in enumerate(
        not_found_samples,
        start=1
    ):

        print(
            f"[{i}]",
            item["race_key"],
            "/",
            item["player_id"],
            "/",
            item["player_name"]
        )

    output = {
        "old_player_count": len(old_players),
        "raw_player_count": raw_player_count,
        "raw_player_id_count": len(
            raw_by_player_id
        ),
        "compared": compared,
        "finish_match": finish_match,
        "exact_match": exact_match,
        "mismatch": mismatch,
        "not_found": not_found,
        "old_recent_length_distribution": dict(
            old_len_counter
        ),
        "raw_recent_length_distribution": dict(
            raw_len_counter
        ),
        "samples": samples,
        "mismatch_samples": mismatch_samples,
        "not_found_samples": not_found_samples,
    }

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            output,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(
        f"\n保存完了: {OUTPUT_PATH}"
    )

    print("=== 219 完了 ===")


if __name__ == "__main__":
    main()