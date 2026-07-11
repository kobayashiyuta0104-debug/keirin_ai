import json
from pathlib import Path
from collections import Counter

SRC = Path(r"C:\競輪AI\230_20260706_features_with_results_fixed.json")
SCHEMA = Path(r"C:\競輪AI\199_model_feature_schema.json")
OUT = Path(r"C:\競輪AI\231_20260706_model_ready_154_features.json")
REPORT = Path(r"C:\競輪AI\231_model_ready_validation_report.json")

PLAYER_FIELDS = [
    "prefecture",
    "previous_class",
    "class",
    "riding_style",
    "graduation_term",
    "age",
    "race_score",
    "nige_count",
    "makuri_count",
    "sashi_count",
    "mark_count",
    "back_count",
    "home_count",
    "start_count",
    "win_rate",
    "top2_rate",
    "top3_rate",
]

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def race_key_of(obj):
    if not isinstance(obj, dict):
        return None
    return obj.get("race_key") or obj.get("raceKey")

def find_race_list(obj):
    candidates = []

    def walk(x):
        if isinstance(x, list) and x and all(isinstance(v, dict) for v in x):
            count = sum(1 for v in x if race_key_of(v))
            if count:
                candidates.append((count, x))
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)

    walk(obj)

    if not candidates:
        return []

    return max(candidates, key=lambda z: z[0])[1]

def find_schema_features(schema):
    preferred_keys = [
        "model_features",
        "selected_features",
        "feature_columns",
        "features",
        "正式採用特徴量",
    ]

    for key in preferred_keys:
        value = schema.get(key) if isinstance(schema, dict) else None
        if isinstance(value, list) and value and all(isinstance(x, str) for x in value):
            return value, f"$.{key}"

    candidates = []

    def walk(x, path="$"):
        if isinstance(x, dict):
            for k, v in x.items():
                walk(v, f"{path}.{k}")
        elif isinstance(x, list):
            if x and all(isinstance(v, str) for v in x):
                pcols = sum(1 for v in x if v.startswith("p") and "_" in v)
                if pcols:
                    candidates.append((pcols, len(x), path, x))
            for i, v in enumerate(x):
                walk(v, f"{path}[{i}]")

    walk(schema)

    if not candidates:
        return [], None

    candidates.sort(key=lambda z: (z[0], z[1]), reverse=True)
    best = candidates[0]
    return best[3], best[2]

def normalize_recent_results(player):
    recent = player.get("recent_meeting_results")
    if isinstance(recent, list):
        return recent
    recent = player.get("recent_meeting")
    if isinstance(recent, dict):
        results = recent.get("results")
        if isinstance(results, list):
            return results
    return []

def recent_finish(player, index):
    recent = normalize_recent_results(player)
    if index < len(recent) and isinstance(recent[index], dict):
        return recent[index].get("finish")
    return None

def player_feature_value(player, suffix):
    if suffix == "recent_finish_1":
        return recent_finish(player, 0)
    if suffix == "recent_finish_2":
        return recent_finish(player, 1)
    if suffix == "recent_finish_3":
        return recent_finish(player, 2)
    if suffix == "recent_venue_code":
        recent = player.get("recent_meeting")
        return recent.get("venue_code") if isinstance(recent, dict) else None
    if suffix == "recent_grade":
        recent = player.get("recent_meeting")
        return recent.get("grade") if isinstance(recent, dict) else None
    return player.get(suffix)

