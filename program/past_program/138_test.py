import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

RESULT_FILE = BASE_DIR / "054_all_results.json"
RACE_FILE = BASE_DIR / "055_all_races.json"

OUTPUT_FILE = BASE_DIR / "138_structural_race_match.json"


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


def is_scalar(value):
    return isinstance(
        value,
        (
            str,
            int,
            float
        )
    )


def find_first_key(obj, key_name, path="ROOT"):
    if isinstance(obj, dict):

        for key, value in obj.items():

            current_path = f"{path}.{key}"

            if (
                key == key_name
                and is_scalar(value)
            ):
                return {
                    "key": key,
                    "value": value,
                    "path": current_path
                }

        for key, value in obj.items():

            current_path = f"{path}.{key}"

            result = find_first_key(
                value,
                key_name,
                current_path
            )

            if result is not None:
                return result

    elif isinstance(obj, list):

        for index, value in enumerate(obj):

            current_path = f"{path}[{index}]"

            result = find_first_key(
                value,
                key_name,
                current_path
            )

            if result is not None:
                return result

    return None


def collect_dict_blocks(obj, path="ROOT", results=None):
    if results is None:
        results = []

    if isinstance(obj, dict):

        results.append({
            "path": path,
            "data": obj
        })

        for key, value in obj.items():

            current_path = f"{path}.{key}"

            collect_dict_blocks(
                value,
                current_path,
                results
            )

    elif isinstance(obj, list):

        for index, value in enumerate(obj):

            current_path = f"{path}[{index}]"

            collect_dict_blocks(
                value,
                current_path,
                results
            )

    return results


def direct_scalar_keys(obj):
    result = []

    if not isinstance(obj, dict):
        return result

    for key, value in obj.items():

        if is_scalar(value):

            result.append({
                "key": key,
                "value": value
            })

    return result


def find_race_number_in_block(block):
    priority_keys = [
        "race_no",
        "selRaceNo",
        "raceNo",
        "race_num",
        "raceNum",
        "raceNumber"
    ]

    scalar_items = direct_scalar_keys(block)

    for target_key in priority_keys:

        for item in scalar_items:

            if item["key"] != target_key:
                continue

            race_no = normalize_race_no(
                item["value"]
            )

            if race_no.isdigit():

                number = int(race_no)

                if 1 <= number <= 12:

                    return {
                        "key": item["key"],
                        "value": race_no
                    }

    return None


def build_result_races(data):
    blocks = collect_dict_blocks(data)

    races = []

    for block_item in blocks:

        block = block_item["data"]
        block_path = block_item["path"]

        if "race" not in block:
            continue

        race_block = block["race"]

        if not isinstance(race_block, dict):
            continue

        if "selKaisai" not in race_block:
            continue

        if "joName" not in race_block:
            continue

        if "selRaceNo" not in race_block:
            continue

        date = normalize_date(
            race_block["selKaisai"]
        )

        venue = normalize_venue(
            race_block["joName"]
        )

        race_no = normalize_race_no(
            race_block["selRaceNo"]
        )

        races.append({
            "date": date,
            "venue": venue,
            "race_no": race_no,
            "block_path": block_path,
            "date_path": f"{block_path}.race.selKaisai",
            "venue_path": f"{block_path}.race.joName",
            "race_path": f"{block_path}.race.selRaceNo"
        })

    return races


def build_structural_races(data):
    blocks = collect_dict_blocks(data)

    race_blocks = []

    for block_item in blocks:

        block_path = block_item["path"]
        block = block_item["data"]

        race_number = find_race_number_in_block(
            block
        )

        if race_number is None:
            continue

        date_item = find_first_key(
            block,
            "selKaisai",
            block_path
        )

        venue_item = find_first_key(
            block,
            "joName",
            block_path
        )

        if date_item is None:
            continue

        if venue_item is None:
            continue

        date = normalize_date(
            date_item["value"]
        )

        venue = normalize_venue(
            venue_item["value"]
        )

        race_no = normalize_race_no(
            race_number["value"]
        )

        race_blocks.append({
            "date": date,
            "venue": venue,
            "race_no": race_no,
            "block_path": block_path,
            "date_path": date_item["path"],
            "venue_path": venue_item["path"],
            "race_key": race_number["key"],
            "race_path": (
                f"{block_path}."
                f"{race_number['key']}"
            )
        })

    unique = {}

    for race in race_blocks:

        key = (
            race["date"],
            race["venue"],
            race["race_no"],
            race["block_path"]
        )

        unique[key] = race

    return list(
        unique.values()
    )


