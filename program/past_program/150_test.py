import json
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "149_player_stats_hunt.json"
OUTPUT_FILE = BASE_DIR / "150_player_stats_value_hunt.json"


def flatten(obj, path="ROOT", results=None):

    if results is None:
        results = []

    if isinstance(obj, dict):

        for key, value in obj.items():

            new_path = f"{path}.{key}"

            if isinstance(value, (dict, list)):

                flatten(
                    value,
                    new_path,
                    results,
                )

            else:

                results.append({
                    "path": new_path,
                    "key": str(key),
                    "value": value,
                    "type": type(value).__name__,
                })

    elif isinstance(obj, list):

        for index, value in enumerate(obj):

            new_path = f"{path}[{index}]"

            if isinstance(value, (dict, list)):

                flatten(
                    value,
                    new_path,
                    results,
                )

            else:

                results.append({
                    "path": new_path,
                    "key": "",
                    "value": value,
                    "type": type(value).__name__,
                })

    return results


def to_number(value):

    if isinstance(value, bool):

        return None

    if isinstance(value, (int, float)):

        return float(value)

    if not isinstance(value, str):

        return None

    text = value.strip()

    if text == "":

        return None

    text = text.replace(",", "")
    text = text.replace("%", "")

    if not re.fullmatch(
        r"-?\d+(\.\d+)?",
        text,
    ):

        return None

    try:

        return float(text)

    except Exception:

        return None


def get_parent_path(path):

    if "." not in path:

        return path

    return path.rsplit(".", 1)[0]


def main():

    print("=" * 70)
    print("🔥 150 選手成績 VALUE特徴探索")
    print("=" * 70)

    if not INPUT_FILE.exists():

        print()
        print("❌ 149 JSONがありません")
        print(INPUT_FILE)

        return

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8",
    ) as f:

        inventory = json.load(f)

    target_files = []

    for item in inventory:

        file_name = item.get("file")

        if file_name:

            target_files.append(file_name)

    print()
    print(
        f"探索対象JSON数: "
        f"{len(target_files)}"
    )

    all_results = []

    for file_name in target_files:

        file_path = BASE_DIR / file_name

        if not file_path.exists():

            continue

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8",
            ) as f:

                data = json.load(f)

        except Exception:

            continue

        items = flatten(data)

        player_ids = []

        for item in items:

            key_lower = item["key"].lower()

            if (
                "numplayer" in key_lower
                or "sensyuregistno" in key_lower
            ):

                value = str(item["value"]).strip()

                if re.fullmatch(
                    r"\d{5,6}",
                    value,
                ):

                    player_ids.append(item)

        score_values = []

        rate_values = []

        percent_values = []

        decimal_values = []

        for item in items:

            number = to_number(item["value"])

            if number is None:

                continue

            value_text = str(item["value"])

            if 70 <= number <= 130:

                score_values.append(item)

            if 0 <= number <= 100:

                rate_values.append(item)

            if "%" in value_text:

                percent_values.append(item)

            if "." in value_text:

                if 0 <= number <= 150:

                    decimal_values.append(item)

        nearby_candidates = []

        for player in player_ids:

            player_parent = get_parent_path(
                player["path"]
            )

            nearby = []

            for item in items:

                if not item["path"].startswith(
                    player_parent
                ):

                    continue

                if item["path"] == player["path"]:

                    continue

                number = to_number(
                    item["value"]
                )

                if number is None:

                    continue

                nearby.append(item)

            nearby_candidates.append({
                "player_path": player["path"],
                "player_id": player["value"],
                "parent_path": player_parent,
                "nearby_numeric_values": nearby,
            })

        if (
            len(player_ids) == 0
            and len(score_values) == 0
            and len(percent_values) == 0
        ):

            continue

        result = {
            "file": file_name,
            "player_id_count": len(player_ids),
            "score_value_count": len(score_values),
            "rate_value_count": len(rate_values),
            "percent_value_count": len(percent_values),
            "decimal_value_count": len(decimal_values),
            "player_ids": player_ids,
            "score_values": score_values,
            "percent_values": percent_values,
            "decimal_values": decimal_values,
            "nearby_candidates": nearby_candidates,
        }

        all_results.append(result)

        print()
        print("=" * 70)
        print(f"🔥 FILE: {file_name}")
        print("=" * 70)

        print(
            f"選手ID候補: "
            f"{len(player_ids)}"
        )

        print(
            f"70〜130数値: "
            f"{len(score_values)}"
        )

        print(
            f"%付きVALUE: "
            f"{len(percent_values)}"
        )

        print(
            f"小数VALUE: "
            f"{len(decimal_values)}"
        )

        if player_ids:

            print()
            print("🔥 選手ID周辺数値")

            for player in nearby_candidates[:3]:

                print()
                print(
                    f"PLAYER ID: "
                    f"{player['player_id']}"
                )

                print(
                    f"PARENT: "
                    f"{player['parent_path']}"
                )

                for item in (
                    player["nearby_numeric_values"][:30]
                ):

                    print(
                        f"{item['path']} "
                        f"= {item['value']}"
                    )

        if score_values:

            print()
            print("🔥 70〜130 VALUE候補")

            for item in score_values[:30]:

                print(
                    f"{item['path']} "
                    f"= {item['value']}"
                )

        if percent_values:

            print()
            print("🔥 % VALUE候補")

            for item in percent_values[:30]:

                print(
                    f"{item['path']} "
                    f"= {item['value']}"
                )

        if decimal_values:

            print()
            print("🔥 小数VALUE候補")

            for item in decimal_values[:30]:

                print(
                    f"{item['path']} "
                    f"= {item['value']}"
                )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            all_results,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print("=" * 70)
    print("🔥 150テスト終了")
    print("=" * 70)

    print(
        f"特徴ありJSON数: "
        f"{len(all_results)}"
    )

    print()
    print("🔥 特徴ありJSON一覧")

    for result in all_results:

        print(
            f"{result['file']} "
            f"| ID:{result['player_id_count']} "
            f"| SCORE:{result['score_value_count']} "
            f"| %:{result['percent_value_count']} "
            f"| DECIMAL:{result['decimal_value_count']}"
        )

    print()
    print(
        f"保存先: "
        f"{OUTPUT_FILE.name}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()