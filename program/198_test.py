import json
from collections import Counter, defaultdict
from pathlib import Path

print("=== 198 AI入力特徴量 品質診断テスト ===")

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "197_model_ready_dataset.json"
OUTPUT_FILE = BASE_DIR / "198_feature_quality_report.json"

with INPUT_FILE.open("r", encoding="utf-8") as f:
    raw = json.load(f)

rows = raw.get("rows", [])
feature_columns = raw.get("feature_columns", [])

report = []
constant_columns = []
all_missing_columns = []
high_missing_columns = []
categorical_columns = []
numeric_columns = []

for col in feature_columns:
    values = [row.get(col) for row in rows]
    non_missing = [v for v in values if v is not None and v != ""]
    missing_count = len(values) - len(non_missing)
    missing_rate = (missing_count / len(values) * 100) if values else 0

    unique_repr = {repr(v) for v in non_missing}
    unique_count = len(unique_repr)

    numeric_count = sum(
        1 for v in non_missing
        if isinstance(v, (int, float)) and not isinstance(v, bool)
    )
    is_numeric = bool(non_missing) and numeric_count == len(non_missing)

    item = {
        "column": col,
        "missing_count": missing_count,
        "missing_rate_percent": round(missing_rate, 2),
        "non_missing_count": len(non_missing),
        "unique_count": unique_count,
        "type_guess": "numeric" if is_numeric else "categorical",
    }
    report.append(item)

    if len(non_missing) == 0:
        all_missing_columns.append(col)
    elif unique_count <= 1:
        constant_columns.append(col)

    if missing_rate >= 20:
        high_missing_columns.append(item)

    if is_numeric:
        numeric_columns.append(col)
    else:
        categorical_columns.append(col)

target_counts = {
    "payout_label": dict(Counter(row.get("target_payout_label") for row in rows)),
    "is_20000_plus": dict(Counter(str(row.get("target_is_20000_plus")) for row in rows)),
    "is_50000_plus": dict(Counter(str(row.get("target_is_50000_plus")) for row in rows)),
}

category_examples = {}
for col in categorical_columns:
    counts = Counter(
        str(row.get(col))
        for row in rows
        if row.get(col) is not None and row.get(col) != ""
    )
    category_examples[col] = counts.most_common(10)

with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump({
        "row_count": len(rows),
        "feature_count": len(feature_columns),
        "numeric_feature_count": len(numeric_columns),
        "categorical_feature_count": len(categorical_columns),
        "all_missing_column_count": len(all_missing_columns),
        "all_missing_columns": all_missing_columns,
        "constant_column_count": len(constant_columns),
        "constant_columns": constant_columns,
        "high_missing_column_count": len(high_missing_columns),
        "high_missing_columns": high_missing_columns,
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "category_examples": category_examples,
        "target_counts": target_counts,
        "feature_report": report,
    }, f, ensure_ascii=False, indent=2)

print()
print("=== 198 結果 ===")
print(f"レース行数: {len(rows)}")
print(f"AI入力特徴量数: {len(feature_columns)}")
print(f"数値特徴量数: {len(numeric_columns)}")
print(f"カテゴリ特徴量数: {len(categorical_columns)}")
print(f"全件欠損列数: {len(all_missing_columns)}")
print(f"固定値列数: {len(constant_columns)}")
print(f"欠損率20%以上列数: {len(high_missing_columns)}")

print()
print("=== 全件欠損列 ===")
if all_missing_columns:
    for col in all_missing_columns:
        print(f"  {col}")
else:
    print("  なし")

print()
print("=== 固定値列 ===")
if constant_columns:
    for col in constant_columns:
        print(f"  {col}")
else:
    print("  なし")

print()
print("=== 欠損率20%以上列 先頭30件 ===")
if high_missing_columns:
    for item in high_missing_columns[:30]:
        print(
            f"  {item['column']} / "
            f"欠損{item['missing_count']}件 / "
            f"{item['missing_rate_percent']}%"
        )
else:
    print("  なし")

print()
print("=== カテゴリ特徴量 先頭20列 ===")
for col in categorical_columns[:20]:
    print(f"  {col} -> {category_examples.get(col)}")

print()
print("=== 正解ラベル分布 ===")
print(f"4分類: {target_counts['payout_label']}")
print(f"2万円以上: {target_counts['is_20000_plus']}")
print(f"5万円以上: {target_counts['is_50000_plus']}")

print()
print(f"保存完了: {OUTPUT_FILE}")
print("=== 198 完了 ===")
