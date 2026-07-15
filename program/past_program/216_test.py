import json
from collections import Counter, defaultdict
from pathlib import Path


INPUT_PATH = Path(r"C:\競輪AI\213_20260706_all_race_raw_capture.json")
OUTPUT_PATH = Path(r"C:\競輪AI\216_recent_result_dict_structure_analysis.json")


def find_race_records(obj):
    """
    JSON全体を再帰探索し、
    JSJ006とJSJ012を同時に持つレース候補を探す。
    """
    found = []

    def walk(x, path="$"):
        if isinstance(x, dict):
            jsj006 = None
            jsj012 = None

            for key, value in x.items():
                key_upper = str(key).upper()

                if key_upper == "JSJ006":
                    jsj006 = value

                if key_upper == "JSJ012":
                    jsj012 = value

            if isinstance(jsj006, dict) and isinstance(jsj012, dict):
                found.append({
                    "path": path,
                    "record": x,
                    "jsj006": jsj006,
                    "jsj012": jsj012,
                })

            for key, value in x.items():
                walk(value, f"{path}.{key}")

        elif isinstance(x, list):
            for i, value in enumerate(x):
                walk(value, f"{path}[{i}]")

    walk(obj)

    # 重複除去
    unique = []
    seen = set()

    for item in found:
        marker = id(item["record"])
        if marker not in seen:
            seen.add(marker)
            unique.append(item)

    return unique


def get_race_key(record, fallback):
    candidates = [
        "race_key",
        "raceKey",
        "key",
    ]

    for key in candidates:
        value = record.get(key)
        if value:
            return str(value)

    return fallback


def analyze_dict(name, value, stats):
    if value is None:
        stats["type_counter"]["NoneType"] += 1
        return

    stats["type_counter"][type(value).__name__] += 1

    if not isinstance(value, dict):
        return

    stats["dict_count"] += 1

    for key in value.keys():
        stats["top_key_counter"][key] += 1

    msg = value.get("msg")
    if msg not in (None, ""):
        stats["msg_counter"][str(msg)] += 1

    kaisai_kbn = value.get("kaisaiKbn")
    if kaisai_kbn not in (None, ""):
        stats["kaisai_kbn_counter"][str(kaisai_kbn)] += 1

    grade = value.get("gaiTeiGrade")
    if grade not in (None, ""):
        stats["grade_counter"][str(grade)] += 1

    venue_code = value.get("bKeirinjyoCd")
    if venue_code not in (None, ""):
        stats["venue_code_counter"][str(venue_code)] += 1

    venue_name = value.get("kerinjyoName")
    if venue_name not in (None, ""):
        stats["venue_name_counter"][str(venue_name)] += 1

    kaisai_first = value.get("kaisaiFirst")
    if kaisai_first not in (None, ""):
        stats["kaisai_first_counter"][str(kaisai_first)] += 1

    result_list = value.get("resultInfoSubData")

    if isinstance(result_list, list):
        stats["result_count_distribution"][len(result_list)] += 1

        finish_sequence = []
        back_sequence = []

        for result in result_list:
            if not isinstance(result, dict):
                stats["result_item_type_counter"][type(result).__name__] += 1
                continue

            stats["result_item_type_counter"]["dict"] += 1

            for key in result.keys():
                stats["result_item_key_counter"][key] += 1

            finish = result.get("imgTyakuiName")
            back = result.get("backTori")

            finish_sequence.append(finish)
            back_sequence.append(back)

            if finish not in (None, ""):
                stats["finish_value_counter"][str(finish)] += 1

            if back not in (None, ""):
                stats["back_value_counter"][str(back)] += 1

            image_path = result.get("imgTyakuiPath")
            if image_path not in (None, ""):
                stats["finish_image_counter"][str(image_path)] += 1

        stats["finish_sequence_counter"][tuple(
            "" if x is None else str(x)
            for x in finish_sequence
        )] += 1

        stats["back_sequence_counter"][tuple(
            "" if x is None else str(x)
            for x in back_sequence
        )] += 1

    else:
        stats["result_count_distribution"]["NOT_LIST"] += 1


def make_stats():
    return {
        "type_counter": Counter(),
        "dict_count": 0,
        "top_key_counter": Counter(),
        "msg_counter": Counter(),
        "kaisai_kbn_counter": Counter(),
        "grade_counter": Counter(),
        "venue_code_counter": Counter(),
        "venue_name_counter": Counter(),
        "kaisai_first_counter": Counter(),
        "result_count_distribution": Counter(),
        "result_item_type_counter": Counter(),
        "result_item_key_counter": Counter(),
        "finish_value_counter": Counter(),
        "back_value_counter": Counter(),
        "finish_image_counter": Counter(),
        "finish_sequence_counter": Counter(),
        "back_sequence_counter": Counter(),
    }


def counter_to_json(counter):
    result = {}

    for key, value in counter.items():
        if isinstance(key, tuple):
            key = "|".join(key)
        else:
            key = str(key)

        result[key] = value

    return result


def stats_to_json(stats):
    result = {}

    for key, value in stats.items():
        if isinstance(value, Counter):
            result[key] = counter_to_json(value)
        else:
            result[key] = value

    return result


def print_counter(title, counter, limit=None):
    print(f"\n=== {title} ===")

    items = counter.most_common(limit)

    if not items:
        print("  なし")
        return

    for key, count in items:
        print(f"  {key}: {count}")