def main():
    print("=== 231 230結果 -> 199正式154特徴量 AI入力形式変換 ===")

    src = load_json(SRC)
    schema = load_json(SCHEMA)

    races = find_race_list(src)
    schema_features, schema_path = find_schema_features(schema)

    print("検出レース数:", len(races))
    print("199正式特徴量PATH:", schema_path)
    print("199正式特徴量数:", len(schema_features))

    if len(schema_features) != 154:
        print("❌ 199正式特徴量が154列として検出できません")
        print("検出数:", len(schema_features))
        return

    rows = []
    problems = []
    player_count_dist = Counter()

    for race in races:
        race_key = race_key_of(race)
        players = race.get("players")

        if not isinstance(players, list):
            problems.append({
                "race_key": race_key,
                "problem": "PLAYERS_NOT_FOUND"
            })
            continue

        players = sorted(
            players,
            key=lambda p: int(p.get("car_no") or 999)
        )

        player_count_dist[len(players)] += 1
        player_by_car = {
            int(p.get("car_no")): p
            for p in players
            if p.get("car_no") is not None
        }

        feature_values = {}

        for feature in schema_features:
            if not feature.startswith("p") or "_" not in feature:
                feature_values[feature] = race.get(feature)
                continue

            prefix, suffix = feature.split("_", 1)

            try:
                car_no = int(prefix[1:])
            except Exception:
                feature_values[feature] = None
                continue

            player = player_by_car.get(car_no)

            if player is None:
                feature_values[feature] = None
            else:
                feature_values[feature] = player_feature_value(player, suffix)

        missing_columns = [
            col for col in schema_features
            if col not in feature_values
        ]

        extra_columns = [
            col for col in feature_values
            if col not in schema_features
        ]

        row = {
            "race_key": race_key,
            "player_count": len(players),
            "features": feature_values,
            "labels": {
                "trifecta_combination": race.get("trifecta_combination"),
                "trifecta_payout": race.get("trifecta_payout"),
                "payout_class_4": race.get("payout_class_4"),
                "is_20000_plus": race.get("is_20000_plus"),
                "is_50000_plus": race.get("is_50000_plus"),
            }
        }

        rows.append(row)

        if len(feature_values) != 154:
            problems.append({
                "race_key": race_key,
                "problem": "FEATURE_COUNT_MISMATCH",
                "count": len(feature_values)
            })

        if missing_columns:
            problems.append({
                "race_key": race_key,
                "problem": "SCHEMA_COLUMNS_MISSING",
                "columns": missing_columns
            })

        if extra_columns:
            problems.append({
                "race_key": race_key,
                "problem": "EXTRA_COLUMNS",
                "columns": extra_columns
            })

    feature_count_dist = Counter(
        len(row["features"]) for row in rows
    )

    schema_exact_count = sum(
        1 for row in rows
        if list(row["features"].keys()) == schema_features
    )

    missing_value_count_dist = Counter(
        sum(v is None for v in row["features"].values())
        for row in rows
    )

    output = {
        "source_file": str(SRC),
        "schema_file": str(SCHEMA),
        "schema_path": schema_path,
        "feature_count": len(schema_features),
        "feature_columns": schema_features,
        "race_count": len(rows),
        "races": rows,
    }

    report = {
        "source_race_count": len(races),
        "generated_race_count": len(rows),
        "schema_feature_count": len(schema_features),
        "feature_count_distribution": dict(feature_count_dist),
        "schema_order_exact_count": schema_exact_count,
        "player_count_distribution": dict(player_count_dist),
        "missing_value_count_distribution": dict(missing_value_count_dist),
        "problem_count": len(problems),
        "problems": problems,
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    with open(REPORT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n=== 231 結果 ===")
    print("元レース数:", len(races))
    print("AI入力生成レース数:", len(rows))
    print("正式特徴量数:", len(schema_features))
    print("特徴量数分布:", dict(feature_count_dist))
    print("199列順完全一致レース:", schema_exact_count)
    print("車立て分布:", dict(player_count_dist))
    print("欠損値数分布:", dict(missing_value_count_dist))
    print("問題件数:", len(problems))

    if rows:
        first = rows[0]
        print("\n=== 先頭1レース確認 ===")
        print("race_key:", first["race_key"])
        print("player_count:", first["player_count"])
        print("features数:", len(first["features"]))
        print("先頭20特徴量:")
        for k, v in list(first["features"].items())[:20]:
            print(" ", k, "=", v)
        print("labels:", first["labels"])

    if problems:
        print("\n=== 問題一覧 先頭30件 ===")
        for p in problems[:30]:
            print(p)

    print("\n保存完了:", OUT)
    print("検証保存:", REPORT)
    print("=== 231 完了 ===")

if __name__ == "__main__":
    main()
