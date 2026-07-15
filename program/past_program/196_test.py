import json
import csv
from collections import Counter
from pathlib import Path

print("=== 196 3連単配当 教師ラベル作成テスト ===")

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "195_ai_training_rows.json"
JSON_OUTPUT = BASE_DIR / "196_labeled_ai_training_rows.json"
CSV_OUTPUT = BASE_DIR / "196_labeled_ai_training_rows.csv"


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def payout_label(payout):
    if payout is None:
        return None, None

    payout = int(payout)

    if payout < 10000:
        return 0, "UNDER_10000"
    elif payout < 20000:
        return 1, "10000_TO_19999"
    elif payout < 50000:
        return 2, "20000_TO_49999"
    else:
        return 3, "50000_PLUS"


raw = load_json(INPUT_FILE)
rows = raw.get("rows", [])

labeled_rows = []
label_counter = Counter()
problems = []

for row in rows:
    new_row = dict(row)
    payout = row.get("trifecta_payout")

    label_id, label_name = payout_label(payout)

    new_row["payout_label_id"] = label_id
    new_row["payout_label"] = label_name
    new_row["is_20000_plus"] = 1 if payout is not None and int(payout) >= 20000 else 0
    new_row["is_50000_plus"] = 1 if payout is not None and int(payout) >= 50000 else 0

    if label_name is None:
        problems.append({
            "race_key": row.get("race_key"),
            "problem": "PAYOUT_LABEL_MISSING",
            "trifecta_payout": payout,
        })
    else:
        label_counter[label_name] += 1

    labeled_rows.append(new_row)

columns = []
seen = set()
for row in labeled_rows:
    for key in row.keys():
        if key not in seen:
            seen.add(key)
            columns.append(key)

summary = {
    "UNDER_10000": label_counter["UNDER_10000"],
    "10000_TO_19999": label_counter["10000_TO_19999"],
    "20000_TO_49999": label_counter["20000_TO_49999"],
    "50000_PLUS": label_counter["50000_PLUS"],
}

with JSON_OUTPUT.open("w", encoding="utf-8") as f:
    json.dump({
        "row_count": len(labeled_rows),
        "column_count": len(columns),
        "label_definition": {
            "0": "UNDER_10000",
            "1": "10000_TO_19999",
            "2": "20000_TO_49999",
            "3": "50000_PLUS",
        },
        "label_summary": summary,
        "problem_count": len(problems),
        "problems": problems,
        "columns": columns,
        "rows": labeled_rows,
    }, f, ensure_ascii=False, indent=2)

with CSV_OUTPUT.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=columns)
    writer.writeheader()
    writer.writerows(labeled_rows)

print()
print("=== 196 結果 ===")
print(f"学習用レース行数: {len(labeled_rows)}")
print(f"列数: {len(columns)}")
print(f"10,000円未満: {summary['UNDER_10000']}")
print(f"10,000～19,999円: {summary['10000_TO_19999']}")
print(f"20,000～49,999円: {summary['20000_TO_49999']}")
print(f"50,000円以上: {summary['50000_PLUS']}")
print(f"20,000円以上レース: {sum(r['is_20000_plus'] for r in labeled_rows)}")
print(f"50,000円以上レース: {sum(r['is_50000_plus'] for r in labeled_rows)}")
print(f"問題件数: {len(problems)}")
print(f"JSON保存: {JSON_OUTPUT}")
print(f"CSV保存: {CSV_OUTPUT}")

print()
print("=== 各配当帯サンプル 最大3件 ===")
for label_name in [
    "UNDER_10000",
    "10000_TO_19999",
    "20000_TO_49999",
    "50000_PLUS",
]:
    print()
    print(f"[{label_name}]")
    samples = [r for r in labeled_rows if r.get("payout_label") == label_name][:3]
    if not samples:
        print("  該当なし")
    for row in samples:
        print(
            f"  {row.get('race_key')} / "
            f"{row.get('trifecta_combination')} / "
            f"{row.get('trifecta_payout')}円 / "
            f"label_id={row.get('payout_label_id')}"
        )

if problems:
    print()
    print("=== 問題一覧 ===")
    for problem in problems:
        print(problem)

print()
print("=== 196 完了 ===")
