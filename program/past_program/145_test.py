import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "142_joined_race_data.json"
OUTPUT_FILE = BASE_DIR / "145_ai_training_race.json"


def normalize_text(value):
    if value is None:
        return ""

    return str(value).replace("　", " ").strip()


def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def safe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def main():

    print("=" * 70)
    print("🔥 145 AI学習用 正規化レースデータ作成テスト")
    print("=" * 70)

    if not INPUT_FILE.exists():
        print()
        print("❌ 入力JSONがありません")
        print(f"INPUT: {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    print()
    print(f"INPUT: {INPUT_FILE.name}")
    print(f"ROOT TYPE: {type(data).__name__}")

    if not isinstance(data, list):
        print("❌ ROOTがlistではありません")
        return

    print(f"レース件数: {len(data)}")

    normalized_races = []

    for race_index, joined in enumerate(data):

        if not isinstance(joined, dict):
            continue

        confirmed_result = joined.get("confirmed_result")

        if not isinstance(confirmed_result, dict):
            continue

        race_data = confirmed_result.get("race", {})
        result_data = confirmed_result.get("result", {})

        if not isinstance(race_data, dict):
            continue

        if not isinstance(result_data, dict):
            continue

        date = normalize_text(
            joined.get("date")
            or race_data.get("selKaisai")
        )

        venue = normalize_text(
            joined.get("venue")
            or race_data.get("joName")
        )

        race_no = normalize_text(
            joined.get("race_no")
            or race_data.get("selRaceNo")
        )

        if race_no.upper().endswith("R"):
            race_no = race_no[:-1]

        race_key = f"{date}_{venue}_{race_no}R"

        print()
        print("-" * 70)
        print(f"🔥 RACE #{race_index + 1}")
        print(f"RACE KEY: {race_key}")

        finish_items = result_data.get("tyakujyunItemSubData", [])

        if not isinstance(finish_items, list):
            print("❌ tyakujyunItemSubData がlistではありません")
            continue

        print(f"着順データ件数: {len(finish_items)}")

        finish_order = []

        for item in finish_items:

            if not isinstance(item, dict):
                continue

            rank = safe_int(item.get("tyaku"))
            car_no = safe_int(item.get("syaban"))

            player_name = normalize_text(
                item.get("sensyuName")
            )

            player_id = normalize_text(
                item.get("sensyuRegistNo")
            )

            finish_gap = normalize_text(
                item.get("tyakusa")
            )

            agari = safe_float(
                item.get("agari")
            )

            kimarite = normalize_text(
                item.get("kimarite")
            )

            bh = normalize_text(
                item.get("BH")
            )

            finish_item = {
                "rank": rank,
                "car_no": car_no,
                "player_id": player_id,
                "player_name": player_name,
                "finish_gap": finish_gap,
                "agari": agari,
                "kimarite": kimarite,
                "bh": bh,
            }

            finish_order.append(finish_item)

        finish_order.sort(
            key=lambda x: (
                x["rank"] is None,
                x["rank"] if x["rank"] is not None else 999
            )
        )

        top3 = [
            item["car_no"]
            for item in finish_order
            if item["rank"] in [1, 2, 3]
            and item["car_no"] is not None
        ]

        if len(top3) == 3:
            sanrentan_result = "-".join(
                str(car_no) for car_no in top3
            )
        else:
            sanrentan_result = None

        normalized_race = {
            "race_key": race_key,
            "date": date,
            "venue": venue,
            "race_no": safe_int(race_no),
            "result": {
                "sanrentan_result": sanrentan_result,
                "finish_order": finish_order,
            },
        }

        normalized_races.append(normalized_race)

        print()
        print("🔥 着順")

        for item in finish_order:
            print(
                f"{item['rank']}着 "
                f"{item['car_no']}番 "
                f"{item['player_name']} "
                f"ID:{item['player_id']} "
                f"上がり:{item['agari']} "
                f"決まり手:{item['kimarite']} "
                f"BH:{item['bh']}"
            )

        print()
        print(f"🔥 3連単結果: {sanrentan_result}")

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            normalized_races,
            f,
            ensure_ascii=False,
            indent=2
        )

    print()
    print("=" * 70)
    print("🔥 145テスト終了")
    print("=" * 70)
    print(f"正規化レース件数: {len(normalized_races)}")

    if normalized_races:
        first = normalized_races[0]

        print(f"RACE KEY: {first['race_key']}")
        print(
            "3連単結果: "
            f"{first['result']['sanrentan_result']}"
        )

        print(
            "着順件数: "
            f"{len(first['result']['finish_order'])}"
        )

    print()
    print(f"保存先: {OUTPUT_FILE.name}")
    print("=" * 70)


if __name__ == "__main__":
    main()