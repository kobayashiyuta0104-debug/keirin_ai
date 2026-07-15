import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
RESULT_DIR = BASE_DIR


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def normalize_text(value):
    if value is None:
        return ""

    return str(value).strip()


def normalize_date(value):
    text = normalize_text(value)

    text = (
        text.replace("/", "")
        .replace("-", "")
        .replace(".", "")
        .replace("年", "")
        .replace("月", "")
        .replace("日", "")
        .replace(" ", "")
    )

    return text


def normalize_venue(value):
    text = normalize_text(value)

    replace_map = {
        "競輪場": "",
        "競輪": "",
        "場": "",
    }

    for old, new in replace_map.items():
        text = text.replace(old, new)

    return text.strip()


def normalize_race_no(value):
    text = normalize_text(value).upper()

    text = text.replace("R", "")
    text = text.replace("レース", "")
    text = text.strip()

    try:
        return str(int(text))
    except Exception:
        return text


def walk_json(obj, path="ROOT"):
    items = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = f"{path}.{key}"

            items.append(
                {
                    "path": current_path,
                    "key": key,
                    "value": value,
                }
            )

            items.extend(walk_json(value, current_path))

    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            current_path = f"{path}[{index}]"
            items.extend(walk_json(value, current_path))

    return items


def extract_race_keys(data):
    result = {
        "date": [],
        "venue": [],
        "race_no": [],
        "race_url_prm": [],
    }

    items = walk_json(data)

    for item in items:
        key = item["key"]
        value = item["value"]
        path = item["path"]

        if isinstance(value, (dict, list)):
            continue

        if key == "selKaisai":
            result["date"].append(
                {
                    "path": path,
                    "key": key,
                    "raw": value,
                    "normalized": normalize_date(value),
                }
            )

        elif key == "race_name":
            result["venue"].append(
                {
                    "path": path,
                    "key": key,
                    "raw": value,
                    "normalized": normalize_venue(value),
                }
            )

        elif key in ("selRaceNo", "race_no"):
            result["race_no"].append(
                {
                    "path": path,
                    "key": key,
                    "raw": value,
                    "normalized": normalize_race_no(value),
                }
            )

        elif key == "raceUrlPrm":
            result["race_url_prm"].append(
                {
                    "path": path,
                    "key": key,
                    "raw": value,
                    "normalized": normalize_text(value),
                }
            )

    return result


def unique_values(items):
    values = []

    for item in items:
        value = item["normalized"]

        if value and value not in values:
            values.append(value)

    return values


def compare_races(file_a, keys_a, file_b, keys_b):
    a_date = set(unique_values(keys_a["date"]))
    b_date = set(unique_values(keys_b["date"]))

    a_venue = set(unique_values(keys_a["venue"]))
    b_venue = set(unique_values(keys_b["venue"]))

    a_race = set(unique_values(keys_a["race_no"]))
    b_race = set(unique_values(keys_b["race_no"]))

    a_url = set(unique_values(keys_a["race_url_prm"]))
    b_url = set(unique_values(keys_b["race_url_prm"]))

    date_match = bool(a_date & b_date)
    venue_match = bool(a_venue & b_venue)
    race_match = bool(a_race & b_race)
    url_match = bool(a_url & b_url)

    score = 0
    reasons = []

    if date_match:
        score += 100
        reasons.append("開催日一致")

    if venue_match:
        score += 100
        reasons.append("競輪場一致")

    if race_match:
        score += 100
        reasons.append("レース番号一致")

    if url_match:
        score += 500
        reasons.append("raceUrlPrm一致")

    if score == 0:
        return None

    return {
        "file_a": file_a,
        "file_b": file_b,
        "score": score,
        "date_match": date_match,
        "venue_match": venue_match,
        "race_match": race_match,
        "url_match": url_match,
        "reasons": reasons,
        "common_date": list(a_date & b_date),
        "common_venue": list(a_venue & b_venue),
        "common_race_no": list(a_race & b_race),
        "common_race_url_prm": list(a_url & b_url),
    }


def main():
    print("=" * 70)
    print("🔥 135 同一レース自動照合テスト")
    print("=" * 70)

    json_files = sorted(RESULT_DIR.glob("*.json"))

    print(f"JSONファイル数: {len(json_files)}")

    race_data = {}

    for path in json_files:
        data = load_json(path)

        if data is None:
            continue

        keys = extract_race_keys(data)

        key_count = sum(
            len(values)
            for values in keys.values()
        )

        if key_count == 0:
            continue

        race_data[path.name] = keys

    print(f"照合対象JSON数: {len(race_data)}")

    print()
    print("🔥 各JSONのレース識別情報")
    print("=" * 70)

    for file_name, keys in race_data.items():
        dates = unique_values(keys["date"])
        venues = unique_values(keys["venue"])
        race_nos = unique_values(keys["race_no"])
        urls = unique_values(keys["race_url_prm"])

        print()
        print(f"📄 {file_name}")
        print(f"開催日: {dates[:10]}")
        print(f"競輪場: {venues[:10]}")
        print(f"レース番号: {race_nos[:20]}")
        print(f"raceUrlPrm: {urls[:5]}")

    file_names = list(race_data.keys())

    matches = []

    print()
    print("=" * 70)
    print("🔥 JSON同士の照合開始")
    print("=" * 70)

    for i in range(len(file_names)):
        for j in range(i + 1, len(file_names)):
            file_a = file_names[i]
            file_b = file_names[j]

            match = compare_races(
                file_a,
                race_data[file_a],
                file_b,
                race_data[file_b],
            )

            if match is not None:
                matches.append(match)

    matches.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    print()
    print(f"照合候補数: {len(matches)}")

    print()
    print("=" * 70)
    print("🔥 TOP50 同一レース候補")
    print("=" * 70)

    for index, match in enumerate(matches[:50], start=1):
        print()
        print("-" * 70)
        print(f"🔥 候補 #{index}")
        print(f"SCORE: {match['score']}")
        print(f"A: {match['file_a']}")
        print(f"B: {match['file_b']}")
        print(f"理由: {match['reasons']}")
        print(f"共通開催日: {match['common_date']}")
        print(f"共通競輪場: {match['common_venue']}")
        print(f"共通レース番号: {match['common_race_no']}")

        if match["common_race_url_prm"]:
            print(
                "共通raceUrlPrm:",
                match["common_race_url_prm"],
            )

    output_path = RESULT_DIR / "135_race_match_candidates.json"

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            matches,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print("=" * 70)
    print("🔥 135テスト終了")
    print("=" * 70)
    print(f"照合対象JSON数: {len(race_data)}")
    print(f"照合候補数: {len(matches)}")
    print()
    print(f"保存先: {output_path.name}")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()