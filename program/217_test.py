import json
from pathlib import Path
from collections import Counter, defaultdict


RAW_PATH = Path(
    r"C:\競輪AI\213_20260706_all_race_raw_capture.json"
)

OLD_FEATURE_PATH = Path(
    r"C:\競輪AI\163_dated_ai_pre_race_features.json"
)

OUTPUT_PATH = Path(
    r"C:\競輪AI\217_recent_feature_mapping_analysis.json"
)


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_races_with_jsj006(obj):
    found = []

    def walk(x, path="$"):
        if isinstance(x, dict):

            jsj006 = None

            for key, value in x.items():
                if str(key).upper() == "JSJ006":
                    jsj006 = value

            if isinstance(jsj006, dict):
                found.append({
                    "path": path,
                    "record": x,
                    "jsj006": jsj006,
                })

            for key, value in x.items():
                walk(value, f"{path}.{key}")

        elif isinstance(x, list):
            for i, value in enumerate(x):
                walk(value, f"{path}[{i}]")

    walk(obj)

    unique = []
    seen = set()

    for item in found:
        marker = id(item["record"])

        if marker not in seen:
            seen.add(marker)
            unique.append(item)

    return unique


def normalize_text(value):
    if value is None:
        return None

    value = str(value).strip()

    if value == "":
        return None

    return value


def get_race_key(record):
    for key in [
        "race_key",
        "raceKey",
        "key",
    ]:
        value = record.get(key)

        if value:
            return str(value)

    return None


def get_feature_records(obj):
    records = []

    def walk(x, path="$"):
        if isinstance(x, dict):

            has_recent = any(
                str(key).endswith("recent_finish_1")
                for key in x.keys()
            )

            if has_recent:
                records.append({
                    "path": path,
                    "record": x,
                })

            for key, value in x.items():
                walk(value, f"{path}.{key}")

        elif isinstance(x, list):
            for i, value in enumerate(x):
                walk(value, f"{path}[{i}]")

    walk(obj)

    return records


def build_raw_player_rows(raw_data):
    races = find_races_with_jsj006(raw_data)

    rows = []

    for race in races:

        record = race["record"]
        jsj006 = race["jsj006"]

        race_key = get_race_key(record)

        players = jsj006.get("sensyuTypeInfo")

        if not isinstance(players, list):
            continue

        for player in players:

            if not isinstance(player, dict):
                continue

            tyo4 = player.get("tyo4InfoSubData")

            finishes = []
            venue_code = None
            grade = None
            msg = None

            if isinstance(tyo4, dict):

                venue_code = normalize_text(
                    tyo4.get("bKeirinjyoCd")
                )

                grade = normalize_text(
                    tyo4.get("gaiTeiGrade")
                )

                msg = normalize_text(
                    tyo4.get("msg")
                )

                result_list = tyo4.get(
                    "resultInfoSubData"
                )

                if isinstance(result_list, list):

                    for result in result_list:

                        if isinstance(result, dict):

                            finishes.append(
                                normalize_text(
                                    result.get(
                                        "imgTyakuiName"
                                    )
                                )
                            )

            rows.append({
                "race_key": race_key,
                "car_no": normalize_text(
                    player.get("syaban")
                ),
                "player_id": normalize_text(
                    player.get("sensyuRegistNo")
                ),
                "player_name": normalize_text(
                    player.get("sensyuName")
                ),
                "raw_finishes": finishes,
                "raw_finish_1": (
                    finishes[0]
                    if len(finishes) >= 1
                    else None
                ),
                "raw_finish_2": (
                    finishes[1]
                    if len(finishes) >= 2
                    else None
                ),
                "raw_finish_3": (
                    finishes[2]
                    if len(finishes) >= 3
                    else None
                ),
                "raw_venue_code": venue_code,
                "raw_grade": grade,
                "raw_msg": msg,
            })

    return rows


def flatten_feature_records(feature_data):
    candidates = get_feature_records(feature_data)

    rows = []

    for candidate in candidates:

        record = candidate["record"]

        race_key = get_race_key(record)

        for player_no in range(1, 10):

            prefix = f"p{player_no}_"

            id_key = prefix + "player_id"
            name_key = prefix + "player_name"

            player_id = normalize_text(
                record.get(id_key)
            )

            player_name = normalize_text(
                record.get(name_key)
            )

            if (
                player_id is None
                and player_name is None
            ):
                continue

            rows.append({
                "race_key": race_key,
                "player_no": player_no,
                "player_id": player_id,
                "player_name": player_name,
                "feature_finish_1": record.get(
                    prefix + "recent_finish_1"
                ),
                "feature_finish_2": record.get(
                    prefix + "recent_finish_2"
                ),
                "feature_finish_3": record.get(
                    prefix + "recent_finish_3"
                ),
                "feature_venue_code": record.get(
                    prefix + "recent_venue_code"
                ),
                "feature_grade": record.get(
                    prefix + "recent_grade"
                ),
            })

    return rows


