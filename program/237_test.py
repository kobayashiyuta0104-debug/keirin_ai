import json
import csv
from pathlib import Path
from collections import Counter

SRC = Path(r"C:\競輪AI\231_20260706_model_ready_154_features.json")
OUT_CSV = Path(r"C:\競輪AI\237_20260706_training_dataset.csv")
OUT_JSON = Path(r"C:\競輪AI\237_training_dataset_validation.json")

LABEL_KEYS = [
    "trifecta_combination",
    "trifecta_payout",
    "payout_class_4",
    "is_20000_plus",
    "is_50000_plus",
]

def main():
    print("=== 237 70レース 学習用CSV正式出力・最終構造検証 ===")

    data = json.loads(SRC.read_text(encoding="utf-8"))
    races = data.get("races", [])

    if not races:
        raise RuntimeError("231のracesが見つかりません")

    feature_keys = list(races[0]["features"].keys())
    rows = []
    problems = []
    feature_count_dist = Counter()
    label_missing = Counter()
    payout_class_dist = Counter()
    player_count_dist = Counter()

    for race in races:
        rk = race.get("race_key")
        features = race.get("features", {})
        labels = race.get("labels", {})
        player_count = race.get("player_count")

        feature_count_dist[len(features)] += 1
        player_count_dist[player_count] += 1

        if list(features.keys()) != feature_keys:
            problems.append({
                "race_key": rk,
                "problem": "FEATURE_ORDER_MISMATCH"
            })

        if len(features) != 154:
            problems.append({
                "race_key": rk,
                "problem": "FEATURE_COUNT_NOT_154",
                "count": len(features)
            })

        for key in LABEL_KEYS:
            if key not in labels or labels.get(key) is None:
                label_missing[key] += 1
                problems.append({
                    "race_key": rk,
                    "problem": "LABEL_MISSING",
                    "label": key
                })

        payout_class_dist[labels.get("payout_class_4")] += 1

        row = {
            "race_key": rk,
            "player_count": player_count,
        }
        for key in feature_keys:
            row[key] = features.get(key)
        for key in LABEL_KEYS:
            row[key] = labels.get(key)
        rows.append(row)

    columns = ["race_key", "player_count"] + feature_keys + LABEL_KEYS

    with OUT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    report = {
        "source": str(SRC),
        "race_count": len(races),
        "feature_count": len(feature_keys),
        "csv_column_count": len(columns),
        "feature_count_distribution": dict(feature_count_dist),
        "player_count_distribution": dict(player_count_dist),
        "payout_class_distribution": dict(payout_class_dist),
        "label_missing_distribution": dict(label_missing),
        "problem_count": len(problems),
        "problems": problems,
        "feature_order": feature_keys,
        "csv_path": str(OUT_CSV),
    }

    OUT_JSON.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print("\n=== 237 結果 ===")
    print("対象レース数:", len(races))
    print("正式特徴量数:", len(feature_keys))
    print("CSV総列数:", len(columns))
    print("特徴量数分布:", dict(feature_count_dist))
    print("車立て分布:", dict(player_count_dist))
    print("4分類分布:", dict(payout_class_dist))
    print("ラベル欠損:", dict(label_missing))
    print("問題件数:", len(problems))

    print("\n=== CSV先頭1行確認 ===")
    print("race_key:", rows[0]["race_key"])
    print("player_count:", rows[0]["player_count"])
    print("trifecta_combination:", rows[0]["trifecta_combination"])
    print("trifecta_payout:", rows[0]["trifecta_payout"])
    print("payout_class_4:", rows[0]["payout_class_4"])
    print("is_20000_plus:", rows[0]["is_20000_plus"])
    print("is_50000_plus:", rows[0]["is_50000_plus"])

    if problems:
        print("\n=== 問題一覧 先頭50件 ===")
        for p in problems[:50]:
            print(p)

    print("\nCSV保存完了:", OUT_CSV)
    print("検証保存完了:", OUT_JSON)
    print("=== 237 完了 ===")

if __name__ == "__main__":
    main()
