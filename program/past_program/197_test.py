import json
import csv
from pathlib import Path

print("=== 197 AI入力特徴量・正解ラベル 完全分離テスト ===")

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "196_labeled_ai_training_rows.json"
JSON_OUTPUT = BASE_DIR / "197_model_ready_dataset.json"
CSV_OUTPUT = BASE_DIR / "197_model_ready_dataset.csv"

RESULT_SUFFIXES = {
    "finish_rank",
    "result_status",
    "result_note",
    "result_car_no",
    "agari",
    "kimarite",
    "BH",
}

RACE_RESULT_COLUMNS = {
    "trifecta_combination",
    "trifecta_payout",
    "trifecta_popularity",
    "numeric_finish_count",
    "abnormal_result_count",
}

LABEL_COLUMNS = {
    "payout_label_id",
    "payout_label",
    "is_20000_plus",
    "is_50000_plus",
}

IDENTIFIER_COLUMNS = {
    "race_key",
    "race_date",
    "venue",
    "race_no",
}

NON_MODEL_PLAYER_SUFFIXES = {
    "id",
    "name",
}

with INPUT_FILE.open("r", encoding="utf-8") as f:
    raw = json.load(f)

rows = raw.get("rows", [])

model_rows = []
feature_columns = []
feature_seen = set()
leakage_found = []
problems = []

for row in rows:
    feature_data = {}

    for key, value in row.items():
        if key in IDENTIFIER_COLUMNS:
            continue
        if key in RACE_RESULT_COLUMNS:
            continue
        if key in LABEL_COLUMNS:
            continue

        is_player_result = False
        is_non_model_player = False

        if key.startswith("p") and "_" in key:
            parts = key.split("_", 1)
            if len(parts) == 2 and parts[0][1:].isdigit():
                suffix = parts[1]
                if suffix in RESULT_SUFFIXES:
                    is_player_result = True
                if suffix in NON_MODEL_PLAYER_SUFFIXES:
                    is_non_model_player = True

        if is_player_result or is_non_model_player:
            continue

        feature_data[key] = value

    out = {
        "race_key": row.get("race_key"),
        "race_date": row.get("race_date"),
        "venue": row.get("venue"),
        "race_no": row.get("race_no"),
        **feature_data,
        "target_payout_label_id": row.get("payout_label_id"),
        "target_payout_label": row.get("payout_label"),
        "target_is_20000_plus": row.get("is_20000_plus"),
        "target_is_50000_plus": row.get("is_50000_plus"),
    }

    for key in feature_data:
        if key not in feature_seen:
            feature_seen.add(key)
            feature_columns.append(key)

    for key in feature_data:
        if key in RACE_RESULT_COLUMNS or key in LABEL_COLUMNS:
            leakage_found.append({"race_key": row.get("race_key"), "column": key})
        if key.startswith("p") and "_" in key:
            suffix = key.split("_", 1)[1]
            if suffix in RESULT_SUFFIXES:
                leakage_found.append({"race_key": row.get("race_key"), "column": key})

    if out["target_payout_label_id"] is None:
        problems.append({
            "race_key": row.get("race_key"),
            "problem": "TARGET_MISSING",
        })

    model_rows.append(out)

output_columns = []
seen = set()
for row in model_rows:
    for key in row:
        if key not in seen:
            seen.add(key)
            output_columns.append(key)

with JSON_OUTPUT.open("w", encoding="utf-8") as f:
    json.dump({
        "row_count": len(model_rows),
        "feature_count": len(feature_columns),
        "feature_columns": feature_columns,
        "target_columns": [
            "target_payout_label_id",
            "target_payout_label",
            "target_is_20000_plus",
            "target_is_50000_plus",
        ],
        "leakage_count": len(leakage_found),
        "leakage_found": leakage_found,
        "problem_count": len(problems),
        "problems": problems,
        "rows": model_rows,
    }, f, ensure_ascii=False, indent=2)

with CSV_OUTPUT.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=output_columns)
    writer.writeheader()
    writer.writerows(model_rows)

print()
print("=== 197 結果 ===")
print(f"モデル用レース行数: {len(model_rows)}")
print(f"AI入力特徴量数: {len(feature_columns)}")
print(f"結果漏洩検出数: {len(leakage_found)}")
print(f"問題件数: {len(problems)}")
print(f"JSON保存: {JSON_OUTPUT}")
print(f"CSV保存: {CSV_OUTPUT}")

print()
print("=== AI入力特徴量 先頭30列 ===")
for key in feature_columns[:30]:
    print(f"  {key}")

if model_rows:
    sample = model_rows[0]
    print()
    print("=== 先頭1レース確認 ===")
    print(f"race_key: {sample.get('race_key')}")
    print(f"p1_race_score: {sample.get('p1_race_score')}")
    print(f"p1_riding_style: {sample.get('p1_riding_style')}")
    print(f"p1_recent_finish_1: {sample.get('p1_recent_finish_1')}")
    print(f"target_payout_label_id: {sample.get('target_payout_label_id')}")
    print(f"target_payout_label: {sample.get('target_payout_label')}")
    print(f"target_is_20000_plus: {sample.get('target_is_20000_plus')}")
    print(f"target_is_50000_plus: {sample.get('target_is_50000_plus')}")

if leakage_found:
    print()
    print("=== 結果漏洩一覧 先頭20件 ===")
    for item in leakage_found[:20]:
        print(item)

if problems:
    print()
    print("=== 問題一覧 ===")
    for item in problems:
        print(item)

print()
print("=== 197 完了 ===")
