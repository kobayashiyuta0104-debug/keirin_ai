import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

RESULT_FILE = BASE_DIR / "054_all_results.json"
RACE_FILE = BASE_DIR / "055_all_races.json"

OUTPUT_FILE = BASE_DIR / "139_official_race_match.json"


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


def build_result_races(data):

    races = []

    if not isinstance(data, list):
        return races

    for index, item in enumerate(data):

        if not isinstance(item, dict):
            continue

        race = item.get("race")

        if not isinstance(race, dict):
            continue

        if "selKaisai" not in race:
            continue

        if "joName" not in race:
            continue

        if "selRaceNo" not in race:
            continue

        races.append({
            "date": normalize_date(
                race.get("selKaisai")
            ),
            "venue": normalize_venue(
                race.get("joName")
            ),
            "race_no": normalize_race_no(
                race.get("selRaceNo")
            ),
            "block_path": f"ROOT[{index}]",
            "date_path": (
                f"ROOT[{index}].race.selKaisai"
            ),
            "venue_path": (
                f"ROOT[{index}].race.joName"
            ),
            "race_path": (
                f"ROOT[{index}].race.selRaceNo"
            )
        })

    return races


def build_official_races(data):

    races = []

    if not isinstance(data, list):
        return races

    for index, item in enumerate(data):

        if not isinstance(item, dict):
            continue

        jsj001 = item.get("jsj001")

        if not isinstance(jsj001, dict):
            continue

        c0201 = jsj001.get("C0201data")

        if not isinstance(c0201, dict):
            continue

        if "selKaisai" not in c0201:
            continue

        if "joName" not in c0201:
            continue

        if "selRaceNo" not in c0201:
            continue

        date = normalize_date(
            c0201.get("selKaisai")
        )

        venue = normalize_venue(
            c0201.get("joName")
        )

        race_no = normalize_race_no(
            c0201.get("selRaceNo")
        )

        races.append({
            "date": date,
            "venue": venue,
            "race_no": race_no,
            "block_path": f"ROOT[{index}]",
            "official_path": (
                f"ROOT[{index}]."
                f"jsj001.C0201data"
            ),
            "date_path": (
                f"ROOT[{index}]."
                f"jsj001.C0201data.selKaisai"
            ),
            "venue_path": (
                f"ROOT[{index}]."
                f"jsj001.C0201data.joName"
            ),
            "race_path": (
                f"ROOT[{index}]."
                f"jsj001.C0201data.selRaceNo"
            )
        })

    return races


def main():

    print("=" * 70)
    print("🔥 139 正式3点照合テスト")
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

    official_races = build_official_races(
        race_data
    )

    print()
    print(
        f"A 確定結果レース数: "
        f"{len(result_races)}"
    )

    print(
        f"B 正式レース数: "
        f"{len(official_races)}"
    )

    print()
    print("=" * 70)
    print("🔥 B 正式レース一覧")
    print("=" * 70)

    for index, race in enumerate(
        official_races,
        start=1
    ):

        print()
        print("-" * 60)

        print(
            f"🔥 OFFICIAL RACE #{index}"
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
            f"OFFICIAL PATH: "
            f"{race['official_path']}"
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
            f"RACE PATH: "
            f"{race['race_path']}"
        )

    print()
    print("=" * 70)
    print("🔥 正式3点照合開始")
    print("=" * 70)

    matches = []

    for result_race in result_races:

        for official_race in official_races:

            if (
                result_race["date"]
                != official_race["date"]
            ):
                continue

            if (
                result_race["venue"]
                != official_race["venue"]
            ):
                continue

            if (
                result_race["race_no"]
                != official_race["race_no"]
            ):
                continue

            matches.append({
                "result": result_race,
                "race": official_race
            })

    print()
    print(
        f"🔥 正式3点完全一致数: "
        f"{len(matches)}"
    )

    print()
    print("=" * 70)
    print("🔥 正式一致詳細")
    print("=" * 70)

    for index, match in enumerate(
        matches,
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
        print("A 確定結果")

        print(
            f"BLOCK: "
            f"{result_race['block_path']}"
        )

        print(
            f"DATE PATH: "
            f"{result_race['date_path']}"
        )

        print(
            f"VENUE PATH: "
            f"{result_race['venue_path']}"
        )

        print(
            f"RACE PATH: "
            f"{result_race['race_path']}"
        )

        print()
        print("B レース前情報")

        print(
            f"BLOCK: "
            f"{race['block_path']}"
        )

        print(
            f"OFFICIAL PATH: "
            f"{race['official_path']}"
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
            f"RACE PATH: "
            f"{race['race_path']}"
        )

    output_data = {
        "result_races": result_races,
        "official_races": official_races,
        "matches": matches
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            output_data,
            f,
            ensure_ascii=False,
            indent=2
        )

    print()
    print("=" * 70)
    print("🔥 139テスト終了")
    print("=" * 70)

    print(
        f"A 確定結果レース数: "
        f"{len(result_races)}"
    )

    print(
        f"B 正式レース数: "
        f"{len(official_races)}"
    )

    print(
        f"正式3点完全一致数: "
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