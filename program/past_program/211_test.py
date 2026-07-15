import json
from pathlib import Path
from collections import Counter

BASE = Path(r"C:\競輪AI")
SRC = BASE / "210_jsj057_082_response_capture.json"
OUT = BASE / "211_jsj057_kinfo_structure_analysis.json"

print("=== 211 JSJ057 kInfo 開催会場入口地図 構造解析 ===")

with open(SRC, "r", encoding="utf-8") as f:
    captures = json.load(f)

jsj057 = next((x for x in captures if x.get("type") == "JSJ057"), None)
if not jsj057:
    raise RuntimeError("JSJ057 capture が見つかりません")

data = jsj057.get("data") or {}
kinfo = data.get("kInfo") or []

print("kInfo件数:", len(kinfo))
print("JSJ057 TOP KEYS:", list(data.keys()))

all_keys = Counter()

for i, item in enumerate(kinfo, 1):
    if not isinstance(item, dict):
        print(f"[{i}] dictではありません: {type(item).__name__}")
        continue

    all_keys.update(item.keys())

    print()
    print("=" * 80)
    print(f"[開催 {i}]")
    print("KEYS:", list(item.keys()))

    for k, v in item.items():
        if isinstance(v, (dict, list)):
            if isinstance(v, list):
                print(f"  {k}: LIST 件数={len(v)}")
                if v and isinstance(v[0], dict):
                    print(f"    FIRST KEYS: {list(v[0].keys())}")
            else:
                print(f"  {k}: DICT KEYS={list(v.keys())}")
        else:
            print(f"  {k}: {v}")

print()
print("=== kInfo 全キー 出現回数 ===")
for k, cnt in all_keys.most_common():
    print(f"{k}: {cnt}")

# 暗号パラメータらしい値を再帰探索
def walk(x, path="$", hits=None):
    if hits is None:
        hits = []
    if isinstance(x, dict):
        for k, v in x.items():
            p = f"{path}.{k}"
            if isinstance(v, str) and 35 <= len(v) <= 60:
                if all(c.isalnum() or c in "-_" for c in v):
                    hits.append({"path": p, "key": k, "value": v})
            walk(v, p, hits)
    elif isinstance(x, list):
        for i, v in enumerate(x):
            walk(v, f"{path}[{i}]", hits)
    return hits

token_hits = walk(kinfo, "$.kInfo")

print()
print("=== 暗号パラメータ候補 ===")
print("件数:", len(token_hits))
for hit in token_hits:
    print(f"{hit['path']} -> {hit['value']}")

result = {
    "kinfo_count": len(kinfo),
    "top_keys": list(data.keys()),
    "key_counts": dict(all_keys),
    "kInfo": kinfo,
    "token_hits": token_hits,
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print()
print("保存完了:", OUT)
print("=== 211 完了 ===")
