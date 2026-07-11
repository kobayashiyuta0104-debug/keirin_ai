import json
from pathlib import Path

BASE = Path(r"C:\競輪AI")
SRC = BASE / "205_manual_historical_navigation_capture.json"
OUT = BASE / "209_jsj057_082_structure_analysis.json"

print("=== 209 JSJ057 / JSJ082 過去開催入口地図 構造解析 ===")

with open(SRC, "r", encoding="utf-8") as f:
    root = json.load(f)

targets = []

def walk(x, path="$"):
    if isinstance(x, dict):
        t = x.get("type")
        data = x.get("data")
        if t in ("JSJ057", "JSJ082"):
            targets.append({"type": t, "path": path, "data": data})
        for k, v in x.items():
            walk(v, f"{path}.{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            walk(v, f"{path}[{i}]")

walk(root)

print(f"対象capture数: {len(targets)}")

KEYWORDS = ("enc", "prm", "para", "url", "kj", "jo", "race", "kaisai", "kday", "date", "name", "txt")

def flatten(x, path="$", out=None):
    if out is None:
        out = []
    if isinstance(x, dict):
        for k, v in x.items():
            p = f"{path}.{k}"
            out.append((p, k, v))
            flatten(v, p, out)
    elif isinstance(x, list):
        for i, v in enumerate(x):
            flatten(v, f"{path}[{i}]", out)
    return out

result = []

for cap in targets:
    t = cap["type"]
    data = cap["data"]
    print()
    print("=" * 80)
    print(f"TYPE: {t}")
    print(f"PATH: {cap['path']}")
    print(f"DATA TYPE: {type(data).__name__}")

    if isinstance(data, dict):
        print("TOP KEYS:", list(data.keys()))
    elif isinstance(data, list):
        print("LIST COUNT:", len(data))
        if data and isinstance(data[0], dict):
            print("FIRST KEYS:", list(data[0].keys()))

    flat = flatten(data)
    hits = []
    for p, k, v in flat:
        kl = str(k).lower()
        if any(word in kl for word in KEYWORDS):
            if not isinstance(v, (dict, list)):
                hits.append((p, v))

    print()
    print(f"特別候補数: {len(hits)}")
    for p, v in hits[:300]:
        print(f"{p} -> {v}")

    # 43文字前後の暗号パラメータ候補
    token_hits = []
    for p, k, v in flat:
        if isinstance(v, str) and 35 <= len(v) <= 60:
            if all(c.isalnum() or c in "-_" for c in v):
                token_hits.append((p, v))

    print()
    print(f"暗号パラメータ候補数: {len(token_hits)}")
    for p, v in token_hits[:200]:
        print(f"{p} -> {v}")

    result.append({
        "type": t,
        "capture_path": cap["path"],
        "data_type": type(data).__name__,
        "top_keys": list(data.keys()) if isinstance(data, dict) else None,
        "special_hits": [{"path": p, "value": v} for p, v in hits],
        "token_hits": [{"path": p, "value": v} for p, v in token_hits],
    })

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print()
print("保存完了:", OUT)
print("=== 209 完了 ===")