def main():
    print("=== 216 recent result DICT 完全構造解析 ===")

    with INPUT_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    races = find_race_records(data)

    print(f"検出レース数: {len(races)}")

    kon_stats = make_stats()
    tyo4_stats = make_stats()

    total_players = 0
    samples = []
    abnormal = []

    player_detail_rows = []

    for race_index, race in enumerate(races, start=1):
        record = race["record"]
        jsj006 = race["jsj006"]

        race_key = get_race_key(
            record,
            f"race_{race_index}"
        )

        players = jsj006.get("sensyuTypeInfo")

        if not isinstance(players, list):
            abnormal.append({
                "race_key": race_key,
                "reason": "sensyuTypeInfo_not_list",
            })
            continue

        for player in players:
            if not isinstance(player, dict):
                continue

            total_players += 1

            kon = player.get("konResultInfoSubData")
            tyo4 = player.get("tyo4InfoSubData")

            analyze_dict(
                "konResultInfoSubData",
                kon,
                kon_stats
            )

            analyze_dict(
                "tyo4InfoSubData",
                tyo4,
                tyo4_stats
            )

            def extract_detail(value):
                if not isinstance(value, dict):
                    return {
                        "type": type(value).__name__,
                        "msg": None,
                        "kaisaiKbn": None,
                        "bKeirinjyoCd": None,
                        "kerinjyoName": None,
                        "kaisaiFirst": None,
                        "gaiTeiGrade": None,
                        "result_count": None,
                        "finishes": [],
                        "backs": [],
                    }

                result_list = value.get("resultInfoSubData")

                finishes = []
                backs = []

                if isinstance(result_list, list):
                    for result in result_list:
                        if isinstance(result, dict):
                            finishes.append(
                                result.get("imgTyakuiName")
                            )
                            backs.append(
                                result.get("backTori")
                            )

                return {
                    "type": "dict",
                    "msg": value.get("msg"),
                    "kaisaiKbn": value.get("kaisaiKbn"),
                    "bKeirinjyoCd": value.get("bKeirinjyoCd"),
                    "kerinjyoName": value.get("kerinjyoName"),
                    "kaisaiFirst": value.get("kaisaiFirst"),
                    "gaiTeiGrade": value.get("gaiTeiGrade"),
                    "result_count": (
                        len(result_list)
                        if isinstance(result_list, list)
                        else None
                    ),
                    "finishes": finishes,
                    "backs": backs,
                }

            detail = {
                "race_key": race_key,
                "car_no": player.get("syaban"),
                "player_id": player.get("sensyuRegistNo"),
                "player_name": player.get("sensyuName"),
                "kon": extract_detail(kon),
                "tyo4": extract_detail(tyo4),
            }

            player_detail_rows.append(detail)

            if len(samples) < 20:
                samples.append(detail)

    print("\n" + "=" * 80)
    print("=== 216 結果 ===")
    print(f"レース数: {len(races)}")
    print(f"解析選手数: {total_players}")
    print(f"問題件数: {len(abnormal)}")

    for label, stats in [
        ("konResultInfoSubData", kon_stats),
        ("tyo4InfoSubData", tyo4_stats),
    ]:
        print("\n" + "=" * 80)
        print(f"=== {label} ===")

        print_counter(
            "TYPE分布",
            stats["type_counter"]
        )

        print(f"\nDICT件数: {stats['dict_count']}")

        print_counter(
            "TOPキー出現回数",
            stats["top_key_counter"]
        )

        print_counter(
            "kaisaiKbn分布",
            stats["kaisai_kbn_counter"]
        )

        print_counter(
            "resultInfoSubData 件数分布",
            stats["result_count_distribution"]
        )

        print_counter(
            "resultInfoSubData 内部キー",
            stats["result_item_key_counter"]
        )

        print_counter(
            "着順値分布",
            stats["finish_value_counter"]
        )

        print_counter(
            "backTori分布",
            stats["back_value_counter"]
        )

        print_counter(
            "msg分布",
            stats["msg_counter"]
        )

        print_counter(
            "グレード分布",
            stats["grade_counter"]
        )

        print_counter(
            "競輪場コード分布",
            stats["venue_code_counter"]
        )

        print_counter(
            "競輪場略称分布",
            stats["venue_name_counter"]
        )

        print_counter(
            "開催初日 上位20",
            stats["kaisai_first_counter"],
            limit=20
        )

        print_counter(
            "着順シーケンス 上位30",
            stats["finish_sequence_counter"],
            limit=30
        )

        print_counter(
            "backシーケンス 上位20",
            stats["back_sequence_counter"],
            limit=20
        )

    print("\n" + "=" * 80)
    print("=== 選手サンプル 先頭20人 ===")

    for i, sample in enumerate(samples, start=1):
        print("\n" + "-" * 70)
        print(
            f"[{i}] "
            f"{sample['race_key']} / "
            f"{sample['car_no']}番車 / "
            f"{sample['player_name']}"
        )

        print("  kon:")
        print(
            json.dumps(
                sample["kon"],
                ensure_ascii=False,
                indent=4
            )
        )

        print("  tyo4:")
        print(
            json.dumps(
                sample["tyo4"],
                ensure_ascii=False,
                indent=4
            )
        )

    output = {
        "race_count": len(races),
        "player_count": total_players,
        "abnormal_count": len(abnormal),
        "konResultInfoSubData": stats_to_json(kon_stats),
        "tyo4InfoSubData": stats_to_json(tyo4_stats),
        "player_details": player_detail_rows,
        "abnormal": abnormal,
    }

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(
            output,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(
        f"\n保存完了: {OUTPUT_PATH}"
    )
    print("=== 216 完了 ===")


if __name__ == "__main__":
    main()