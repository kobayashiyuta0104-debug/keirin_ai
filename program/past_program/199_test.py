import json
from pathlib import Path

print("=== 199 AI正式特徴量スキーマ確定テスト ===")

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_FILE = BASE_DIR / "197_model_ready_dataset.json"
QUALITY_FILE = BASE_DIR / "198_feature_quality_report.json"
OUTPUT_FILE = BASE_DIR / "199_model_feature_schema.json"

with DATASET_FILE.open("r", encoding="utf-8") as f:
    dataset = json.load(f)

with QUALITY_FILE.open("r", encoding="utf-8") as f:
    quality = json.load(f)

rows = dataset.get("rows", [])
feature_columns = dataset.get("feature_columns", [])
numeric_columns = set(quality.get("numeric_columns", []))
categorical_columns = set(quality.get("categorical_columns", []))
constant_columns = set(quality.get("constant_columns", []))
all_missing_columns = set(quality.get("all_missing_columns", []))

excluded_columns = sorted(constant_columns | all_missing_columns)
selected_columns = [
    col for col in feature_columns
    if col not in excluded_columns
]

selected_numeric = [
    col for col in selected_columns
    if col in numeric_columns
]

selected_categorical = [
    col for col in selected_columns
    if col in categorical_columns
]

unknown_type_columns = [
    col for col in selected_columns
    if col not in numeric_columns and col not in categorical_columns
]

missing_selected_columns = []
for col in selected_columns:
    if not any(col in row for row in rows):
        missing_selected_columns.append(col)

forbidden_fragments = [
    "finish_rank",
    "result_status",
    "result_note",
    "result_car_no",
    "agari",
    "kimarite",
    "trifecta",
    "payout",
    "target_",
]

leakage_candidates = []
for col in selected_columns:
    lower = col.lower()
    if any(fragment.lower() in lower for fragment in forbidden_fragments):
        leakage_candidates.append(col)

schema = {
    "schema_version": "199_v1",
    "source_dataset": DATASET_FILE.name,
    "row_count_at_schema_creation": len(rows),
    "original_feature_count": len(feature_columns),
    "selected_feature_count": len(selected_columns),
    "numeric_feature_count": len(selected_numeric),
    "categorical_feature_count": len(selected_categorical),
    "excluded_feature_count": len(excluded_columns),
    "excluded_features": excluded_columns,
    "selected_features": selected_columns,
    "numeric_features": selected_numeric,
    "categorical_features": selected_categorical,
    "target_definitions": {
        "four_class": {
            "column": "target_payout_label_id",
            "labels": {
                "0": "UNDER_10000",
                "1": "10000_TO_19999",
                "2": "20000_TO_49999",
                "3": "50000_PLUS"
            }
        },
        "binary_20000_plus": {
            "column": "target_is_20000_plus",
            "positive": "trifecta_payout >= 20000"
        },
        "binary_50000_plus": {
            "column": "target_is_50000_plus",
            "positive": "trifecta_payout >= 50000"
        }
    },
    "validation": {
        "unknown_type_column_count": len(unknown_type_columns),
        "unknown_type_columns": unknown_type_columns,
        "missing_selected_column_count": len(missing_selected_columns),
        "missing_selected_columns": missing_selected_columns,
        "leakage_candidate_count": len(leakage_candidates),
        "leakage_candidates": leakage_candidates
    }
}

with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump(schema, f, ensure_ascii=False, indent=2)

print()
print("=== 199 結果 ===")
print(f"元の特徴量数: {len(feature_columns)}")
print(f"正式採用特徴量数: {len(selected_columns)}")
print(f"正式採用 数値特徴量数: {len(selected_numeric)}")
print(f"正式採用 カテゴリ特徴量数: {len(selected_categorical)}")
print(f"除外特徴量数: {len(excluded_columns)}")
print(f"型不明列数: {len(unknown_type_columns)}")
print(f"選択列欠落数: {len(missing_selected_columns)}")
print(f"結果漏洩候補数: {len(leakage_candidates)}")

print()
print("=== 除外特徴量 ===")
if excluded_columns:
    for col in excluded_columns:
        print(f"  {col}")
else:
    print("  なし")

print()
print("=== 正式採用 数値特徴量 先頭20列 ===")
for col in selected_numeric[:20]:
    print(f"  {col}")

print()
print("=== 正式採用 カテゴリ特徴量 先頭20列 ===")
for col in selected_categorical[:20]:
    print(f"  {col}")

if unknown_type_columns:
    print()
    print("=== 型不明列 ===")
    for col in unknown_type_columns:
        print(f"  {col}")

if missing_selected_columns:
    print()
    print("=== 選択列欠落 ===")
    for col in missing_selected_columns:
        print(f"  {col}")

if leakage_candidates:
    print()
    print("=== 結果漏洩候補 ===")
    for col in leakage_candidates:
        print(f"  {col}")

print()
print(f"保存完了: {OUTPUT_FILE}")
print("=== 199 完了 ===")
