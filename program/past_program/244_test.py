import json
from pathlib import Path
from collections import Counter

SRC = Path(r"C:\競輪AI\242_20260705_06_model_ready_154_features.json")
OUT = Path(r"C:\競輪AI\244_20260705_06_official_dataset.json")


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():

    print("=== 244 正式9車対応JSON生成 ===")

    races = load_json(SRC)

    output = []

    player_counter = Counter()
    nine_races = []

    for race in races:

        player_count = race.get("player_count", 0)

        player_counter[player_count] += 1

        new_race = {
            "race_key": race.get("race_key"),
            "race_date": race.get("race_date"),
            "venue": race.get("venue"),
            "race_no": race.get("race_no"),
            "player_count": player_count,

            # 231/242で作ったplayersをそのまま保持
            "players": race.get("players", []),

            # labelsだけ別管理
            "labels": {
                "trifecta_combination": race.get("labels", {}).get("trifecta_combination"),
                "trifecta_payout": race.get("labels", {}).get("trifecta_payout"),
                "payout_class_4": race.get("labels", {}).get("payout_class_4"),
                "is_20000_plus": race.get("labels", {}).get("is_20000_plus"),
                "is_50000_plus": race.get("labels", {}).get("is_50000_plus"),
            }
        }

        output.append(new_race)

        if player_count == 9:
            nine_races.append(new_race)

    OUT.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print()
    print("=== 244 結果 ===")
    print("対象レース数:", len(output))
    print("車立て分布:", dict(sorted(player_counter.items())))
    print("9車レース数:", len(nine_races))
    print("保存完了:", OUT)

    if nine_races:

        race = nine_races[0]

        print()
        print("=== 先頭9車レース確認 ===")
        print("race_key:", race["race_key"])
        print("player_count:", race["player_count"])

        print()

        print("選手一覧")

        for p in race["players"]:

            print(
                p["car_no"],
                p["player_id"],
                p["player_name"],
                "score=",
                p["race_score"]
            )

        print()

        print("labels")

        print(json.dumps(
            race["labels"],
            ensure_ascii=False,
            indent=2
        ))

    print("=== 244 完了 ===")


if __name__ == "__main__":
    main()