def main():

    print("=" * 70)
    print("🔥 138 B側構造ブロック照合テスト")
    print("=" * 70)

    result_data = load_json(
        RESULT_FILE
    )

    race_data = load_json(
        RACE_FILE
    )

    print()
    print("🔥 JSON読込完了")

    result_races = build_result_races(
        result_data
    )

    structural_races = build_structural_races(
        race_data
    )

    print()
    print(
        f"A 確定結果レース数: "
        f"{len(result_races)}"
    )

    print(
        f"B 構造レース候補数: "
        f"{len(structural_races)}"
    )

    print()
    print("=" * 70)
    print("🔥 B構造レース TOP50")
    print("=" * 70)

    for index, race in enumerate(
        structural_races[:50],
        start=1
    ):

        print()
        print("-" * 60)

        print(
            f"🔥 B RACE #{index}"
        )

        print(
            f"開催日: {race['date']}"
        )

        print(
            f"競輪場: {race['venue']}"
        )

        print(
            f"レース番号: {race['race_no']}"
        )

        print(
            f"BLOCK PATH: "
            f"{race['block_path']}"
        )

        print(
            f"DATE PATH: "
            f"{race['date_path']}"
        )

        print(
            f"VENUE PATH: "
            f"{race['venue_path']}"
        )

        print(
            f"RACE KEY: "
            f"{race['race_key']}"
        )

        print(
            f"RACE PATH: "
            f"{race['race_path']}"
        )

    print()
    print("=" * 70)
    print("🔥 3点照合")
    print("=" * 70)

    matches = []

    for result_race in result_races:

        for race in structural_races:

            if (
                result_race["date"]
                != race["date"]
            ):
                continue

            if (
                result_race["venue"]
                != race["venue"]
            ):
                continue

            if (
                result_race["race_no"]
                != race["race_no"]
            ):
                continue

            matches.append({
                "result": result_race,
                "race": race
            })

    print()
    print(
        f"🔥 3点完全一致数: "
        f"{len(matches)}"
    )

    print()
    print("=" * 70)
    print("🔥 完全一致詳細")
    print("=" * 70)

    for index, match in enumerate(
        matches[:50],
        start=1
    ):

        result_race = match["result"]
        race = match["race"]

        print()
        print("-" * 60)

        print(
            f"🔥 MATCH #{index}"
        )

        print(
            f"開催日: "
            f"{result_race['date']}"
        )

        print(
            f"競輪場: "
            f"{result_race['venue']}"
        )

        print(
            f"レース番号: "
            f"{result_race['race_no']}"
        )

        print()
        print(
            f"A BLOCK: "
            f"{result_race['block_path']}"
        )

        print(
            f"B BLOCK: "
            f"{race['block_path']}"
        )

        print(
            f"B RACE KEY: "
            f"{race['race_key']}"
        )

        print(
            f"B RACE PATH: "
            f"{race['race_path']}"
        )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            {
                "result_races": result_races,
                "structural_races": structural_races,
                "matches": matches
            },
            f,
            ensure_ascii=False,
            indent=2
        )

    print()
    print("=" * 70)
    print("🔥 138テスト終了")
    print("=" * 70)

    print(
        f"A 確定結果レース数: "
        f"{len(result_races)}"
    )

    print(
        f"B 構造レース候補数: "
        f"{len(structural_races)}"
    )

    print(
        f"3点完全一致数: "
        f"{len(matches)}"
    )

    print()
    print(
        f"保存先: "
        f"{OUTPUT_FILE.name}"
    )

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()