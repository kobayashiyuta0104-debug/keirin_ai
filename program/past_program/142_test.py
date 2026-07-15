import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

MATCH_FILE = BASE_DIR / "139_official_race_match.json"
RESULT_FILE = BASE_DIR / "054_all_results.json"
RACE_FILE = BASE_DIR / "055_all_races.json"

OUTPUT_FILE = BASE_DIR / "142_joined_race_data.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_by_path(data, path):
    """
    ROOT[0].race.selKaisai
    ROOT[4].jsj001.C0201data.selRaceNo
    のようなPATHから値を取得
    """

    if not path:
        return None

    if not path.startswith("ROOT"):
        return None

    text = path[4:]
    current = data

    i = 0

    try:
        while i < len(text):

            if text[i] == ".":

                i += 1
                start = i

                while (
                    i < len(text)
                    and text[i] not in ".["
                ):
                    i += 1

                key = text[start:i]

                if not key:
                    return None

                current = current[key]

            elif text[i] == "[":

                end = text.find("]", i)

                if end == -1:
                    return None

                index_text = text[i + 1:end]

                index = int(index_text)

                current = current[index]

                i = end + 1

            else:
                i += 1

        return current

    except (
        KeyError,
        IndexError,
        TypeError,
        ValueError,
    ):
        return None


def normalize(value):
    if value is None:
        return ""

    return str(value).strip()


def main():

    print("=" * 70)
    print("🔥 142 正式照合結果 本結合テスト")
    print("=" * 70)

    if not MATCH_FILE.exists():
        print(f"❌ ファイルなし: {MATCH_FILE.name}")
        return

    if not RESULT_FILE.exists():
        print(f"❌ ファイルなし: {RESULT_FILE.name}")
        return

    if not RACE_FILE.exists():
        print(f"❌ ファイルなし: {RACE_FILE.name}")
        return

    match_json = load_json(MATCH_FILE)
    result_json = load_json(RESULT_FILE)
    race_json = load_json(RACE_FILE)

    matches = match_json.get("matches", [])

    print()
    print(f"matches件数: {len(matches)}")

    joined = []

    print()
    print("=" * 70)
    print("🔥 MATCH結合開始")
    print("=" * 70)

    for no, match in enumerate(matches, start=1):

        print()
        print("-" * 70)
        print(f"🔥 MATCH #{no}")

        if not isinstance(match, dict):
            print("❌ MATCHがdictではありません")
            continue

        result_info = match.get("result")
        race_info = match.get("race")

        if not isinstance(result_info, dict):
            print("❌ result情報なし")
            continue

        if not isinstance(race_info, dict):
            print("❌ race情報なし")
            continue

        result_date = normalize(result_info.get("date"))
        result_venue = normalize(result_info.get("venue"))
        result_race_no = normalize(result_info.get("race_no"))

        race_date = normalize(race_info.get("date"))
        race_venue = normalize(race_info.get("venue"))
        race_race_no = normalize(race_info.get("race_no"))

        print(f"RESULT: {result_date} / {result_venue} / {result_race_no}R")
        print(f"RACE  : {race_date} / {race_venue} / {race_race_no}R")

        same_date = result_date == race_date
        same_venue = result_venue == race_venue
        same_race = result_race_no == race_race_no

        print()
        print(f"DATE一致 : {same_date}")
        print(f"VENUE一致: {same_venue}")
        print(f"RACE一致 : {same_race}")

        if not (
            same_date
            and same_venue
            and same_race
        ):
            print("❌ 3点一致失敗")
            continue

        result_block_path = result_info.get("block_path")
        race_block_path = race_info.get("block_path")
        official_path = race_info.get("official_path")

        result_block = get_by_path(
            result_json,
            result_block_path,
        )

        race_block = get_by_path(
            race_json,
            race_block_path,
        )

        official_block = get_by_path(
            race_json,
            official_path,
        )

        print()
        print(f"RESULT BLOCK PATH : {result_block_path}")
        print(f"RACE BLOCK PATH   : {race_block_path}")
        print(f"OFFICIAL PATH     : {official_path}")

        print()
        print(
            f"RESULT BLOCK TYPE : "
            f"{type(result_block).__name__}"
        )

        print(
            f"RACE BLOCK TYPE   : "
            f"{type(race_block).__name__}"
        )

        print(
            f"OFFICIAL TYPE     : "
            f"{type(official_block).__name__}"
        )

        if result_block is None:
            print("❌ 確定結果BLOCK取得失敗")
            continue

        if race_block is None:
            print("❌ レース前BLOCK取得失敗")
            continue

        race_key = (
            f"{result_date}_"
            f"{result_venue}_"
            f"{result_race_no}R"
        )

        joined_item = {
            "race_key": race_key,
            "date": result_date,
            "venue": result_venue,
            "race_no": result_race_no,
            "confirmed_result": result_block,
            "pre_race_data": race_block,
            "official_race_data": official_block,
            "source": {
                "confirmed_result_file": RESULT_FILE.name,
                "pre_race_file": RACE_FILE.name,
                "match_file": MATCH_FILE.name,
                "confirmed_result_block_path": result_block_path,
                "pre_race_block_path": race_block_path,
                "official_path": official_path,
            },
        }

        joined.append(joined_item)

        print()
        print("🔥🔥🔥 本結合成功")
        print(f"RACE KEY: {race_key}")

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
    print("🔥 142テスト終了")
    print("=" * 70)

    print(f"matches件数: {len(matches)}")
    print(f"本結合成功件数: {len(joined)}")

    if joined:

        print()
        print("🔥 結合RACE KEY")

        for item in joined:
            print(f"- {item['race_key']}")

    print()
    print(f"保存先: {OUTPUT_FILE.name}")

    print("=" * 70)


if __name__ == "__main__":
    main()