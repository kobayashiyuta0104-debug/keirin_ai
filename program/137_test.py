import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

RESULT_FILE = BASE_DIR / "054_all_results.json"
RACE_FILE = BASE_DIR / "055_all_races.json"

OUTPUT_FILE = BASE_DIR / "137_race_triple_match.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_text(value):
    if value is None:
        return ""

    return str(value).strip()


def normalize_date(value):
    value = normalize_text(value)

    value = value.replace("/", "")
    value = value.replace("-", "")
    value = value.replace(".", "")

    return value


def normalize_venue(value):
    value = normalize_text(value)

    value = value.replace("競輪場", "")
    value = value.replace(" ", "")
    value = value.replace("　", "")

    return value


def normalize_race_no(value):
    value = normalize_text(value).upper()

    value = value.replace("Ｒ", "R")
    value = value.replace("R", "")
    value = value.replace(" ", "")
    value = value.replace("　", "")

    try:
        return str(int(value))
    except:
        return value


def walk_json(obj, path="ROOT"):
    items = []

    if isinstance(obj, dict):

        for key, value in obj.items():

            current_path = f"{path}.{key}"

            items.append({
                "path": current_path,
                "key": key,
                "value": value
            })

            items.extend(
                walk_json(
                    value,
                    current_path
                )
            )

    elif isinstance(obj, list):

        for index, value in enumerate(obj):

            current_path = f"{path}[{index}]"

            items.extend(
                walk_json(
                    value,
                    current_path
                )
            )

    return items


def find_values(items, key_name):

    results = []

    for item in items:

        if item["key"] == key_name:

            value = item["value"]

            if isinstance(
                value,
                (
                    str,
                    int,
                    float
                )
            ):

                results.append(item)

    return results


def get_parent_path(path, levels=1):

    result = path

    for _ in range(levels):

        if "." in result:
            result = result.rsplit(".", 1)[0]

    return result


def build_result_races(data):

    items = walk_json(data)

    dates = find_values(
        items,
        "selKaisai"
    )

    venues = find_values(
        items,
        "joName"
    )

    race_nos = find_values(
        items,
        "selRaceNo"
    )

    races = []

    for date_item in dates:

        date_parent = get_parent_path(
            date_item["path"],
            2
        )

        for venue_item in venues:

            venue_parent = get_parent_path(
                venue_item["path"],
                2
            )

            if venue_parent != date_parent:
                continue

            for race_item in race_nos:

                race_parent = get_parent_path(
                    race_item["path"],
                    2
                )

                if race_parent != date_parent:
                    continue

                races.append({
                    "date": normalize_date(
                        date_item["value"]
                    ),
                    "venue": normalize_venue(
                        venue_item["value"]
                    ),
                    "race_no": normalize_race_no(
                        race_item["value"]
                    ),
                    "date_path": date_item["path"],
                    "venue_path": venue_item["path"],
                    "race_path": race_item["path"]
                })

    return races


def find_race_no_candidates(items):

    candidates = []

    race_keywords = [
        "raceNo",
        "race_no",
        "raceNum",
        "raceNumber",
        "selRaceNo",
        "race"
    ]

    for item in items:

        key = str(
            item["key"]
        )

        value = item["value"]

        if not isinstance(
            value,
            (
                str,
                int
            )
        ):
            continue

        key_lower = key.lower()

        if not any(
            keyword.lower() in key_lower
            for keyword in race_keywords
        ):
            continue

        normalized = normalize_race_no(
            value
        )

        if normalized.isdigit():

            number = int(normalized)

            if 1 <= number <= 12:

                candidates.append(item)

    return candidates


def build_race_info(data):

    items = walk_json(data)

    dates = find_values(
        items,
        "selKaisai"
    )

    venues = find_values(
        items,
        "joName"
    )

    race_nos = find_race_no_candidates(
        items
    )

    races = []

    for date_item in dates:

        date_value = normalize_date(
            date_item["value"]
        )

        for venue_item in venues:

            venue_value = normalize_venue(
                venue_item["value"]
            )

            for race_item in race_nos:

                race_value = normalize_race_no(
                    race_item["value"]
                )

                races.append({
                    "date": date_value,
                    "venue": venue_value,
                    "race_no": race_value,
                    "date_path": date_item["path"],
                    "venue_path": venue_item["path"],
                    "race_path": race_item["path"],
                    "race_key": race_item["key"]
                })

    return races


def main():

    print(
        "=" * 70
    )

    print(
        "🔥 137 開催日＋競輪場＋レース番号 3点照合テスト"
    )

    print(
        "=" * 70
    )

    result_data = load_json(
        RESULT_FILE
    )

    race_data = load_json(
        RACE_FILE
    )

    print()
    print(
        "🔥 JSON読込完了"
    )

    result_races = build_result_races(
        result_data
    )

    race_infos = build_race_info(
        race_data
    )

    print()
    print(
        f"A 確定結果レース候補数: {len(result_races)}"
    )

    print(
        f"B レース情報候補数: {len(race_infos)}"
    )

    print()
    print(
        "=" * 70
    )

    print(
        "🔥 3点照合開始"
    )

    print(
        "=" * 70
    )

    matches = []

    for result_race in result_races:

        for race_info in race_infos:

            if (
                result_race["date"]
                != race_info["date"]
            ):
                continue

            if (
                result_race["venue"]
                != race_info["venue"]
            ):
                continue

            if (
                result_race["race_no"]
                != race_info["race_no"]
            ):
                continue

            matches.append({
                "result": result_race,
                "race": race_info
            })

    print()
    print(
        f"🔥 3点完全一致数: {len(matches)}"
    )

    print()
    print(
        "=" * 70
    )

    print(
        "🔥 TOP30 完全一致"
    )

    print(
        "=" * 70
    )

    for index, match in enumerate(
        matches[:30],
        start=1
    ):

        result_race = match["result"]
        race_info = match["race"]

        print()
        print(
            "-" * 60
        )

        print(
            f"🔥 MATCH #{index}"
        )

        print(
            f"開催日: {result_race['date']}"
        )

        print(
            f"競輪場: {result_race['venue']}"
        )

        print(
            f"レース番号: {result_race['race_no']}"
        )

        print()
        print(
            "A 確定結果"
        )

        print(
            f"DATE PATH: {result_race['date_path']}"
        )

        print(
            f"VENUE PATH: {result_race['venue_path']}"
        )

        print(
            f"RACE PATH: {result_race['race_path']}"
        )

        print()
        print(
            "B レース情報"
        )

        print(
            f"DATE PATH: {race_info['date_path']}"
        )

        print(
            f"VENUE PATH: {race_info['venue_path']}"
        )

        print(
            f"RACE KEY: {race_info['race_key']}"
        )

        print(
            f"RACE PATH: {race_info['race_path']}"
        )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            matches,
            f,
            ensure_ascii=False,
            indent=2
        )

    print()
    print(
        "=" * 70
    )

    print(
        "🔥 137テスト終了"
    )

    print(
        "=" * 70
    )

    print(
        f"A 確定結果候補数: {len(result_races)}"
    )

    print(
        f"B レース情報候補数: {len(race_infos)}"
    )

    print(
        f"3点完全一致数: {len(matches)}"
    )

    print()
    print(
        f"保存先: {OUTPUT_FILE.name}"
    )

    print()
    print(
        "=" * 70
    )


if __name__ == "__main__":
    main()