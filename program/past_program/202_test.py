import json
from pathlib import Path
from collections import Counter

print("=== 202 JSJ004 過去レース地図構造解析テスト ===")

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "201_historical_json_route_capture.json"
OUTPUT_FILE = BASE_DIR / "202_jsj004_historical_map_analysis.json"

with INPUT_FILE.open("r", encoding="utf-8") as f:
    raw = json.load(f)

captures = raw.get("captures", [])
jsj004_items = [x for x in captures if x.get("type") == "JSJ004"]

analysis = {
    "jsj004_count": len(jsj004_items),
    "items": [],
}

def walk(obj, path="$", out=None):
    if out is None:
        out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}"
            out.append({
                "path": p,
                "key": k,
                "value_type": type(v).__name__,
                "value": v if not isinstance(v, (dict, list)) else None,
                "length": len(v) if isinstance(v, (dict, list)) else None,
            })
            walk(v, p, out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk(v, f"{path}[{i}]", out)
    return out

special_words = [
    "race", "url", "kaisai", "jyo", "jo", "kjcd", "bkcd",
    "kday", "date", "enc", "prm", "param", "no", "round"
]

for idx, item in enumerate(jsj004_items, 1):
    data = item.get("data")
    paths = walk(data)
    special = []
    for x in paths:
        key_lower = str(x["key"]).lower()
        path_lower = str(x["path"]).lower()
        if any(word in key_lower or word in path_lower for word in special_words):
            special.append(x)

    item_result = {
        "index": idx,
        "request_url": item.get("url"),
        "top_keys": list(data.keys()) if isinstance(data, dict) else None,
        "raceUrl": data.get("raceUrl") if isinstance(data, dict) else None,
        "kaisaiData": data.get("kaisaiData") if isinstance(data, dict) else None,
        "special_paths": special,
    }
    analysis["items"].append(item_result)

with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump(analysis, f, ensure_ascii=False, indent=2)

print()
print("=== 202 結果 ===")
print(f"201通信数: {len(captures)}")
print(f"JSJ004数: {len(jsj004_items)}")

for idx, result in enumerate(analysis["items"], 1):
    print()
    print("=" * 70)
    print(f"JSJ004 #{idx}")
    print(f"REQUEST URL: {result['request_url']}")
    print(f"TOP KEYS: {result['top_keys']}")

    race_url = result["raceUrl"]
    print()
    print("=== raceUrl ===")
    print(json.dumps(race_url, ensure_ascii=False, indent=2))

    kaisai_data = result["kaisaiData"]
    print()
    print("=== kaisaiData ===")
    print(json.dumps(kaisai_data, ensure_ascii=False, indent=2))

    print()
    print("=== race/url/kaisai/日付/コード系パス ===")
    for x in result["special_paths"][:100]:
        if x["value"] is not None:
            value_text = repr(x["value"])
            if len(value_text) > 250:
                value_text = value_text[:250] + "..."
            print(f"{x['path']} -> {value_text}")
        else:
            print(
                f"{x['path']} -> "
                f"{x['value_type']} / 件数:{x['length']}"
            )

print()
print(f"保存完了: {OUTPUT_FILE}")
print("=== 202 完了 ===")
