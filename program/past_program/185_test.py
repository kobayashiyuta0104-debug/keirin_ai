import json
from pathlib import Path
from collections import Counter, defaultdict
from urllib.parse import urlparse, parse_qs

print("=== 185 JSJ006通信ルート・encp集中解析テスト ===")

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "181_verified_jsj006_capture.json"
OUTPUT_FILE = BASE_DIR / "185_jsj006_route_analysis.json"

def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def normalize_captures(raw):
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        if isinstance(raw.get("captures"), list):
            return raw["captures"]
        result = []
        for key, value in raw.items():
            if isinstance(value, dict):
                item = dict(value)
                item.setdefault("race_key", key)
                result.append(item)
        return result
    return []

def walk(obj, path="$"):
    if isinstance(obj, dict):
        for key, value in obj.items():
            child = f"{path}.{key}"
            yield child, key, value
            yield from walk(value, child)
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            yield from walk(value, f"{path}[{i}]")

def short(value, limit=1000):
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False)
    else:
        text = str(value)
    return text if len(text) <= limit else text[:limit] + "...<truncated>"

raw = load_json(INPUT_FILE)
captures = normalize_captures(raw)

print(f"解析対象capture数: {len(captures)}")
if not captures:
    raise RuntimeError("captureを認識できませんでした。")

route_records = []
url_counter = Counter()
method_counter = Counter()
query_key_counter = Counter()
query_values = defaultdict(list)
special_paths = defaultdict(list)
all_key_names = Counter()

SPECIAL_WORDS = (
    "enc", "prm", "param", "url", "racebasic",
    "kaisai", "keirinjo", "jocode", "racecode",
    "raceno", "race_no", "date"
)

for capture in captures:
    race_key = capture.get("race_key")
    request_url = capture.get("request_url")
    request_method = capture.get("request_method")
    request_post_data = capture.get("request_post_data")

    method_counter[str(request_method)] += 1

    parsed_info = None
    if request_url:
        parsed = urlparse(request_url)
        query = parse_qs(parsed.query, keep_blank_values=True)
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        url_counter[base_url] += 1

        parsed_info = {
            "base_url": base_url,
            "raw_query": parsed.query,
            "query": query,
        }

        for key, values in query.items():
            query_key_counter[key] += 1
            for value in values:
                query_values[key].append({
                    "race_key": race_key,
                    "value": value,
                })

    hits = []
    for path, key, value in walk(capture):
        all_key_names[key] += 1
        key_lower = key.lower()
        path_lower = path.lower()

        if any(word in key_lower or word in path_lower for word in SPECIAL_WORDS):
            # 選手の過去成績kkrParameter大量表示は除外
            if "resultinfosubdata" in path_lower and key_lower == "kkrparameter":
                continue
            if "tyo4infosubdata.kkparameter" in path_lower:
                continue

            item = {
                "path": path,
                "key": key,
                "value": short(value),
                "value_type": type(value).__name__,
            }
            hits.append(item)
            special_paths[path].append({
                "race_key": race_key,
                "value": short(value),
            })

    route_records.append({
        "race_key": race_key,
        "venue": capture.get("venue"),
        "race_no": capture.get("race_no"),
        "request_method": request_method,
        "request_url": request_url,
        "request_post_data": request_post_data,
        "parsed_request_url": parsed_info,
        "special_hits": hits,
    })

path_summary = []
for path, rows in special_paths.items():
    unique = []
    seen = set()
    for row in rows:
        value = row["value"]
        if value not in seen:
            seen.add(value)
            unique.append(row)

    path_summary.append({
        "path": path,
        "occurrence_count": len(rows),
        "unique_value_count": len(unique),
        "changes": len(unique) > 1,
        "samples": unique[:10],
    })

path_summary.sort(key=lambda x: (-x["unique_value_count"], x["path"]))

query_summary = {}
for key, rows in query_values.items():
    unique = []
    seen = set()
    for row in rows:
        if row["value"] not in seen:
            seen.add(row["value"])
            unique.append(row)

    query_summary[key] = {
        "occurrence_count": len(rows),
        "unique_value_count": len(unique),
        "samples": unique[:20],
    }

result = {
    "capture_count": len(captures),
    "request_methods": dict(method_counter),
    "base_urls": dict(url_counter),
    "query_key_counts": dict(query_key_counter),
    "query_summary": query_summary,
    "special_path_summary": path_summary,
    "all_key_names": dict(all_key_names),
    "records": route_records,
}

with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print()
print("=== REQUEST METHOD ===")
for key, count in method_counter.items():
    print(f"{key}: {count}件")

print()
print("=== JSJ006 REQUEST BASE URL ===")
for url, count in url_counter.most_common():
    print(f"{count}件: {url}")

print()
print("=== URL QUERY KEY ===")
if not query_key_counter:
    print("URLクエリなし")
else:
    for key, count in query_key_counter.most_common():
        info = query_summary[key]
        print(f"{key}: 出現{count}件 / 値{info['unique_value_count']}種類")
        for sample in info["samples"][:5]:
            print(f"  {sample['race_key']} -> {sample['value']}")

print()
print("=== enc / prm / param / url / race系 特別候補 TOP50 ===")
for item in path_summary[:50]:
    print(
        f"[値{item['unique_value_count']}種類 / 出現{item['occurrence_count']}件] "
        f"{item['path']}"
    )
    for sample in item["samples"][:3]:
        print(f"  {sample['race_key']} -> {sample['value']}")
    print()

print("=== 全JSONキー名から enc / prm / param / url を含むもの ===")
found = False
for key, count in sorted(all_key_names.items()):
    lower = key.lower()
    if any(word in lower for word in ("enc", "prm", "param", "url")):
        found = True
        print(f"{key}: {count}回")
if not found:
    print("該当キー名なし")

print()
print(f"保存完了: {OUTPUT_FILE}")
print("=== 185 完了 ===")
