import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
RESULT_DIR = BASE_DIR

MATCH_FILE = BASE_DIR / "139_official_race_match.json"
OUTPUT_FILE = BASE_DIR / "140_joined_race_data.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_by_path(data, path):
    """
    ROOT[0].race.selKaisai
    ROOT[4].jsj001.C0201data.selKaisai
    のようなPATHからVALUEを取得
    """

    if not path:
        return None

    path = path.replace("ROOT", "")

    current = data

    parts = []
    buf = ""
    i = 0

    while i < len(path):

        if path[i] == ".":
            if buf:
                parts.append(("key", buf))
                buf = ""
            i += 1
            continue

        if path[i] == "[":
            if buf:
                parts.append(("key", buf))
                buf = ""

            end = path.find("]", i)

            if end == -1:
                return None

            index_text = path[i + 1:end]

            try:
                index = int(index_text)
            except ValueError:
                return None

            parts.append(("index", index))

            i = end + 1
            continue

        buf += path[i]
        i += 1

    if buf:
        parts.append(("key", buf))

    try:

        for part_type, value in parts:

            if part_type == "key":
                current = current[value]

            elif part_type == "index":
                current = current[value]

        return current

    except (KeyError, IndexError, TypeError):
        return None


def get_block_path(path):
    """
    ROOT[0].race.selKaisai
    ↓
    ROOT[0]

    ROOT[4].jsj001.C0201data.selKaisai
    ↓
    ROOT[4]
    """

    if not path:
        return None

    if not path.startswith("ROOT["):
        return None

    end = path.find("]")

    if end == -1:
        return None

    return path[:end + 1]


def main():

    print("=" * 70)
    print("🔥 140 確定結果＋レース前情報 結合テスト")
    print("=" * 70)

    if not MATCH_FILE.exists():
        print("❌ 139_official_race_match.json がありません")
        return

    match_data = load_json(MATCH_FILE)

    print(f"139照合データ件数: {len(match_data)}")

    joined = []

    for no, match in enumerate(match_data, start=1):

        print()
        print("-" * 70)
        print(f"🔥 MATCH #{no}")

        a_file = match.get("a_file") or match.get("A_FILE")
        b_file = match.get("b_file") or match.get("B_FILE")

        date_path_a = (
            match.get("a_date_path")
            or match.get("A_DATE_PATH")
            or match.get("date_path_a")
        )

        venue_path_a = (
            match.get("a_venue_path")
            or match.get("A_VENUE_PATH")
            or match.get("venue_path_a")
        )

        race_path_a = (
            match.get("a_race_path")
            or match.get("A_RACE_PATH")
            or match.get("race_path_a")
        )

        date_path_b = (
            match.get("b_date_path")
            or match.get("B_DATE_PATH")
            or match.get("date_path_b")
        )

        venue_path_b = (
            match.get("b_venue_path")
            or match.get("B_VENUE_PATH")
            or match.get("venue_path_b")
        )

        race_path_b = (
            match.get("b_race_path")
            or match.get("B_RACE_PATH")
            or match.get("race_path_b")
        )

        # 139側にファイル名が無い場合の固定候補
        if not a_file:
            a_file = "054_all_results.json"

        if not b_file:
            b_file = "055_all_races.json"

        a_path = RESULT_DIR / a_file
        b_path = RESULT_DIR / b_file

        print(f"A FILE: {a_file}")
        print(f"B FILE: {b_file}")

        if not a_path.exists():
            print(f"❌ A FILEなし: {a_path}")
            continue

        if not b_path.exists():
            print(f"❌ B FILEなし: {b_path}")
            continue

        a_json = load_json(a_path)
        b_json = load_json(b_path)

        # PATHが139に保存されていない場合
        if not date_path_a:
            date_path_a = "ROOT[0].race.selKaisai"

        if not venue_path_a:
            venue_path_a = "ROOT[0].race.joName"

        if not race_path_a:
            race_path_a = "ROOT[0].race.selRaceNo"

        if not date_path_b:
            date_path_b = "ROOT[4].jsj001.C0201data.selKaisai"

        if not venue_path_b:
            venue_path_b = "ROOT[4].jsj001.C0201data.joName"

        if not race_path_b:
            race_path_b = "ROOT[4].jsj001.C0201data.selRaceNo"

        date_a = get_by_path(a_json, date_path_a)
        venue_a = get_by_path(a_json, venue_path_a)
        race_a = get_by_path(a_json, race_path_a)

        date_b = get_by_path(b_json, date_path_b)
        venue_b = get_by_path(b_json, venue_path_b)
        race_b = get_by_path(b_json, race_path_b)

        print(f"開催日: {date_a}")
        print(f"競輪場: {venue_a}")
        print(f"レース番号: {race_a}")

        print()
        print("A 確定結果")
        print(f"DATE : {date_a}")
        print(f"VENUE: {venue_a}")
        print(f"RACE : {race_a}")

        print()
        print("B レース前情報")
        print(f"DATE : {date_b}")
        print(f"VENUE: {venue_b}")
        print(f"RACE : {race_b}")

        same_date = str(date_a) == str(date_b)
        same_venue = str(venue_a) == str(venue_b)
        same_race = str(race_a) == str(race_b)

        print()
        print(f"DATE一致 : {same_date}")
        print(f"VENUE一致: {same_venue}")
        print(f"RACE一致 : {same_race}")

        if not (same_date and same_venue and same_race):
            print("❌ 3点不一致")
            continue

        a_block_path = get_block_path(date_path_a)
        b_block_path = get_block_path(date_path_b)

        a_block = get_by_path(a_json, a_block_path)
        b_block = get_by_path(b_json, b_block_path)

        joined_item = {
            "race_key": {
                "date": str(date_a),
                "venue": str(venue_a),
                "race_no": str(race_a),
            },
            "confirmed_result": a_block,
            "pre_race_data": b_block,
            "source": {
                "confirmed_result_file": a_file,
                "pre_race_file": b_file,
                "confirmed_result_block": a_block_path,
                "pre_race_block": b_block_path,
            },
        }

        joined.append(joined_item)

        print()
        print("🔥 結合成功")
        print(
            f"RACE KEY: "
            f"{date_a} / {venue_a} / {race_a}R"
        )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            joined,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print("=" * 70)
    print("🔥 140テスト終了")
    print("=" * 70)

    print(f"139照合件数: {len(match_data)}")
    print(f"結合成功件数: {len(joined)}")

    print()
    print(f"保存先: {OUTPUT_FILE.name}")

    print("=" * 70)


if __name__ == "__main__":
    main()