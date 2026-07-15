import json
from pathlib import Path

BASE = Path(r"C:\競輪AI")
SRC = BASE / "205_manual_historical_navigation_capture.json"
OUT = BASE / "208_jsj001_map_structure_analysis.json"

print("=== 208 JSJ001 過去開催・全レース地図 構造解析 ===")

with open(SRC, "r", encoding="utf-8") as f:
    root = json.load(f)

c0201 = None

def walk(x):
    global c0201
    if isinstance(x, dict):
        if isinstance(x.get("C0201data"), dict):
            c0201 = x["C0201data"]
        for v in x.values():
            walk(v)
    elif isinstance(x, list):
        for v in x:
            walk(v)

walk(root)

if not c0201:
    raise RuntimeError("C0201data が見つかりません")

kaisai = c0201.get("C0201kaisai", [])
races = c0201.get("C0201race", [])

print(f"開催件数: {len(kaisai)}")
print(f"レース件数: {len(races)}")

print()
print("=== C0201data TOP KEYS ===")
print(list(c0201.keys()))

print()
print("=== 開催データ詳細 ===")
for i, x in enumerate(kaisai, 1):
    print()
    print(f"[開催 {i}]")
    for k, v in x.items():
        print(f"  {k}: {v}")

print()
print("=== レースデータ詳細 ===")
for i, x in enumerate(races, 1):
    print()
    print(f"[レース {i}]")
    for k, v in x.items():
        print(f"  {k}: {v}")

# キーごとの値種類を整理
def summarize(rows):
    keys = sorted({k for row in rows if isinstance(row, dict) for k in row.keys()})
    result = {}
    for k in keys:
        vals = []
        for row in rows:
            if k in row:
                val = row[k]
                if val not in vals:
                    vals.append(val)
        result[k] = vals
    return result

kaisai_summary = summarize(kaisai)
race_summary = summarize(races)

print()
print("=== 開催キー別 値種類 ===")
for k, vals in kaisai_summary.items():
    print(f"{k}: {len(vals)}種類")
    for v in vals[:20]:
        print(f"  {v}")

print()
print("=== レースキー別 値種類 ===")
for k, vals in race_summary.items():
    print(f"{k}: {len(vals)}種類")
    for v in vals[:20]:
        print(f"  {v}")

with open(OUT, "w", encoding="utf-8") as f:
    json.dump({
        "source": str(SRC),
        "top_keys": list(c0201.keys()),
        "kaisai_count": len(kaisai),
        "race_count": len(races),
        "kaisai": kaisai,
        "races": races,
        "kaisai_key_summary": kaisai_summary,
        "race_key_summary": race_summary,
    }, f, ensure_ascii=False, indent=2)

print()
print("保存完了:", OUT)
print("=== 208 完了 ===")
