import json
from pathlib import Path
from collections import Counter, defaultdict

SRC = Path(r"C:\競輪AI\231_20260706_model_ready_154_features.json")
OUT = Path(r"C:\競輪AI\232_missing_value_structure_analysis.json")

def main():
    print("=== 232 154特徴量 欠損構造・車立て別完全解析 ===")

    with open(SRC, "r", encoding="utf-8") as f:
        data = json.load(f)

    races = data.get("races", [])
    feature_columns = data.get("feature_columns", [])

    col_missing = Counter()
    count_by_player_count = Counter()
    missing_by_player_count = defaultdict(Counter)
    race_rows = []
    unexpected = []

    for race in races:
        race_key = race.get("race_key")
        player_count = race.get("player_count")
        features = race.get("features", {})

        missing_cols = [
            col for col in feature_columns
            if features.get(col) is None
        ]

        count_by_player_count[player_count] += 1

        for col in missing_cols:
            col_missing[col] += 1
            missing_by_player_count[player_count][col] += 1

        structural = []
        non_structural = []

        for col in missing_cols:
            structural_flag = False

            if col.startswith("p") and "_" in col:
                prefix = col.split("_", 1)[0]
                try:
                    car_no = int(prefix[1:])
                    if car_no > int(player_count):
                        structural_flag = True
                except Exception:
                    pass

            if structural_flag:
                structural.append(col)
            else:
                non_structural.append(col)

        race_rows.append({
            "race_key": race_key,
            "player_count": player_count,
            "missing_count": len(missing_cols),
            "structural_missing_count": len(structural),
            "non_structural_missing_count": len(non_structural),
            "structural_missing_columns": structural,
            "non_structural_missing_columns": non_structural,
        })

        if non_structural:
            unexpected.append({
                "race_key": race_key,
                "player_count": player_count,
                "columns": non_structural,
            })

    print("\n=== 232 結果 ===")
    print("対象レース数:", len(races))
    print("正式特徴量数:", len(feature_columns))
    print("車立て分布:", dict(count_by_player_count))
    print("欠損あり列数:", len(col_missing))
    print("非構造欠損ありレース数:", len(unexpected))

    print("\n=== 欠損列ランキング 全件 ===")
    for col, cnt in col_missing.most_common():
        print(f"{col}: {cnt}")

    print("\n=== 車立て別 欠損列 ===")
    for pc in sorted(missing_by_player_count):
        print(f"\n--- {pc}車 ---")
        for col, cnt in missing_by_player_count[pc].most_common():
            print(f"{col}: {cnt}")

    print("\n=== レース別 欠損分類 ===")
    for row in race_rows:
        print(
            f'{row["race_key"]} / {row["player_count"]}車 / '
            f'全欠損={row["missing_count"]} / '
            f'構造欠損={row["structural_missing_count"]} / '
            f'非構造欠損={row["non_structural_missing_count"]}'
        )

    print("\n=== 非構造欠損 詳細 ===")
    if not unexpected:
        print("なし")
    else:
        for x in unexpected:
            print(x)

    report = {
        "source_file": str(SRC),
        "race_count": len(races),
        "feature_count": len(feature_columns),
        "player_count_distribution": dict(count_by_player_count),
        "missing_column_counts": dict(col_missing),
        "missing_by_player_count": {
            str(k): dict(v)
            for k, v in missing_by_player_count.items()
        },
        "race_missing_analysis": race_rows,
        "non_structural_missing_race_count": len(unexpected),
        "non_structural_missing": unexpected,
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n保存完了:", OUT)
    print("=== 232 完了 ===")

if __name__ == "__main__":
    main()