def build_index(rows):
    by_id = defaultdict(list)
    by_name = defaultdict(list)

    for row in rows:

        if row["player_id"]:
            by_id[row["player_id"]].append(row)

        if row["player_name"]:
            by_name[row["player_name"]].append(row)

    return by_id, by_name


def main():

    print(
        "=== 217 recent特徴量 旧特徴量との実値突合テスト ==="
    )

    raw_data = load_json(RAW_PATH)
    feature_data = load_json(OLD_FEATURE_PATH)

    raw_rows = build_raw_player_rows(raw_data)

    feature_rows = flatten_feature_records(
        feature_data
    )

    print(
        f"JSJ006生データ選手行数: {len(raw_rows)}"
    )

    print(
        f"旧特徴量選手行数: {len(feature_rows)}"
    )

    raw_by_id, raw_by_name = build_index(
        raw_rows
    )

    matched = []

    unmatched = []

    mapping_counter = {
        "finish_1": Counter(),
        "finish_2": Counter(),
        "finish_3": Counter(),
        "venue_code": Counter(),
        "grade": Counter(),
    }

    for feature in feature_rows:

        candidates = []

        if feature["player_id"]:

            candidates = raw_by_id.get(
                feature["player_id"],
                []
            )

        if (
            not candidates
            and feature["player_name"]
        ):

            candidates = raw_by_name.get(
                feature["player_name"],
                []
            )

        if not candidates:

            unmatched.append(feature)
            continue

        raw = candidates[0]

        row = {
            "feature": feature,
            "raw": raw,
        }

        matched.append(row)

        pairs = [
            (
                "finish_1",
                raw["raw_finish_1"],
                feature["feature_finish_1"],
            ),
            (
                "finish_2",
                raw["raw_finish_2"],
                feature["feature_finish_2"],
            ),
            (
                "finish_3",
                raw["raw_finish_3"],
                feature["feature_finish_3"],
            ),
            (
                "venue_code",
                raw["raw_venue_code"],
                feature["feature_venue_code"],
            ),
            (
                "grade",
                raw["raw_grade"],
                feature["feature_grade"],
            ),
        ]

        for field, raw_value, feature_value in pairs:

            key = (
                str(raw_value),
                str(feature_value),
            )

            mapping_counter[field][key] += 1

    print("\n=== 217 結果 ===")

    print(
        f"突合成功選手数: {len(matched)}"
    )

    print(
        f"未突合選手数: {len(unmatched)}"
    )

    for field, counter in mapping_counter.items():

        print("\n" + "=" * 80)

        print(
            f"=== {field} RAW -> OLD FEATURE 対応 ==="
        )

        for (
            raw_value,
            feature_value
        ), count in counter.most_common(100):

            print(
                f"  RAW={raw_value!r}"
                f" -> FEATURE={feature_value!r}"
                f": {count}"
            )

    print("\n" + "=" * 80)

    print("=== 突合サンプル 先頭50件 ===")

    for i, item in enumerate(
        matched[:50],
        start=1
    ):

        raw = item["raw"]
        feature = item["feature"]

        print("\n" + "-" * 70)

        print(
            f"[{i}] "
            f"{raw['player_name']} / "
            f"ID={raw['player_id']}"
        )

        print(
            "  RAW finishes:",
            raw["raw_finishes"]
        )

        print(
            "  FEATURE finishes:",
            [
                feature["feature_finish_1"],
                feature["feature_finish_2"],
                feature["feature_finish_3"],
            ]
        )

        print(
            "  RAW venue/grade:",
            raw["raw_venue_code"],
            raw["raw_grade"]
        )

        print(
            "  FEATURE venue/grade:",
            feature["feature_venue_code"],
            feature["feature_grade"]
        )

    output = {
        "raw_player_count": len(raw_rows),
        "feature_player_count": len(feature_rows),
        "matched_count": len(matched),
        "unmatched_count": len(unmatched),
        "mapping": {
            field: {
                f"{raw} -> {feature}": count
                for (
                    raw,
                    feature
                ), count in counter.items()
            }
            for field, counter
            in mapping_counter.items()
        },
        "matched": matched,
        "unmatched": unmatched,
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

    print("=== 217 完了 ===")


if __name__ == "__main__":
    main()